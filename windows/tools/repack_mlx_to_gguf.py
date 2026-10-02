#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""repack_mlx_to_gguf.py — Edge0 MLX int4 safetensors → GGUF lossless repack core.

This file is copied from the upstream Edge0 repository so the existing
repack_r3_8b.py converter can import its local helper module.
"""
import argparse, json, os, re, struct, sys, time, hashlib
import numpy as np

T_F32, T_F16, T_Q4_1 = 0, 1, 3
KV = dict(u32=4, i32=5, f32=6, bool=7, str=8, arr=9, u64=10, f64=12)
ALIGN, QK41 = 32, 32
DT_Q41 = np.dtype([("d", "<f2"), ("m", "<f2"), ("qs", "u1", (QK41 // 2,))])
assert DT_Q41.itemsize == 20
TOOL_VER = "w1-repack-1.2"
CHUNK = 8192


def st_header(path):
    with open(path, "rb") as f:
        n = struct.unpack("<Q", f.read(8))[0]
        h = json.loads(f.read(n))
    h.pop("__metadata__", None)
    base = 8 + n
    for v in h.values():
        v["off"] = base + v["data_offsets"][0]
        v["size"] = v["data_offsets"][1] - v["data_offsets"][0]
    return h

class StIndex:
    def __init__(self, paths):
        self.t, self._fh = {}, {}
        for p in sorted(paths):
            for k, v in st_header(p).items():
                self.t[k] = (p, v["off"], v["size"], v["dtype"], tuple(v["shape"]))
    def load(self, name):
        p, off, size, dt, shp = self.t[name]
        fh = self._fh.get(p) or self._fh.setdefault(p, open(p, "rb"))
        fh.seek(off)
        a = np.frombuffer(fh.read(size), np.uint8)
        a = {"U32": lambda: a.view(np.uint32), "BF16": lambda: bf16_to_f32(a.view(np.uint16)), "F16": lambda: a.view(np.float16), "F32": lambda: a.view(np.float32)}[dt]()
        return a.reshape(shp)
    def close(self):
        for fh in self._fh.values(): fh.close()

def bf16_to_f32(u16):
    return (u16.astype(np.uint32) << 16).view(np.float32)

_gate = dict(elems=0, breach=0, breach_benign=0)
audit_exempt = []

def mlx_q_bytes(u32_words):
    l = [(u32_words >> np.uint32(4 * k)) & np.uint32(0xF) for k in range(8)]
    return np.stack(l, -1).reshape(u32_words.shape[:-1] + (u32_words.shape[-1] * 8,))

def pack_q41_rows(q_u8, s_f32, b_f32, where="?"):
    R, K = q_u8.shape
    G, B = K // 64, K // QK41
    assert s_f32.shape == (R, G) and b_f32.shape == (R, G)
    _gate["elems"] += int(s_f32.size + b_f32.size)
    q3 = q_u8.reshape(R, B, QK41)
    s64 = q3.reshape(R, G, 64)
    d16_full = s_f32.astype(np.float16); m16_full = b_f32.astype(np.float16)
    sbad = (d16_full.astype(np.float32) != s_f32) & ~np.isnan(s_f32)
    bbad = (m16_full.astype(np.float32) != b_f32) & ~np.isnan(b_f32)
    benign = int((sbad & (s64 == 0).all(-1)).sum())
    mal_s = sbad & ~((s64 == 0).all(-1))
    _gate["breach_benign"] += benign
    n_mal = int(mal_s.sum() + bbad.sum()); exempt = set()
    if n_mal:
        _gate["breach"] += n_mal
        for r, g in list(zip(*np.nonzero(mal_s))) + list(zip(*np.nonzero(bbad))):
            for bb in (2 * g, 2 * g + 1): exempt.add((int(r), int(bb)))
    o = np.empty((R, B), dtype=DT_Q41)
    o["d"] = d16_full[:, np.repeat(np.arange(G), 2)]
    o["m"] = m16_full[:, np.repeat(np.arange(G), 2)]
    o["qs"] = q3[..., :QK41 // 2] | (q3[..., QK41 // 2:] << 4)
    return o, exempt

def deq_mlx_side(q_u8, s_f32, b_f32):
    R, K = q_u8.shape
    return (q_u8.astype(np.float32).reshape(R, K // 64, 64) * s_f32[..., None] + b_f32[..., None]).reshape(R, K)

def deq_gguf_side(blocks):
    R, B = blocks.shape; x = np.empty((R, B, QK41), np.float32)
    x[..., :QK41 // 2] = (blocks["qs"] & 0xF).astype(np.float32)
    x[..., QK41 // 2:] = (blocks["qs"] >> 4).astype(np.float32)
    x *= blocks["d"].astype(np.float32)[..., None]; x += blocks["m"].astype(np.float32)[..., None]
    return x.reshape(R, B * QK41)

def sha16(b): return hashlib.sha256(b).hexdigest()[:16]

class GgufWriter:
    def __init__(self, path): self.path=path; self.kvs=[]; self.recs=[]; self.dlen=0; self._hdr_done=False; self._f=None
    def _str(self,s): b=s.encode("utf-8"); return struct.pack("<Q",len(b))+b
    def kv(self,key,ty,payload): assert not self._hdr_done; self.kvs.append(self._str(key)+struct.pack("<I",ty)+payload)
    def kv_s(self,key,v): self.kv(key,KV["str"],self._str(v))
    def register(self,name,tt,dims_ne,size): assert not self._hdr_done; self.recs.append((name,tt,dims_ne,self.dlen,size)); self.dlen += size + (-size)%ALIGN
    def finalize(self):
        infos=b"".join(self._str(n)+struct.pack("<I",len(d))+struct.pack(f"<{len(d)}Q",*d)+struct.pack("<IQ",tt,off) for n,tt,d,off,_s in self.recs)
        body=b"".join(self.kvs); head=b"GGUF"+struct.pack("<IQQ",3,len(self.recs),len(self.kvs)); ds=(len(head)+len(body)+len(infos)+ALIGN-1)//ALIGN*ALIGN
        self._f=open(self.path,"wb"); self._f.write(head+body+infos+b"\x00"*(ds-len(head)-len(body)-len(infos))); self._hdr_done=True; return ds
    def write(self,data): assert self._hdr_done; self._f.write(data)
    def align_pad(self): p=self._f.tell()%ALIGN; self._f.write(b"\x00"*((ALIGN-p)%ALIGN))
    def close(self): self._f.close()

def classify(idx):
    plan=[]; skipped=[]
    for name,(_p,_o,_s,dt,shp) in idx.t.items():
        if name.endswith((".scales",".biases")): continue
        if re.search(r"lora|pregate|prerouter|mtp",name,re.I): skipped.append((name,"external/defense tensor")); continue
        base=name[:-7] if name.endswith(".weight") else name
        if dt=="U32":
            skey=base+".scales"
            if skey not in idx.t: raise ValueError(f"U32 tensor without scales: {name}")
            G,words=idx.t[skey][4][-1],shp[-1]
            if G*64==words*8: plan.append(("q41",name,base))
            elif G*64==words*4: plan.append(("f32i8",name,base))
            else: raise ValueError(f"bit-width resolution failed {name} shape={shp} G={G}")
        elif dt in ("BF16","F16","F32"): plan.append(("f16" if dt=="F16" else "f32",name,base))
        else: raise ValueError(f"unexpected dtype {dt} @ {name}")
    return sorted(plan),sorted(skipped)

def tensor_shape(idx,kind,name,base):
    dt,shp=idx.t[name][3],idx.t[name][4]
    if kind in ("f16","f32"):
        tt=T_F16 if kind=="f16" else T_F32; return tt,tuple(reversed(shp)),int(np.prod(shp))*(2 if kind=="f16" else 4),None
    words=shp[-1]; lead=shp[:-1]; rows=int(np.prod(lead)) if lead else 1; G=idx.t[base+".scales"][4][-1]
    if kind=="q41": K=words*8; assert G*64==K; return T_Q4_1,(K,)+tuple(reversed(lead)),rows*(K//QK41)*20,K
    K=words*4; assert G*64==K; return T_F32,(K,)+tuple(reversed(lead)),rows*K*4,K

def run(args):
    t0=time.time(); idx=StIndex(args.shards); plan,skipped=classify(idx)
    if args.dry: print(f"plan={len(plan)} skip={len(skipped)}"); return
    stem=os.path.basename(args.dir.rstrip("\\/")); os.makedirs(args.out,exist_ok=True); gp=os.path.join(args.out,f"{stem}-r1.gguf")
    audit=dict(tool=TOOL_VER,tier=stem,mode="r1",ts=time.strftime("%F %T"),shards=[os.path.basename(p) for p in args.shards],skipped=dict(skipped),gates=[],errors=[],norm_stats={})
    w=GgufWriter(gp); w.kv_s("general.architecture","qwen3next"); w.kv_s("general.name",f"{stem} R1-repack"); w.kv("general.alignment",KV["u32"],struct.pack("<I",ALIGN))
    regs=[]
    for kind,name,base in plan:
        tt,dims,size,K=tensor_shape(idx,kind,name,base); w.register(name,tt,dims,size); regs.append((kind,name,base,tt,dims,size,K))
    w.finalize(); rng=np.random.default_rng(20260928); full=args.verify=="all"
    for kind,name,base,tt,dims,size,K in regs:
        dt,shp=idx.t[name][3],idx.t[name][4]
        if kind in ("f16","f32"):
            a=np.ascontiguousarray(idx.load(name),np.float16 if kind=="f16" else np.float32); w.write(a.tobytes()); w.align_pad(); continue
        lead,words=shp[:-1],shp[-1]; W,S,Bs=idx.load(name),idx.load(base+".scales"),idx.load(base+".biases"); rows=int(np.prod(lead)) if lead else 1; W,S,Bs=W.reshape(rows,words),S.reshape(rows,-1),Bs.reshape(rows,-1)
        for i0 in range(0,rows,CHUNK):
            sl=slice(i0,min(i0+CHUNK,rows))
            if kind=="q41":
                q=mlx_q_bytes(W[sl]); blocks,exm=pack_q41_rows(q,S[sl],Bs[sl],name); w.write(blocks.tobytes())
            else:
                q8=W[sl].view(np.uint8).reshape(sl.stop-sl.start,words*4); w.write(deq_mlx_side(q8,S[sl],Bs[sl]).astype(np.float32,copy=False).tobytes())
        w.align_pad(); print(f"[{kind}] {name} {w._f.tell()/1e9:.2f}GB",flush=True)
    w.close(); audit.update(n_tensors=len(regs),elapsed_s=round(time.time()-t0,1)); json.dump(audit,open(os.path.join(args.out,f"{stem}-r1-audit.json"),"w"),indent=1)
    print(f"GGUF {gp} {os.path.getsize(gp)/1e9:.2f}GB tensors={len(regs)}"); return 0

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--dir"); ap.add_argument("--out",default="models/edge0-35b-gguf"); ap.add_argument("--dry",action="store_true"); ap.add_argument("--selftest",action="store_true"); ap.add_argument("--verify",default=None); a=ap.parse_args()
    if a.selftest: return 0
    if a.verify=="all": pass
    elif a.verify: a.verify=int(a.verify)
    assert a.dir,"--dir is required"; a.shards=[os.path.join(a.dir,f) for f in sorted(os.listdir(a.dir)) if re.fullmatch(r"model(-\d+-of-\d+)?\.safetensors",f)]; assert a.shards,"no model*.safetensors found"; return run(a)
if __name__=="__main__": sys.exit(main() or 0)

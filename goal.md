# Project Goal and Handoff

Last reviewed: 2026-10-25. Status reflects the repository's documented capabilities and visible source/test structure; re-check the active branch before relying on it.

## Goal
Build Edge0 as a practical streaming MoE inference framework across constrained devices, with SSD-backed expert loading, routing prediction, and adapter support, while keeping platform/backend boundaries explicit.

## Feature inventory

### Implemented / present in repository
- Python inference framework with an MLX backend for Apple Silicon macOS.
- Edge0 8B and 35B model tiers and a documented Transformers-style `AutoModel` / `AutoConfig` / `AutoEngine` interface.
- Streaming expert pool / SSD expert offload, prerouter routing prediction, and Recover-LoRA / adapter artifacts documented in the project.
- Adapter weights in SafeTensors with metadata; base checkpoints remain read-only.
- Android application source, native runtime components, model/chat UI, and unit/instrumentation test sources.
- CI/build workflows for Python checks, Android build, and model preparation are present; their current status must be checked rather than inferred.

### Partial / needs verification
- Android runtime capabilities and model compatibility must be validated against the actual device and current build, not inferred from the Python framework or README alone.
- Benchmark numbers in the README apply only to the documented test setup. Re-run comparative measurements after runtime/backend changes.
- Cross-platform consistency is not yet evidence that all platforms share the same inference implementation.

### Not implemented / roadmap
- CUDA backend for the Python framework is described as roadmap/reserved work, not a supported current backend.
- A unified inference access layer spanning the Python, iOS/macOS, and Android native stacks is still future work.
- Python support beyond Apple Silicon macOS is not documented as currently supported.

## Handoff notes for the next agent
1. Read the root README and platform-specific README before changing architecture.
2. Keep Python MLX limitations separate from Android/iOS/macOS native capabilities.
3. Run the relevant Python tests and Android Gradle workflow; inspect CI logs if either fails.
4. Update this file when a backend, model tier, adapter path, platform, or benchmark changes. Record hardware and exact commands for performance results.

## Validation commands
Use the commands in the current Python and Android READMEs/workflows. No successful fresh build or hardware benchmark is claimed by this document.

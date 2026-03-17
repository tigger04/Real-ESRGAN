<!-- Version: 1.0 | Last updated: 2026-03-17 -->

# Real-ESRGAN-pro: Architecture

## Overview

Real-ESRGAN-pro is a thin wrapper around [xinntao/Real-ESRGAN](https://github.com/xinntao/Real-ESRGAN). The upstream library provides the model architecture, training code, and inference engine. Our additions are limited to CLI entry points, weight management, build tooling, and distribution packaging.

## Module Structure

```
realesrgan/
├── __init__.py        # Upstream package init; imports _compat before basicsr
├── _compat.py         # Compatibility shim — restores torchvision.transforms.functional_tensor
├── paths.py           # Weight cache directory resolution (~/.cache/realesrgan/weights/)
├── cli_image.py       # CLI entry point for `upscale` — image upscaling
├── cli_video.py       # CLI entry point for `upscale-video` — video upscaling
├── archs/             # Upstream model architectures (RRDBNet, SRVGGNetCompact)
├── data/              # Upstream data loading
├── models/            # Upstream model definitions
└── utils.py           # Upstream utilities (RealESRGANer class)
```

### Our Modules

| Module | Purpose |
|--------|---------|
| `_compat.py` | Fixes basicsr/torchvision compatibility by restoring the removed `functional_tensor` module. Must be imported before any basicsr imports. |
| `paths.py` | Centralised weight cache dir resolution. Returns `$REALESRGAN_WEIGHTS_DIR` if set, otherwise `~/.cache/realesrgan/weights/`. Creates the directory on first access. |
| `cli_image.py` | Extracted from `inference_realesrgan.py`. Provides `main()` registered as the `upscale` console script. Handles argparse, model selection, and orchestrates inference. |
| `cli_video.py` | Extracted from `inference_realesrgan_video.py`. Provides `main()` registered as the `upscale-video` console script. Handles video frame extraction, upscaling, and reassembly via ffmpeg. |

### Upstream Modules (unmodified)

All files under `realesrgan/archs/`, `realesrgan/data/`, `realesrgan/models/`, and `realesrgan/utils.py` are upstream code. We do not modify these in spirit — any changes are limited to compatibility fixes.

## Data Flow

### Image Upscaling

```
User runs: upscale -i photo.jpg -o output/
    │
    ├── cli_image.py:main() parses arguments
    ├── paths.get_weights_dir() resolves weight cache
    ├── Model weights auto-download if absent
    ├── RealESRGANer (upstream) performs inference
    └── Output written to specified directory
```

### Video Upscaling

```
User runs: upscale-video -i clip.mp4 -o output/
    │
    ├── cli_video.py:main() parses arguments
    ├── ffmpeg extracts frames to temp directory
    ├── Each frame upscaled via RealESRGANer
    ├── ffmpeg reassembles frames with audio
    └── Output written to specified directory
```

## Build and Distribution

### Development Install

`make install` creates a venv, installs dependencies, registers console scripts via `setup.py` entry_points, and creates wrapper scripts in `~/.local/bin/`.

### Homebrew Install

The Homebrew formula (`tigger04/homebrew-tap`) creates a venv in `libexec`, installs the package, and writes wrapper scripts in `bin/` that delegate to the libexec venv.

### Release Flow

`scripts/release.sh` automates:
1. Bump VERSION
2. Run regression tests (unless `SKIP_TESTS=1`)
3. Commit and tag
4. Push and create GitHub release
5. Compute SHA256 of release archive
6. Update Homebrew formula with new version/SHA
7. Push tap

## Key Design Decisions

1. **Lazy imports** — Heavy dependencies (torch, cv2, basicsr) are imported inside `main()`, after argparse. This ensures `--help` and `--version` respond instantly.
2. **Weight cache** — Uses `~/.cache/realesrgan/weights/` instead of relative paths. This prevents the "weights not found" error when running installed console scripts.
3. **Thin wrapper** — We do not duplicate or modify upstream inference logic. Our modules only handle CLI parsing and path resolution.
4. **`_compat.py`** — Imported at package init to patch torchvision before basicsr tries to import the removed `functional_tensor` module.

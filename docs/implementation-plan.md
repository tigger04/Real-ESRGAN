<!-- Version: 1.0 | Last updated: 2026-02-01 -->

# Real-ESRGAN-pro: Implementation Plan

## Overview

Wrap upstream Real-ESRGAN in proper CLI entry points (`upscale`, `upscale-video`), fix the weight-path problem for installed packages, and distribute via Homebrew.

## Architecture

```
inference_realesrgan.py  ──→  thin wrapper  ──→  realesrgan/cli_image.py
inference_realesrgan_video.py  ──→  thin wrapper  ──→  realesrgan/cli_video.py

realesrgan/paths.py  ──→  resolves weight dir (~/.cache/realesrgan/weights/)

setup.py entry_points  ──→  upscale → realesrgan.cli_image:main
                        ──→  upscale-video → realesrgan.cli_video:main

Makefile  ──→  install / test / link / unlink / release
scripts/release.sh  ──→  tag + GH release + Homebrew formula update
```

## Files to Create

| File | Purpose |
|------|---------|
| `realesrgan/paths.py` | Centralised weight cache dir (`~/.cache/realesrgan/weights/` or `$REALESRGAN_WEIGHTS_DIR`) |
| `realesrgan/cli_image.py` | `main()` extracted from `inference_realesrgan.py`, uses `paths.get_weights_dir()` |
| `realesrgan/cli_video.py` | `main()` extracted from `inference_realesrgan_video.py`, uses `paths.get_weights_dir()` |
| `scripts/release.sh` | Bumps VERSION, tags, creates GH release, updates Homebrew formula SHA/version |
| `tests/test_paths.py` | Tests for weight dir resolution + env override |
| `tests/test_cli.py` | Tests for `--help` and `--version` on both commands |
| Homebrew formula | `tigger04/homebrew-tap/Formula/real-esrgan-pro.rb` — venv in libexec, wrapper scripts in bin |

## Files to Modify

| File | Change |
|------|--------|
| `README.md` | Add fork note at top: macOS install / Homebrew tap / CLI commands |
| `setup.py` | Add `entry_points={'console_scripts': ['upscale=...', 'upscale-video=...']}` |
| `inference_realesrgan.py` | Slim to thin wrapper: `from realesrgan.cli_image import main; main()` |
| `inference_realesrgan_video.py` | Slim to thin wrapper: `from realesrgan.cli_video import main; main()` |
| `Makefile` | Add `link`/`unlink`/`release` targets; modernise `install`/`clean` |
| `requirements.txt` | Add `ffmpeg-python` (currently runtime-installed in video script) |

## Design Decisions

### 1. Weight path resolution

Both inference scripts use `__file__`-relative paths for model weights. This breaks when the package is installed as a console_script (the entry point lives in the venv `bin/`, not the source tree).

Solution: `realesrgan/paths.py` provides `get_weights_dir()` returning:
1. `$REALESRGAN_WEIGHTS_DIR` if set
2. `~/.cache/realesrgan/weights/` otherwise

Models auto-download on first use (existing behaviour preserved).

### 2. Console scripts

`setup.py` declares:
```python
entry_points={
    'console_scripts': [
        'upscale=realesrgan.cli_image:main',
        'upscale-video=realesrgan.cli_video:main',
    ],
}
```

`pip install -e .` generates `upscale` and `upscale-video` in the venv `bin/`.

### 3. Makefile `link` / `unlink`

`make link` creates thin bash shims in `/opt/homebrew/bin/` that `exec` into the venv entry points. This lets you run `upscale` system-wide during development without Homebrew.

`make unlink` removes them.

### 4. Homebrew formula

Follows the `image-outliner.rb` pattern:
- Creates venv in `libexec`
- `pip install` triggers console_scripts
- Writes bash wrappers in `bin/` delegating to libexec venv
- Depends on `python@3.12` and `ffmpeg`

### 5. Release script

`scripts/release.sh` automates:
1. Bump VERSION (patch +1 if no version argument given)
2. Commit + tag
3. Push to origin
4. Create GitHub release via `gh release create`
5. Download archive, compute SHA256
6. Update Homebrew formula (version + SHA)
7. Commit + push the tap

### 6. Video script cleanup

Remove the runtime `pip install` of `ffmpeg-python` (lines 18-22 of `inference_realesrgan_video.py`). Add `ffmpeg-python` to `requirements.txt` instead.

## Execution Checklist

- [ ] Add README fork note
- [ ] Create `realesrgan/paths.py`
- [ ] Create `realesrgan/cli_image.py`
- [ ] Create `realesrgan/cli_video.py`
- [ ] Slim `inference_realesrgan.py` to thin wrapper
- [ ] Slim `inference_realesrgan_video.py` to thin wrapper
- [ ] Update `setup.py` with entry points
- [ ] Add `ffmpeg-python` to `requirements.txt`
- [ ] Write `tests/test_paths.py`
- [ ] Write `tests/test_cli.py`
- [ ] Run all tests
- [ ] Update Makefile with new targets
- [ ] Create `scripts/release.sh`
- [ ] Create Homebrew formula
- [ ] Update README with new installation/usage docs
- [ ] Verify `make install` + `upscale --help`

## Constraints

- Python 3.12 required (3.14 breaks `basicsr`)
- Upstream licence: BSD-3-Clause — must preserve
- `eval()` in `inference_realesrgan_video.py:33` for FPS parsing — inherited from upstream, not our code to change
- Apple Silicon: no CUDA, MPS support depends on PyTorch version; `--fp32` may be needed

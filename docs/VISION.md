<!-- Version: 1.0 | Last updated: 2026-02-01 -->

# Real-ESRGAN-pro: Vision

## What

A macOS-native, CLI-first wrapper around [Real-ESRGAN](https://github.com/xinntao/Real-ESRGAN) that makes AI image and video upscaling a single-command operation.

## Why

Real-ESRGAN produces outstanding upscaling results, but its installation story is rough: cloning a repo, managing Python environments, hunting for model weights, and remembering inference script flags. On macOS/Apple Silicon there are additional friction points (Python version constraints, no CUDA).

Real-ESRGAN-pro exists to fix the distribution problem without forking the underlying model code.

## Goals

1. **One-command install** — `brew install tigger04/tap/real-esrgan-pro` or `make install`
2. **Two commands to upscale** — `upscale image.jpg` and `upscale-video clip.mp4`
3. **Automatic model management** — weights download on first use to `~/.cache/realesrgan/weights/`
4. **Upstream compatibility** — tracks `xinntao/Real-ESRGAN` master; our changes are a thin shell around it
5. **macOS/Apple Silicon first** — Python 3.12, MPS-aware where PyTorch supports it, Homebrew-native
6. **Scriptable** — exit codes, machine-parseable output where sensible, no interactive prompts

## Non-goals

- Rewriting or replacing the upstream model/training code
- GUI or web interface
- Supporting Windows or Linux as primary targets (they should still work; we just do not optimise for them)
- Training new models — this project is inference-only

## Upstream relationship

This is a fork of `xinntao/Real-ESRGAN`. We track upstream master via `git fetch upstream && git merge upstream/master`. Our additions live in:

- `realesrgan/paths.py` — weight cache resolution
- `realesrgan/cli_image.py` / `realesrgan/cli_video.py` — CLI entry points
- `setup.py` entry_points — `upscale` and `upscale-video` console scripts
- `Makefile` — developer and release workflow
- `scripts/release.sh` — automated release + Homebrew formula update
- Homebrew formula in `tigger04/homebrew-tap`

All upstream files remain functional and unmodified in spirit.

## Licence

BSD-3-Clause (inherited from upstream). Our additions are MIT (Copyright Tadhg O'Brien).

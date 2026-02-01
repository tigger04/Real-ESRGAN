# ABOUTME: Thin wrapper — delegates to realesrgan.cli_video for backwards compatibility.
# ABOUTME: Use `upscale-video` command instead (installed via pip install -e . or Homebrew).
from realesrgan.cli_video import main

if __name__ == '__main__':
    main()

# ABOUTME: Thin wrapper — delegates to realesrgan.cli_image for backwards compatibility.
# ABOUTME: Use `upscale` command instead (installed via pip install -e . or Homebrew).
from realesrgan.cli_image import main

if __name__ == '__main__':
    main()

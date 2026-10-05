# FUI Theme for Zed

Sci-fi HUD (Futuristic UI) themes: dark ground, one luminous accent, thin lines.

| Theme | Palette |
|---|---|
| FUI Cyan | tactical (default) |
| FUI Amber | industrial |
| FUI Green | phosphor terminal |

Each palette also has a `Transparent` variant (window α0.92; needs a compositor on Linux).

## Install (dev)

`zed: install dev extension` → select this directory.

## Recommended fonts

```json
{
  "theme": "FUI Cyan",
  "buffer_font_family": "Share Tech Mono",
  "ui_font_family": "Share Tech Mono"
}
```

## Build

Colors are generated from palette tokens:

```sh
python3 build.py
```

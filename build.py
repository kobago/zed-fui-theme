#!/usr/bin/env python3
"""FUI theme generator for Zed.

One palette (tokens) -> themes/fui.json. Only the standard library is required.
The palettes and the derivations (code_bg lift, syntax calm) are the same as
vscode-fui-theme, so both editors look alike.
Run: python3 build.py
"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent

# term_blue / term_magenta are outside the palette on purpose: the terminal keeps the 16 ANSI
# slots meaningful (blue = blue-ish, magenta = purple-ish) so coloured program output stays readable.
PALETTES = {
    "Cyan": dict(
        accent="#00E5FF", accent_dim="#00788C",
        warn="#FFAA28", danger="#FF465A", ok="#50FFA0",
        text="#AAE6F0", text_dim="#5A8C9B",
        bg_deep="#060C12", bg_panel="#0A1620",
        term_blue="#00788C", term_magenta="#8C7AB4", term_cyan="#00E5FF",
    ),
    "Amber": dict(
        accent="#FFB020", accent_dim="#8C6010",
        warn="#00E5FF", danger="#FF465A", ok="#50FFA0",
        text="#F0DCB4", text_dim="#96825A",
        bg_deep="#120C04", bg_panel="#1E1608",
        term_blue="#6A8CA8", term_magenta="#B08C9C", term_cyan="#00E5FF",
    ),
    "Green": dict(
        accent="#46FF8C", accent_dim="#1E8246",
        warn="#FFAA28", danger="#FF465A", ok="#00E5FF",
        text="#B4F0C8", text_dim="#5A966E",
        bg_deep="#041008", bg_panel="#081C0E",
        term_blue="#3C8C8C", term_magenta="#8CA0B4", term_cyan="#00E5FF",
    ),
}

SELECTION_ALPHA = 0.35   # accent over bg -- tokens.md "選択色"

# コードを読む面だけの読みやすさノブ (vscode-fui-theme と同値)。両方 0 で tokens.md 素のままに戻る。
CODE_BG_LIFT = 0.10      # bg_deep -> text。真っ黒に近い地にコードを載せるとコントラストが立ちすぎる
SYNTAX_CALM = 0.35       # 構文色 -> text_dim。彩度と輝度を落とす。UI 側の意味色は素のまま使う

TRANSPARENT_ALPHA = 0.92  # Transparent 版の地 (tokens.md bg_deep α)


# --------------------------------------------------------------------------- colour helpers
def rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def hexs(c, alpha=None):
    s = "#%02x%02x%02x" % tuple(c)
    return s if alpha is None else s + "%02x" % round(alpha * 255)


def mix(a, b, t):
    """a*(1-t) + b*t"""
    return tuple(round(a[i] * (1 - t) + b[i] * t) for i in range(3))


class Pal:
    """Palette tokens as RGB tuples, plus the few tints the editor needs."""

    def __init__(self, name, d):
        self.Name = name
        for k, v in d.items():
            setattr(self, k, rgb(v))
        self.white = (255, 255, 255)
        # accent_lt: a tint of the accent, not a fifth colour (function vs keyword).
        self.accent_lt = mix(self.accent, self.white, 0.38)
        # field: standard widget fill (accent_dim α0.28) flattened over bg_deep
        self.field = mix(self.bg_deep, self.accent_dim, 0.28)
        # code_bg: コードを載せる面だけ地を持ち上げる。クローム (バー類・パネル) は bg_deep / bg_panel のまま
        self.code_bg = mix(self.bg_deep, self.text, CODE_BG_LIFT)
        # 地を持ち上げた分だけ補助色も持ち上げないと、コメントのコントラストが落ちる
        self.code_dim = mix(self.text_dim, self.text, CODE_BG_LIFT)

    def h(self, name, alpha=None):
        return hexs(getattr(self, name), alpha)

    def calm(self, name):
        """構文色を text_dim 方向へ寄せ、彩度と輝度を落とす。"""
        return hexs(mix(getattr(self, name), self.text_dim, SYNTAX_CALM))


NONE = "#00000000"


# --------------------------------------------------------------------------- syntax
def syntax(p):
    """4 base colours (text / code_dim / accent / accent tint) + 2 meaning colours
    (ok = strings, warn = literals), all calmed. danger is not used in syntax."""
    accent, accent_lt = p.calm("accent"), p.calm("accent_lt")
    text, dim = p.h("text"), hexs(p.code_dim)
    ok, warn = p.calm("ok"), p.calm("warn")

    def s(color, style=None, weight=None):
        d = {"color": color}
        if style:
            d["font_style"] = style
        if weight:
            d["font_weight"] = weight
        return d

    return {
        "attribute": s(warn),
        "boolean": s(warn),
        "comment": s(dim, "italic"),
        "comment.doc": s(dim, "italic"),
        "constant": s(warn),
        "constructor": s(accent_lt),
        "embedded": s(text),
        "emphasis": s(text, "italic"),
        "emphasis.strong": s(text, weight=700),
        "enum": s(accent_lt),
        "function": s(accent_lt),
        "function.method": s(accent_lt),
        "function.builtin": s(accent_lt),
        "hint": s(dim, "italic"),
        "keyword": s(accent),
        "label": s(accent),
        "link_text": s(accent),
        "link_uri": s(accent),
        "namespace": s(accent),
        "number": s(warn),
        "operator": s(accent),
        "predictive": s(dim, "italic"),
        "preproc": s(accent),
        "primary": s(text),
        "property": s(text),
        "punctuation": s(dim),
        "punctuation.bracket": s(dim),
        "punctuation.delimiter": s(dim),
        "punctuation.list_marker": s(accent),
        "punctuation.special": s(accent),
        "selector": s(accent_lt),
        "string": s(ok),
        "string.escape": s(warn),
        "string.regex": s(warn),
        "string.special": s(warn),
        "string.special.symbol": s(warn),
        "tag": s(accent_lt),
        "text.literal": s(ok),
        "title": s(accent, weight=700),
        "type": s(accent_lt),
        "type.builtin": s(accent_lt),
        "variable": s(text),
        "variable.special": s(accent),
        "variant": s(warn),
    }


# --------------------------------------------------------------------------- terminal
ANSI_NAMES = ["black", "red", "green", "yellow", "blue", "magenta", "cyan", "white"]


def terminal(p):
    """16 ANSI colours: bright = normal mixed 30 % towards white, dim = 40 % towards bg."""
    base = [p.bg_panel, p.danger, p.ok, p.warn, p.term_blue, p.term_magenta, p.term_cyan, p.text]
    out = {}
    for name, c in zip(ANSI_NAMES, base):
        out[f"terminal.ansi.{name}"] = hexs(c)
        out[f"terminal.ansi.bright_{name}"] = hexs(p.text_dim if name == "black" else mix(c, p.white, 0.3))
        out[f"terminal.ansi.dim_{name}"] = hexs(mix(c, p.bg_deep, 0.4))
    return out


# --------------------------------------------------------------------------- UI
def status_colors(p):
    out = {}
    for key, tok in {
        "conflict": "warn", "created": "ok", "deleted": "danger", "error": "danger",
        "hidden": "text_dim", "hint": "text_dim", "ignored": "text_dim", "info": "accent",
        "modified": "warn", "predictive": "text_dim", "renamed": "accent", "success": "ok",
        "unreachable": "text_dim", "warning": "warn",
    }.items():
        out[key] = p.h(tok)
        out[f"{key}.background"] = p.h(tok, 0.12)
        out[f"{key}.border"] = p.h(tok, 0.55)
    return out


def style(p, transparent):
    """Flat fills, 1px accent_dim rules, accent for anything focused or selected,
    meaning colours only where they mean something."""
    if transparent:
        # Window carries α0.92; other surfaces are tints so alphas don't compound.
        bg, deep, panel, code = (p.h("bg_deep", TRANSPARENT_ALPHA), NONE,
                                 p.h("bg_panel", 0.55), p.h("text", CODE_BG_LIFT * 0.6))
    else:
        bg, deep, panel, code = p.h("bg_deep"), p.h("bg_deep"), p.h("bg_panel"), hexs(p.code_bg)
    sel = p.h("accent", SELECTION_ALPHA)

    return {
        "background.appearance": "transparent" if transparent else "opaque",
        "accents": [p.calm("accent"), p.calm("accent_lt"), p.calm("warn")],
        # -- surfaces: chrome = bg_deep / bg_panel, code = code_bg
        "background": bg,
        "surface.background": panel,
        "elevated_surface.background": p.h("bg_panel"),
        "panel.background": panel,
        "status_bar.background": deep,
        "title_bar.background": deep,
        "title_bar.inactive_background": deep,
        "tab_bar.background": deep,
        "tab.inactive_background": panel,
        "tab.active_background": code,
        "toolbar.background": code,
        "editor.background": code,
        "editor.gutter.background": code,
        "editor.subheader.background": panel,
        "terminal.background": code,
        "terminal.ansi.background": code,
        "drop_target.background": p.h("accent", 0.15),
        # -- rules
        "border": p.h("accent_dim"),
        "border.variant": p.h("accent_dim", 0.6),
        "border.focused": p.h("accent", 0.60),
        "border.selected": p.h("accent", 0.60),
        "border.transparent": NONE,
        "border.disabled": p.h("accent_dim", 0.35),
        "pane.focused_border": p.h("accent", 0.60),
        "pane_group.border": p.h("accent_dim"),
        "panel.focused_border": p.h("accent", 0.60),
        # -- elements (hover = background tint)
        "element.background": hexs(p.field),
        "element.hover": p.h("accent", 0.10),
        "element.active": p.h("accent", 0.22),
        "element.selected": sel,
        "element.disabled": p.h("accent_dim", 0.15),
        "ghost_element.background": NONE,
        "ghost_element.hover": p.h("accent", 0.10),
        "ghost_element.active": p.h("accent", 0.22),
        "ghost_element.selected": p.h("accent", 0.18),
        "ghost_element.disabled": NONE,
        # -- text / icons
        "text": p.h("text"),
        "text.muted": p.h("text_dim"),
        "text.placeholder": p.h("text_dim"),
        "text.disabled": hexs(mix(p.text_dim, p.bg_deep, 0.35)),
        "text.accent": p.h("accent"),
        "link_text.hover": hexs(p.accent_lt),
        "icon": p.h("text_dim"),
        "icon.muted": p.h("text_dim"),
        "icon.disabled": hexs(mix(p.text_dim, p.bg_deep, 0.35)),
        "icon.placeholder": p.h("text_dim"),
        "icon.accent": p.h("accent"),
        # -- editor
        "editor.foreground": p.h("text"),
        "editor.active_line.background": p.h("accent", 0.06),
        "editor.highlighted_line.background": p.h("accent", 0.10),
        "editor.line_number": p.h("accent_dim"),
        "editor.active_line_number": p.h("accent"),
        "editor.invisible": p.h("accent_dim", 0.5),
        "editor.wrap_guide": p.h("accent_dim", 0.35),
        "editor.active_wrap_guide": p.h("accent_dim", 0.6),
        "editor.indent_guide": p.h("accent_dim", 0.35),
        "editor.indent_guide_active": p.h("accent_dim"),
        "editor.document_highlight.read_background": p.h("accent", 0.15),
        "editor.document_highlight.write_background": p.h("accent", 0.22),
        "editor.document_highlight.bracket_background": p.h("accent", 0.18),
        "search.match_background": p.h("warn", 0.22),
        "search.active_match_background": p.h("warn", 0.40),
        "panel.indent_guide": p.h("accent_dim", 0.6),
        "panel.indent_guide_hover": p.h("accent_dim"),
        "panel.indent_guide_active": p.h("accent_dim"),
        "scrollbar.thumb.background": p.h("accent", 0.18),
        "scrollbar.thumb.hover_background": p.h("accent", 0.35),
        "scrollbar.thumb.border": NONE,
        "scrollbar.track.background": NONE,
        "scrollbar.track.border": NONE,
        # -- version control (read by Zed, newer than the v0.2.0 schema)
        "version_control.added": p.h("ok"),
        "version_control.modified": p.h("warn"),
        "version_control.deleted": p.h("danger"),
        "version_control.conflict_marker.ours": p.h("ok", 0.15),
        "version_control.conflict_marker.theirs": p.h("accent", 0.15),
        # -- terminal
        "terminal.foreground": p.h("text"),
        "terminal.bright_foreground": hexs(p.accent_lt),
        "terminal.dim_foreground": p.h("text_dim"),
        **terminal(p),
        **status_colors(p),
        "players": [
            {"cursor": p.h("accent"), "background": p.h("accent"), "selection": sel},
            {"cursor": p.h("warn"), "background": p.h("warn"), "selection": p.h("warn", 0.25)},
            {"cursor": p.h("ok"), "background": p.h("ok"), "selection": p.h("ok", 0.25)},
            {"cursor": p.h("term_magenta"), "background": p.h("term_magenta"),
             "selection": p.h("term_magenta", 0.25)},
        ],
        "syntax": syntax(p),
    }


# --------------------------------------------------------------------------- output
def main():
    themes = []
    for transparent in (False, True):
        for name, d in PALETTES.items():
            p = Pal(name, d)
            themes.append({
                "name": f"FUI {name}" + (" Transparent" if transparent else ""),
                "appearance": "dark",
                "style": style(p, transparent),
            })
    family = {
        "$schema": "https://zed.dev/schema/themes/v0.2.0.json",
        "name": "FUI",
        "author": "kobago",
        "themes": themes,
    }
    out = ROOT / "themes" / "fui.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(family, indent=2) + "\n")
    print(f"wrote {out} ({len(themes)} themes)")


if __name__ == "__main__":
    main()

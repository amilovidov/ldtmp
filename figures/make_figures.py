"""Generate the LDTMP figures as light and dark SVG pairs.

Run from the repo root: python3 figures/make_figures.py
"""

from pathlib import Path

OUT = Path(__file__).parent
FONT = "-apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif"

THEMES = {
    "light": {
        "text": "#1f2328", "muted": "#59636e", "guide": "#d1d9e0",
        "lane": "#f6f8fa", "lane_stroke": "#d1d9e0",
        "n_light": "#eaf2fc", "s_light": "#a5c1e8",
        "n_mod": "#c3d7f3", "s_mod": "#6f97cf",
        "n_deep": "#2f5fa7", "s_deep": "#244b85", "t_deep": "#ffffff",
        "gated": "#2f5fa7", "forward": "#59636e", "retreat": "#8c959f",
    },
    "dark": {
        "text": "#e6edf3", "muted": "#9198a1", "guide": "#30363d",
        "lane": "#151b23", "lane_stroke": "#30363d",
        "n_light": "#1a2636", "s_light": "#3d5a80",
        "n_mod": "#22406a", "s_mod": "#4f7ab8",
        "n_deep": "#6ea2ec", "s_deep": "#8db6f2", "t_deep": "#0d1117",
        "gated": "#79a8ec", "forward": "#9198a1", "retreat": "#656c76",
    },
}


def markers(c):
    out = []
    for name in ("gated", "forward", "retreat"):
        out.append(
            f'<marker id="a-{name}" viewBox="0 0 10 10" refX="9" refY="5" '
            f'markerUnits="userSpaceOnUse" markerWidth="9" markerHeight="9" orient="auto-start-reverse">'
            f'<path d="M0,1 L9,5 L0,9 z" fill="{c[name]}"/></marker>'
        )
    return "<defs>" + "".join(out) + "</defs>"


def text(x, y, s, c, size=14, anchor="middle", color=None, weight=400):
    return (
        f'<text x="{x}" y="{y}" font-size="{size}" font-weight="{weight}" '
        f'text-anchor="{anchor}" dominant-baseline="central" '
        f'fill="{color or c["text"]}">{s}</text>'
    )


def figure1(c):
    """The six layers placed by intensity, so the arc is visible as a shape."""
    w, h = 1320, 400
    node_w, node_h = 176, 46
    xs = [188 + i * 206 for i in range(6)]
    level_y = {"light": 70, "moderate": 175, "deep": 280}
    layers = [
        ("Icebreaker", "light"), ("Surface", "light"),
        ("Initial descent", "moderate"), ("Emotional saturation", "deep"),
        ("Relief arc", "moderate"), ("Reentry", "light"),
    ]
    style = {
        "light": (c["n_light"], c["s_light"], c["text"]),
        "moderate": (c["n_mod"], c["s_mod"], c["text"]),
        "deep": (c["n_deep"], c["s_deep"], c["t_deep"]),
    }
    p = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" '
         f'font-family="{FONT}" role="img" aria-label="LDTMP layer arc">', markers(c)]

    for name, y in level_y.items():
        p.append(f'<line x1="56" y1="{y}" x2="{w - 24}" y2="{y}" stroke="{c["guide"]}" '
                 f'stroke-width="1" stroke-dasharray="2 5"/>')
        p.append(text(24, y, name, c, size=14, anchor="start", color=c["muted"]))

    def edge(i, j, kind):
        """Same level: straight. Level change: one bend, forward on the outer corner."""
        (x1, y1), (x2, y2) = (xs[i], level_y[layers[i][1]]), (xs[j], level_y[layers[j][1]])
        width = {"gated": 2.2, "forward": 1.6, "retreat": 1.3}[kind]
        dash = ' stroke-dasharray="5 4"' if kind == "retreat" else ""
        half_w, half_h, gap = node_w / 2, node_h / 2, 4
        if y1 == y2:
            dy = -7 if j > i else 8
            sx = x1 + half_w if j > i else x1 - half_w
            ex = x2 - half_w - gap if j > i else x2 + half_w + gap
            d = f"M{sx},{y1 + dy} L{ex},{y2 + dy}"
        else:
            down = y2 > y1
            if j > i:   # forward: leave the side, enter the top or bottom of the target
                sx, sy = x1 + half_w, y1
                ex = x2 + (24 if x1 > x2 else -24)  # enter on the side facing the source
                ey = (y2 - half_h - gap) if down else (y2 + half_h + gap)
                d = f"M{sx},{sy} C{ex},{sy} {ex},{sy} {ex},{ey}"
            else:       # retreat: leave the side, enter the top or bottom of the earlier layer
                sx, sy = x1 - half_w, y1
                ex = x2 + (24 if x1 > x2 else -24)  # enter on the side facing the source
                ey = (y2 - half_h - gap) if down else (y2 + half_h + gap)
                d = f"M{sx},{sy} C{ex},{sy} {ex},{sy} {ex},{ey}"
        return (f'<path d="{d}" fill="none" stroke="{c[kind]}" stroke-width="{width}"{dash} '
                f'marker-end="url(#a-{kind})"/>')

    for i in range(5):
        p.append(edge(i, i + 1, "gated" if i < 3 else "forward"))
        p.append(edge(i + 1, i, "retreat"))

    for (label, level), x in zip(layers, xs):
        fill, stroke, tc = style[level]
        y = level_y[level]
        p.append(f'<rect x="{x - node_w / 2}" y="{y - node_h / 2}" width="{node_w}" '
                 f'height="{node_h}" rx="21" fill="{fill}" stroke="{stroke}" stroke-width="1"/>')
        p.append(text(x, y, label, c, size=16, color=tc, weight=500))

    ly = 362
    items = [("gated", "forward, safety gate applies"),
             ("forward", "forward, no gate"), ("retreat", "retreat")]
    x = 360
    for kind, label in items:
        width = {"gated": 2.4, "forward": 1.6, "retreat": 1.3}[kind]
        dash = ' stroke-dasharray="5 4"' if kind == "retreat" else ""
        p.append(f'<line x1="{x}" y1="{ly}" x2="{x + 34}" y2="{ly}" stroke="{c[kind]}" '
                 f'stroke-width="{width}"{dash} marker-end="url(#a-{kind})"/>')
        p.append(text(x + 44, ly, label, c, size=14, anchor="start", color=c["muted"]))
        x += 44 + len(label) * 7.6 + 44
    p.append("</svg>")
    return "\n".join(p)


def box(x, y, w, h, label, c, kind="step"):
    fills = {
        "step": (c["n_light"], c["s_light"], c["text"]),
        "choice": (c["lane"], c["s_mod"], c["text"]),
        "out": (c["n_mod"], c["s_mod"], c["text"]),
        "model": (c["n_deep"], c["s_deep"], c["t_deep"]),
    }
    fill, stroke, tc = fills[kind]
    rx = 8 if kind != "choice" else 20
    dash = ' stroke-dasharray="4 3"' if kind == "choice" else ""
    out = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" '
           f'stroke="{stroke}" stroke-width="1.2"{dash}/>']
    lines = label.split("|")
    for k, line in enumerate(lines):
        ty = y + h / 2 + (k - (len(lines) - 1) / 2) * 17
        out.append(text(x + w / 2, ty, line, c, size=14, color=tc, weight=500))
    return "".join(out)


def arrow(d, c, kind="forward"):
    width = {"gated": 2.0, "forward": 1.5, "retreat": 1.3}[kind]
    dash = ' stroke-dasharray="5 4"' if kind == "retreat" else ""
    return (f'<path d="{d}" fill="none" stroke="{c[kind]}" stroke-width="{width}"{dash} '
            f'marker-end="url(#a-{kind})"/>')


def label(x, y, s, c):
    return text(x, y, s, c, size=13, color=c["muted"])


def figure2(c):
    """One turn: the controller settles the layer, then the model writes inside it."""
    w, h = 1160, 470
    p = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" '
         f'font-family="{FONT}" role="img" aria-label="One LDTMP turn">', markers(c)]

    for y0, title in ((30, "CONTROLLER  (deterministic)"), (270, "MODEL  (generative)")):
        p.append(f'<rect x="20" y="{y0}" width="{w - 60}" height="190" rx="12" '
                 f'fill="{c["lane"]}" stroke="{c["lane_stroke"]}"/>')
        p.append(text(40, y0 + 22, title, c, size=11, anchor="start",
                      color=c["muted"], weight=600))

    cy = 135
    p.append(box(50, cy - 24, 160, 48, "Signals and scores", c))
    p.append(box(280, cy - 24, 150, 48, "Rule fires?", c, "choice"))
    p.append(box(510, cy - 32, 210, 64, "Descending and|safety below 0.5?", c, "choice"))
    p.append(box(890, cy - 24, 180, 48, "Layer for this turn", c, "out"))

    p.append(arrow(f"M210,{cy} L276,{cy}", c))
    p.append(arrow(f"M430,{cy} L506,{cy}", c))
    p.append(label(468, cy - 12, "yes", c))
    p.append(arrow(f"M720,{cy} L886,{cy}", c))
    p.append(label(803, cy - 12, "no: move", c))
    p.append(arrow(f"M615,{cy + 32} C615,{cy + 62} 980,{cy + 62} 980,{cy + 28}", c))
    p.append(label(800, cy + 66, "yes: veto, stay", c))
    p.append(arrow(f"M355,{cy - 24} C355,{cy - 72} 980,{cy - 72} 980,{cy - 28}", c))
    p.append(label(668, cy - 70, "no rule: stay", c))

    my = 375
    p.append(arrow(f"M1070,{cy} L1130,{cy} Q1138,{cy} 1138,{cy + 8} L1138,237 Q1138,245 1130,245 "
                   f"L183,245 Q175,245 175,253 L175,{my - 28}", c, "gated"))
    p.append(text(610, 233, "layer constraints", c, size=12, color=c["gated"], weight=600))

    p.append(box(50, my - 24, 160, 48, "Prompt", c))
    p.append(box(300, my - 24, 220, 48, "Model writes one question", c, "model"))
    p.append(box(610, my - 24, 170, 48, "Fits the layer?", c, "choice"))
    p.append(box(890, my - 24, 180, 48, "Question to user", c, "out"))

    p.append(arrow(f"M210,{my} L296,{my}", c))
    p.append(arrow(f"M520,{my} L606,{my}", c))
    p.append(arrow(f"M780,{my} L886,{my}", c))
    p.append(label(833, my - 12, "yes", c))
    p.append(arrow(f"M695,{my + 24} C695,{my + 62} 410,{my + 62} 410,{my + 28}", c, "retreat"))
    p.append(label(552, my + 62, "no: regenerate once", c))
    p.append("</svg>")
    return "\n".join(p)


if __name__ == "__main__":
    for theme, colors in THEMES.items():
        (OUT / f"fig1-layer-arc-{theme}.svg").write_text(figure1(colors))
        (OUT / f"fig2-one-turn-{theme}.svg").write_text(figure2(colors))
    print("wrote", sorted(p.name for p in OUT.glob("*.svg")))

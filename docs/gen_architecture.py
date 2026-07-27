"""Generates docs/architecture.svg — the README hero image. Hand-drawn
(Excalidraw-style) rendering of the real graph topology in
sales_prep/research_agent/graph.py: same node names, same edges, same
routing conditions.

    python3 docs/gen_architecture.py docs/architecture.svg

Deterministic (seeded RNG), so regenerating an unchanged diagram produces a
byte-identical file rather than a noisy diff.

The committed docs/architecture.png is that SVG rasterized — the handwriting
font is resolved at render time and isn't embedded in the SVG, so the PNG is
what the README points at, not the SVG. To refresh it:

    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \\
      --headless --disable-gpu --hide-scrollbars \\
      --force-device-scale-factor=1 --window-size=2240,1322 \\
      --screenshot=docs/architecture.png file:///path/to/wrapper.html

where wrapper.html is the SVG inlined in a zero-margin white <body>.
"""

import math
import random

W, H = 2240, 1322

INK = "#1e1e1e"
BLUE = "#a5d8ff"
YELLOW = "#ffe98a"
YELLOW_SOFT = "#ffeeb0"
ORANGE = "#ffd8a8"
ORANGE_DEEP = "#ffc9a0"
WHITE = "#ffffff"

FONT = "'Comic Sans MS', 'Chalkboard SE', 'Bradley Hand', cursive"
MONO = "'Comic Sans MS', 'Chalkboard SE', 'Bradley Hand', cursive"

rng = random.Random(20260726)
out = []


# ---------------------------------------------------------------- rough prims

def _j(amount):
    return rng.uniform(-amount, amount)


def rough_line(x1, y1, x2, y2, amp=1.9, passes=2):
    """Two slightly-divergent bezier passes over the same line — the core of
    the hand-drawn look (this is what rough.js does under the hood)."""
    ds = []
    length = math.hypot(x2 - x1, y2 - y1)
    o = amp * min(2.2, 0.6 + length / 220.0)
    for p in range(passes):
        k = 1.0 if p == 0 else 0.75
        sx, sy = x1 + _j(o * k), y1 + _j(o * k)
        ex, ey = x2 + _j(o * k), y2 + _j(o * k)
        c1x = x1 + (x2 - x1) * 0.32 + _j(o * 1.7 * k)
        c1y = y1 + (y2 - y1) * 0.32 + _j(o * 1.7 * k)
        c2x = x1 + (x2 - x1) * 0.68 + _j(o * 1.7 * k)
        c2y = y1 + (y2 - y1) * 0.68 + _j(o * 1.7 * k)
        ds.append(f"M{sx:.1f} {sy:.1f}C{c1x:.1f} {c1y:.1f} {c2x:.1f} {c2y:.1f} {ex:.1f} {ey:.1f}")
    return ds


def rough_arc(cx, cy, r, a0, a1, amp=1.4, passes=2):
    """Corner arcs, sampled and jittered coarsely."""
    ds = []
    for p in range(passes):
        k = 1.0 if p == 0 else 0.75
        pts = []
        steps = 4
        for i in range(steps + 1):
            a = a0 + (a1 - a0) * i / steps
            pts.append((cx + r * math.cos(a) + _j(amp * k), cy + r * math.sin(a) + _j(amp * k)))
        d = f"M{pts[0][0]:.1f} {pts[0][1]:.1f}"
        for i in range(1, len(pts)):
            d += f"L{pts[i][0]:.1f} {pts[i][1]:.1f}"
        ds.append(d)
    return ds


def stroke(ds, width=2.6, dash=None, color=None):
    da = f' stroke-dasharray="{dash}"' if dash else ""
    c = color or INK
    for d in ds:
        out.append(
            f'<path d="{d}" fill="none" stroke="{c}" stroke-width="{width}" '
            f'stroke-linecap="round" stroke-linejoin="round"{da}/>'
        )


def rounded_rect_path(x, y, w, h, r):
    return (
        f"M{x + r} {y}H{x + w - r}A{r} {r} 0 0 1 {x + w} {y + r}"
        f"V{y + h - r}A{r} {r} 0 0 1 {x + w - r} {y + h}"
        f"H{x + r}A{r} {r} 0 0 1 {x} {y + h - r}"
        f"V{y + r}A{r} {r} 0 0 1 {x + r} {y}Z"
    )


def rough_rounded_rect(x, y, w, h, r=18, fill=None, sw=2.6, dash=None, amp=1.9):
    if fill:
        out.append(f'<path d="{rounded_rect_path(x, y, w, h, r)}" fill="{fill}" stroke="none"/>')
    ds = []
    ds += rough_line(x + r, y, x + w - r, y, amp)
    ds += rough_line(x + w, y + r, x + w, y + h - r, amp)
    ds += rough_line(x + w - r, y + h, x + r, y + h, amp)
    ds += rough_line(x, y + h - r, x, y + r, amp)
    ds += rough_arc(x + w - r, y + r, r, -math.pi / 2, 0, amp * 0.7)
    ds += rough_arc(x + w - r, y + h - r, r, 0, math.pi / 2, amp * 0.7)
    ds += rough_arc(x + r, y + h - r, r, math.pi / 2, math.pi, amp * 0.7)
    ds += rough_arc(x + r, y + r, r, math.pi, 1.5 * math.pi, amp * 0.7)
    stroke(ds, sw, dash)


def rough_diamond(cx, cy, hw, hh, fill=None, sw=2.6):
    if fill:
        out.append(
            f'<path d="M{cx} {cy - hh}L{cx + hw} {cy}L{cx} {cy + hh}L{cx - hw} {cy}Z" '
            f'fill="{fill}" stroke="none"/>'
        )
    ds = []
    ds += rough_line(cx, cy - hh, cx + hw, cy)
    ds += rough_line(cx + hw, cy, cx, cy + hh)
    ds += rough_line(cx, cy + hh, cx - hw, cy)
    ds += rough_line(cx - hw, cy, cx, cy - hh)
    stroke(ds, sw)


def arrow_head(x, y, angle, size=17):
    ds = []
    for s in (+1, -1):
        a = angle + math.pi + s * 0.42
        ds += rough_line(x, y, x + size * math.cos(a), y + size * math.sin(a), amp=1.0, passes=2)
    stroke(ds, 2.8)


def arrow(pts, sw=2.8, head=True):
    """Polyline arrow through pts, rough-drawn, with an arrowhead at the end."""
    ds = []
    for i in range(len(pts) - 1):
        (x1, y1), (x2, y2) = pts[i], pts[i + 1]
        ds += rough_line(x1, y1, x2, y2, amp=1.5)
    stroke(ds, sw)
    if head:
        (px, py), (qx, qy) = pts[-2], pts[-1]
        arrow_head(qx, qy, math.atan2(qy - py, qx - px))


# ---------------------------------------------------------------------- text

def text(x, y, s, size=26, weight="bold", anchor="middle", color=INK, family=FONT, italic=False):
    st = ' font-style="italic"' if italic else ""
    s = s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    out.append(
        f'<text x="{x}" y="{y}" font-family="{family}" font-size="{size}" '
        f'font-weight="{weight}" fill="{color}" text-anchor="{anchor}"{st}>{s}</text>'
    )


def label(x, y, s, size=21, rot=0):
    """Edge label with a white knock-out behind it so it stays readable."""
    w = len(s) * size * 0.50 + 14
    g = f'<g transform="rotate({rot} {x} {y})">' if rot else "<g>"
    out.append(g)
    out.append(
        f'<rect x="{x - w / 2:.0f}" y="{y - size * 0.82:.0f}" width="{w:.0f}" '
        f'height="{size * 1.35:.0f}" rx="6" fill="{WHITE}" opacity="0.92"/>'
    )
    text(x, y, s, size=size, weight="bold")
    out.append("</g>")


def node(x, y, w, h, lines, fill, r=18, sw=2.8):
    """lines: list of (string, size, italic)."""
    rough_rounded_rect(x, y, w, h, r=r, fill=fill, sw=sw)
    total = sum(sz * 1.30 for _, sz, _ in lines)
    cy = y + h / 2 - total / 2
    for s, sz, it in lines:
        cy += sz * 1.30
        text(x + w / 2, cy - sz * 0.28, s, size=sz, weight="bold", italic=it)


# ============================================================ diagram content

out.append(f'<rect width="{W}" height="{H}" fill="{WHITE}"/>')

# ---- LEFT container: human-gated planning ---------------------------------
rough_rounded_rect(40, 40, 400, 700, r=22, fill=None, sw=2.8, dash="2 12", amp=2.4)
text(240, 96, "Plan & Refine", size=36)
text(240, 126, "human in the loop", size=20, weight="normal", italic=True)

node(185, 150, 110, 52, [("START", 22, False)], WHITE, r=26, sw=2.6)
arrow([(240, 202), (240, 240)])

node(76, 240, 328, 88, [
    ("ingest_research_context", 23, False),
    ("run_id · iteration caps", 18, True),
], WHITE)
arrow([(240, 328), (240, 366)])

node(76, 366, 328, 118, [
    ("generate_research_plan", 23, False),
    ("claude-sonnet-5", 19, True),
    ("goals scoped to deal_stage", 18, True),
], BLUE)

arrow([(186, 484), (186, 566)])
arrow([(294, 566), (294, 484)])
label(360, 528, "revise", 20)

node(76, 566, 328, 118, [
    ("plan_approval_gate", 23, False),
    ("interrupt()", 19, True),
    ("approve or send feedback", 18, True),
], YELLOW)

# ---- RIGHT container: autonomous research ---------------------------------
rough_rounded_rect(486, 108, 1700, 1160, r=24, fill=None, sw=2.8, dash="2 12", amp=2.4)
text(1336, 168, "Autonomous Research", size=36)

rough_rounded_rect(524, 200, 1624, 1030, r=22, fill=ORANGE, sw=2.8)
text(1336, 252, "one section per approved goal, in order", size=24, italic=True)

# plan_approval_gate -> build_outline
arrow([(404, 625), (462, 625), (462, 386), (582, 386)])
label(462, 505, "approved", 20, rot=-90)

node(582, 330, 300, 112, [
    ("build_outline", 24, False),
    ("no LLM —", 18, True),
    ("plan becomes sections", 18, True),
], YELLOW)

arrow([(882, 386), (960, 386)])

node(960, 330, 356, 112, [
    ("gather_section", 24, False),
    ("iteration 0 · fixture providers", 18, True),
], YELLOW)

# ---- inner loop panel -----------------------------------------------------
# Drawn before the gather -> critique arrow: the panel's fill is opaque and
# would otherwise paint over the part of that arrow that runs inside it.
rough_rounded_rect(582, 556, 1092, 544, r=22, fill=YELLOW_SOFT, sw=2.8)
text(1128, 604, "refine loop", size=26)
text(1128, 634, "bounded by max_iterations_per_section", size=20, italic=True)

arrow([(1138, 442), (1138, 502), (818, 502), (818, 700)])

node(640, 700, 356, 130, [
    ("critique_section", 24, False),
    ("claude-sonnet-5 — “would a rep", 18, True),
    ("feel ready for this call?”", 18, True),
], ORANGE_DEEP)

rough_diamond(1300, 765, 172, 128, fill=ORANGE_DEEP)
text(1300, 758, "gap", size=24)
text(1300, 788, "found?", size=24)

arrow([(996, 765), (1128, 765)])

# no -> advance
arrow([(1472, 765), (1746, 765)])
label(1600, 736, "no / max iters", 20)

# yes -> follow-up web search
arrow([(1300, 893), (1300, 990), (1218, 990)])
label(1352, 945, "yes", 20)

node(700, 934, 518, 112, [
    ("gather_section", 24, False),
    ("iteration ≥ 1 · Anthropic web_search, aimed", 17, True),
    ("at the exact gap the critique named", 17, True),
], ORANGE_DEEP)

arrow([(850, 934), (850, 830)])

# ---- advance / compose ----------------------------------------------------
node(1746, 706, 330, 118, [
    ("advance_section", 24, False),
    ("next goal, or done", 18, True),
], YELLOW)

# loop back to gather_section for the next section
arrow([(2076, 765), (2116, 765), (2116, 288), (1138, 288), (1138, 330)])
label(1640, 288, "next section", 20)

arrow([(1911, 824), (1911, 916)])
label(1911, 878, "all done", 20)

node(1746, 916, 330, 148, [
    ("compose_report", 24, False),
    ("claude-sonnet-5 · max_tokens=8192", 16, True),
    ("citation registry built in Python", 16, True),
    ("before the model ever sees it", 16, True),
], YELLOW)

arrow([(1911, 1064), (1911, 1128)])
node(1846, 1128, 130, 56, [("END", 22, False)], WHITE, r=28, sw=2.6)

svg = (
    f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
    f'viewBox="0 0 {W} {H}">\n' + "\n".join(out) + "\n</svg>\n"
)

import sys
open(sys.argv[1], "w").write(svg)
print(f"wrote {sys.argv[1]} ({len(svg)} bytes)")

"""Render the animated SVG cards for the profile README into cards/.

Reads data/contributions.json (refreshed daily by the GitHub Action) and
data/portrait.txt. Set STATIC=1 to render every card at its final frame.
"""
import base64
import json
import os
from datetime import date, timedelta
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CARDS = ROOT / "cards"
STATIC = os.environ.get("STATIC") == "1"

# ---------- palette ----------
BG = "#0E1013"
BG2 = "#14171C"
LINE = "#FFFFFF"
INK = "#EDEDEF"
MUTED = "#8A8F98"
FAINT = "#5B616B"
AMBER = "#F5A524"
RED = "#F0533F"
BLUE = "#5B8CFF"
LEVELS = ["#1B1E24", "#3D2C10", "#7A5413", "#C2821A", "#F5A524"]


def font(name: str, file: str) -> str:
    b64 = base64.b64encode((ROOT / "fonts" / file).read_bytes()).decode()
    return f"@font-face{{font-family:'{name}';src:url(data:font/woff2;base64,{b64}) format('woff2')}}"


FONTS = {
    "serif": font("Serif", "serif-400.woff2"),
    "italic": font("SerifItalic", "serif-400-italic.woff2"),
    "mono": font("Mono", "mono-400.woff2"),
    "sans": font("Sans", "sans-400.woff2"),
}
SERIF = "'Serif', Georgia, serif"
ITALIC = "'SerifItalic', Georgia, serif"
MONO = "'Mono', ui-monospace, Menlo, Consolas, monospace"
SANS = "'Sans', -apple-system, 'Segoe UI', Helvetica, Arial, sans-serif"

KEYFRAMES = """
@keyframes rise{from{opacity:0;transform:translateY(18px)}to{opacity:1;transform:none}}
@keyframes fade{from{opacity:0}to{opacity:1}}
@keyframes grow{from{transform:scaleY(0)}to{transform:scaleY(1)}}
@keyframes pop{0%{opacity:0;transform:scale(.4)}70%{opacity:1;transform:scale(1.12)}100%{opacity:1;transform:scale(1)}}
@keyframes swing{0%{opacity:0;transform:translateY(46px) rotate(4deg)}65%{opacity:1;transform:translateY(-5px) rotate(-.6deg)}100%{opacity:1;transform:none}}
@keyframes pulse{0%,100%{opacity:1}50%{opacity:.35}}
@keyframes ring{0%{opacity:.55;transform:scale(.4)}100%{opacity:0;transform:scale(2.6)}}
@keyframes nudge{0%,70%,100%{transform:none}80%{transform:translateX(4px)}}
@keyframes sweep{0%{transform:translateX(0) skewX(-20deg)}35%,100%{transform:translateX(620px) skewX(-20deg)}}
"""
REDUCED = "*{animation:none!important;opacity:1!important}"


def svg(w: int, h: int, label: str, fonts: list[str], css: str, body: str) -> str:
    style = "".join(FONTS[f] for f in fonts) + KEYFRAMES + css
    if STATIC:
        style += REDUCED
    else:
        style += f"@media (prefers-reduced-motion:reduce){{{REDUCED}}}"
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
        f'role="img" aria-label="{escape(label)}"><style>{style}</style>'
        f'<rect x=".5" y=".5" width="{w-1}" height="{h-1}" rx="18" fill="{BG}" stroke="{LINE}" stroke-opacity=".08"/>'
        f"{body}</svg>"
    )


def write(name: str, content: str) -> None:
    CARDS.mkdir(exist_ok=True)
    (CARDS / name).write_text(content, encoding="utf-8")


# ---------- hero ----------
def hero() -> None:
    rows = (ROOT / "data" / "portrait.txt").read_text(encoding="utf-8").rstrip("\n").split("\n")
    lh = 5.0
    x0, y0 = 540, 42
    art = []
    for i, r in enumerate(rows):
        if not r.strip():
            continue
        d = 0.5 + i * 0.022
        art.append(
            f'<text x="{x0}" y="{y0 + i * lh:.2f}" style="animation:fade .25s ease {d:.3f}s both" xml:space="preserve">{escape(r)}</text>'
        )
    css = f"""
.tag{{font:13px {MONO};fill:{MUTED};letter-spacing:1.6px}}
.n1{{font:118px {SERIF};fill:{INK};letter-spacing:-2px}}
.n2{{font:118px {ITALIC};letter-spacing:-2px}}
.sub{{font:18px {SANS};fill:{MUTED}}}
.link{{font:14px {MONO};fill:{INK}}}
.art{{font:5.6px {MONO};fill:#E9E2D6;fill-opacity:.78}}
.r1{{animation:rise .9s cubic-bezier(.2,.7,.2,1) .1s both}}
.r2{{animation:rise .9s cubic-bezier(.2,.7,.2,1) .28s both}}
.r3{{animation:rise .8s cubic-bezier(.2,.7,.2,1) .6s both}}
.r4{{animation:fade .8s ease .9s both}}
.dot{{animation:pulse 2.4s ease-in-out infinite}}
.arrow{{animation:nudge 3s ease-in-out 2s infinite}}
"""
    shine = "" if STATIC else (
        '<animateTransform attributeName="gradientTransform" type="translate" '
        'values="-1.2 0;1.2 0;1.2 0" keyTimes="0;.4;1" dur="5s" begin="1.4s" repeatCount="indefinite"/>'
    )
    body = f"""
<defs>
  <linearGradient id="shine" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0" stop-color="{INK}"/><stop offset=".42" stop-color="{INK}"/>
    <stop offset=".5" stop-color="{AMBER}"/><stop offset=".58" stop-color="{INK}"/>
    <stop offset="1" stop-color="{INK}"/>{shine}
  </linearGradient>
  <radialGradient id="glow" cx=".78" cy=".45" r=".45">
    <stop offset="0" stop-color="{AMBER}" stop-opacity=".10"/><stop offset="1" stop-color="{AMBER}" stop-opacity="0"/>
  </radialGradient>
</defs>
<rect x="1" y="1" width="878" height="418" rx="18" fill="url(#glow)"/>
<g class="r4"><rect class="dot" x="48" y="46" width="8" height="8" rx="2" fill="{AMBER}"/>
<text class="tag" x="66" y="55">FOUNDER · TECHAMBER</text></g>
<text class="n1 r1" x="42" y="178">Safi</text>
<text class="n2 r2" x="44" y="284" fill="url(#shine)">Abdullah</text>
<text class="sub r3" x="48" y="336">I build software that sells.</text>
<g class="r4"><text class="link" x="48" y="378">techamber.in</text>
<text class="link arrow" x="168" y="378" fill="{AMBER}" style="fill:{AMBER}">↗</text></g>
<g class="art">{''.join(art)}</g>
"""
    write("hero.svg", svg(880, 420, "Safi Abdullah. Founder, TechAmber. I build software that sells.",
                          ["serif", "italic", "mono", "sans"], css, body))


# ---------- contribution data ----------
def load_days() -> list[tuple[date, int]]:
    raw = json.loads((ROOT / "data" / "contributions.json").read_text(encoding="utf-8"))
    days = [(date.fromisoformat(d["date"]), int(d["count"])) for d in raw["days"]]
    days.sort()
    return days


def streaks(days: list[tuple[date, int]]) -> tuple[int, int]:
    longest = run = 0
    for _, c in days:
        run = run + 1 if c > 0 else 0
        longest = max(longest, run)
    current = 0
    seq = list(days)
    if seq and seq[-1][1] == 0:  # today not committed yet doesn't break the streak
        seq = seq[:-1]
    for _, c in reversed(seq):
        if c == 0:
            break
        current += 1
    return current, longest


# ---------- monthly bars ----------
def bars(days: list[tuple[date, int]]) -> None:
    months: dict[tuple[int, int], int] = {}
    for d, c in days:
        months[(d.year, d.month)] = months.get((d.year, d.month), 0) + c
    keys = sorted(months)[-12:]
    vals = [months[k] for k in keys]
    total = sum(c for _, c in days)
    best = max(range(len(vals)), key=lambda i: vals[i]) if vals else 0
    top = max(vals) if vals and max(vals) > 0 else 1
    active = sum(1 for _, c in days if c > 0)
    current, longest = streaks(days)
    busiest = max((c for _, c in days), default=0)

    names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    bx, bw, gap, base, maxh = 40, 38, 9.5, 292, 150
    parts = []
    for i, (k, v) in enumerate(zip(keys, vals)):
        h = max(6, v / top * maxh)
        x = bx + i * (bw + gap)
        last = i == len(keys) - 1
        fill = AMBER if i == best else ("#2A2E35" if last else "#D9D6CF")
        d = 0.5 + i * 0.07
        parts.append(
            f'<rect x="{x:.1f}" y="{base - h:.1f}" width="{bw}" height="{h:.1f}" rx="4" fill="{fill}" '
            f'style="transform-box:fill-box;transform-origin:bottom;animation:grow .7s cubic-bezier(.2,.8,.2,1) {d:.2f}s both"/>'
        )
        parts.append(f'<text class="mlab" x="{x + bw / 2:.1f}" y="{base + 22}" text-anchor="middle">{names[k[1] - 1]}</text>')
        if i == best:
            parts.append(
                f'<text class="bestn" x="{x + bw / 2:.1f}" y="{base - h - 9:.1f}" text-anchor="middle" '
                f'style="animation:fade .5s ease {0.5 + len(keys) * 0.07 + 0.4:.2f}s both">{v:,}</text>'
            )
    streak_word = "current streak, and the longest" if current == longest else f"current streak · longest {longest}"
    stats = [
        (f'{current}<tspan class="it"> {"day" if current == 1 else "days"}</tspan>', streak_word),
        (f'{active}<tspan class="faint"> / {len(days)}</tspan>', "days with a commit"),
        (f"{busiest}", "on the busiest day"),
    ]
    sx = 650
    for i, (big, small) in enumerate(stats):
        y = 92 + i * 92
        d = 1.0 + i * 0.15
        parts.append(f'<g style="animation:rise .7s cubic-bezier(.2,.7,.2,1) {d:.2f}s both">'
                     f'<text class="stat" x="{sx}" y="{y}">{big}</text>'
                     f'<text class="slab" x="{sx}" y="{y + 24}">{small}</text></g>')
        if i < 2:
            parts.append(f'<line x1="{sx}" x2="840" y1="{y + 46}" y2="{y + 46}" stroke="{LINE}" stroke-opacity=".08"/>')
    css = f"""
.tag{{font:12px {MONO};fill:{MUTED};letter-spacing:1.6px}}
.big{{font:50px {SERIF};fill:{INK};letter-spacing:-1px}}
.it{{font-family:{ITALIC}}}
.faint{{fill:{FAINT}}}
.mlab{{font:11px {MONO};fill:{FAINT}}}
.bestn{{font:11px {MONO};fill:{AMBER}}}
.stat{{font:40px {SERIF};fill:{INK};letter-spacing:-.5px}}
.slab{{font:13px {SANS};fill:{MUTED}}}
"""
    body = f"""
<text class="tag" x="40" y="58" style="animation:fade .6s ease .1s both">THE LAST 12 MONTHS ON GITHUB</text>
<text class="big" x="38" y="112" style="animation:rise .8s cubic-bezier(.2,.7,.2,1) .2s both">{total:,}<tspan class="it"> contributions</tspan></text>
{''.join(parts)}
"""
    write("activity.svg", svg(880, 340, f"{total:,} contributions in the last 12 months. {current}-day streak.",
                              ["serif", "italic", "mono", "sans"], css, body))


# ---------- contribution graph ----------
def graph(days: list[tuple[date, int]]) -> None:
    last = days[-1][0]
    start = last - timedelta(days=364)
    start -= timedelta(days=(start.weekday() + 1) % 7)  # back to Sunday
    counts = {d: c for d, c in days}
    nz = sorted(c for c in counts.values() if c > 0)

    def level(c: int) -> int:
        if c <= 0 or not nz:
            return 0
        q = [nz[int(len(nz) * p)] for p in (0.25, 0.5, 0.75)]
        return 1 + sum(c > t for t in q)

    s, g = 11.6, 3.0
    x0, y0 = 40, 92
    cells, labels = [], []
    d = start
    col = 0
    seen_month = None
    while d <= last:
        row = (d.weekday() + 1) % 7
        if row == 0 and d.month != seen_month and d.day <= 7:
            labels.append(f'<text class="mlab" x="{x0 + col * (s + g):.1f}" y="{y0 + 7 * (s + g) + 16:.1f}">{d.strftime("%b")}</text>')
            seen_month = d.month
        lv = level(counts.get(d, 0))
        delay = 0.4 + col * 0.022 + row * 0.012
        cells.append(
            f'<rect x="{x0 + col * (s + g):.1f}" y="{y0 + row * (s + g):.1f}" width="{s}" height="{s}" rx="2.5" fill="{LEVELS[lv]}" '
            f'style="transform-box:fill-box;transform-origin:center;animation:pop .35s ease {delay:.3f}s both"/>'
        )
        if row == 6:
            col += 1
        d += timedelta(days=1)
    legend = "".join(
        f'<rect x="{758 + i * 15}" y="{y0 + 7 * (s + g) + 30}" width="11" height="11" rx="2" fill="{c}"/>'
        for i, c in enumerate(LEVELS)
    )
    ly = y0 + 7 * (s + g) + 40
    css = f"""
.title{{font:34px {SERIF};fill:{INK};letter-spacing:-.5px}}
.it{{font-family:{ITALIC};fill:{AMBER}}}
.tag{{font:12px {MONO};fill:{MUTED};letter-spacing:1.6px}}
.mlab{{font:11px {MONO};fill:{FAINT}}}
"""
    body = f"""
<text class="title" x="40" y="62" style="animation:rise .8s cubic-bezier(.2,.7,.2,1) .1s both">Every day,<tspan class="it"> in amber</tspan></text>
<text class="tag" x="840" y="58" text-anchor="end" style="animation:fade .6s ease .3s both">REFRESHED DAILY</text>
{''.join(cells)}{''.join(labels)}
<text class="mlab" x="752" y="{ly:.1f}" text-anchor="end">less</text>{legend}<text class="mlab" x="{758 + 5 * 15 + 2}" y="{ly:.1f}">more</text>
"""
    write("graph.svg", svg(880, 272, "Contribution graph for the last year.", ["serif", "italic", "mono"], css, body))


# ---------- tiles ----------
def tile(name: str, label: str, num: int, word: str, color: str, delay: float) -> None:
    w, h = 290, 210
    end = delay + 0.6
    frames = 18
    if STATIC:
        count_txt = f'<text class="num" x="26" y="118">{num}+</text>'
    else:
        sets = []
        for f in range(frames + 1):
            v = round(num * (1 - (1 - f / frames) ** 3))
            b = end + f * 0.045
            sets.append(
                f'<text class="num" x="26" y="118" visibility="hidden">{v}+'
                f'<set attributeName="visibility" to="visible" begin="{b:.3f}s"/>'
                + ("" if f == frames else f'<set attributeName="visibility" to="hidden" begin="{b + 0.045:.3f}s"/>')
                + "</text>"
            )
        count_txt = "".join(sets)
    css = f"""
.lab{{font:12px {MONO};fill:{color};letter-spacing:1.8px}}
.num{{font:72px {SERIF};fill:{INK};letter-spacing:-1.5px}}
.it{{font:28px {ITALIC};fill:{color}}}
.arr{{font:15px {MONO};fill:{MUTED};animation:nudge 3s ease-in-out {end + 1:.1f}s infinite}}
.card{{transform-box:fill-box;transform-origin:50% 100%;animation:swing .9s cubic-bezier(.2,.8,.25,1) {delay:.2f}s both}}
.ring{{transform-box:fill-box;transform-origin:center;animation:ring 2.8s ease-out {end:.1f}s infinite}}
.sh{{animation:sweep 6s ease-in-out {end + 1.2:.1f}s infinite}}
"""
    body = f"""
<defs>
  <radialGradient id="g" cx="1" cy="0" r="1">
    <stop offset="0" stop-color="{color}" stop-opacity=".22"/><stop offset=".6" stop-color="{color}" stop-opacity="0"/>
  </radialGradient>
  <linearGradient id="s" x1="0" x2="1"><stop offset="0" stop-color="#fff" stop-opacity="0"/>
    <stop offset=".5" stop-color="#fff" stop-opacity=".06"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>
  <clipPath id="c"><rect x="1" y="1" width="{w-2}" height="{h-2}" rx="17"/></clipPath>
</defs>
<g class="card"><g clip-path="url(#c)">
  <rect x="1" y="1" width="{w-2}" height="{h-2}" rx="17" fill="url(#g)"/>
  <circle class="ring" cx="{w - 34}" cy="34" r="10" fill="none" stroke="{color}" stroke-width="1.5"/>
  <rect class="sh" x="-140" y="0" width="90" height="{h}" fill="url(#s)"/>
</g>
<rect x="28" y="30" width="7" height="7" rx="1.5" fill="{color}"/>
<text class="lab" x="44" y="37">{label}</text>
<text class="arr" x="{w - 40}" y="39">→</text>
{count_txt}
<text class="it" x="28" y="162" style="animation:fade .6s ease {end + 0.5:.2f}s both">{word}</text>
</g>
"""
    write(name, svg(w, h, f"{num}+ {word}", ["serif", "italic", "mono"], css, body))


def main() -> None:
    hero()
    data = ROOT / "data" / "contributions.json"
    if data.exists():
        days = load_days()
        graph(days)
        bars(days)
    tile("build.svg", "BUILD", 98, "projects", AMBER, 0.2)
    tile("learn.svg", "LEARN", 6, "failed ventures", RED, 0.38)
    tile("trust.svg", "TRUST", 78, "clients", BLUE, 0.56)
    print("cards written to", CARDS)


if __name__ == "__main__":
    main()

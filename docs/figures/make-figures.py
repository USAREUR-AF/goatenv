#!/usr/bin/env python3
"""Draw the repository's figures from the tree.

    python3 -I docs/figures/make-figures.py           # write docs/figures/*.svg
    python3 -I docs/figures/make-figures.py --check   # exit 1 if a committed figure is out of date

Each figure is written twice, `<name>-light.svg` and `<name>-dark.svg`, for a
`<picture>` element. Every name and value in a figure is read from the tree:
`goatcore.ref`, `goatlite.yaml`, the site's group_vars and inventory. The
output is deterministic. Standard library only.
"""

import os
import re
import sys
from xml.sax.saxutils import escape

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))

THEMES = {
    "light": {
        "paper": "#ffffff", "panel": "#f6f8fa", "ink": "#1f2328", "quiet": "#59636e", "rule": "#d1d9e0",
        "line": "#818b98", "accent": "#0969da", "accent_soft": "#ddf4ff", "on_accent": "#ffffff",
        "good": "#1a7f37", "good_bg": "#dafbe1", "crit": "#cf222e", "crit_bg": "#ffebe9", "mute": "#6e7781",
        "s0": "#0969da", "s1": "#bc4c00", "s2": "#1a7f37", "s3": "#8250df",
    },
    "dark": {
        "paper": "#0d1117", "panel": "#161b22", "ink": "#e6edf3", "quiet": "#9198a1", "rule": "#3d444d",
        "line": "#7d8590", "accent": "#4493f8", "accent_soft": "#132c4c", "on_accent": "#0d1117",
        "good": "#3fb950", "good_bg": "#12261e", "crit": "#f85149", "crit_bg": "#2f1517", "mute": "#8b949e",
        "s0": "#4493f8", "s1": "#f0883e", "s2": "#3fb950", "s3": "#bc8cff",
    },
}
SANS = "-apple-system, BlinkMacSystemFont, 'Segoe UI', 'Noto Sans', Helvetica, Arial, sans-serif"
MONO = "ui-monospace, SFMono-Regular, 'SF Mono', Menlo, Consolas, 'Liberation Mono', monospace"


def n(v):
    return ("%.1f" % v).rstrip("0").rstrip(".")


def tw(s, size, mono=False, bold=False):
    """Text width estimate; the browser check in the README confirms it."""
    if mono:
        return len(s) * size * 0.62
    w = 0.0
    for c in s:
        if c in "il.,:;|!'`·1 ":
            w += 0.30
        elif c in "ft()[]/-":
            w += 0.36
        elif c in "mwMW@%":
            w += 0.86
        elif c.isupper() or c in "0123456789≤≥²→":
            w += 0.64
        else:
            w += 0.55
    return w * size * (1.06 if bold else 1.0)


def wrap(s, width, size, mono=False, bold=False):
    out, line = [], ""
    for word in s.split(" "):
        t = word if not line else line + " " + word
        if tw(t, size, mono, bold) <= width or not line:
            line = t
        else:
            out.append(line)
            line = word
    if line:
        out.append(line)
    return out


class SVG:
    def __init__(self, w, h, title, desc):
        self.w, self.h, self.title, self.desc = w, h, title, desc
        self.items = []

    def add(self, s):
        self.items.append(s)

    def rect(self, x, y, w, h, fill="panel", stroke="rule", rx=8, sw=1, dash=None):
        d = ' stroke-dasharray="%s"' % dash if dash else ""
        self.add('<rect x="%s" y="%s" width="%s" height="%s" rx="%s" fill="{%s}" stroke="{%s}" stroke-width="%s"%s/>'
                 % (n(x), n(y), n(w), n(h), n(rx), fill, stroke, n(sw), d))

    def text(self, x, y, s, size=14, fill="ink", anchor="start", bold=False, mono=False, italic=False):
        self.add('<text x="%s" y="%s" font-size="%s" fill="{%s}" text-anchor="%s"%s%s%s>%s</text>'
                 % (n(x), n(y), n(size), fill, anchor, ' font-weight="600"' if bold else "",
                    ' font-family="%s"' % MONO if mono else "", ' font-style="italic"' if italic else "", escape(s)))

    def lines(self, x, y, rows, size=14, lead=1.4, **kw):
        for i, r in enumerate(rows):
            self.text(x, y + i * size * lead, r, size, **kw)
        return y + len(rows) * size * lead

    def line(self, x1, y1, x2, y2, stroke="line", sw=1.5, dash=None, arrow=False):
        d = ' stroke-dasharray="%s"' % dash if dash else ""
        m = ' marker-end="url(#arrow)"' if arrow else ""
        self.add('<line x1="%s" y1="%s" x2="%s" y2="%s" stroke="{%s}" stroke-width="%s"%s%s/>'
                 % (n(x1), n(y1), n(x2), n(y2), stroke, n(sw), d, m))

    def path(self, d, stroke="line", fill="none", sw=1.5, dash=None, arrow=False):
        dd = ' stroke-dasharray="%s"' % dash if dash else ""
        m = ' marker-end="url(#arrow)"' if arrow else ""
        f = "none" if fill == "none" else "{%s}" % fill
        self.add('<path d="%s" fill="%s" stroke="{%s}" stroke-width="%s"%s%s/>' % (d, f, stroke, n(sw), dd, m))

    def circle(self, x, y, r, fill="ink", stroke=None, sw=1.5):
        s = ' stroke="{%s}" stroke-width="%s"' % (stroke, n(sw)) if stroke else ""
        f = "none" if fill == "none" else "{%s}" % fill
        self.add('<circle cx="%s" cy="%s" r="%s" fill="%s"%s/>' % (n(x), n(y), n(r), f, s))

    def ellipse(self, x, y, rx, ry, fill="none", stroke="line", sw=1.5, dash=None, opacity=None):
        d = ' stroke-dasharray="%s"' % dash if dash else ""
        f = "none" if fill == "none" else "{%s}" % fill
        o = ' fill-opacity="%s"' % opacity if opacity is not None else ""
        self.add('<ellipse cx="%s" cy="%s" rx="%s" ry="%s" fill="%s"%s stroke="{%s}" stroke-width="%s"%s/>'
                 % (n(x), n(y), n(rx), n(ry), f, o, stroke, n(sw), d))

    def render(self, theme):
        t = THEMES[theme]
        body = "\n".join(self.items)
        for k, v in t.items():
            body = body.replace("{%s}" % k, v)
        return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d" role="img" '
                'aria-labelledby="t d" font-family="%s">\n<title id="t">%s</title>\n<desc id="d">%s</desc>\n'
                '<defs><marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" '
                'orient="auto-start-reverse"><path d="M0,0L10,5L0,10z" fill="%s"/></marker></defs>\n'
                '<rect width="100%%" height="100%%" rx="12" fill="%s"/>\n%s\n</svg>\n'
                % (self.w, self.h, self.w, self.h, SANS.replace("'", "&apos;"), escape(self.title), escape(self.desc),
                   t["line"], t["paper"], body))


def header(f, title, sub):
    """Title and subtitle at the top left."""
    f.text(24, 38, title, 20, bold=True)
    f.text(24, 62, sub, 14, fill="quiet")



# ---------------------------------------------------------------- tree facts
def read(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as fh:
        return fh.read()


def lite_facts():
    """The four facts under `lite:` in goatlite.yaml, in file order."""
    out, inside = [], False
    for line in read("goatlite.yaml").splitlines():
        if re.match(r"^lite:\s*$", line):
            inside = True
            continue
        if inside:
            m = re.match(r"^  (\w+):\s*(\S.*?)\s*$", line)
            if m:
                out.append((m.group(1), m.group(2)))
            elif line and not line.startswith(" "):
                break
    return out


def site_vars(name):
    text = read("ops", "ansible", "group_vars", name + "_hosts", "vars.yml")
    v = {}
    for line in text.splitlines():
        m = re.match(r"^(\w+):\s*\"?([^\"#]*?)\"?\s*(#.*)?$", line)
        if m:
            v[m.group(1)] = m.group(2)
    return v


def expand(s, v):
    return re.sub(r"\{\{\s*(\w+)\s*\}\}", lambda m: v[m.group(1)], s)


def machine(name):
    text = read("ops", "ansible", "inventory", "mgmt-hosts.ini")
    m = re.search(r"^\[%s_hosts\]\s*\n(\S+)" % re.escape(name), text, re.M)
    if not m:
        sys.exit("make-figures: no host under [%s_hosts] in ops/ansible/inventory/mgmt-hosts.ini" % name)
    return m.group(1)


def service_names(v):
    """The service host names the site's vars render, in a fixed order."""
    out = []
    for key in ("site_vip_dns", "auth_issuer", "portal_traefik_host", "portal_router_endpoint"):
        host = re.sub(r"^(https?://|tls/)", "", expand(v[key], v))
        out.append(re.split(r"[/:]", host)[0])
    return out


def owned_paths(name):
    paths = ["ops/ansible/group_vars/%s_hosts/" % name, "ops/ansible/inventory/", "ops/pins/", "ops/enrollment/"]
    for p in paths:
        if not os.path.exists(os.path.join(ROOT, p)):
            sys.exit("make-figures: %s is missing" % p)
    return paths


W = 880


def fit(s, size, width, mono=False, bold=False):
    """Refuse to draw text wider than its space."""
    if tw(s, size, mono, bold) > width:
        sys.exit("make-figures: %r does not fit in %d units; shorten it or widen the box" % (s, width))


def arrow_label(f, x1, x2, y, label):
    f.line(x1, y, x2 - 2, y, sw=2, arrow=True)
    f.text((x1 + x2) / 2, y - 10, label, 13, fill="quiet", anchor="middle")


def fig_assembly():
    ref = read("goatcore.ref").strip()
    facts = lite_facts()
    name = dict(facts)["name"]
    v = site_vars(name)
    zone, acme = v["site_dns_zone"], v.get("has_acme", "")
    box = machine(name)
    services = service_names(v)
    paths = owned_paths(name)

    title = "goatcore at a pinned release, plus this overlay, is one goatnet"
    desc = ("goatcore at %s holds the code: plays, the ops/scripts/ tools and the image builds. This repository holds "
            "only what the environment owns: four facts in goatlite.yaml (%s) and what is rendered from them (%s). "
            "Copying the overlay over a goatcore checkout gives one tree; standing it up gives the LAN goatnet %s: "
            "one box, %s, with the DNS zone %s served by the host and peers enrolling over the LAN."
            % (ref, ", ".join("%s %s" % kv for kv in facts), ", ".join(paths), name, box, zone))
    f = SVG(W, 446, title, desc)
    header(f, title, "%s is built from invented facts: every value in this repository is an example." % name)

    # left column: the two inputs
    lx, lw = 24, 292
    # goatcore
    y = 92
    f.rect(lx, y, lw, 108, fill="panel", stroke="rule", sw=1.5)
    f.text(lx + 16, y + 28, "goatcore", 16, bold=True)
    f.text(lx + lw - 16, y + 28, ref, 13, fill="quiet", mono=True, anchor="end")
    f.text(lx + 16, y + 54, "the code, at the tag in goatcore.ref:", 14, fill="quiet")
    f.text(lx + 16, y + 76, "plays, the ops/scripts/ tools,", 14)
    f.text(lx + 16, y + 96, "image builds and their base images", 14)
    # overlay
    y2 = 220
    oh = 200
    f.rect(lx, y2, lw, oh, fill="accent_soft", stroke="accent", sw=2)
    f.text(lx + 16, y2 + 28, "goatenv: this overlay", 16, bold=True)
    f.text(lx + 16, y2 + 52, "goatlite.yaml, the four facts", 14, fill="quiet")
    ky = y2 + 76
    for k, val in facts:
        f.text(lx + 28, ky, "%s:" % k, 13, mono=True, fill="quiet")
        f.text(lx + 120, ky, val, 13, mono=True, bold=True)
        ky += 19
    f.text(lx + 16, ky + 8, "rendered from them: site vars,", 14, fill="quiet")
    f.text(lx + 16, ky + 28, "inventory, pins, the CA's public half", 14, fill="quiet")

    # middle: the assembled checkout
    mx, mw = 362, 180
    my, mh = 150, 160
    f.rect(mx, my, mw, mh, fill="panel", stroke="line", sw=1.5)
    f.text(mx + mw / 2, my + 28, "one checkout", 16, bold=True, anchor="middle")
    f.text(mx + mw / 2, my + 52, "the overlay copied", 14, anchor="middle", fill="quiet")
    f.text(mx + mw / 2, my + 72, "over goatcore", 14, anchor="middle", fill="quiet")
    for i, part in enumerate(("cp -R ops", "goatlite.yaml", "goatcore/")):
        fit(part, 13, mw - 32, mono=True)
        f.text(mx + 16, my + 102 + i * 19, part, 13, mono=True)
    # converging arrows from both inputs
    f.path("M%s %s C %s %s, %s %s, %s %s" % (lx + lw, 146, lx + lw + 30, 146, mx - 30, my + 50, mx - 2, my + 50),
           sw=2, arrow=True)
    f.path("M%s %s C %s %s, %s %s, %s %s" % (lx + lw, 320, lx + lw + 30, 320, mx - 30, my + mh - 50, mx - 2, my + mh - 50),
           stroke="accent", sw=2, arrow=True)

    # right: the goatnet
    rx, rw = 604, 252
    ry, rh = 92, 328
    f.rect(rx, ry, rw, rh, fill="good_bg", stroke="good", sw=2)
    f.text(rx + 16, ry + 28, "goatnet %s" % name, 16, bold=True)
    f.text(rx + 16, ry + 50, "a LAN goatnet, one box", 14, fill="quiet")
    bx, by, bw, bh = rx + 16, ry + 70, rw - 32, 132
    f.rect(bx, by, bw, bh, fill="paper", stroke="good", sw=1.5)
    f.text(bx + 12, by + 24, box, 13, mono=True, bold=True)
    for i, s in enumerate(services):
        fit(s, 13, bw - 24, mono=True)
        f.text(bx + 12, by + 50 + i * 20, s, 13, mono=True)
    arrow_label(f, mx + mw, rx, my + mh / 2, "standup")
    # peers enrolling over the LAN
    py = by + bh + 58
    xs = [rx + 40 + i * ((rw - 80) / 4) for i in range(5)]
    for x in xs:
        f.line(x, py - 10, x if abs(x - (bx + bw / 2)) < 1 else x + (bx + bw / 2 - x) * 0.25, by + bh + 4,
               stroke="good", sw=1.2, dash="3,3")
        f.circle(x, py, 7, fill="good")
    f.text(rx + 16, py + 32, "peers enroll over the LAN", 14)
    f.text(rx + 16, py + 52, "DNS zone %s%s" % (zone, ", no ACME" if acme == "false" else ""), 13, fill="quiet")
    return f


FIGURES = [("goatnet-assembly", fig_assembly)]


def main(argv):
    check = "--check" in argv
    stale = []
    for name, fn in FIGURES:
        fig = fn()
        for theme in THEMES:
            p = os.path.join(HERE, "%s-%s.svg" % (name, theme))
            out = fig.render(theme)
            if check:
                if not os.path.isfile(p) or open(p, encoding="utf-8").read() != out:
                    stale.append(os.path.relpath(p, ROOT))
            else:
                with open(p, "w", encoding="utf-8") as fh:
                    fh.write(out)
                print(os.path.relpath(p, ROOT))
    if stale:
        print("out of date: " + ", ".join(stale) + "; run python3 -I docs/figures/make-figures.py", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

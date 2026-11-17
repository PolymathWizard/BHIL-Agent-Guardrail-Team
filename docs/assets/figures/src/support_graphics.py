#!/usr/bin/env python3
"""BHIL Guardrails Team support graphics SG01-SG10.
Writes self-contained SVG (brand fonts embedded) to ./out/svg and 2x PNG to ./out/png.
Register: BHIL Brand Guidelines v1.0, white ground, 760x460 logical canvas.
"""
import base64, math, os, sys
from html import escape

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")
W, H = 760, 460

INK, NAVY = "#0A0A0A", "#0D1B2E"
BLUE, BLUE2, BLUE3, BRIGHT = "#4FA3D1", "#2E80B0", "#1E3A5F", "#6CC0E8"
COPPER, STONE, RULE, PAPER3 = "#D97757", "#6B6258", "#D9D9D4", "#F3F3F0"

FONTS = [
    ("Newsreader", 400, "normal", "newsreader/files/newsreader-latin-400-normal.woff2"),
    ("Newsreader", 500, "normal", "newsreader/files/newsreader-latin-500-normal.woff2"),
    ("Newsreader", 400, "italic", "newsreader/files/newsreader-latin-400-italic.woff2"),
    ("IBM Plex Sans", 400, "normal", "ibm-plex-sans/files/ibm-plex-sans-latin-400-normal.woff2"),
    ("IBM Plex Sans", 600, "normal", "ibm-plex-sans/files/ibm-plex-sans-latin-600-normal.woff2"),
    ("IBM Plex Mono", 400, "normal", "ibm-plex-mono/files/ibm-plex-mono-latin-400-normal.woff2"),
    ("IBM Plex Mono", 500, "normal", "ibm-plex-mono/files/ibm-plex-mono-latin-500-normal.woff2"),
]


def font_css():
    css = []
    for fam, wt, st, path in FONTS:
        with open(os.path.join(HERE, "node_modules/@fontsource", path), "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
        css.append(
            f"@font-face{{font-family:'{fam}';font-weight:{wt};font-style:{st};"
            f"src:url(data:font/woff2;base64,{b64}) format('woff2');}}"
        )
    return "".join(css)


FAM = {
    "serif": "'Newsreader',Georgia,serif",
    "sans": "'IBM Plex Sans',Helvetica,Arial,sans-serif",
    "mono": "'IBM Plex Mono',Menlo,monospace",
}


class Fig:
    def __init__(self, num, section, title, dek):
        self.num, self.el = num, []
        self.chevron(36, 24.5)
        self.t(46, 30, f"FIG. {num:02d} · {section}", "mono", 7.5, BLUE2, w=500, ls=0.22)
        self.t(36, 58, title, "serif", 20.5, INK, w=500)
        self.t(36, 77, dek, "serif", 12, STONE, italic=True)
        self.line(36, 420, 724, 420, RULE)
        self.t(36, 437, "SOURCE  BHIL GUARDRAILS TEAM ROSTER AND SPECS · DRAFT · NOVEMBER 2026",
               "mono", 6.3, STONE, ls=0.2)
        self.t(724, 437, "BHIL · HUMAN-DIRECTED. AI-ENABLED. COMMERCIALLY TESTED.",
               "mono", 6.3, INK, anchor="end", ls=0.2, w=500)

    # primitives -----------------------------------------------------------
    def chevron(self, x, y, c=BLUE2, s=5):
        self.el.append(f'<path d="M{x},{y} l{s},{s*0.6:.1f} l-{s},{s*0.6:.1f} z" fill="{c}"/>')

    def t(self, x, y, s, fam="sans", size=8, fill=INK, w=400, anchor="start", ls=0, italic=False, rot=None):
        a = f' text-anchor="{anchor}"' if anchor != "start" else ""
        l = f' letter-spacing="{ls}em"' if ls else ""
        i = ' font-style="italic"' if italic else ""
        r = f' transform="rotate({rot} {x} {y})"' if rot is not None else ""
        self.el.append(
            f'<text x="{x}" y="{y}" font-family="{FAM[fam]}" font-size="{size}" font-weight="{w}" '
            f'fill="{fill}"{a}{l}{i}{r}>{escape(s)}</text>'
        )

    def ts(self, x, y, lines, lh=10, **kw):
        for i, s in enumerate(lines):
            self.t(x, y + i * lh, s, **kw)

    def line(self, x1, y1, x2, y2, c=RULE, sw=1, dash=None, arrow=False):
        d = f' stroke-dasharray="{dash}"' if dash else ""
        m = f' marker-end="url(#a{c[1:]})"' if arrow else ""
        self.el.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{c}" stroke-width="{sw}"{d}{m}/>')

    def path(self, d, c=BLUE2, sw=1, dash=None, arrow=False):
        da = f' stroke-dasharray="{dash}"' if dash else ""
        m = f' marker-end="url(#a{c[1:]})"' if arrow else ""
        self.el.append(f'<path d="{d}" fill="none" stroke="{c}" stroke-width="{sw}"{da}{m}/>')

    def rect(self, x, y, w, h, c=BLUE2, fill="none", sw=1, dash=None, op=None):
        da = f' stroke-dasharray="{dash}"' if dash else ""
        o = f' fill-opacity="{op}"' if op else ""
        st = f'stroke="{c}" stroke-width="{sw}"' if c else 'stroke="none"'
        self.el.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}" {st}{da}{o}/>')

    def diamond(self, x, y, r=6, c=COPPER, fill=COPPER):
        self.el.append(f'<path d="M{x},{y-r} L{x+r},{y} L{x},{y+r} L{x-r},{y} z" fill="{fill}" stroke="{c}"/>')

    def circle(self, x, y, r, c=BLUE2, fill="#FFFFFF", sw=1):
        self.el.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{fill}" stroke="{c}" stroke-width="{sw}"/>')

    def box(self, x, y, w, h, lines, c=BLUE2, fill="none", tc=INK, size=8, wt=600, sub=None, subc=STONE):
        """Hairline box with centered label lines and optional smaller sub lines."""
        self.rect(x, y, w, h, c, fill)
        sub = sub or []
        n = len(lines) + len(sub)
        lh = size + 2
        total = len(lines) * lh + len(sub) * (size + 0.5)
        yy = y + (h - total) / 2 + size - 0.5
        for s in lines:
            self.t(x + w / 2, yy, s, "sans", size, tc, w=wt, anchor="middle")
            yy += lh
        for s in sub:
            self.t(x + w / 2, yy - 0.5, s, "sans", size - 1.2, subc, anchor="middle")
            yy += size + 0.5

    def svg(self, fonts):
        cols = [BLUE2, COPPER, STONE, INK, BLUE3, NAVY]
        markers = "".join(
            f'<marker id="a{c[1:]}" viewBox="0 0 8 8" refX="7" refY="4" markerWidth="6" markerHeight="6" '
            f'orient="auto-start-reverse"><path d="M0,0.8 L7.5,4 L0,7.2 z" fill="{c}"/></marker>'
            for c in cols
        )
        return (
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">'
            f"<defs><style>{fonts}</style>{markers}</defs>"
            f'<rect width="{W}" height="{H}" fill="#FFFFFF"/>' + "".join(self.el) + "</svg>"
        )


# ---------------------------------------------------------------------------
def sg01():
    f = Fig(1, "TEAM FUNCTIONS", "One conductor, nine specialists, and a person at every exit",
            "Work fans out from the Conductor and returns to it. Nothing leaves the team without a human decision.")
    f.box(300, 100, 160, 34, ["CONDUCTOR"], NAVY, NAVY, "#FFFFFF", 8.5, 600,
          sub=["routes work · delegates only"], subc=BRIGHT)
    order = [("02", ["Intake"]), ("03", ["Threat", "Modeler"]), ("07", ["Privacy", "Guardian"]),
             ("06", ["Supply Chain", "Auditor"]), ("05", ["Code", "Reviewer"]),
             ("04", ["Policy", "Steward"]), ("08", ["Red", "Team"]), ("09", ["Verifier"]), ("10", ["Sentinel"])]
    x0, bw, gap, by, bh = 59, 66, 6, 186, 54
    xs = [x0 + i * (bw + gap) for i in range(9)]
    groups = [("ASSESS", 0, 4), ("CHANGE AND TEST", 5, 6), ("CHECK", 7, 7), ("WATCH", 8, 8)]
    f.line(380, 134, 380, 146, BLUE2)
    centers = []
    for name, a, b in groups:
        gx1, gx2 = xs[a], xs[b] + bw
        cx = (gx1 + gx2) / 2
        centers.append(cx)
        f.line(cx, 146, cx, 156, BLUE2)
        f.t(cx, 168, name, "mono", 6.3, BLUE2, w=500, anchor="middle", ls=0.2)
        f.line(gx1, 176, gx2, 176, BLUE2)
    f.line(centers[0], 146, centers[-1], 146, BLUE2)
    for (num, nm), x in zip(order, xs):
        f.rect(x, by, bw, bh, BLUE2)
        f.t(x + 6, by + 12, num, "mono", 6.3, BLUE2, w=500, ls=0.1)
        yy = by + (30 if len(nm) == 1 else 26)
        for s in nm:
            f.t(x + bw / 2, yy, s, "sans", 8.3, INK, w=600, anchor="middle")
            yy += 10.5
    # human exits
    vx, sx = xs[7] + bw / 2, xs[8] + bw / 2
    hy = 300
    f.path(f"M{vx},{by+bh} V272 H502 V{hy-1}", COPPER, arrow=True)
    f.path(f"M{vx},272 V{hy-1}", COPPER, arrow=True)
    f.path(f"M{sx},{by+bh} V{hy-1}", COPPER, arrow=True)
    for x, w, a, b in [(460, 84, "CLEAR", "engagement lead"), (554, 84, "MERGE", "repo or security owner"),
                       (644, 80, "RESUME", "engagement lead")]:
        f.rect(x, hy, w, 40, COPPER)
        f.t(x + w / 2, hy + 17, a, "mono", 7.5, COPPER, w=500, anchor="middle", ls=0.2)
        f.t(x + w / 2, hy + 30, b, "sans", 7, INK, anchor="middle")
    f.t(450, hy + 17, "HUMAN", "mono", 6.3, COPPER, w=500, anchor="end", ls=0.2)
    f.t(450, hy + 28, "DECISIONS", "mono", 6.3, COPPER, w=500, anchor="end", ls=0.2)
    f.ts(59, 286, ["Specialists never message each other.",
                   "Every result returns to the Conductor",
                   "as a validated record."], 13, fam="sans", size=9.5, fill=INK)
    # legend
    ly = 380
    for x, c, fill, lab in [(59, NAVY, NAVY, "Orchestrator"), (150, BLUE2, "none", "Specialist agent"),
                            (262, COPPER, "none", "Decision a person owns")]:
        f.rect(x, ly - 7, 9, 9, c, fill)
        f.t(x + 15, ly + 1, lab, "sans", 8, STONE)
    return f


def sg02():
    f = Fig(2, "PROCESS · SAFE-PROJECT CLEARANCE", "A project clears in eight steps, and a person takes the seventh",
            "Three specialists assess in parallel at step three. The Verifier recommends; the engagement lead decides.")
    steps = [
        (["Conductor"], ["opens the run,", "sets the budget"]),
        (["Intake"], ["scope manifest,", "classification,", "risk tier"]),
        None,
        (["Policy", "Steward"], ["maps controls,", "opens a PR", "for each gap"]),
        (["Red Team"], ["runs the corpus", "in the sandbox", "(Standard, High)"]),
        (["Verifier"], ["re-checks findings,", "builds the", "clearance packet"]),
        (["Engagement", "lead"], ["Clear, Clear with", "conditions,", "or Block"]),
        (["Sentinel"], ["14 days in detect", "mode, then", "continuous"]),
    ]
    x0, cw, bw, cy, bh = 40, 86, 72, 190, 32
    for i in range(8):
        x = x0 + i * cw
        f.t(x + bw / 2, 124, f"{i+1:02d}", "mono", 7, COPPER if i == 6 else BLUE2, w=500, anchor="middle", ls=0.2)
        if i == 2:
            par = [(["Threat", "Modeler"], 136), (["Privacy", "Guardian"], cy - bh / 2), (["Supply Chain", "Auditor"], 212)]
            for nm, y in par:
                f.box(x, y, bw, bh, nm, BLUE2, size=7.8)
            f.line(x - 7, 152, x - 7, 228, BLUE2)
            f.line(x + bw + 7, 152, x + bw + 7, 228, BLUE2)
            for y in (152, 228):
                f.line(x - 7, y, x, y, BLUE2)
                f.line(x + bw, y, x + bw + 7, y, BLUE2)
            f.ts(x + bw / 2, 264, ["threat table,", "data review,", "tool review"], 9.5,
                 fam="sans", size=7.5, fill=STONE, anchor="middle")
        else:
            nm, cap = steps[i]
            if i == 6:
                f.box(x, cy - bh / 2, bw, bh, nm, COPPER, size=7.8)
            elif i == 0:
                f.box(x, cy - bh / 2, bw, bh, nm, NAVY, NAVY, "#FFFFFF", size=7.8)
            else:
                f.box(x, cy - bh / 2, bw, bh, nm, BLUE2, size=7.8)
            f.ts(x + bw / 2, 264, cap, 9.5, fam="sans", size=7.5, fill=STONE, anchor="middle")
        if i < 7:
            c = COPPER if i in (5, 6) else BLUE2
            a = x + bw + (8 if i == 2 else 1)
            b = x + cw - (8 if i == 1 else 1)
            f.line(a, cy, b, cy, c, arrow=True)
    # risk tier strip
    f.line(40, 304, 724, 304, RULE)
    f.t(40, 322, "RISK TIER, SET AT STEP 02", "mono", 6.5, BLUE2, w=500, ls=0.2)
    tiers = [("LOW", ["Read-only on public data,", "no memory writes."], BLUE, 40),
             ("STANDARD", ["Everything between.", "Red Team joins from here."], BLUE2, 240),
             ("HIGH", ["External comms, spend, code execution, personal or client", "data, or a new MCP server. Needs a second human at step 07."], BLUE3, 440)]
    for nm, ls_, c, x in tiers:
        f.line(x, 336, x, 392, c, 2)
        f.t(x + 9, 346, nm, "mono", 7, c, w=500, ls=0.2)
        f.ts(x + 9, 362, ls_, 11, fam="sans", size=8, fill=INK)
    return f


def sg03():
    f = Fig(3, "PROCESS · CODE REVIEW", "The agents draft the review. A person owns the merge.",
            "Every pull request gets the Code Reviewer; the other specialists join only when the diff touches their ground.")
    lanes = [("CONDUCTOR", 100, 140), ("REVIEWERS", 140, 236), ("RED TEAM", 236, 276),
             ("VERIFIER", 276, 316), ("PERSON", 316, 356)]
    for nm, y1, y2 in lanes:
        f.line(40, y1, 724, y1, RULE)
        f.t(40, (y1 + y2) / 2 + 2.5, nm, "mono", 6.5, COPPER if nm == "PERSON" else BLUE2, w=500, ls=0.2)
    f.line(40, 356, 724, 356, RULE)
    f.box(130, 108, 120, 24, ["Opens a run on the diff hash"], NAVY, NAVY, "#FFFFFF", 7.5)
    rv = [(148, "Code Reviewer", "every pull request"),
          (176, "Supply Chain Auditor", "if dependencies, MCP config or tool definitions change"),
          (204, "Privacy Guardian", "if data handling changes")]
    f.path("M190,132 V187 H262", BLUE2)
    f.line(262, 159, 262, 215, BLUE2)
    for y, nm, cond in rv:
        f.line(262, y + 11, 271, y + 11, BLUE2, arrow=True)
        f.rect(272, y, 100, 22, BLUE2)
        f.t(322, y + 14, nm, "sans", 7.8, INK, w=600, anchor="middle")
        f.t(380, y + 14, cond, "sans", 7.5, STONE, italic=False)
    # collector to red team
    f.path("M572,159 H580 V215 H572", BLUE2)
    f.path("M580,187 H640 V256 H601", BLUE2, arrow=True)
    f.rect(500, 245, 100, 22, BLUE2)
    f.t(550, 259, "Red Team", "sans", 7.8, INK, w=600, anchor="middle")
    f.t(492, 259, "if prompts, tools, message handling or memory change", "sans", 7.5, STONE, anchor="end")
    f.path("M550,267 V284", BLUE2, arrow=True)
    f.rect(470, 285, 160, 22, BLUE2)
    f.t(550, 299, "Verifier: one consolidated review", "sans", 7.8, INK, w=600, anchor="middle")
    f.t(462, 299, "Approve, Changes requested, or Block", "sans", 7.5, STONE, anchor="end")
    f.path("M550,307 V324", COPPER, arrow=True)
    f.rect(470, 325, 160, 22, COPPER)
    f.t(550, 339, "Repo owner merges", "sans", 7.8, INK, w=600, anchor="middle")
    f.ts(40, 378, ["Every finding points to a file and a line. Text in the diff that addresses the reviewer",
                   "is reported as a finding and never followed."], 12, fam="sans", size=8.5, fill=INK)
    return f


def sg04():
    f = Fig(4, "PROCESS · GUARDRAILS UPKEEP", "Upkeep is a loop that ends in a signed policy bundle",
            "A change in the threat picture travels through four agents and one person before any agent loads it.")
    cx, cy, r = 268, 252, 92
    nodes = [("01", "Trigger", ["drift watch, incident", "or new threat"], STONE),
             ("02", "Threat Modeler", ["proposes the change,", "with source links"], BLUE2),
             ("03", "Policy Steward", ["drafts the policy", "or schema PR"], BLUE2),
             ("04", "Red Team", ["adds corpus cases,", "runs the regression"], BLUE2),
             ("05", "Verifier", ["checks mappings", "and thresholds"], BLUE2),
             ("06", "Security owner", ["merges; CI signs", "the bundle"], COPPER)]
    pos = []
    for i in range(6):
        a = math.radians(-90 + 60 * i)
        pos.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    for i in range(6):
        a1 = math.radians(-90 + 60 * i + 11)
        a2 = math.radians(-90 + 60 * (i + 1) - 12)
        x1, y1 = cx + r * math.cos(a1), cy + r * math.sin(a1)
        x2, y2 = cx + r * math.cos(a2), cy + r * math.sin(a2)
        c = COPPER if i in (4, 5) else BLUE2
        f.path(f"M{x1:.1f},{y1:.1f} A{r},{r} 0 0 1 {x2:.1f},{y2:.1f}", c, arrow=True)
    for i, ((num, nm, sub, c), (x, y)) in enumerate(zip(nodes, pos)):
        f.circle(x, y, 12, c)
        f.t(x, y + 2.5, num, "mono", 7, c, w=500, anchor="middle")
        if i == 0:
            f.t(x, y - 34, nm, "sans", 8.5, INK, w=600, anchor="middle")
            f.t(x, y - 23, "drift watch, incident or new threat", "sans", 7.5, STONE, anchor="middle")
        elif i == 3:
            f.t(x, y + 26, nm, "sans", 8.5, INK, w=600, anchor="middle")
            f.t(x, y + 37, "adds corpus cases, runs the regression", "sans", 7.5, STONE, anchor="middle")
        else:
            right = i in (1, 2)
            lx = x + 20 if right else x - 20
            an = "start" if right else "end"
            f.t(lx, y - 5, nm, "sans", 8.5, INK, w=600, anchor=an)
            f.ts(lx, y + 6, sub, 9.5, fam="sans", size=7.5, fill=STONE, anchor=an)
    f.t(cx, cy - 3, "POLICY", "mono", 6.5, BLUE2, w=500, anchor="middle", ls=0.22)
    f.t(cx, cy + 8, "AS CODE", "mono", 6.5, BLUE2, w=500, anchor="middle", ls=0.22)
    # thresholds panel
    px = 520
    f.line(px - 22, 108, px - 22, 396, RULE)
    f.t(px, 120, "WHAT THE VERIFIER HOLDS THE CHANGE TO", "mono", 6.3, BLUE2, w=500, ls=0.18)
    f.t(px, 176, "95%", "serif", 44, INK, w=400)
    f.t(px, 192, "MINIMUM BLOCK RATE", "mono", 6.5, STONE, ls=0.2)
    f.t(px, 205, "on the red-team corpus, per threat ID", "sans", 8, INK)
    f.t(px, 268, "2%", "serif", 44, INK, w=400)
    f.t(px, 284, "MAXIMUM FALSE POSITIVES", "mono", 6.5, STONE, ls=0.2)
    f.t(px, 297, "on the same run", "sans", 8, INK)
    f.line(px, 322, 724, 322, RULE)
    f.ts(px, 340, ["After the merge, the Sentinel confirms", "every agent loaded the new bundle version."], 11.5,
         fam="sans", size=8.5, fill=INK)
    return f


def sg05():
    f = Fig(5, "AGENT CAPABILITIES", "Ten narrow grants, and three columns only a person can fill",
            "Each row is one agent's whole reach. Anything not marked is denied by default.")
    cols = [["READ"], ["PROPOSE"], ["OPEN", "A PR"], ["RUN IN", "SANDBOX"], ["DELEGATE"], ["PAUSE", "OR HALT"],
            ["CLEAR"], ["MERGE"], ["RESUME"]]
    rows = [("01", "Conductor", [4]), ("02", "Intake", [0]), ("03", "Threat Modeler", [0, 1]),
            ("04", "Policy Steward", [0, 2]), ("05", "Code Reviewer", [0, 1]),
            ("06", "Supply Chain Auditor", [0, 1]), ("07", "Privacy Guardian", [0]),
            ("08", "Red Team", [0, 1, 3]), ("09", "Verifier", [0]), ("10", "Sentinel", [0, 5])]
    x0, cw, y0, rh = 218, 56, 136, 22.5
    for j, lab in enumerate(cols):
        cx = x0 + j * cw + cw / 2
        c = COPPER if j >= 6 else BLUE2
        for k, s in enumerate(lab):
            f.t(cx, 122 - (len(lab) - 1 - k) * 8.5, s, "mono", 6.2, c, w=500, anchor="middle", ls=0.18)
    f.line(x0 + 6 * cw + 4, 101, x0 + 9 * cw - 4, 101, COPPER)
    f.t(x0 + 7.5 * cw, 97, "PEOPLE ONLY", "mono", 6.2, COPPER, w=500, anchor="middle", ls=0.22)
    f.line(40, y0 - 6, 724, y0 - 6, INK)
    for i, (num, nm, marks) in enumerate(rows):
        y = y0 + i * rh
        f.t(40, y + 10, num, "mono", 6.5, BLUE2, w=500, ls=0.1)
        f.t(62, y + 10.5, nm, "sans", 8.8, INK, w=600 if i == 0 else 400)
        for j in range(9):
            cx = x0 + j * cw + cw / 2
            if j in marks:
                f.rect(cx - 4.5, y + 2.5, 9, 9, BLUE2, NAVY if i == 0 else BLUE2)
            else:
                f.line(cx - 3, y + 7, cx + 3, y + 7, RULE)
        f.line(40, y + rh - 5.5, 724, y + rh - 5.5, RULE)
    y = y0 + 10 * rh + 3
    f.line(40, y - 8.5, 724, y - 8.5, INK)
    f.t(62, y + 10.5, "People", "sans", 8.8, COPPER, w=600)
    for j in range(9):
        cx = x0 + j * cw + cw / 2
        if j >= 5:
            f.rect(cx - 4.5, y + 2.5, 9, 9, COPPER, COPPER)
        else:
            f.line(cx - 3, y + 7, cx + 3, y + 7, RULE)
    f.t(40, 404, "Read means the agent's own inputs only. The Conductor sees validated result fields, never raw content.",
        "sans", 7.5, STONE)
    return f


def sg06():
    f = Fig(6, "PROCESS CONCEPTS · MESSAGE TRUST", "Six checks stand between one agent's message and the next agent's context",
            "Every result is treated as untrusted input, even when it comes from a teammate.")
    y = 228
    f.box(40, y - 26, 112, 52, ["Specialist"], BLUE2, size=9, sub=["sends a signed", "task result"])
    f.box(612, y - 26, 112, 52, ["Conductor"], NAVY, NAVY, "#FFFFFF", 9, sub=["sees validated", "fields only"], subc=BRIGHT)
    f.line(152, y, 611, y, BLUE2, arrow=True)
    gates = [("01", "Signature", ["verify the sender's key"]),
             ("02", "Replay", ["reject a reused nonce or", "a message over 120 s old"]),
             ("03", "Schema", ["validate the payload"]),
             ("04", "Edge", ["is this intent allowed", "between these two agents"]),
             ("05", "Taint", ["tainted free text goes", "to the input filter"]),
             ("06", "Role tags", ["strip look-alike", "system or tool tags"])]
    for i, (num, nm, sub) in enumerate(gates):
        x = 202 + i * 72
        up = i % 2 == 0
        f.line(x, y - 58, x, y + 58, BLUE2)
        f.diamond(x, y, 5, BLUE2, "#FFFFFF")
        if up:
            by = y - 70 - (len(sub) - 1) * 9.5
            f.t(x, by - 22, num, "mono", 6.5, BLUE2, w=500, anchor="middle", ls=0.2)
            f.t(x, by - 11, nm, "sans", 9, INK, w=600, anchor="middle")
            f.ts(x, by, sub, 9.5, fam="sans", size=7.5, fill=STONE, anchor="middle")
        else:
            by = y + 72
            f.t(x, by, num, "mono", 6.5, BLUE2, w=500, anchor="middle", ls=0.2)
            f.t(x, by + 11, nm, "sans", 9, INK, w=600, anchor="middle")
            f.ts(x, by + 22, sub, 9.5, fam="sans", size=7.5, fill=STONE, anchor="middle")
    f.line(40, 356, 724, 356, RULE)
    f.t(40, 376, "IF ANY CHECK FAILS", "mono", 6.5, COPPER, w=500, ls=0.2)
    f.t(40, 392, "The message is quarantined, the receiver gets a typed refusal, and the event is logged against the sender's agent ID.",
        "sans", 8.8, INK)
    return f


def sg07():
    f = Fig(7, "PROCESS CONCEPTS · READ AND ACT", "The agents that read untrusted material hold no tools that act",
            "An injected instruction can reach a reader. It cannot reach a tool, a merge or a send.")
    heads = [(40, "UNTRUSTED MATERIAL", STONE), (262, "READERS · NO SIDE-EFFECT TOOLS", BLUE2),
             (548, "VALIDATED RECORDS ONLY", BLUE2)]
    for x, s, c in heads:
        f.t(x, 112, s, "mono", 6.5, c, w=500, ls=0.2)
    mats = ["Project briefs", "Repos and diffs", "Web pages", "Tool results", "Other agents' messages"]
    for i, s in enumerate(mats):
        y = 126 + i * 34
        f.rect(40, y, 150, 24, STONE, dash="3 2")
        f.t(115, y + 15, s, "sans", 8.5, INK, anchor="middle")
    f.line(190, 206, 252, 206, STONE, arrow=True)
    readers = [["Intake"], ["Threat Modeler"], ["Code Reviewer"], ["Supply Chain Auditor"], ["Privacy Guardian"], ["Red Team"]]
    for i, nm in enumerate(readers):
        cx_, ry = 262 + (i % 2) * 118, 126 + (i // 2) * 40
        f.box(cx_, ry, 108, 28, nm, BLUE2, size=8.3)
    f.rect(254, 118, 242, 176, RULE)
    f.ts(262, 258, ["Each returns one JSON schema.", "Every finding carries an evidence pointer."], 11,
         fam="sans", size=8, fill=STONE)
    # validation line
    f.line(522, 104, 522, 298, BLUE2, 1.6)
    f.t(522, 312, "SCHEMA AND SIGNATURE CHECK", "mono", 6, BLUE2, w=500, ls=0.2, anchor="middle")
    f.line(496, 143, 546, 143, BLUE2, arrow=True)
    f.box(548, 126, 176, 34, ["Conductor"], NAVY, NAVY, "#FFFFFF", 8.5, sub=["delegates only"], subc=BRIGHT)
    f.box(548, 178, 176, 34, ["Verifier"], BLUE2, size=8.5, sub=["read-only, context-isolated"])
    f.box(548, 242, 176, 34, ["A person"], COPPER, size=8.5, sub=["clears, merges, resumes"])
    f.line(636, 160, 636, 177, BLUE2, arrow=True)
    f.line(636, 212, 636, 241, COPPER, arrow=True)
    f.line(40, 330, 724, 330, RULE)
    f.t(40, 358, "Instructions found inside the material are reported as findings.", "serif", 15, INK, w=400)
    f.t(40, 380, "They are never followed.", "serif", 15, BLUE2, italic=True)
    return f


def sg08():
    f = Fig(8, "TEAM FUNCTIONS · HUMAN DECISIONS", "Five decisions stay with people",
            "The agent on the left prepares the evidence. The person on the right owns the outcome.")
    f.t(40, 112, "AGENT PREPARES", "mono", 6.5, BLUE2, w=500, ls=0.2)
    f.t(330, 112, "DECISION", "mono", 6.5, COPPER, w=500, ls=0.2)
    f.t(560, 112, "OWNER", "mono", 6.5, COPPER, w=500, ls=0.2)
    f.line(40, 120, 724, 120, INK)
    rows = [("D1", "Verifier", "clearance packet with a recommendation", ["Clear a project"],
             ["Engagement lead", "second person for High tier"]),
            ("D2", "Verifier", "one consolidated review of the PR", ["Merge code"], ["Repo owner"]),
            ("D3", "Policy Steward", "policy or schema pull request", ["Merge a policy bundle"], ["Security owner"]),
            ("D4", "Supply Chain Auditor", "trust-tier recommendation", ["Allowlist an MCP server or accept", "a changed tool definition"],
             ["Security owner"]),
            ("D5", "Sentinel", "incident record with trace IDs", ["Resume after a pause or halt"], ["Engagement lead"])]
    rh = 55
    for i, (code, ag, prep, dec, own) in enumerate(rows):
        yc = 120 + i * rh + rh / 2
        f.t(40, yc - 2, ag, "sans", 9.5, BLUE2, w=600)
        f.t(40, yc + 10, prep, "sans", 8, STONE)
        f.line(222, yc, 286, yc, BLUE2)
        f.diamond(296, yc, 7)
        f.t(296, yc - 12, code, "mono", 6.5, COPPER, w=500, anchor="middle", ls=0.15)
        f.line(304, yc, 322, yc, COPPER, arrow=True)
        if len(dec) == 1:
            f.t(330, yc + 4, dec[0], "serif", 13.5, INK, w=500)
        else:
            f.ts(330, yc - 3, dec, 15, fam="serif", size=13.5, fill=INK, w=500)
        if len(own) == 1:
            f.t(560, yc + 3.5, own[0], "sans", 9.5, INK, w=600)
        else:
            f.t(560, yc - 2, own[0], "sans", 9.5, INK, w=600)
            f.t(560, yc + 10, own[1], "sans", 8, STONE)
        f.line(40, 120 + (i + 1) * rh, 724, 120 + (i + 1) * rh, RULE)
    return f


def sg09():
    f = Fig(9, "PROCESS CONCEPTS · KILL SWITCH", "Three ways to stop, and only a person can restart",
            "Stopping works by revoking grants at the policy service and tool gateways, never by asking an agent to stop.")
    base = 318
    lv = [("LEVEL 1", "Pause one agent", ["That agent's grant is suspended."], 84, BLUE,
           "more than 3 authorization", "denials in 5 minutes", "Sentinel or any person", INK),
          ("LEVEL 2", "Halt the run", ["Every grant in the run is revoked.", "Memory writes freeze.",
                                       "Pending approvals are cancelled."], 126, BLUE2,
           "any cross-engagement", "access", "Sentinel or any person", INK),
          ("LEVEL 3", "Global stop", ["All runs and all agents stop."], 168, BLUE3,
           "never automatic", "", "A person only", COPPER)]
    for i, (lab, nm, eff, h, c, t1, t2, who, wc) in enumerate(lv):
        x = 50 + i * 222
        w = 200
        f.rect(x, base - h, w, h, c, sw=1.4)
        f.t(x + 12, base - h + 18, lab, "mono", 6.5, c, w=500, ls=0.22)
        f.t(x + 12, base - h + 38, nm, "serif", 16, INK, w=500)
        f.ts(x + 12, base - h + 54, eff, 11, fam="sans", size=8, fill=STONE)
        f.t(x, base + 18, "AUTOMATIC ON", "mono", 6, STONE, ls=0.2)
        f.t(x, base + 30, t1, "sans", 8.3, INK)
        if t2:
            f.t(x, base + 40.5, t2, "sans", 8.3, INK)
        f.t(x, base + 58, "TRIGGERED BY", "mono", 6, STONE, ls=0.2)
        f.t(x, base + 70, who, "sans", 8.3, wc, w=600)
    f.line(40, base, 724, base, INK)
    # resume arrow
    f.path("M694,134 H52", COPPER, dash="4 3", arrow=True)
    f.t(50, 124, "RESUME · ENGAGEMENT LEAD ONLY", "mono", 6.5, COPPER, w=500, ls=0.22)
    f.path("M694,150 V134", COPPER, dash="4 3")
    return f


def sg10():
    f = Fig(10, "ROLLOUT", "The team stands up in five stages, read-only first",
            "Each stage runs 14 days in detect mode on non-client work before its output counts.")
    stages = [("STAGE 1", "Code-review core", ["Conductor, Code Reviewer,", "Verifier"], 3, 3),
              ("STAGE 2", "Wider review", ["Supply Chain Auditor,", "Privacy Guardian"], 5, 2),
              ("STAGE 3", "Clearance: Low, Standard", ["Intake,", "Threat Modeler"], 7, 2),
              ("STAGE 4", "Clearance: High tier", ["Red Team (sandbox, corpus),", "Sentinel (telemetry)"], 9, 2),
              ("STAGE 5", "Upkeep", ["Policy Steward (repo", "and CI in place)"], 10, 1)]
    base, u, cw, bw = 318, 18, 132, 96
    f.t(40, 110, "AGENTS LIVE", "mono", 6.3, STONE, ls=0.2)
    for i, (lab, nm, add, n, new) in enumerate(stages):
        x = 66 + i * cw
        for k in range(n):
            y = base - (k + 1) * u
            isnew = k >= n - new
            f.rect(x, y + 1.5, bw, u - 3, BLUE2 if isnew else RULE, BLUE if isnew else "none", op=0.28 if isnew else None)
        f.t(x + bw / 2, base - n * u - 8, str(n), "serif", 22, INK, w=400, anchor="middle")
        f.t(x, base + 18, lab, "mono", 6.3, BLUE2, w=500, ls=0.22)
        f.t(x, base + 31, nm, "sans", 8.8, INK, w=600)
        f.t(x, base + 44, "adds", "sans", 7.3, STONE, italic=True)
        f.ts(x, base + 54, add, 9.5, fam="sans", size=7.6, fill=STONE)
    f.line(40, base, 724, base, INK)
    f.rect(150, 102, 9, 9, BLUE2, BLUE, op=0.28)
    f.t(164, 110, "added at this stage", "sans", 7.5, STONE)
    f.rect(250, 102, 9, 9, RULE)
    f.t(264, 110, "carried over", "sans", 7.5, STONE)
    return f


FIGS = [sg01, sg02, sg03, sg04, sg05, sg06, sg07, sg08, sg09, sg10]
NAMES = ["team-map", "project-clearance", "code-review", "upkeep-loop", "grant-matrix", "message-checks",
         "read-act-separation", "human-decisions", "kill-switch", "rollout"]


def main():
    os.makedirs(os.path.join(OUT, "svg"), exist_ok=True)
    os.makedirs(os.path.join(OUT, "png"), exist_ok=True)
    fonts = font_css()
    paths = []
    for fn, nm in zip(FIGS, NAMES):
        fig = fn()
        base = f"SG{fig.num:02d}_{nm}"
        p = os.path.join(OUT, "svg", base + ".svg")
        with open(p, "w") as fh:
            fh.write(fig.svg(fonts))
        paths.append((p, os.path.join(OUT, "png", base + ".png")))
    if "--no-png" in sys.argv:
        return
    from playwright.sync_api import sync_playwright
    with sync_playwright() as pw:
        br = pw.chromium.launch(executable_path="/usr/bin/google-chrome", args=["--no-sandbox"])
        pg = br.new_page(viewport={"width": W, "height": H}, device_scale_factor=2)
        for svg, png in paths:
            pg.goto("file://" + svg)
            pg.evaluate("document.fonts.ready")
            pg.wait_for_timeout(150)
            pg.screenshot(path=png)
        br.close()


if __name__ == "__main__":
    main()

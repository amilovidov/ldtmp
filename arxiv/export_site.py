"""Export LDTMP.md as an MDX research page for alexmilovidov.com.

Run from the repo root: python3 arxiv/export_site.py <site-repo>
Writes content/research/ldtmp.md and copies the figures and the PDF
into public/papers/ in the site repo.
"""

import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REPO = "https://github.com/amilovidov/ldtmp"
site = Path(sys.argv[1]).resolve()
src = (ROOT / "LDTMP.md").read_text()

date = re.search(r"Specification 1\.0, (\d{4}-\d{2}-\d{2})", src).group(1)
body = src[src.index("## Abstract"):]

# Figures: GitHub's <picture> pairs become a single light-theme <img>.
def figure(m):
    name = re.search(r"figures/(fig\d-[a-z-]+-light\.svg)", m.group(0)).group(1)
    alt = re.search(r'alt="([^"]+)"', m.group(0)).group(1)
    return f'<img src="/papers/ldtmp/{name}" alt="{alt}" />'

body = re.sub(r"<picture>.*?</picture>", figure, body, flags=re.S)

# Repo-relative links point at GitHub.
body = re.sub(r"\]\((ldtmp\.config\.json|LICENSE)\)", rf"]({REPO}/blob/main/\1)", body)

# MDX reads < and { as JSX. Escape them in prose; code spans and blocks stay literal.
def escape_prose(text):
    out = []
    for part in re.split(r"(```.*?```|`[^`\n]+`|<img [^>]+/>)", text, flags=re.S):
        if part.startswith("`") or part.startswith("<img"):
            out.append(part)
        else:
            out.append(part.replace("<", "&lt;").replace("{", "\\{").replace("}", "\\}"))
    return "".join(out)

body = escape_prose(body)

front = f'''---
title: "LDTMP: A Layered Depth Tension Modulation Protocol"
description: "A protocol that paces emotional depth in AI-led conversations. Deterministic rules choose the layer, and the language model writes inside it."
status: "Published"
---

*Technical report, Specification 1.0, {date}. Alexander Milovidov, independent researcher.*
*[Download the PDF](/papers/ldtmp.pdf). Source, constants and license on [GitHub]({REPO}). CC BY 4.0.*

'''

out = site / "content" / "research" / "ldtmp.md"
out.write_text(front + body)
figs = site / "public" / "papers" / "ldtmp"
figs.mkdir(parents=True, exist_ok=True)
for svg in (ROOT / "figures").glob("*-light.svg"):
    shutil.copy(svg, figs / svg.name)
shutil.copy(ROOT / "arxiv" / "ldtmp.pdf", site / "public" / "papers" / "ldtmp.pdf")
print(f"wrote {out}")

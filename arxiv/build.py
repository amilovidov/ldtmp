"""Build the arXiv LaTeX source and PDF from LDTMP.md.

Run from the repo root: python3 arxiv/build.py [path/to/tectonic]
Writes arxiv/ldtmp.tex and, when a TeX engine is given, arxiv/ldtmp.pdf.
The .tex uses only pdfLaTeX-safe characters, so arXiv can compile it.
"""

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "arxiv"
FIGS = {"fig1-layer-arc": "fig:arc", "fig2-one-turn": "fig:turn"}

src = (ROOT / "LDTMP.md").read_text()

# Front matter: title, date and abstract move into the template.
title = re.search(r"^# (.+)$", src, re.M).group(1)
date = re.search(r"Specification 1\.0, (\d{4}-\d{2}-\d{2})", src).group(1)
abstract = re.search(r"## Abstract\n\n(.+?)\n\n\*\*Keywords:\*\* (.+?)\n", src, re.S)
body = src[src.index("## 1. Introduction"):]

# Figures: replace each <picture> block and its bold caption with a LaTeX float.
def figure(m):
    name = re.search(r"figures/(fig\d-[a-z-]+)-light\.svg", m.group(1)).group(1)
    caption = m.group(3).strip()
    return (f"```{{=latex}}\n\\begin{{figure}}[t]\n\\centering\n"
            f"\\includegraphics[width=\\linewidth]{{{name}.pdf}}\n"
            f"\\caption{{{caption}}}\n\\label{{{FIGS[name]}}}\n\\end{{figure}}\n```")

body = re.sub(r"<picture>(.*?)</picture>\n\n\*\*Figure (\d)\.\*\* (.+?)\n", figure, body, flags=re.S)

# Pipe tables: size each column by its longest cell, so pandoc sets proportional widths.
def size_columns(m):
    rows = m.group(0).rstrip("\n").split("\n")
    cells = [[c.strip() for c in r.strip("|").split("|")] for r in rows]
    def weight(cell):
        longest = max((len(w) for w in cell.split()), default=0)
        return max(10, round(1.7 * longest), min(len(cell), 36))
    widths = [max(weight(row[i]) for k, row in enumerate(cells) if k != 1 and i < len(row))
              for i in range(len(cells[0]))]
    rows[1] = "|" + "|".join("-" * max(3, w) for w in widths) + "|"
    return "\n".join(rows) + "\n"

body = re.sub(r"(?:^\|.*\|\n)+", size_columns, body, flags=re.M)

# Tables: "**Table N.** caption" above a pipe table becomes pandoc's "Table:" caption.
body = re.sub(r"\*\*Table \d\.\*\* (.+?)\n\n", r"Table: \1\n\n", body)

meta = [
    "--metadata", f"title={title}",
    "--metadata", "author=Alexander Milovidov",
    "--metadata", f"date=Technical report, Specification 1.0, {date}",
]

def to_latex(text, *extra):
    return subprocess.run(
        ["pandoc", "-f", "markdown-auto_identifiers+autolink_bare_uris", "-t", "latex", "--no-highlight", *extra],
        input=text, capture_output=True, text=True, check=True).stdout

abstract_tex = to_latex(abstract.group(1))
keywords_tex = to_latex(abstract.group(2)).strip()
tex = subprocess.run(
    ["pandoc", "-f", "markdown-auto_identifiers+autolink_bare_uris", "-t", "latex", "--no-highlight", "--shift-heading-level-by=-1",
     "--template", str(OUT / "template.tex"), *meta,
     "--variable", f"abstract={abstract_tex}", "--variable", f"keywords={keywords_tex}"],
    input=body, capture_output=True, text=True, check=True).stdout

# pdfLaTeX-safe characters. Verbatim blocks take ASCII, prose takes math.
def fix_verbatim(m):
    return m.group(0).replace("\u2265", ">=").replace("\u2264", "<=")

tex = re.sub(r"\\begin\{verbatim\}.*?\\end\{verbatim\}", fix_verbatim, tex, flags=re.S)
tex = (tex.replace("\u2265", r"$\geq$").replace("\u2264", r"$\leq$")
          .replace("\u220e", r"\hfill$\blacksquare$"))
# Long identifiers such as EMOTIONAL_SATURATION may break after an underscore.
tex = tex.replace("\\_", "\\_\\allowbreak{}")
leftover = sorted({c for c in tex if ord(c) > 127})
if leftover:
    sys.exit(f"non-ASCII characters left in ldtmp.tex: {leftover}")

# References: hanging indent, as in APA reference lists.
start = tex.index("\\section{References}")
end = tex.index("\\section{Appendix A")
head, _, entries = tex[start:end].partition("\n\n")
tex = (tex[:start] + head + "\n\n{\\small\\setlength{\\parindent}{-1.5em}\\setlength{\\leftskip}{1.5em}\n"
       + entries.rstrip() + "\\par}\n\n" + tex[end:])

(OUT / "ldtmp.tex").write_text(tex)
print("wrote arxiv/ldtmp.tex")

if len(sys.argv) > 1:
    subprocess.run([sys.argv[1], "--keep-logs", "ldtmp.tex"], cwd=OUT, check=True)
    print("wrote arxiv/ldtmp.pdf")

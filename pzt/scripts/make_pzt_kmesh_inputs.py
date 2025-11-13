#!/usr/bin/env python3
import re
from pathlib import Path

# Template SCF input (relaxed PZT, LDA, 60/480)
template_path = Path("pzt/scf/pzt_scf.in")
text = template_path.read_text()

# Match either "K_POINTS automatic" or "K_POINTS {automatic}"
# plus the following line with 6 integers (mesh + shifts)
pattern = re.compile(
    r"K_POINTS\s*(?:\{automatic\}|automatic)\s*\n\s*"
    r"\d+\s+\d+\s+\d+\s+\d+\s+\d+\s+\d+",
    re.IGNORECASE,
)

nks = [4, 6, 8, 10]

for nk in nks:
    new_block = f"K_POINTS automatic\n {nk} {nk} {nk} 0 0 0\n"
    new_text, n_sub = pattern.subn(new_block, text, count=1)
    if n_sub != 1:
        raise RuntimeError(
            f"Could not replace K_POINTS block in template for nk = {nk}. "
            "Check pzt/scf/pzt_scf.in format."
        )
    out_path = Path(f"pzt/scf/pzt_scf_nk{nk}.in")
    out_path.write_text(new_text)
    print(f"Wrote {out_path}")

import re
from pathlib import Path

# base SCF input (relaxed quartz, LDA, 60/480)
base_path = Path("quartz/scf/quartz_scf.in")
text = base_path.read_text()

# regex to find the K_POINTS automatic block
kp_re = re.compile(
    r"K_POINTS\s+automatic\s*\n\s*\d+\s+\d+\s+\d+\s+\d+\s+\d+\s+\d+",
    re.MULTILINE
)

# k-meshes to test
nk_list = [4, 6, 8, 10]

for nk in nk_list:
    new_block = f"K_POINTS automatic\n {nk} {nk} {nk}  1 1 1"
    new_text = kp_re.sub(new_block, text, count=1)

    out_path = Path(f"quartz/scf/quartz_scf_nk{nk}.in")
    out_path.write_text(new_text)
    print(f"Written {out_path}")

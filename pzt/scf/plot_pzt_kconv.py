import numpy as np
import matplotlib.pyplot as plt
import re

nk_list = []
E_list = []

with open("pzt/scf/pzt_kconv_summary.txt", "r") as f:
    for line in f:
        line = line.strip()
        # skip comments and blank lines
        if not line or line.startswith("#"):
            continue

        # find all numbers (ints or floats, +- allowed)
        nums = re.findall(r"[-+]?\d*\.\d+|[-+]?\d+", line)

        # if we don't have at least 2 numbers, skip line
        if len(nums) < 2:
            continue

        # assume: first number = nk, last number = Energy (Ry)
        nk = float(nums[0])
        E  = float(nums[-1])

        nk_list.append(nk)
        E_list.append(E)

nk = np.array(nk_list)
E = np.array(E_list)

# sort by nk just in case
idx = np.argsort(nk)
nk = nk[idx]
E = E[idx]

# energy differences in meV relative to most converged
E_rel_meV = (E - E.min()) * 1000.0  # Ry differences × 1000 ≈ meV

plt.figure(figsize=(6,4))
plt.plot(nk, E_rel_meV, "-o", linewidth=2, markersize=8)
plt.xlabel("Nk in Nk × Nk × Nk", fontsize=12)
plt.ylabel("ΔE (meV per cell)", fontsize=12)
plt.title("PZT k-point Convergence (60/480 Ry)", fontsize=14)
plt.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig("pzt/scf/pzt_kconv_plot.png", dpi=300)
print("Saved: pzt/scf/pzt_kconv_plot.png")

plt.show()

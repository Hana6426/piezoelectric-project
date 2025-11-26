#!/usr/bin/env python3
import os
import re

# Directories for the three Berry-phase runs
runs = {
    "p005": "quartz/e11/e11_PvsStrain/eps_p0.005/tmp_quartz_e11_p0.005/quartz_e11_p0.005.save",
    "m005": "quartz/e11/e11_PvsStrain/eps_m0.005/tmp_quartz_e11_m0.005/quartz_e11_m0.005.save",
}

def get_P_from_xml(savedir):
    """
    Read QE data-file-schema.xml and extract the most recent polarization vector.
    Returns (Px, Py, Pz) in C/m^2.
    """
    xml_path = os.path.join(savedir, "data-file-schema.xml")
    if not os.path.isfile(xml_path):
        raise FileNotFoundError(f"No data-file-schema.xml in {savedir}")

    with open(xml_path, "r") as f:
        lines = f.readlines()

    candidate_lines = []
    for line in lines:
        low = line.lower()
        if "polarization" in low and any(c.isdigit() for c in line):
            candidate_lines.append(line.strip())

    if not candidate_lines:
        raise RuntimeError(f"No polarization-like lines found in {xml_path}")

    # last valid polarization line
    for last in reversed(candidate_lines):
        nums = re.findall(r"[-+]?\d+\.\d*(?:[eE][-+]?\d+)?", last)
        if len(nums) >= 3:
            Px, Py, Pz = [float(x) for x in nums[:3]]
            return Px, Py, Pz

    raise RuntimeError("Could not parse polarization numbers from XML.")

# --- main ---
Px_vals = {}

for key, savedir in runs.items():
    Px, Py, Pz = get_P_from_xml(savedir)
    Px_vals[key] = Px
    print(f"{key:4s}: Px = {Px: .6e}  Py = {Py: .6e}  Pz = {Pz: .6e}  (C/m^2)")

# central finite-difference derivative for e11 = dPx/d(epsilon_xx)
eps = 0.005  # ±0.5% strain

Px_p = Px_vals["p005"]
Px_m = Px_vals["m005"]

e11 = (Px_p - Px_m) / (2.0 * eps)

print("\nFinite-difference e11 from Berry-phase polarization:")
print(f"  Px(+0.5%) = {Px_p: .6e} C/m^2")
print(f"  Px(-0.5%) = {Px_m: .6e} C/m^2")
print(f"  e11 ≈ {e11: .6e} C/m^2")

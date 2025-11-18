#!/usr/bin/env python3
import os
import re

# Directories for the three Berry-phase runs
runs = {
    "0"   : "tmp_pzt/pzt_polar_zz_0.save",
    "p002": "tmp_pzt/pzt_polar_zz_p002.save",
    "m002": "tmp_pzt/pzt_polar_zz_m002.save",
}

def get_Pz_from_xml(savedir):
    """
    Read QE data-file-schema.xml as plain text and extract the last
    line containing 'polarization' with three numeric components.
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
        # Be stricter: require the word "polarization", not just "polar"
        if "polarization" in low and any(c.isdigit() for c in line):
            candidate_lines.append(line.strip())

    if not candidate_lines:
        raise RuntimeError(f"No polarization-like lines found in {xml_path}")

    # Walk backwards through candidates until we find one with ≥3 numbers
    for last in reversed(candidate_lines):
        nums = re.findall(r"[-+]?\d+\.\d*(?:[eE][-+]?\d+)?", last)
        if len(nums) >= 3:
            Px, Py, Pz = [float(x) for x in nums[:3]]
            return Px, Py, Pz

    # If we got here, none of the 'polarization' lines actually had numbers
    raise RuntimeError(
        f"Could not find a 'polarization' line with ≥3 floats in {xml_path}.\n"
        f"Last candidate was:\n{candidate_lines[-1]}"
    )

# ---- main ----
Pz = {}

for key, savedir in runs.items():
    Px, Py, Pz_val = get_Pz_from_xml(savedir)
    Pz[key] = Pz_val
    print(f"{key:4s}: Px = {Px: .6e}  Py = {Py: .6e}  Pz = {Pz_val: .6e}  (C/m^2)")

# central finite difference for e33 = dPz/d(ε_zz)
eps = 0.002  # ±0.2% strain
Pz_p = Pz["p002"]
Pz_m = Pz["m002"]
Pz_0 = Pz["0"]

e33 = (Pz_p - Pz_m) / (2.0 * eps)  # C/m^2 per unit strain

print("\nFinite-difference e33 from Berry-phase polarization:")
print(f"  Pz(0)     = {Pz_0: .6e} C/m^2")
print(f"  Pz(+0.2%) = {Pz_p: .6e} C/m^2")
print(f"  Pz(-0.2%) = {Pz_m: .6e} C/m^2")
print(f"  e33 ≈ {e33: .6e} C/m^2")

#!/usr/bin/env python3
import os
import xml.etree.ElementTree as ET

RY_TO_EV = 13.605693009
EV_TO_ME = 1000.0

# Directories for the three Berry-phase runs
runs = {
    "0"   : "tmp_pzt/pzt_polar_zz_0.save",
    "p002": "tmp_pzt/pzt_polar_zz_p002.save",
    "m002": "tmp_pzt/pzt_polar_zz_m002.save",
}

def get_Pz_from_xml(savedir):
    """
    Parse QE data-file-schema.xml and return Pz (C/m^2).
    We look for tags whose name contains 'polarization'.
    We then assume the last such tag has 3 components: Px, Py, Pz.
    """
    xml_path = os.path.join(savedir, "data-file-schema.xml")
    if not os.path.isfile(xml_path):
        raise FileNotFoundError(f"No data-file-schema.xml in {savedir}")

    tree = ET.parse(xml_path)
    root = tree.getroot()

    pol_elems = []
    for elem in root.iter():
        tag_lower = elem.tag.lower()
        if "polarization" in tag_lower and elem.text is not None:
            txt = elem.text.strip()
            # Only keep entries that look like numbers
            if any(c.isdigit() for c in txt):
                pol_elems.append(elem)

    if not pol_elems:
        raise RuntimeError(f"No polarization-like elements found in {xml_path}")

    # Take the last one (usually the final Berry-phase polarization)
    last = pol_elems[-1]
    comps = last.text.split()
    if len(comps) < 3:
        raise RuntimeError(f"Polarization element in {xml_path} does not have 3 components: {last.text}")

    Px, Py, Pz = [float(x) for x in comps[:3]]
    return Px, Py, Pz

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
print(f"  Pz(0)    = {Pz_0: .6e} C/m^2")
print(f"  Pz(+0.2%)= {Pz_p: .6e} C/m^2")
print(f"  Pz(-0.2%)= {Pz_m: .6e} C/m^2")
print(f"  e33 ≈ {e33: .6e} C/m^2")

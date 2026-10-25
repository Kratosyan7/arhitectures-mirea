"""Список входных пинов в .circ: схема, метка, loc, разрядность, ориентация."""
import re
import sys
import xml.etree.ElementTree as ET


def input_pins(path):
    root = ET.parse(path).getroot()
    out = {}
    for circ in root.iter("circuit"):
        for comp in circ.iter("comp"):
            if comp.get("name") != "Pin":
                continue
            a = {x.get("name"): x.get("val") for x in comp.iter("a")}
            if a.get("output") == "true":
                continue
            x, y = map(int, re.findall(r"-?\d+", comp.get("loc")))
            out[(circ.get("name"), a.get("label", ""))] = ((x, y), int(a.get("width", 1)), a.get("facing", "east"))
    return out


if __name__ == "__main__":
    for f in sys.argv[1:]:
        print("==", f)
        for k, v in input_pins(f).items():
            print(" ", k, v)

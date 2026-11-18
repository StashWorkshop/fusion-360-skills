"""Contrôle des fichiers de fabrication réellement exportés (Gerber RS-274X + perçage Excellon, sortie Fusion/EAGLE).

Usage :
    python check_gerbers.py <dossier GerberFiles> <fichier .xln> [--pads pads.json] [--clearance 0.3] [--px 0.025]

pads.json : la réponse brute de `fusion_mcp_electronics_read` sur `electronics.Pad`
(champs x, y, signal ; `coordinate_unit` inch ou mm), enregistrée telle quelle.

Vérifie : connectivité cuivre (vias compris) contre la netlist, isolement entre nets, cuivre près du bord,
sérigraphie sur les ouvertures de vernis, trait de sérigraphie trop fin, dimensions de la carte.
Codes de sortie : 0 OK ; 1 BLOQUANT (court-circuit, liaison ouverte, isolement < 0,15 mm, sérigraphie sur
pastille) ; 2 À CORRIGER (isolement sous la cible, fabricable mais risque de pont de soudure).
"""
import argparse
import json
import math
import re
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

PCBWAY_MIN_CLEARANCE = 0.15  # mm
PCBWAY_MIN_SILK = 0.15  # mm


class Gerber:
    """Lecteur du sous-ensemble RS-274X produit par Fusion : apertures C/R/O/OC8, D01/D02/D03, régions, arcs."""

    def __init__(self, path: Path):
        self.text = path.read_text(errors="replace")
        m = re.search(r"%FSLAX(\d)(\d)Y\d\d\*%", self.text)
        self.scale = 10 ** int(m.group(2)) if m else 10000
        self.inch = "%MOIN*%" in self.text

    def coord(self, value: str) -> float:
        v = int(value) / self.scale
        return v * 25.4 if self.inch else v

    def draw(self, img: Image.Image, to_px, px_mm: float) -> None:
        draw = ImageDraw.Draw(img)
        apertures, cur, color = {}, ("C", 0.0, 0.0), 255
        pos, region, verts, mode = (0.0, 0.0), False, [], "G01"
        unit = 25.4 if self.inch else 1.0
        for raw in self.text.replace("\n", "").split("*"):
            line = raw.strip().lstrip("%")
            m = re.match(r"ADD(\d+)(C|R|O|OC8)?,?([\d.]+)?(?:X([\d.]+))?", line)
            if m and m.group(3):
                shape = "R" if m.group(2) == "R" else "C"  # ovale et octogone : approchés par un cercle/rectangle
                if m.group(2) == "O":
                    shape = "O"
                apertures[int(m.group(1))] = (shape, float(m.group(3)) * unit, float(m.group(4) or 0) * unit)
                continue
            if line.startswith("LPD"):
                color = 255
            elif line.startswith("LPC"):
                color = 0
            elif line == "G36":
                region, verts = True, []
            elif line == "G37":
                if len(verts) >= 3:
                    draw.polygon([to_px(*v) for v in verts], fill=color)
                region = False
            elif line in ("G01", "G02", "G03"):
                mode = line
            m = re.fullmatch(r"(?:G0([123]))?D(\d+)", line)
            if m and int(m.group(2)) >= 10:
                cur = apertures.get(int(m.group(2)), cur)
                continue
            m = re.fullmatch(r"(?:G0([123]))?(?:X(-?\d+))?(?:Y(-?\d+))?(?:I(-?\d+))?(?:J(-?\d+))?D0([123])", line)
            if not m:
                continue
            if m.group(1):
                mode = "G0" + m.group(1)
            x = self.coord(m.group(2)) if m.group(2) else pos[0]
            y = self.coord(m.group(3)) if m.group(3) else pos[1]
            op = m.group(6)
            points = [pos, (x, y)]
            if op == "1" and mode in ("G02", "G03") and (m.group(4) or m.group(5)):
                cx = pos[0] + (self.coord(m.group(4)) if m.group(4) else 0)
                cy = pos[1] + (self.coord(m.group(5)) if m.group(5) else 0)
                a0, a1 = math.atan2(pos[1] - cy, pos[0] - cx), math.atan2(y - cy, x - cx)
                if mode == "G03" and a1 <= a0:
                    a1 += 2 * math.pi
                if mode == "G02" and a1 >= a0:
                    a1 -= 2 * math.pi
                r = math.hypot(pos[0] - cx, pos[1] - cy)
                steps = max(4, int(abs(a1 - a0) * r / 0.05))
                points = [(cx + r * math.cos(a0 + (a1 - a0) * i / steps), cy + r * math.sin(a0 + (a1 - a0) * i / steps))
                          for i in range(steps + 1)]
            if region:
                if op == "2":
                    verts = [(x, y)]
                elif op == "1":
                    verts.extend(points[1:])
            elif op == "1":
                width = max(1, round(cur[1] / px_mm))
                draw.line([to_px(*p) for p in points], fill=color, width=width, joint="curve")
                for p in (points[0], points[-1]):
                    X, Y = to_px(*p)
                    r = cur[1] / 2 / px_mm
                    draw.ellipse([X - r, Y - r, X + r, Y + r], fill=color)
            elif op == "3":
                X, Y = to_px(x, y)
                shape, a, b = cur
                if shape == "C":
                    r = a / 2 / px_mm
                    draw.ellipse([X - r, Y - r, X + r, Y + r], fill=color)
                else:
                    b = b or a
                    draw.rounded_rectangle([X - a / 2 / px_mm, Y - b / 2 / px_mm, X + a / 2 / px_mm, Y + b / 2 / px_mm],
                                           radius=min(a, b) / 2 / px_mm if shape == "O" else 0, fill=color)
            pos = (x, y)

    def extent(self) -> tuple[float, float, float, float]:
        xs = [self.coord(v) for v in re.findall(r"X(-?\d+)", self.text)]
        ys = [self.coord(v) for v in re.findall(r"Y(-?\d+)", self.text)]
        return min(xs), min(ys), max(xs), max(ys)


def read_drill(path: Path) -> list[tuple[float, float, float]]:
    """Trous (x, y, diamètre) en mm. Format Excellon de Fusion : METRIC|INCH, TZ, 000.000 → 3 décimales implicites."""
    text = path.read_text(errors="replace")
    inch = "INCH" in text and "METRIC" not in text
    fmt = re.search(r"(?:METRIC|INCH),\w+,(0+)\.(0+)", text)
    decimals = len(fmt.group(2)) if fmt else 3
    unit = 25.4 if inch else 1.0
    tools, holes, tool = {}, [], None
    for line in text.splitlines():
        line = line.strip()
        m = re.fullmatch(r"(T\d+)C([\d.]+)", line)
        if m:
            tools[m.group(1)] = float(m.group(2)) * unit
            continue
        if re.fullmatch(r"T\d+", line):
            tool = line
            continue
        m = re.fullmatch(r"X(-?[\d.]+)Y(-?[\d.]+)", line)
        if m and tool in tools:
            conv = lambda v: (float(v) if "." in v else int(v) / 10 ** decimals) * unit  # noqa: E731
            holes.append((conv(m.group(1)), conv(m.group(2)), tools[tool]))
    return holes


def disk(radius_px: int) -> list[tuple[int, int]]:
    return [(dx, dy) for dy in range(-radius_px, radius_px + 1) for dx in range(-radius_px, radius_px + 1)
            if dx * dx + dy * dy <= radius_px * radius_px]


def dilate(mask: np.ndarray, radius_px: int) -> np.ndarray:
    out = np.zeros_like(mask)
    h, w = mask.shape
    for dx, dy in disk(radius_px):
        out[max(0, dy):h + min(0, dy), max(0, dx):w + min(0, dx)] |= mask[max(0, -dy):h + min(0, -dy), max(0, -dx):w + min(0, -dx)]
    return out


def label(mask: np.ndarray, seeds: list[tuple[int, int]]) -> tuple[np.ndarray, list[int]]:
    """Étiquette les composantes de cuivre touchées par chaque graine (0 = pas de cuivre au centre)."""
    img = Image.fromarray(mask.astype(np.uint8) * 255).convert("I")
    labels = []
    for i, (X, Y) in enumerate(seeds):
        if not (0 <= X < img.width and 0 <= Y < img.height):
            labels.append(0)
            continue
        v = img.getpixel((X, Y))
        if v == 255:
            ImageDraw.floodfill(img, (X, Y), 1000 + i)
            v = 1000 + i
        labels.append(v if v >= 1000 else 0)
    return np.array(img), labels


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("gerbers", type=Path)
    ap.add_argument("drill", type=Path)
    ap.add_argument("--pads", type=Path, help="réponse JSON de fusion_mcp_electronics_read sur electronics.Pad")
    ap.add_argument("--clearance", type=float, default=0.3, help="isolement visé en mm (défaut 0,3)")
    ap.add_argument("--px", type=float, default=0.025, help="résolution en mm par pixel")
    args = ap.parse_args()
    g, PX, blocking, to_fix = args.gerbers, args.px, [], []

    x0, y0, x1, y1 = Gerber(g / "profile.gbr").extent()
    W, H = int((x1 - x0) / PX) + 2, int((y1 - y0) / PX) + 2
    to_px = lambda x, y: ((x - x0) / PX, (y1 - y) / PX)  # noqa: E731
    print(f"Carte : {x1 - x0:.2f} × {y1 - y0:.2f} mm")

    def render(name: str) -> np.ndarray:
        img = Image.new("L", (W, H), 0)
        Gerber(g / name).draw(img, to_px, PX)
        return np.array(img) > 127

    holes = read_drill(args.drill)
    sizes = sorted({round(d, 2) for *_, d in holes})
    print(f"Perçages : {len(holes)} trous, diamètres {sizes} mm" + ("  ← perçage < 0,3 mm" if sizes and sizes[0] < 0.3 else ""))
    seeds = [tuple(map(int, to_px(x, y))) for x, y, _ in holes]

    # Connectivité : composantes du dessus et du dessous reliées par chaque trou métallisé.
    layers = {"dessus": render("copper_top.gbr"), "dessous": render("copper_bottom.gbr")}
    parent = list(range(len(holes)))

    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    for mask in layers.values():
        _, labels = label(mask, seeds)
        first = {}
        for i, lab in enumerate(labels):
            if lab:
                parent[find(i)] = find(first.setdefault(lab, i))
    clusters = {}
    for i in range(len(holes)):
        clusters.setdefault(find(i), []).append(i)
    hole_net = {i: root for root, members in clusters.items() for i in members}

    if args.pads:
        data = json.loads(args.pads.read_text(encoding="utf-8-sig"))
        factor = 25.4 if data.get("coordinate_unit", "inch") == "inch" else 1.0
        expected = {}
        for pad in data["items"]:
            if pad.get("signal"):
                expected.setdefault(pad["signal"], []).append((pad["x"] * factor, pad["y"] * factor))
        def nearest(x, y):
            i = min(range(len(holes)), key=lambda k: math.hypot(holes[k][0] - x, holes[k][1] - y))
            return i if math.hypot(holes[i][0] - x, holes[i][1] - y) < 0.2 else None
        net_of_cluster, problems = {}, []
        for net, points in expected.items():
            idx = [nearest(x, y) for x, y in points]
            if None in idx:
                problems.append(f"OUVERT ? {net} : une pastille sans perçage à sa position (CMS ou décalage)")
                continue
            roots = {hole_net[i] for i in idx}
            if len(roots) > 1:
                problems.append(f"OUVERT : {net} coupé en {len(roots)} morceaux")
            for r in roots:
                if net_of_cluster.setdefault(r, net) != net:
                    problems.append(f"COURT-CIRCUIT : {net} relié à {net_of_cluster[r]}")
        print("Connectivité contre la netlist :", "OK" if not problems else f"{len(problems)} défaut(s)")
        for p in problems:
            print("  " + p)
        blocking += problems
    else:
        print(f"Connectivité : {sum(len(m) > 1 for m in clusters.values())} groupes de trous reliés (sans netlist : non comparé)")

    # Isolement : chaque composante dilatée de d/2 ne doit toucher aucune autre composante dilatée de d/2.
    for side, mask in layers.items():
        img, labels = label(mask, seeds)
        comp_net = {}
        for i, lab in enumerate(labels):
            if lab:
                comp_net.setdefault(lab, hole_net[i])
        worst = {}
        for d in (PCBWAY_MIN_CLEARANCE, args.clearance):
            r = max(1, round((d - PX) / 2 / PX))  # un pixel de tolérance : pas d'alerte sur un isolement pile au seuil
            seen = {}
            for lab, net in comp_net.items():
                ys, xs = np.nonzero(img == lab)
                if not len(xs):
                    continue
                ya, yb, xa, xb = max(0, ys.min() - 2 * r), ys.max() + 2 * r + 1, max(0, xs.min() - 2 * r), xs.max() + 2 * r + 1
                grown = dilate(img[ya:yb, xa:xb] == lab, 2 * r)
                hits = np.unique(img[ya:yb, xa:xb][grown & (img[ya:yb, xa:xb] >= 1000) & (img[ya:yb, xa:xb] != lab)])
                for other in hits:
                    if comp_net.get(int(other), net) != net:
                        key = tuple(sorted((lab, int(other))))
                        if key not in seen:
                            yy, xx = np.nonzero(grown & (img[ya:yb, xa:xb] == other))
                            seen[key] = ((xx[0] + xa) * PX + x0, y1 - (yy[0] + ya) * PX)
            worst[d] = seen
        under_min = worst[PCBWAY_MIN_CLEARANCE]
        under_target = {k: v for k, v in worst[args.clearance].items() if k not in under_min}
        print(f"Isolement cuivre {side} : {len(under_min)} cas < {PCBWAY_MIN_CLEARANCE} mm, "
              f"{len(under_target)} cas < {args.clearance} mm (précision ±{PX:.3f} mm)")
        for (a, b), (x, y) in list(under_min.items()) + list(under_target.items()):
            print(f"  près de ({x:.2f} ; {y:.2f}) mm")
        blocking += [f"isolement < {PCBWAY_MIN_CLEARANCE} mm ({side})"] * len(under_min)
        to_fix += [f"{len(under_target)} isolement(s) < {args.clearance} mm ({side})"] if under_target else []
        band = max(1, round(0.3 / PX))
        edge = mask[:band].any() or mask[-band:].any() or mask[:, :band].any() or mask[:, -band:].any()
        print(f"  cuivre à moins de 0,3 mm du bord : {'OUI' if edge else 'non'}")

    # Sérigraphie : jamais sur une ouverture de vernis ; trait ≥ 0,15 mm.
    for side, suffix in (("dessus", "top"), ("dessous", "bottom")):
        silk_file, mask_file = g / f"silkscreen_{suffix}.gbr", g / f"soldermask_{suffix}.gbr"
        if not silk_file.exists():
            continue
        silk = render(silk_file.name)
        on_pads = silk & render(mask_file.name) if mask_file.exists() else np.zeros_like(silk)
        k = 2 * round(PCBWAY_MIN_SILK / 2 / PX) + 1
        opened = np.array(Image.fromarray(silk.astype(np.uint8) * 255).filter(ImageFilter.MinFilter(k)).filter(ImageFilter.MaxFilter(k))) > 127
        thin = (silk & ~opened).sum() / max(1, silk.sum())
        print(f"Sérigraphie {side} : {int(on_pads.sum())} px sur pastilles, {thin:.0%} des pixels en traits < 0,15 mm (approx.)")
        if on_pads.any():
            ys, xs = np.nonzero(on_pads)
            print(f"  zone : x {xs.min() * PX + x0:.1f}–{xs.max() * PX + x0:.1f}, y {y1 - ys.max() * PX:.1f}–{y1 - ys.min() * PX:.1f} mm")
            blocking.append(f"sérigraphie sur pastille ({side})")

    if blocking:
        print("VERDICT : BLOQUANT —", "; ".join(sorted(set(blocking))))
        return 1
    if to_fix:  # fabricable, mais risque de pont de soudure au montage manuel
        print("VERDICT : À CORRIGER —", "; ".join(to_fix))
        return 2
    print("VERDICT : OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())

# PCBWay: rules, files and order

## Standard capabilities (2 layers, FR-4) and chosen targets

| Parameter | PCBWay minimum | Recommended target | Why |
|---|---|---|---|
| Copper clearance | 0.15 mm | **0.3 mm** | margin against solder bridges when soldering by hand |
| Track width | 0.15 mm | 0.3 mm signals, 1.0 mm power | current and robustness |
| Drill | 0.3 mm | 0.8 mm and more for components | 0.3 mm vias are accepted, but at the limit |
| Annular ring | 0.15 mm | 0.2 mm and more | |
| Pad for a 0.8 mm drill | | 1.6 mm | otherwise it tears off during desoldering |
| Copper to edge | 0.3 mm | 0.4 mm | |
| Silkscreen stroke | 0.15 mm | 0.18 mm and more | |
| Text height | ~1 mm | 1.2 mm for labels | |
| Board | | ≤ 100 × 100 mm | lowest price |

## Rules block to embed in the `.brd` (before routing)

Place this block in `<board>`, after `<classes>`. Fusion applies it to the DRC and to
the autorouter. Since the API cannot read back the loaded rules, check the
result with `check_gerbers.py`.

```xml
<designrules name="pcbway">
  <param name="layerSetup" value="(1*16)"/>
  <param name="mdWireWire" value="0.3mm"/><param name="mdWirePad" value="0.3mm"/>
  <param name="mdWireVia" value="0.3mm"/><param name="mdPadPad" value="0.3mm"/>
  <param name="mdPadVia" value="0.3mm"/><param name="mdViaVia" value="0.3mm"/>
  <param name="mdSmdPad" value="0.3mm"/><param name="mdSmdVia" value="0.3mm"/><param name="mdSmdSmd" value="0.3mm"/>
  <param name="mdCopperDimension" value="0.4mm"/><param name="mdDrill" value="0.5mm"/>
  <param name="msWidth" value="0.15mm"/><param name="msDrill" value="0.3mm"/>
  <param name="rvPadTop" value="0.25"/><param name="rvPadInner" value="0.25"/><param name="rvPadBottom" value="0.25"/>
  <param name="rvViaOuter" value="0.25"/><param name="rvViaInner" value="0.25"/>
  <param name="rlMinPadTop" value="0.2mm"/><param name="rlMaxPadTop" value="0.5mm"/>
  <param name="rlMinPadInner" value="0.2mm"/><param name="rlMaxPadInner" value="0.5mm"/>
  <param name="rlMinPadBottom" value="0.2mm"/><param name="rlMaxPadBottom" value="0.5mm"/>
  <param name="rlMinViaOuter" value="0.2mm"/><param name="rlMaxViaOuter" value="0.5mm"/>
  <param name="rlMinViaInner" value="0.2mm"/><param name="rlMaxViaInner" value="0.5mm"/>
  <param name="mlMinStopFrame" value="0.05mm"/><param name="mlMaxStopFrame" value="0.1mm"/>
</designrules>
```

The net classes carry the widths:

```xml
<classes>
  <class number="0" name="signal" width="0.3" drill="0"/>
  <class number="1" name="power" width="1.0" drill="0"/>
</classes>
```

Each `<signal>` and each `<net>` then carries `class="0"` or `class="1"`.

## Silkscreen

- EAGLE text: add the attribute `ratio="18"`, because the default stroke, at 8%, is
  too thin. Height of at least 1 mm, 1.2 mm for labels.
- Part names go on layer 21 (tPlace). Avoid also leaving
  `>NAME` and `>VALUE` there on layers 25 and 27: depending on the export template, they
  come out twice.
- No text or stroke may touch a pad. Keep a distance of pad
  radius + 0.3 mm. An automatic pad has a radius of about drill/2 + 0.4 mm.
- Marks to plan: polarities, pin 1, pin names of the connectors, insertion
  direction of the modules and wire entry side of the terminal blocks.
- Back side: layer 22 (bPlace), mirrored.

## Files to send

Send the zip produced by Fusion. It contains `copper_top/bottom`, `profile`,
`soldermask_*`, `silkscreen_*`, `solderpaste_*`, `gerber_job.gbrjob` and
`DrillFiles/drill_1_16.xln`. The `gerber_job` file already gives the size and the
number of layers.

The mounting holes are in the same drill file as the pads, so they
are plated. If PCBWay asks "NPTH?", answer "non-plated", or "it does not
matter" for an M3 screw.

## Order settings (to give to the user, who places the order themselves)

- 2 layers, FR-4, thickness 1.6 mm
- 1 oz copper, HASL finish with lead or lead-free
- solder mask: the colour of the user's choice, white silkscreen
- quantity: 5, the minimum
- dimensions: those of the outline, to check in the PCBWay summary

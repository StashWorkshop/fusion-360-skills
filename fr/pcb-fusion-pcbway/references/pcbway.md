# PCBWay : règles, fichiers et commande

## Capacités standard (2 couches, FR-4) et cibles retenues

| Paramètre | Minimum PCBWay | Cible conseillée | Pourquoi |
|---|---|---|---|
| Isolement cuivre | 0,15 mm | **0,3 mm** | marge contre les ponts de soudure à la main |
| Largeur de piste | 0,15 mm | 0,3 mm signaux, 1,0 mm puissance | courant et robustesse |
| Perçage | 0,3 mm | 0,8 mm et plus pour les composants | les vias à 0,3 mm sont acceptés, mais à la limite |
| Bague de cuivre | 0,15 mm | 0,2 mm et plus | |
| Pastille pour un perçage de 0,8 mm | | 1,6 mm | sinon elle arrache au dessoudage |
| Cuivre au bord | 0,3 mm | 0,4 mm | |
| Trait de sérigraphie | 0,15 mm | 0,18 mm et plus | |
| Hauteur de texte | ~1 mm | 1,2 mm pour les libellés | |
| Carte | | ≤ 100 × 100 mm | tarif le plus bas |

## Bloc de règles à intégrer dans le `.brd` (avant routage)

Place ce bloc dans `<board>`, après `<classes>`. Fusion l'applique au DRC et à
l'autorouteur. Comme l'API ne permet pas de relire les règles chargées, vérifie le
résultat avec `check_gerbers.py`.

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

Les classes de signaux portent les largeurs :

```xml
<classes>
  <class number="0" name="signal" width="0.3" drill="0"/>
  <class number="1" name="power" width="1.0" drill="0"/>
</classes>
```

Chaque `<signal>` et chaque `<net>` porte ensuite `class="0"` ou `class="1"`.

## Sérigraphie

- Texte EAGLE : ajoute l'attribut `ratio="18"`, car le trait par défaut, à 8 %, est
  trop fin. Hauteur d'au moins 1 mm, 1,2 mm pour les libellés.
- Les noms des pièces se placent sur la couche 21 (tPlace). Évite d'y laisser aussi
  `>NAME` et `>VALUE` sur les couches 25 et 27 : selon le gabarit d'export, ils
  sortent en double.
- Aucun texte ni trait ne doit toucher une pastille. Garde une distance de rayon de
  pastille + 0,3 mm. Une pastille automatique fait environ perçage/2 + 0,4 mm de rayon.
- Marques à prévoir : polarités, broche 1, nom des broches des connecteurs, sens
  d'insertion des modules et côté d'entrée des fils des borniers.
- Face arrière : couche 22 (bPlace), en miroir.

## Fichiers à envoyer

Envoie le zip produit par Fusion. Il contient `copper_top/bottom`, `profile`,
`soldermask_*`, `silkscreen_*`, `solderpaste_*`, `gerber_job.gbrjob` et
`DrillFiles/drill_1_16.xln`. Le fichier `gerber_job` indique déjà la taille et le
nombre de couches.

Les trous de fixation sont dans le même fichier de perçage que les pastilles, donc ils
sont métallisés. Si PCBWay demande « NPTH ? », réponds « non métallisés », ou « peu
importe » pour une vis M3.

## Réglages de commande (à donner à l'utilisateur, qui commande lui-même)

- 2 couches, FR-4, épaisseur 1,6 mm
- cuivre 1 oz, finition HASL avec plomb ou sans plomb
- vernis : la couleur au choix de l'utilisateur, sérigraphie blanche
- quantité : 5, le minimum
- dimensions : celles du contour, à vérifier dans le récapitulatif de PCBWay

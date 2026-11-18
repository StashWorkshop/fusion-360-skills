---
name: pcb-fusion-pcbway
description: Concevoir, vérifier et préparer à la commande un circuit imprimé dans Fusion 360 (Electronics) pour PCBWay, en pilotant Fusion par le MCP local `fusion` (outils `mcp__fusion__*`). Utilise ce skill dès que l'utilisateur parle de PCB, de carte électronique, de schéma ou de routage dans Fusion (ou « Fusion 360 », « EAGLE »), de Gerber, de fichiers de fabrication, de DRC/ERC, ou de commander une carte chez PCBWay (ou JLCPCB, même logique), même s'il ne cite pas PCBWay ni le skill. Il évite les erreurs coûteuses (isolement, polarité, export d'une version non routée) et rend les vérifications rapides.
---

# PCB dans Fusion 360 pour PCBWay

Une carte commandée avec un défaut coûte une semaine et un envoi. Ce skill rassemble
les règles qui évitent ces défauts, l'usage efficace du MCP Fusion, et un contrôle
automatique des fichiers réellement envoyés au fabricant.

**Principe :** les contrôles de Fusion (ERC, DRC) ne suffisent pas, car ils portent sur le
document, pas sur ce que PCBWay reçoit. Rien ne part sans le verdict de
`scripts/check_gerbers.py` sur les Gerber exportés.

## Références à lire au bon moment

- `references/fusion-mcp.md` : recettes MCP (import, routage, DRC, extraction de la
  netlist, enregistrement, export) et pièges de Fusion. **À lire avant le premier appel
  `mcp__fusion__*`**, cela évite des allers-retours coûteux.
- `references/pcbway.md` : capacités PCBWay, bloc de règles de conception à intégrer
  à la carte, sérigraphie, perçages, réglages de commande. À lire avant de fixer les
  règles ou de préparer la commande.

## Déroulé

1. **Netlist validée d'abord.** Une carte se dessine à partir d'un brochage testé (sur
   breadboard si possible). Lis la sérigraphie réelle des modules reçus : l'ordre des
   broches d'un module ou d'un écran varie d'un vendeur à l'autre. Recoupe chaque
   brochage de module avec une source officielle (fichier de carte du fabricant) plutôt
   qu'un dessin de vendeur.
2. **Règles avant routage.** Intègre les règles PCBWay à la carte (bloc
   `<designrules>`, voir `references/pcbway.md`) avant de lancer l'autorouteur :
   l'autorouteur et le DRC les appliquent tous les deux. Isolement visé : **0,3 mm**,
   pas le minimum de 0,15 mm. Ce minimum se fabrique, mais il se ponte à la soudure
   manuelle.
3. **Placement pensé pour le montage.** Connecteurs au bord, orientés vers l'extérieur,
   avec le côté d'entrée des fils marqué en sérigraphie. Puissance d'un côté, signaux
   de l'autre. Condensateur de découplage collé à sa broche. Connecteur moteur dans
   l'ordre des sorties du driver, pour des pistes sans croisement. Vérifie l'encombrement
   réel des modèles 3D : une empreinte peut être plus petite que son composant.
4. **Routage et contrôles Fusion.** Import lié du schéma et de la carte, autorouteur,
   puis ERC (« le circuit imprimé et le schéma sont cohérents », 0 erreur) et DRC
   (0 erreur, aucune liaison non routée). Vérifie la largeur des pistes de puissance.
5. **Enregistrer, puis exporter.** Fusion n'exporte que la **dernière version
   enregistrée**. Enregistrer dans le cloud Fusion est une action visible pour
   l'utilisateur : demande son accord et propose un nom. Ensuite seulement, exporte
   Gerber et perçages.
6. **Contrôle des fichiers exportés.** Extrais la netlist des pastilles depuis Fusion,
   puis lance :
   ```
   python scripts/check_gerbers.py <dossier GerberFiles> <fichier .xln> --pads <pads.json> --clearance 0.3
   ```
   Lis le verdict :
   - **0, OK :** la carte est commandable.
   - **2, À CORRIGER :** isolement sous la cible. Corrige, re-route, puis recommence à
     l'étape 4.
   - **1, BLOQUANT :** court-circuit, liaison ouverte, isolement sous 0,15 mm ou
     sérigraphie sur une pastille. Ne commande pas.

   Le script ne voit pas les erreurs de brochage, seulement l'écart entre les fichiers
   et la netlist de Fusion. Le brochage reste à valider à l'étape 1. Il demande Pillow
   et numpy (`pip install pillow numpy`) ; s'ils sont installés dans le site utilisateur,
   lance Python sans `-I`.
7. **Relecture indépendante** pour toute première révision : confie à un agent neuf la
   spec, la netlist et les Gerber, avec les points de l'étape 6 et les polarités. Une
   relecture fraîche a trouvé, sur la carte d'origine, un brochage inversé que les
   tests de l'auteur reproduisaient.
8. **Test papier** avant de souder : imprime à 100 % un gabarit des perçages et pique
   les modules dedans pour vérifier les écartements.

## Règles qui ont déjà coûté cher

- **Ne coche jamais « Oui » à la question de Fusion sur la dernière version enregistrée**
  si la carte routée n'a pas été enregistrée : l'export partirait sans pistes.
- **Écartement entre rangées d'un module :** une mesure au pied à coulisse entre bords
  intérieurs se corrige de l'épaisseur d'une broche (0,64 mm), puis s'arrondit au pas
  de 2,54 mm.
- **Polarités en sérigraphie :** « + » du condensateur côté + ; bande de cathode de la
  diode ; pastille carrée en broche 1 ; noms des broches de chaque connecteur ; sens
  d'insertion des modules (USB, EN). Un test doit le vérifier, pas l'œil.
- **Texte de sérigraphie :** EAGLE trace par défaut à 8 % de la hauteur, soit un trait
  trop fin. Mets le ratio à 18 % ou plus, avec une hauteur d'au moins 1 mm (1,2 mm
  pour les libellés).
- **Pastilles traversantes :** au moins 1,6 mm pour un perçage de 0,8 mm, sinon elles
  arrachent au dessoudage.
- **Un logo en image** se trace en rectangles de 0,1 mm de haut, sans traits de moins de
  0,15 mm, sur une zone sans pastille. Sur la face arrière, il se trace en miroir.
- **Le routage n'existe que dans Fusion et dans l'archive exportée.** Conserve le zip
  daté avec le projet.

## Compte rendu à l'utilisateur

Termine par :
- un verdict clair, commandable ou non ;
- les preuves : ERC, DRC, sortie de `check_gerbers.py`, et taille et couches de la carte ;
- les réglages de commande ;
- ce qui n'a pas été vérifié, en général le brochage réel des modules.

La commande, c'est l'utilisateur qui la passe, jamais l'agent.

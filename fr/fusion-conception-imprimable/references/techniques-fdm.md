# Techniques de conception pour l'impression FDM

Catalogue des règles à appliquer pendant la modélisation. Valeurs de départ pour une buse de 0,4 mm, des couches de 0,2 mm et du PLA ; le PETG demande en général un peu plus de jeu. Les jeux dépendent de l'imprimante : quand un ajustement compte, prévois une pièce d'essai (peigne de jeux) ou mets la valeur en paramètre.

## Sommaire
1. Orientation et résistance
2. Surplombs et chanfreins
3. Trous horizontaux
4. Ponts et couches sacrificielles
5. Trous verticaux et précision
6. Première couche (pied d'éléphant)
7. Parois, nervures, angles
8. Jeux et ajustements
9. Quincaillerie : inserts, écrous, vis
10. Print-in-place (charnières, pivots)
11. Clips et pièces souples
12. Textes et marquages
13. Filetages imprimés
14. Supports quand on ne peut pas les éviter
15. Grandes pièces et assemblages

## 1. Orientation et résistance
- Une pièce FDM est anisotrope : la liaison entre couches résiste 2 à 4 fois moins bien que le filament dans le plan. Les efforts de traction et de flexion doivent courir dans le plan des couches.
- Choisis l'orientation avant de dessiner, puis dessine chaque détail pour cette orientation (« le haut » de l'impression n'est pas forcément le haut du modèle).
- Une grande face plane sur le plateau = bonne adhérence et pas de support.
- Les cylindres précis (axes, alésages) s'impriment mieux axe vertical : cercle propre dans chaque couche.

## 2. Surplombs et chanfreins
- Règle des 45° : une face qui penche de plus de 45° par rapport à la verticale s'imprime mal sans support. Entre 45° et 60°, ça passe souvent en PLA avec un bon refroidissement, mais l'état de surface se dégrade.
- Sous un surplomb, mets un **chanfrein à 45°**, pas un congé : le bas d'un congé est horizontal et s'effondre.
- Congés : sur les arêtes verticales et dans le plan des couches (ils renforcent et ne posent pas de problème). Chanfreins : sur les arêtes en bas de pièce et sous les avancées.
- Une avancée (bord, lèvre, crochet) peut presque toujours devenir un gousset ou un chanfrein à 45° dessous.

## 3. Trous horizontaux (axe parallèle au plateau)
- **Goutte** : ajoute au-dessus du cercle un triangle dont les côtés sont tangents au cercle et forment 90° entre eux ; la pointe est à r·√2 du centre. Pointe vers le haut de l'impression. Pour une cote précise en haut du trou, tronque la pointe par un méplat (0,3–0,5 × r au-dessus du cercle) : petit pont, mais le trou garde son diamètre fonctionnel.
- **Losange** : pour les gros passages non fonctionnels, un carré tourné de 45°.
- Grandes ouvertures (fenêtres, poches) : toit en pointe à 45°, hexagone ou octogone à méplat court.
- Un petit trou horizontal (≤ 5–6 mm) passe souvent sans goutte, mais ressort ovalisé en haut : la goutte le garde rond sur sa partie basse.

## 4. Ponts et couches sacrificielles
- Un pont (plafond horizontal tenu aux deux bouts) passe bien jusqu'à 10–15 mm en PLA, parfois 20–30 mm avec un bon refroidissement, mais la face du dessous reste moins propre. Au-delà, mets un toit à 45° ou coupe le pont par un appui.
- **Lamage tourné vers le plateau** (tête de vis sous la pièce) : le trou de passage débouche au milieu du plafond du lamage, sans rien sur quoi s'appuyer. Solution des « ponts successifs » : au fond du lamage, une première couche (0,2 mm) en pont qui réduit l'ouverture à une fente de la largeur du trou, puis une deuxième couche en pont perpendiculaire qui la réduit au carré du trou. Le trou rond reprend au-dessus.
- **Membrane sacrificielle** : un trou qui doit déboucher au-dessus d'un vide peut être fermé par une couche de 0,2 mm, percée ensuite à la main. Utile aussi pour imprimer un trou de vis par-dessus un logement d'écrou.

## 5. Trous verticaux et précision
- Les trous sortent plus petits que dessinés (0,1 à 0,3 mm au diamètre selon la taille et le profil) et les cylindres extérieurs un peu plus gros.
- Pour un ajustement précis : mets le diamètre en paramètre, imprime un essai, ou alèse au foret ensuite.
- Les petits trous très précis peuvent être dessinés en polygone (polyhole) : un hexagone ou octogone circonscrit compense la sous-cote des cercles.

## 6. Première couche (pied d'éléphant)
- La première couche écrasée déborde de 0,2 à 0,5 mm. Mets un chanfrein de 0,4 à 0,6 mm (45°) sur toutes les arêtes en contact avec le plateau quand une cote ou un assemblage compte.
- En print-in-place, c'est la première cause de pièces soudées au niveau du plateau : chanfreine aussi le bas des pièces mobiles.

## 7. Parois, nervures, angles
- Épaisseurs en multiples de la largeur de ligne (≈ 0,45 mm) : 0,9 / 1,2 / 1,6 / 2 mm. Minimum 1,2 mm pour une paroi qui travaille.
- La résistance vient surtout des parois (périmètres) : pour une pièce mécanique, 4 parois et 30–40 % de remplissage valent mieux que 100 % de remplissage avec 2 parois.
- Nervures plutôt que masse pleine ; épaisseur de nervure ≈ 0,6 à 1 × la paroi qui la porte.
- Angles intérieurs : congé (rayon ≥ épaisseur/2) dans le plan des couches pour éviter la concentration de contraintes.
- Évite les pièces fines et hautes isolées (> 8–10 × leur épaisseur) : elles vibrent à l'impression ; ajoute un raidisseur ou change l'orientation.

## 8. Jeux et ajustements (points de départ, à calibrer)
| Usage | Jeu (par côté) |
|---|---|
| Serré / emmanché | 0,10–0,15 mm |
| Juste, sans jeu | 0,20 mm |
| Glissant | 0,25–0,30 mm |
| Libre | 0,40 mm |
| Print-in-place (mobile imprimé assemblé) | 0,30–0,50 mm en XY, au moins 2 couches (0,4 mm) en Z |

- Le jeu entre surfaces verticales (en XY) est plus fiable qu'entre surfaces horizontales (en Z) : prévois plus de jeu en Z.
- Un jeu perpendiculaire à un flanc incliné d'angle a s'obtient avec un décalage horizontal de jeu / cos(a).

## 9. Quincaillerie : inserts, écrous, vis
- **Inserts laiton à chaud** : trou au diamètre du fabricant (paramètre), profondeur = longueur + 0,5 à 1 mm (la matière fondue a besoin de place), chanfrein d'entrée de 0,5 à 0,8 mm pour centrer l'insert, au moins 1,5–2 mm de matière autour. Pose fer à 220–230 °C (PLA), insert bien perpendiculaire.
- **Écrous prisonniers** : logement hexagonal avec 0,2–0,3 mm de jeu sur plats ; si le logement est horizontal, pense à la membrane sacrificielle ou au toit à 45°. Un logement en fente latérale (écrou glissé de côté) évite les ponts.
- **Vis directement dans le plastique** : avant-trou ≈ 0,8–0,85 × le diamètre nominal pour les vis autotaraudeuses, bonne profondeur et paroi épaisse autour.
- Passages de vis : M3 → 3,4 ; M4 → 4,5 ; M5 → 5,5 ; M6 → 6,5 mm.
- Têtes fraisées : une fraisure (cône à 90°) s'imprime sans support dans les deux sens ; tournée vers le plateau, son plafond est un surplomb à 45°, à la limite mais correct. Un lamage (fond plat) tourné vers le plateau demande des ponts successifs.

## 10. Print-in-place (charnières, pivots)
- Axe de charnière horizontal : axe et alésage à profil en goutte ou en losange pour que rien ne pende ; jeu 0,3–0,5 mm.
- Butées coniques à 45° plutôt que faces planes face à face : un cône s'imprime sans support et se sépare facilement.
- Aucune surface mobile ne doit reposer à plat sur une autre pendant l'impression : laisse au moins 0,3–0,4 mm (2 couches) entre elles en Z.
- Chanfrein en bas des pièces mobiles (pied d'éléphant).
- Prévois un moyen de « décoller » la pièce après impression (tourner, tirer) : le premier mouvement casse les petits ponts.

## 11. Clips et pièces souples
- La partie qui fléchit doit fléchir dans le plan des couches (sinon elle casse entre deux couches).
- Bras de clip long et effilé ; déformation admissible faible en PLA (~1–2 %) : préférer le PETG pour les clips qui servent souvent.
- Congé à la base du bras.

## 12. Textes et marquages
- Relief ou creux ≥ 0,6 mm (3 couches), trait ≥ 0,8 mm (2 lignes), police sans empattement et assez grasse.
- Le texte s'imprime mieux sur une face horizontale du dessus ou une face verticale ; en creux sur une face verticale, il donne de petits ponts.

## 13. Filetages imprimés
- Filetages modélisés : fiables à partir d'environ M8–M10, axe vertical, avec un peu de jeu radial (0,2–0,3 mm). Profils à 45° (ISO 60°, trapézoïdal) imprimables sans support.
- En dessous : insert laiton, écrou prisonnier ou taraudage dans un avant-trou.

## 14. Supports quand on ne peut pas les éviter
- Les limiter à une petite zone accessible, posée sur le plateau (pas sur la pièce).
- Supports intégrés au modèle : nervures fines séparées de la pièce par un jeu de 0,2 mm (une couche), faciles à casser.
- Le dire à l'utilisateur, avec l'endroit et le réglage (« supports sur plateau uniquement », bloqueur, renforçateur).

## 15. Grandes pièces et assemblages
- Si une pièce dépasse le plateau ou cumule les surplombs, la couper en éléments imprimables à plat et prévoir l'assemblage : queues d'aronde, goupilles (trou + tige avec jeu), vis + inserts.
- Plan de coupe loin des zones très sollicitées, ou recouvrement pour reprendre l'effort.

## Sources consultées
- Hubs, « How to design parts for FDM 3D printing » (chanfreins sur les arêtes au plateau).
- FacFox, « FDM 3D Printing Design Tips » (pied d'éléphant).
- Sovol, « Print-in-Place 3D Printing » (jeux, pied d'éléphant en print-in-place).
- Wevolver, « FDM 3D printing design tips » ; EduHK (longueurs de pont).
- Chief Delphi, « Prepare to Print FeatureScript » (gouttes, lamages à ponts).
- Skills communautaires : andreahaku/openscad_claude_skill (parois 1,2 mm, jeux press 0,15 / close 0,25 / slide 0,30 / loose 0,40, surplombs < 45°), flowful-ai/cad-skill (relecture de conception).

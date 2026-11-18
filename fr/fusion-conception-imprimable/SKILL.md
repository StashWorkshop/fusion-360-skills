---
name: fusion-conception-imprimable
description: Concevoir des pièces dans Fusion 360 par le MCP local `fusion` (outils `mcp__fusion__*`) en pensant dès le départ à l'impression 3D FDM — pièces imprimables, print-in-place si possible, avec le moins de supports possible. Utilise ce skill dès que l'utilisateur demande de modéliser, modifier ou exporter une pièce dans Fusion 360 (ou « Fusion », « conclusion 360 » en dictée), même s'il ne parle pas d'impression : le skill part du principe que ses pièces Fusion sont destinées à être imprimées.
---

# Conception Fusion 360 pour l'impression FDM

Ce skill suppose que l'utilisateur imprime ses pièces en FDM (PLA le plus souvent). Une pièce n'est réussie que si elle sort de l'imprimante sans support, ou presque, et sans reprise. Pense donc à l'orientation d'impression **avant** de dessiner, et revois chaque trou, chaque surplomb et chaque logement de quincaillerie avec cette orientation en tête.

> Brouillon : ce skill commence par des règles notées au fil des projets. Ajoute ici chaque nouvelle règle que l'utilisateur donne.

## 1. Choisir l'orientation d'abord

- Les couches résistent mal en traction entre elles : oriente la pièce pour que les efforts principaux (levier, flexion) restent dans le plan des couches.
- Cherche l'orientation qui donne le plus de faces planes sur le plateau et le moins de surplombs.
- Note l'orientation choisie (quelle face sur le plateau, quel sens est « vers le haut ») : toutes les règles ci-dessous en dépendent.

## 2. Supprimer les supports

- **Surplombs** : au-delà de 45° par rapport à la verticale, remplace par un chanfrein à 45° plutôt qu'un congé ou une face plate.
- **Trous horizontaux (axe parallèle au plateau) : profil en goutte.** Ajoute au-dessus du cercle un triangle dont les deux côtés sont tangents au cercle et forment 90° entre eux (45° de chaque côté de la verticale). La pointe se trouve un peu au-dessus du cercle (à r·√2 du centre). Extrude ce profil de toute la profondeur du trou. Le trou s'imprime ainsi sans support. Oriente la pointe vers le haut **de l'impression**, pas vers le haut du modèle.
- **Grandes ouvertures horizontales** (évidements, fenêtres, poches) : même idée, toit en pointe à 45° (hexagone, octogone avec méplat court de moins de 10–15 mm, losange).
- **Ponts** : un plafond horizontal court (≲ 10–15 mm) passe ; au-delà, mets un toit à 45°.
- **Lamage tourné vers le plateau** : ponts successifs (une couche en fente, puis une couche perpendiculaire en carré) au fond du lamage, ou membrane sacrificielle de 0,2 mm à percer.
- **Pied d'éléphant** : chanfrein de 0,4 à 0,6 mm sur les arêtes posées sur le plateau dès qu'une cote ou un assemblage compte.
- Si un support reste inévitable (ex. queue d'aronde à épaulement), limite-le à une petite zone posée sur le plateau et dis-le à l'utilisateur.

Le catalogue complet (parois, jeux, écrous, clips, textes, filetages, assemblages) est dans `references/techniques-fdm.md` : lis-le avant de dessiner une pièce mécanique, et relis la section concernée dès qu'un détail l'appelle.

## 3. Print-in-place

- Quand des pièces doivent bouger ensemble (charnière, pivot, glissière), essaie d'abord de les imprimer assemblées.
- Garde un jeu entre pièces mobiles (0,3 à 0,5 mm en XY, au moins deux couches en Z, en paramètre) et évite que les surfaces en vis-à-vis soient horizontales l'une sur l'autre (elles se soudent) : décale-les ou remplace-les par des cônes à 45°.
- Axes de charnière horizontaux en goutte ou en losange ; chanfrein en bas des pièces mobiles.
- Jeux d'ajustement de départ : serré 0,15, juste 0,2, glissant 0,3, libre 0,4 mm ; à calibrer sur l'imprimante quand l'ajustement compte.

## 4. Quincaillerie

- **Inserts laiton thermo-posés** : trou au diamètre conseillé par le fabricant (paramètre), profondeur = longueur de l'insert + 0,5 mm, et **un petit chanfrein d'entrée** (0,5 à 0,8 mm, moins d'1 mm) pour centrer l'insert avant de le chauffer. Le trou d'insert suit aussi la règle de la goutte s'il est horizontal.
- Trous de passage : jeu standard (M3 → 3,4 ; M4 → 4,5 ; M5 → 5,5).
- Écrous prisonniers : hexagone avec 0,2–0,3 mm de jeu sur plats, de préférence en fente latérale pour éviter les ponts.
- Fraisures : vers le haut de l'impression, rien à faire ; vers le plateau, le plafond est un cône à 45° qui passe sans support. Lamages vers le plateau : ponts successifs.
- Parois en multiples de la largeur de ligne (≈ 0,45 mm), 1,2 mm minimum ; la résistance vient des parois plus que du remplissage.
- Liste toujours la quincaillerie à prévoir (inserts, vis, longueurs).

## 5. Modélisation paramétrique

- Toutes les cotes réglables vont dans les **Paramètres utilisateur**, avec un nom court et un commentaire (rôle). Distingue les paramètres de saisie des paramètres calculés.
- Esquisses entièrement contraintes ; cotes pilotées par les paramètres (`dim.parameter.expression = 'nom'`).
- Après construction, change quelques paramètres pour vérifier que la chronologie se recalcule sans erreur, puis remets les valeurs.

## 6. Pièges de l'API Fusion (par le MCP)

- Le script tourne dans une seule transaction : une exception annule tout le script. Découpe en plusieurs appels et vérifie volume / boîte englobante après chaque étape.
- `importToTarget` d'un STEP peut échouer dans un document vierge : utilise `importToNewDocument`, puis copie les corps avec `TemporaryBRepManager.copy` dans une `baseFeature`.
- Dépouille d'extrusion (`taperAngle`) : le signe dépend du sens ; contrôle la boîte englobante juste après.
- `addTwoPointRectangle` ne pose pas toujours les contraintes horizontale/verticale : ajoute-les à la main.
- `addScribedPolygon` crée un point centre libre : ajoute une coïncidence avec l'origine et une contrainte horizontale sur un côté.
- Un chanfrein de grande taille sur une arête concave échoue souvent : dessine plutôt la forme voulue dans l'esquisse.
- Les cotes de distance sont toujours positives : place la géométrie du bon côté avant de coter, et écris les expressions pour qu'elles restent positives.

## 7. Vérifier et livrer

- Contrôle d'interférence et de jeu avec les pièces de référence (booléens temporaires, `measureMinimumDistance`).
- Masse estimée (PLA 1,24 g/cm³) en plein et avec remplissage réaliste.
- Une seule capture à la fois, à demi-résolution.
- Enregistre dans Fusion ; exporte STEP + 3MF dans le dossier que l'utilisateur valide.
- **Exporte chaque pièce déjà dans son orientation d'impression** : face posée sur le plateau à z = 0, pièce centrée sur l'origine en x et y, haut d'impression vers +z. À l'import dans le trancheur, la pièce est directement à plat et sans support, sans rien tourner. Le modèle Fusion reste dans le repère d'assemblage : copie le corps (`TemporaryBRepManager.copy`), applique la rotation et la translation, exporte cette copie (composant temporaire visible), puis supprime-la. Vérifie en réimportant : volume identique, `minPoint.z = 0`, face plateau en bas. Pièces de test : même orientation que leur pièce d'origine.
- Après chaque export, vérifie que le fichier contient un solide (STEP : `MANIFOLD_SOLID_BREP`) : Fusion n'exporte pas la géométrie masquée et écrit alors un fichier vide, sans erreur.
- Donne : paramètres et rôle, orientation d'impression, réglages (parois, remplissage), supports éventuels, quincaillerie.

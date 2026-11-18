# Fusion Electronics par le MCP : recettes et pièges

Toutes les recettes passent par `mcp__fusion__fusion_mcp_execute` avec `featureType: "script"`,
un script Python qui définit `run(_context)`. Les commandes électroniques passent par
`app.executeTextCommand(...)`.

## Le piège n°1 : la commande « Sélectionner » bloque les scripts

Dans un document électronique, Fusion laisse presque toujours la commande « Sélectionner »
(`Electron::Group`) ouverte. Un script qui modifie le document échoue alors avec
« Cannot perform 'script' while a command dialog is open ».

- **Lecture seule :** passe `readOnly: true`. Ça marche même avec la commande ouverte,
  mais sans `executeTextCommand`.
- **Écriture :** ramène Fusion au premier plan, puis envoie Échap deux fois par le
  contrôle du bureau (accès à demander pour `fusion360.exe`). Sous Windows :
  ```powershell
  Add-Type -Name W -Namespace U -MemberDefinition '[DllImport("user32.dll")] public static extern bool ShowWindow(System.IntPtr h,int c); [DllImport("user32.dll")] public static extern bool SetForegroundWindow(System.IntPtr h);'
  $p = Get-Process Fusion360 | ? { $_.MainWindowHandle -ne 0 } | select -First 1
  [U.W]::ShowWindow($p.MainWindowHandle,6); sleep -m 400; [U.W]::ShowWindow($p.MainWindowHandle,3); [U.W]::SetForegroundWindow($p.MainWindowHandle)
  ```
  Clique ensuite dans la ligne de commande de Fusion, puis envoie `escape` deux fois.
  Si Fusion a été mis à jour, le chemin de l'exécutable change : redemande l'accès.
- **Regroupement :** enchaîne plusieurs commandes dans un même script, une seule fois
  après Échap.

## Importer un schéma et une carte liés

```python
app.executeTextCommand('Electron.importSchAndBrd "C:\\...\\carte.sch" "C:\\...\\carte.brd"')
```

Cette commande crée un projet électronique avec ses trois onglets : projet, schéma et
carte. Le schéma et la carte y sont **liés**, et l'ERC le confirme. Ouvrir le `.sch` et
le `.brd` séparément donne deux documents non liés. Chaque import ajoute des onglets
« Sans nom » : signale à l'utilisateur ceux à fermer.

## Router et contrôler en un appel

```python
app.executeTextCommand('Electron.run "RATSNEST; AUTO ! GND ; RATSNEST; DRC ;"')
```

- `AUTO ! GND` route tout sauf la masse, que le polygone de la face inférieure prend en
  charge.
- L'appel dépasse souvent le délai du MCP (« timed out »), mais il continue dans Fusion.
  Attends environ 20 s, puis vérifie le résultat.
- Les largeurs de piste viennent des classes de signaux. L'isolement vient du bloc
  `<designrules>` de la carte.

## Lire les erreurs sans capture d'écran

- **Erreurs DRC :** `fusion_mcp_electronics_read` avec `entity_type: "electronics.Error"`
  et `fields: ["description"]`. Une liste vide signifie aucune erreur. Les
  avertissements « Angle aigu » viennent de l'autorouteur et sont sans effet en
  fabrication industrielle.
- **Largeurs de piste :** `electronics.Wire`, champs `signal_object_id`, `width`, `layer`,
  croisés avec `electronics.Signal`. Les unités sont en pouces : 0,03937 = 1,0 mm.
- **ERC :** active le document schéma, puis exécute `Electron.run "ERC ;"`. L'API n'expose
  pas le bilan : fais un zoom d'écran sur le panneau Erreurs, qui doit indiquer
  « le circuit imprimé et le schéma sont cohérents ».
- **Changer de document :** `app.documents.item(i).activate()`. Le type se lit avec
  `d.products.item(0).productType` : `EcadDesignProductType`, `SchematicProductType`,
  `BoardProductType`.

## Extraire la netlist des pastilles sans la faire transiter par la conversation

Une réponse brute de `electronics.Pad` pèse plusieurs milliers de jetons. Fais-la plutôt
écrire directement dans un fichier par Fusion. Le JSON doit être **entre guillemets, avec
les guillemets intérieurs échappés** :

```python
import adsk.core, json, os
def run(_context: str):
    app = adsk.core.Application.get()
    q = {'entity_type': 'electronics.Pad', 'object': {'fields': ['x', 'y', 'signal'], 'pagination': {'limit': 1000}}}
    arg = json.dumps(q, separators=(',', ':')).replace('"', '\\"')
    out = os.path.join(os.environ['TEMP'], 'pads.json')
    open(out, 'w', encoding='utf-8').write(app.executeTextCommand('MCP.ElectronicsRead "' + arg + '"'))
```

Ce script se lance en `readOnly: true`, avec le document carte actif. Le fichier
produit est l'entrée `--pads` de `check_gerbers.py`. Les coordonnées sont en pouces,
et le script les convertit.

## Enregistrer (avec l'accord de l'utilisateur)

```python
ecad = [d for d in docs if d.products.item(0).productType == 'EcadDesignProductType'][-1]
project = next(p for p in (app.data.dataProjects.item(i) for i in range(app.data.dataProjects.count)) if p.name == 'Default Project')
ecad.saveAs('Nom de la carte r1', project.rootFolder, 'description', '')
```

`saveAs` crée un nouveau fichier et n'écrase jamais l'ancien. Pour chaque révision,
ajoute un suffixe (r2, r3…) et indique à l'utilisateur quelle version est périmée.
Évite les accents dans le nom.

## Exporter Gerber et perçages

Il faut d'abord **enregistrer la carte**. Sinon, Fusion propose d'exporter « la
dernière version enregistrée », qui peut être sans pistes : réponds Annuler.

- **Par script** (carte active, après Échap) :
  ```python
  cam = r'<Fusion>\Applications\Electron\LibEagle\examples\cam\examples\example_2_layer.cam'
  app.executeTextCommand(f'Electron.mfgexport "{dossier}" "{cam}"')
  ```
  Les fichiers arrivent dans un chemin inattendu :
  `<parent de dossier>\example_2_layer\example_2_layer.gbr\<hub>\<projet>\CAMOutputs\`.
  Cherche `CAMOutputs` sous le dossier parent. Le dossier `<Fusion>` est celui de
  `(Get-Process Fusion360).Path`.
- **Par l'interface :** ouvre l'onglet FABRICATION, choisis l'icône « Exporter les sorties
  Gerber, de perçage NC… », valide avec OK, puis Enregistrer. Tu obtiens un zip complet,
  à envoyer tel quel.
- Le gabarit `example_2_layer.cam` sort le cuivre, le contour, les masques, la
  sérigraphie des deux faces et le perçage `drill_1_16.xln`. Il ne sépare pas les trous
  métallisés des trous non métallisés.

## Pièges de format

- Les Gerber de Fusion sont au format `FSLAX34Y34`, en mm : **4** décimales implicites.
- Le perçage Excellon est au format `METRIC,TZ,000.000` : **3** décimales implicites.
  En les confondant, les trous se retrouvent à un dixième de leur position.
- Une bibliothèque comme pygerber ne lit pas tous les fichiers Fusion (le contour,
  notamment) et rend un logo en rectangles comme des rayures. Ce sont des artefacts de
  rendu, pas des défauts : `check_gerbers.py` mesure, lui.

## Modèles 3D

L'API ne permet pas d'attacher un modèle 3D à une empreinte, ni de créer le PCB 3D lié
(`NuElectronCommands.ReferenceToPCBCmd` n'est pas disponible depuis un script). Pour le
boîtier, construis un assemblage séparé :
- un circuit extrudé de 1,6 mm ;
- les modèles STEP posés aux positions des pastilles.

Les STEP de KiCad se trouvent dans `KiCad\<version>\share\kicad\3dmodels` : leur
origine est la pastille 1, et z = 0 correspond au dessus du circuit. Les modules
(cartes ESP32, drivers) viennent de GrabCAD. Le téléchargement demande un compte :
c'est l'utilisateur qui le fait.

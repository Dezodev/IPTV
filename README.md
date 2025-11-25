# IPTV M3U Editor

Script Python interactif pour modifier les informations EXTINF de fichiers M3U (groupe, EPG ID, logo).

## Fonctionnalités

- **Édition du groupe**: Historique des groupes utilisés pour réutilisation rapide
- **Détection automatique de l'EPG ID**: Recherche dans la base de données [iptv-org](https://github.com/iptv-org/iptv) avec validation manuelle
- **Gestion des logos**:
  - Recherche automatique via l'API iptv-org
  - Prévisualisation dans le terminal (macOS)
  - Téléchargement local pour hébergement sur GitHub
- **Traitement partiel**: Possibilité de traiter uniquement jusqu'à une ligne spécifique
- **Fichier de sortie séparé**: Le fichier original reste intact

## Prérequis

### Python 3.x
Le script utilise uniquement la bibliothèque standard Python (aucune dépendance externe requise).

### imgcat (optionnel, pour macOS)
Pour afficher les logos directement dans le terminal :

```bash
brew install imgcat
```

Sans imgcat, le script fonctionnera normalement mais affichera uniquement l'URL du logo.

## Installation

1. Clonez ou téléchargez ce repository
2. Le script est prêt à l'emploi (aucune installation de packages nécessaire)

## Utilisation

### Lancement du script

```bash
python3 m3u_editor.py
```

### Workflow interactif

1. **Spécifier le fichier M3U source**
   ```
   Fichier M3U source (ex: lists/input.m3u): lists/mylist.m3u
   ```

2. **Définir le nombre de lignes à traiter**
   ```
   Traiter jusqu'à la ligne numéro: 50
   ```

3. **Pour chaque ligne EXTINF**, vous pouvez modifier :

   #### Groupe
   - Sélectionner un groupe déjà utilisé
   - Entrer un nouveau groupe
   - Sauter (garder l'actuel)

   #### TVG ID
   - Voir les suggestions automatiques depuis iptv-org
   - Saisir manuellement
   - Garder l'actuel

   #### Logo
   - Voir les logos proposés avec prévisualisation
   - Saisir une URL manuellement
   - **Télécharger et héberger** : Ajoutez `h` après votre choix
     - Exemples : `1 h` (option 1 + hébergement) ou `m h` (manuel + hébergement)
   - Garder l'actuel

### Exemple de session

```
============================================================
LIGNE 15: TR: ATV
============================================================

GROUPE ACTUEL: undefinedTR| TÜRKIYE ⁴ᴷ ᵀⱽ

Sélectionnez ou entrez un nouveau groupe:
  1. Turkey 4K
  2. Turkey HD
  n. Nouvelle valeur
  s. Sauter (garder l'actuel)
Choix: 1

TVG-ID ACTUEL: 295768

🔍 3 résultat(s) trouvé(s):
  1. [TR] ATV → ATV.tr
  2. [TR] ATV Avrupa → ATVAvrupa.tr
  3. [TR] ATV Europe → ATVEurope.tr
  m. Saisir manuellement
  s. Sauter (garder l'actuel)
Choix: 1

LOGO ACTUEL: http://icon-tmdb.me/stalker_portal/misc/logos/320/882.jpg

🖼️  Logo(s) trouvé(s):

  1. https://i.imgur.com/xFGDk3k.png
  [Image affichée dans le terminal]

  m. Saisir URL manuellement
  s. Sauter (garder l'actuel)
Choix (ajoutez 'h' pour héberger, ex: '1 h' ou 'm h'): 1 h

📦 Hébergement sur GitHub...
✓ Fichier téléchargé: /Users/deniz/Documents/IPTV/logos/ATV_tr.png
ℹ️  Après push, l'URL sera: https://raw.githubusercontent.com/VOTRE_USER/VOTRE_REPO/main/logos/ATV_tr.png
```

## Structure des fichiers

```
IPTV/
├── m3u_editor.py          # Script principal
├── .gitignore             # Exclut le dossier lists/
├── README.md              # Cette documentation
├── logos/                 # Logos téléchargés (créé automatiquement)
│   ├── channel1.png
│   └── channel2.jpg
└── lists/                 # Vos fichiers M3U (non versionné)
    ├── input.m3u
    └── input_edited.m3u   # Fichier généré
```

## Hébergement des logos sur GitHub

Après avoir téléchargé des logos localement, suivez ces étapes pour les héberger :

### 1. Initialiser le repository Git

```bash
git init
git add m3u_editor.py .gitignore README.md logos/
git commit -m "Initial commit with IPTV tools and logos"
```

### 2. Créer un repository sur GitHub

1. Allez sur https://github.com/new
2. Nommez votre repository (ex: `iptv-tools`)
3. Ne cochez pas "Initialize with README" (vous en avez déjà un)
4. Créez le repository

### 3. Pusher vers GitHub

```bash
git remote add origin https://github.com/VOTRE_USERNAME/iptv-tools.git
git branch -M main
git push -u origin main
```

### 4. Utiliser les URLs des logos hébergés

Les logos seront accessibles via :
```
https://raw.githubusercontent.com/VOTRE_USERNAME/iptv-tools/main/logos/NOM_DU_FICHIER.png
```

Vous pouvez ensuite éditer votre fichier M3U pour remplacer les chemins locaux par ces URLs.

## Format EXTINF supporté

Le script gère les lignes EXTINF avec ce format :

```
#EXTINF:-1 group-title="Groupe" tvg-id="channel.id" tvg-logo="http://url.com/logo.png",NOM DE LA CHAÎNE
```

Les attributs peuvent être dans n'importe quel ordre.

## API utilisée

Le script utilise l'API publique de [iptv-org](https://github.com/iptv-org/iptv) :
- Base de données de milliers de chaînes TV mondiales
- IDs EPG normalisés
- URLs de logos

## Limitations

- La recherche automatique dépend de la disponibilité de l'API iptv-org
- L'affichage d'images dans le terminal nécessite `imgcat` (macOS uniquement)
- Les chaînes non présentes dans iptv-org nécessitent une saisie manuelle

## Dépannage

### "Command not found: imgcat"
L'affichage d'image dans le terminal est désactivé. Installez imgcat avec `brew install imgcat` ou continuez sans (les URLs seront affichées).

### "Erreur de chargement de la base iptv-org"
Vérifiez votre connexion Internet. Le script télécharge la base de données au démarrage.

### Le fichier de sortie n'est pas créé
Vérifiez les permissions d'écriture dans le dossier du fichier source.

## Licence

Libre d'utilisation pour usage personnel et éducatif.

## Contribution

Les suggestions et améliorations sont les bienvenues !

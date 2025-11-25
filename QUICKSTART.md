# Guide de démarrage rapide

## Installation rapide

```bash
# Aucune dépendance requise, Python 3 uniquement
python3 m3u_editor.py
```

## Utilisation en 3 étapes

### 1. Lancer le script
```bash
python3 m3u_editor.py
```

### 2. Indiquer le fichier et la ligne limite
```
Fichier M3U source: lists/mylist.m3u
Traiter jusqu'à la ligne numéro: 50
```

### 3. Éditer chaque chaîne
Pour chaque ligne EXTINF, vous verrez :

#### Groupe
```
GROUPE ACTUEL: undefinedTR| HABER ⁴ᴷ

Sélectionnez ou entrez un nouveau groupe:
  1. TR - HABER - 1
  n. Nouvelle valeur
  s. Sauter
Choix: 1
```

#### EPG ID (détection automatique par pays)
```
TVG-ID ACTUEL: 295768

🔍 5 résultat(s) trouvé(s):
  1. [TR] ATV → ATV.tr          ← Les résultats sont triés par pertinence
  2. [TR] ATV Avrupa → ATVAvrupa.tr
  m. Saisir manuellement
  s. Sauter
Choix: 1
```

#### Logo (prévisualisation + hébergement)
```
LOGO ACTUEL: http://example.com/logo.jpg

🖼️  Logo(s) trouvé(s):
  1. https://i.imgur.com/xFGDk3k.png
  [Image affichée si imgcat installé]

  m. Saisir URL manuellement
  s. Sauter
Choix (ajoutez 'h' pour héberger): 1 h
                                    ↑ ↑
                                    │ └─ Télécharger pour GitHub
                                    └─── Choisir l'option 1

📦 Hébergement sur GitHub...
✓ Fichier téléchargé: logos/ATV_tr.png
```

## Syntaxe pour l'hébergement GitHub

Pour télécharger un logo localement (afin de l'héberger sur GitHub) :

| Action | Syntaxe |
|--------|---------|
| Choisir option 1 + héberger | `1 h` ou `1h` |
| Choisir option 2 + héberger | `2 h` ou `2h` |
| Saisir manuellement + héberger | `m h` ou `mh` |
| Sans hébergement | `1`, `2`, `m` |
| Sauter | `s` |

## Fichier de sortie

Le fichier modifié sera sauvegardé automatiquement :
```
lists/mylist.m3u → lists/mylist_edited.m3u
```

## Hébergement des logos sur GitHub

Après avoir édité votre fichier M3U :

```bash
# 1. Initialiser Git (si pas déjà fait)
git init

# 2. Ajouter les fichiers
git add m3u_editor.py logos/ .gitignore README.md

# 3. Commit
git commit -m "Add IPTV tools and logos"

# 4. Créer un repo sur GitHub et pusher
git remote add origin https://github.com/VOTRE_USER/VOTRE_REPO.git
git push -u origin main
```

Les logos seront accessibles via :
```
https://raw.githubusercontent.com/VOTRE_USER/VOTRE_REPO/main/logos/NOM_FICHIER.png
```

## Astuces

### Voir les images dans le terminal (macOS)
```bash
# Télécharger imgcat
curl -O https://iterm2.com/utilities/imgcat
chmod +x imgcat
sudo mv imgcat /usr/local/bin/
```

### Arrêter l'édition en cours
Tapez `q` quand on vous demande de continuer après avoir édité une ligne.

### Traiter tout le fichier
Indiquez un numéro de ligne très élevé (ex: 99999).

## Dépannage rapide

| Problème | Solution |
|----------|----------|
| Erreur 403 lors du téléchargement | ✓ Corrigé (User-Agent ajouté) |
| Les images ne s'affichent pas | Installez imgcat ou ignorez |
| Pas de résultats EPG | Vérifiez le format du nom (doit être `CODE: Nom`) |
| Logo non téléchargé | Vérifiez que vous avez bien tapé `h` après le choix |

## Support

Pour signaler un bug ou demander une fonctionnalité, ouvrez une issue sur le repository GitHub.

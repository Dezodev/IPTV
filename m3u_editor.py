#!/usr/bin/env python3
"""
M3U EXTINF Editor
Permet de modifier les informations EXTINF d'un fichier M3U (groupe, EPG ID, logo)
"""

import re
import sys
import json
import urllib.request
import urllib.parse
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import subprocess
import tempfile


class IPTVOrgAPI:
    """Interface pour l'API iptv-org"""

    CHANNELS_URL = "https://iptv-org.github.io/api/channels.json"

    def __init__(self):
        self.channels_data = None
        self._load_channels()

    def _load_channels(self):
        """Charge les données des chaînes depuis l'API"""
        try:
            print("📡 Chargement de la base de données iptv-org...", end=" ", flush=True)
            with urllib.request.urlopen(self.CHANNELS_URL, timeout=10) as response:
                self.channels_data = json.loads(response.read().decode('utf-8'))
            print(f"✓ {len(self.channels_data)} chaînes chargées")
        except Exception as e:
            print(f"✗ Erreur: {e}")
            self.channels_data = []

    def search_channel(self, channel_name: str) -> List[Dict]:
        """
        Recherche une chaîne par nom
        Retourne une liste de résultats correspondants
        """
        if not self.channels_data:
            return []

        # Extraire le code pays et nettoyer le nom
        country_code = self._extract_country_code(channel_name)
        clean_name = self._clean_channel_name(channel_name)

        # Calculer les scores pour chaque chaîne
        scored_results = []
        for channel in self.channels_data:
            # Recherche dans le nom et les noms alternatifs
            names_to_check = [channel.get('name', '')]
            if 'alt_names' in channel:
                names_to_check.extend(channel['alt_names'])

            best_score = 0
            for name in names_to_check:
                if name:
                    score = self._calculate_match_score(clean_name, name,
                                                        country_code,
                                                        channel.get('country', ''))
                    best_score = max(best_score, score)

            if best_score > 0:
                scored_results.append((best_score, channel))

        # Trier par score décroissant
        scored_results.sort(reverse=True, key=lambda x: x[0])

        # Retourner les 5 meilleurs résultats
        return [channel for score, channel in scored_results[:5]]

    def _extract_country_code(self, name: str) -> Optional[str]:
        """Extrait le code pays du nom (ex: 'TR: ATV' -> 'TR')"""
        match = re.match(r'^([A-Z]{2}):\s*', name)
        return match.group(1) if match else None

    def _calculate_match_score(self, query: str, target: str,
                               query_country: Optional[str],
                               target_country: str) -> int:
        """
        Calcule un score de correspondance entre 0 et 100
        Plus le score est élevé, meilleure est la correspondance
        """
        query = query.lower().strip()
        target = target.lower().strip()

        score = 0

        # Correspondance exacte = 100 points
        if query == target:
            score = 100
        # Le nom de la requête est contenu dans la cible = 80 points
        elif query in target:
            score = 80
        # La cible est contenue dans la requête = 70 points
        elif target in query:
            score = 70
        else:
            # Correspondance sans espaces ni caractères spéciaux
            query_clean = re.sub(r'[^a-z0-9]', '', query)
            target_clean = re.sub(r'[^a-z0-9]', '', target)

            if query_clean == target_clean:
                score = 90
            elif query_clean in target_clean:
                score = 60
            elif target_clean in query_clean:
                score = 50

        # Bonus de 50 points si le pays correspond
        if score > 0 and query_country and query_country.upper() == target_country.upper():
            score += 50

        return score

    def _clean_channel_name(self, name: str) -> str:
        """Nettoie le nom de la chaîne"""
        # Enlever le code pays (ex: "TR: ")
        name = re.sub(r'^[A-Z]{2}:\s*', '', name)
        # Enlever les infos entre crochets
        name = re.sub(r'\[.*?\]', '', name)
        return name.strip()



class LogoManager:
    """Gestionnaire de logos avec prévisualisation et hébergement GitHub"""

    def __init__(self, repo_logos_dir: Path):
        self.repo_logos_dir = repo_logos_dir
        self.repo_logos_dir.mkdir(parents=True, exist_ok=True)

    def _create_request(self, url: str) -> urllib.request.Request:
        """Crée une requête HTTP avec User-Agent pour éviter les erreurs 403"""
        req = urllib.request.Request(
            url,
            headers={
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            }
        )
        return req

    def display_logo(self, logo_url: str) -> bool:
        """Affiche le logo dans le terminal (macOS avec imgcat)"""
        try:
            # Télécharger l'image temporairement
            with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp_file:
                req = self._create_request(logo_url)
                with urllib.request.urlopen(req, timeout=10) as response:
                    tmp_file.write(response.read())
                tmp_path = tmp_file.name

            # Utiliser imgcat si disponible
            try:
                subprocess.run(['imgcat', tmp_path], check=True, timeout=5)
                Path(tmp_path).unlink()
                return True
            except (subprocess.CalledProcessError, FileNotFoundError):
                # imgcat non disponible, afficher juste l'URL
                print(f"   [Logo: {logo_url}]")
                print("   (imgcat non installé - impossible d'afficher l'image)")
                Path(tmp_path).unlink()
                return True
        except Exception as e:
            print(f"   ✗ Erreur d'affichage: {e}")
            return False

    def download_and_host(self, logo_url: str, channel_id: str) -> str:
        """
        Télécharge le logo et le sauvegarde dans le repo GitHub
        Retourne le chemin relatif pour le futur hébergement GitHub
        """
        try:
            # Extraire le nom du fichier final de l'URL (après le dernier /)
            url_filename = logo_url.split('/')[-1].lower()

            # Retirer les paramètres de query (?xxx)
            if '?' in url_filename:
                url_filename = url_filename.split('?')[0]

            # Déterminer l'extension à partir du nom de fichier final
            ext = '.png'  # Par défaut
            if url_filename.endswith('.jpg') or url_filename.endswith('.jpeg'):
                ext = '.jpg'
            elif url_filename.endswith('.svg'):
                ext = '.svg'
            elif url_filename.endswith('.png'):
                ext = '.png'
            elif url_filename.endswith('.webp'):
                ext = '.webp'

            # Créer un nom de fichier sûr
            safe_id = re.sub(r'[^a-zA-Z0-9_-]', '_', channel_id)
            filename = f"{safe_id}{ext}"
            filepath = self.repo_logos_dir / filename

            # Télécharger avec User-Agent
            req = self._create_request(logo_url)
            with urllib.request.urlopen(req, timeout=10) as response:
                filepath.write_bytes(response.read())

            print(f"   ✓ Fichier téléchargé: {filepath}")

            # Retourner l'URL relative (pour futur hébergement GitHub)
            return f"logos/{filename}"
        except Exception as e:
            print(f"   ✗ Erreur de téléchargement: {e}")
            return logo_url  # Retourner l'URL originale en cas d'échec


class M3UEditor:
    """Éditeur de fichiers M3U"""

    EXTINF_PATTERN = re.compile(
        r'#EXTINF:-1\s+'
        r'(?:group-title="([^"]*)")?\s*'
        r'(?:tvg-id="([^"]*)")?\s*'
        r'(?:tvg-logo="([^"]*)")?\s*'
        r',(.+)$'
    )

    def __init__(self, input_file: Path, output_file: Path):
        self.input_file = input_file
        self.output_file = output_file
        self.groups_history: List[str] = []
        self.api = IPTVOrgAPI()
        self.logo_manager = LogoManager(Path(__file__).parent / "logos")

    def parse_extinf(self, line: str) -> Optional[Dict]:
        """Parse une ligne EXTINF et extrait les attributs"""
        # Pattern plus flexible pour gérer différents ordres d'attributs
        attrs = {
            'group-title': '',
            'tvg-id': '',
            'tvg-logo': '',
            'name': ''
        }

        # Extraire le nom (après la dernière virgule)
        if ',' in line:
            header, name = line.rsplit(',', 1)
            attrs['name'] = name.strip()
        else:
            return None

        # Extraire les attributs
        group_match = re.search(r'group-title="([^"]*)"', header)
        if group_match:
            attrs['group-title'] = group_match.group(1)

        id_match = re.search(r'tvg-id="([^"]*)"', header)
        if id_match:
            attrs['tvg-id'] = id_match.group(1)

        logo_match = re.search(r'tvg-logo="([^"]*)"', header)
        if logo_match:
            attrs['tvg-logo'] = logo_match.group(1)

        return attrs

    def build_extinf(self, attrs: Dict) -> str:
        """Construit une ligne EXTINF à partir des attributs"""
        parts = ['#EXTINF:-1']

        if attrs['group-title']:
            parts.append(f'group-title="{attrs["group-title"]}"')
        if attrs['tvg-id']:
            parts.append(f'tvg-id="{attrs["tvg-id"]}"')
        if attrs['tvg-logo']:
            parts.append(f'tvg-logo="{attrs["tvg-logo"]}"')

        return ' '.join(parts) + f',{attrs["name"]}'

    def select_from_list(self, prompt: str, options: List[str], allow_new: bool = True) -> str:
        """Affiche une liste et permet la sélection"""
        if not options:
            if allow_new:
                return input(f"{prompt}: ").strip()
            return ""

        print(f"\n{prompt}")
        for i, opt in enumerate(options, 1):
            print(f"  {i}. {opt}")
        if allow_new:
            print(f"  n. Nouvelle valeur")
        print(f"  s. Sauter (garder l'actuel)")

        while True:
            choice = input("Choix: ").strip().lower()

            if choice == 's':
                return None  # Signal pour garder la valeur actuelle
            elif choice == 'n' and allow_new:
                return input("Nouvelle valeur: ").strip()
            elif choice.isdigit():
                idx = int(choice) - 1
                if 0 <= idx < len(options):
                    return options[idx]

            print("Choix invalide, réessayez.")

    def edit_group(self, current_group: str) -> str:
        """Édite le groupe avec historique"""
        print(f"\n{'='*60}")
        print(f"GROUPE ACTUEL: {current_group}")

        result = self.select_from_list(
            "Sélectionnez ou entrez un nouveau groupe:",
            self.groups_history
        )

        if result is None:  # Sauter
            return current_group

        # Ajouter à l'historique si nouveau
        if result and result not in self.groups_history:
            self.groups_history.append(result)

        return result if result else current_group

    def edit_tvg_id(self, channel_name: str, current_id: str) -> str:
        """Édite le TVG ID avec détection automatique"""
        print(f"\nTVG-ID ACTUEL: {current_id}")

        # Rechercher dans l'API
        results = self.api.search_channel(channel_name)

        if results:
            print(f"\n🔍 {len(results)} résultat(s) trouvé(s):")
            options = []
            for i, channel in enumerate(results, 1):
                channel_id = channel.get('id', '')
                channel_name_api = channel.get('name', '')
                channel_country = channel.get('country', '??')
                print(f"  {i}. [{channel_country}] {channel_name_api} → {channel_id}")
                options.append(channel_id)

            print(f"  m. Saisir manuellement")
            print(f"  s. Sauter (garder l'actuel)")

            while True:
                choice = input("Choix: ").strip().lower()

                if choice == 's':
                    return current_id
                elif choice == 'm':
                    return input("TVG ID: ").strip()
                elif choice.isdigit():
                    idx = int(choice) - 1
                    if 0 <= idx < len(options):
                        return options[idx]

                print("Choix invalide, réessayez.")
        else:
            print("  Aucun résultat trouvé dans la base iptv-org")
            manual = input("  Entrer manuellement (ou Entrée pour garder actuel): ").strip()
            return manual if manual else current_id

    def edit_tvg_logo(self, channel_name: str, current_logo: str, channel_id: str) -> str:
        """Édite le logo avec détection automatique et prévisualisation"""
        print(f"\nLOGO ACTUEL: {current_logo}")

        # Rechercher dans l'API
        results = self.api.search_channel(channel_name)

        logo_options = []
        if results:
            print(f"\n🖼️  Logo(s) trouvé(s):")
            for channel in results:
                logo = channel.get('logo', '')
                if logo:
                    logo_options.append(logo)

        # Ajouter le logo actuel s'il existe
        if current_logo and current_logo not in logo_options:
            logo_options.insert(0, current_logo)

        if logo_options:
            for i, logo_url in enumerate(logo_options, 1):
                print(f"\n  {i}. {logo_url}")
                self.logo_manager.display_logo(logo_url)

            print(f"\n  m. Saisir URL manuellement")
            print(f"  s. Sauter (garder l'actuel)")

            while True:
                choice = input("Choix (ajoutez 'h' pour héberger, ex: '1 h' ou 'm h'): ").strip().lower()

                # Vérifier si l'utilisateur veut héberger sur GitHub
                host_on_github = False
                if ' h' in choice or choice.endswith('h'):
                    host_on_github = True
                    # Enlever le 'h' et les espaces
                    choice = choice.replace(' h', '').replace('h', '').strip()

                selected_logo = None

                if choice == 's':
                    return current_logo
                elif choice == 'm':
                    selected_logo = input("URL du logo: ").strip()
                elif choice.isdigit():
                    idx = int(choice) - 1
                    if 0 <= idx < len(logo_options):
                        selected_logo = logo_options[idx]

                if selected_logo:
                    if host_on_github:
                        print("  📦 Hébergement sur GitHub...")
                        hosted_path = self.logo_manager.download_and_host(selected_logo, channel_id)
                        if hosted_path.startswith('logos/'):  # Succès du téléchargement
                            # Construire l'URL GitHub complète
                            github_url = f"https://raw.githubusercontent.com/Dezodev/IPTV/main/{hosted_path}"
                            print(f"  ✓ URL GitHub: {github_url}")
                            return github_url
                        else:
                            print(f"  ⚠️  Échec du téléchargement, utilisation de l'URL originale")
                            return selected_logo
                    return selected_logo

                print("Choix invalide, réessayez.")
        else:
            print("  Aucun logo trouvé dans la base iptv-org")
            manual = input("  Entrer URL manuellement (ou Entrée pour garder actuel): ").strip()
            return manual if manual else current_logo

    def edit_line(self, line: str, line_num: int) -> Tuple[str, bool]:
        """
        Édite une ligne EXTINF
        Retourne (nouvelle_ligne, continuer)
        """
        attrs = self.parse_extinf(line)
        if not attrs:
            return line, True

        print(f"\n{'#'*60}")
        print(f"LIGNE {line_num}: {attrs['name']}")
        print(f"{'#'*60}")

        # Éditer groupe
        attrs['group-title'] = self.edit_group(attrs['group-title'])

        # Éditer TVG ID
        attrs['tvg-id'] = self.edit_tvg_id(attrs['name'], attrs['tvg-id'])

        # Éditer logo
        attrs['tvg-logo'] = self.edit_tvg_logo(
            attrs['name'],
            attrs['tvg-logo'],
            attrs['tvg-id'] or 'unknown'
        )

        # Reconstruire la ligne
        new_line = self.build_extinf(attrs)

        print(f"\n{'='*60}")
        print("AVANT:", line)
        print("APRÈS:", new_line)
        print(f"{'='*60}")

        # Demander confirmation pour continuer
        cont = input("\n[Entrée] Continuer | [q] Quitter: ").strip().lower()

        return new_line, cont != 'q'

    def process(self, max_line: int):
        """Traite le fichier M3U jusqu'à la ligne spécifiée"""
        if not self.input_file.exists():
            print(f"✗ Fichier introuvable: {self.input_file}")
            return

        print(f"\n📝 Édition de: {self.input_file}")
        print(f"📄 Sortie vers: {self.output_file}")
        print(f"📊 Traitement jusqu'à la ligne: {max_line}")

        with open(self.input_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        output_lines = []
        current_line_num = 0
        continue_editing = True

        for i, line in enumerate(lines):
            current_line_num = i + 1

            # Si on dépasse la limite, copier tel quel
            if current_line_num > max_line:
                output_lines.append(line)
                continue

            # Si c'est une ligne EXTINF et qu'on continue
            if line.strip().startswith('#EXTINF:') and continue_editing:
                new_line, continue_editing = self.edit_line(line.strip(), current_line_num)
                output_lines.append(new_line + '\n')
            else:
                output_lines.append(line)

            # Si l'utilisateur a demandé d'arrêter
            if not continue_editing:
                print("\n⚠️  Arrêt demandé. Copie du reste du fichier...")
                output_lines.extend(lines[i+1:])
                break

        # Écrire le fichier de sortie
        with open(self.output_file, 'w', encoding='utf-8') as f:
            f.writelines(output_lines)

        print(f"\n✓ Fichier modifié sauvegardé: {self.output_file}")
        print(f"✓ {len(self.groups_history)} groupe(s) utilisé(s)")

        # Afficher les logos téléchargés
        logos_dir = Path(__file__).parent / "logos"
        if logos_dir.exists():
            logos_count = len(list(logos_dir.glob('*')))
            if logos_count > 0:
                print(f"✓ {logos_count} logo(s) téléchargé(s) dans: {logos_dir}")


def main():
    """Point d'entrée principal"""
    print("=" * 60)
    print("M3U EXTINF EDITOR")
    print("=" * 60)

    # Demander le fichier d'entrée
    input_path = input("\nFichier M3U source (ex: lists/input.m3u): ").strip()
    if not input_path:
        print("✗ Aucun fichier spécifié")
        sys.exit(1)

    input_file = Path(input_path)
    if not input_file.exists():
        print(f"✗ Fichier introuvable: {input_file}")
        sys.exit(1)

    # Générer le nom du fichier de sortie
    output_file = input_file.parent / f"{input_file.stem}_edited{input_file.suffix}"

    # Demander jusqu'à quelle ligne traiter
    while True:
        max_line_str = input("\nTraiter jusqu'à la ligne numéro: ").strip()
        if max_line_str.isdigit():
            max_line = int(max_line_str)
            break
        print("✗ Veuillez entrer un numéro de ligne valide")

    # Lancer l'édition
    editor = M3UEditor(input_file, output_file)
    editor.process(max_line)

    print("\n✓ Terminé!")

    # Vérifier s'il y a des nouveaux logos
    logos_dir = Path(__file__).parent / "logos"
    if logos_dir.exists():
        logos_count = len(list(logos_dir.glob('*')))
        if logos_count > 0:
            print("\n📌 Pour pousser les nouveaux logos sur GitHub:")
            print("   git add logos/")
            print("   git commit -m 'Add new logos'")
            print("   git push")
            print(f"\n   Les logos seront accessibles via:")
            print(f"   https://raw.githubusercontent.com/Dezodev/IPTV/main/logos/NOM_FICHIER.png")


if __name__ == "__main__":
    main()

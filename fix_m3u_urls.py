#!/usr/bin/env python3
"""
Script pour corriger le décalage des URLs dans le fichier M3U.
À partir de la ligne 5870, les URLs sont décalées d'un cran.
"""
import argparse

def fix_m3u_file(input_file, output_file, start_line=5870):
    """
    Corrige le décalage des URLs dans un fichier M3U à partir d'une ligne donnée.

    Args:
        input_file: Chemin du fichier M3U source
        output_file: Chemin du fichier M3U corrigé
        start_line: Numéro de ligne où commence le décalage (1-indexed)
    """
    print(f"Lecture du fichier: {input_file}")

    with open(input_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    total_lines = len(lines)
    print(f"Total de lignes: {total_lines}")
    print(f"Correction à partir de la ligne: {start_line}")

    # Convertir en index 0-based
    start_index = start_line - 1

    # Extraire les parties avant et après le point de décalage
    before_fix = lines[:start_index]
    after_fix = lines[start_index:]

    # Séparer les lignes EXTINF et les URLs après le point de décalage
    extinf_lines = []
    url_lines = []

    for i, line in enumerate(after_fix):
        if line.startswith('#EXTINF'):
            extinf_lines.append(line)
        elif line.startswith('http://') or line.startswith('https://'):
            url_lines.append(line)
        else:
            # Garder les autres lignes (comme #EXTM3U, lignes vides, etc.)
            if i == 0:  # Si c'est la première ligne après start_index
                extinf_lines.append(line)

    print(f"Lignes EXTINF trouvées: {len(extinf_lines)}")
    print(f"Lignes URL trouvées: {len(url_lines)}")

    # Décaler les URLs d'un cran (prendre à partir de la 2ème URL)
    if len(url_lines) > 1:
        shifted_urls = url_lines[1:]  # Commence à partir de l'URL suivante
        print(f"URLs décalées: {len(shifted_urls)}")

        # Reconstruire la section corrigée
        corrected_section = []
        for i, extinf in enumerate(extinf_lines):
            corrected_section.append(extinf)
            if i < len(shifted_urls):
                corrected_section.append(shifted_urls[i])

        # Combiner toutes les parties
        fixed_lines = before_fix + corrected_section

        # Écrire le fichier corrigé
        print(f"Écriture du fichier corrigé: {output_file}")
        with open(output_file, 'w', encoding='utf-8') as f:
            f.writelines(fixed_lines)

        print("✓ Correction terminée avec succès!")
        print(f"  - Lignes originales: {total_lines}")
        print(f"  - Lignes corrigées: {len(fixed_lines)}")
        print(f"  - Différence: {total_lines - len(fixed_lines)} lignes")
    else:
        print("✗ Erreur: pas assez d'URLs pour effectuer le décalage")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Corrige le décalage des URLs dans un fichier M3U"
    )
    parser.add_argument(
        "input_file",
        help="Chemin du fichier M3U source"
    )
    parser.add_argument(
        "output_file",
        help="Chemin du fichier M3U corrigé à générer"
    )
    parser.add_argument(
        "--start-line",
        type=int,
        default=5870,
        help="Numéro de ligne où commence le décalage (défaut: 5870)"
    )

    args = parser.parse_args()

    # Exécuter la correction
    fix_m3u_file(args.input_file, args.output_file, args.start_line)

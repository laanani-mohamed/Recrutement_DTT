"""
rapid_ocr.py
=============
Méthode d'extraction : RapidOCR (OCR local, sans internet)
-----------------------------------------------------------
Utilise RapidOCRPDF pour extraire le texte d'un PDF
directement via un moteur OCR local basé sur ONNX Runtime.
Aucun appel API externe requis — fonctionne hors ligne.

Dépendances :
    - rapidocr_pdf   : extension RapidOCR dédiée aux fichiers PDF
    - rapidocr       : moteur OCR local rapide (CNN/ONNX)
    - onnxruntime    : runtime pour les modèles ONNX
    - pymupdf        : rendu des pages PDF en images pour l'OCR
    - Pillow         : traitement d'images intermédiaires

Utilisation :
    from src.extraction.rapid_ocr import extract_with_rapidocr
    text = extract_with_rapidocr("/chemin/vers/cv.pdf")
"""

import os
import sys
from rapidocr_pdf import RapidOCRPDF


# ------------------------------------------------------------------
# Initialisation du moteur RapidOCR pour PDF
# L'instance est créée une seule fois (coûteuse à initialiser)
# ------------------------------------------------------------------
_pdf_extractor = RapidOCRPDF()


def extract_with_rapidocr(pdf_path: str) -> str:
    """
    Extrait le texte complet d'un PDF via RapidOCR (local, hors-ligne).

    RapidOCR traite chaque page du PDF comme une image et applique
    un réseau de neurones pour reconnaître le texte.
    Chaque bloc détecté retourne : [numéro_page, texte, score_confiance].

    Args:
        pdf_path (str): Chemin vers le fichier PDF à traiter.

    Returns:
        str: Texte complet extrait, organisé par page avec le score de confiance.

    Raises:
        FileNotFoundError: Si le fichier PDF n'existe pas.
        RuntimeError: Si RapidOCR ne détecte aucun texte dans le document.
    """
    if not os.path.isfile(pdf_path):
        raise FileNotFoundError(f"Fichier PDF introuvable : {pdf_path}")

    print("[RapidOCR] Démarrage de l'extraction OCR locale...", file=sys.stderr)
    resultats = _pdf_extractor(pdf_path)

    if not resultats:
        raise RuntimeError("RapidOCR n'a détecté aucun texte dans le document.")

    # Regroupement des blocs par numéro de page
    pages: dict[int, list[str]] = {}

    for item in resultats:
        if len(item) == 3:
            page_num, texte, confiance = item
            page_num = int(page_num)
            if page_num not in pages:
                pages[page_num] = []
            # Inclure le score de confiance pour le débogage
            # confiance peut être une string selon la version de rapidocr_pdf → on cast en float
            try:
                conf_val = float(confiance)
                conf_str = f"[conf={conf_val:.2f}]"
            except (TypeError, ValueError):
                conf_str = f"[conf={confiance}]"
            pages[page_num].append(f"{texte}  {conf_str}")
        else:
            # Bloc de format inattendu — on l'inclut tel quel
            print(f"[RapidOCR] Format inattendu : {item}", file=sys.stderr)

    # Construction du texte final page par page
    lignes = []
    for page_num in sorted(pages.keys()):
        lignes.append(f"\n--- Page {page_num} ---")
        lignes.extend(pages[page_num])

    return "\n".join(lignes)


# ------------------------------------------------------------------
# Point d'entrée pour test direct du module
# Usage : python -m src.extraction.rapid_ocr /chemin/cv.pdf
# ------------------------------------------------------------------
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage : python rapid_ocr.py <chemin_vers_pdf>")
        sys.exit(1)

    chemin_pdf = sys.argv[1]
    texte = extract_with_rapidocr(chemin_pdf)
    print(texte)

"""
debug.py
=========
Interface de débogage Streamlit pour le projet d'extraction et classification de CV.
------------------------------------------------------------------------------------
Lancement :
    cd APP/
    streamlit run src/debug.py

Sections de la page :
    1. 📄 Extraction  — Choisir un CV depuis app/ressource, choisir la méthode OCR,
                        lancer l'extraction et afficher le résultat.
    2. 🏷️ Classification — Section réservée pour la future intégration du modèle
                           de classification des CV (en cours de développement).
"""

import os
import sys
import time
import traceback

import streamlit as st

# ------------------------------------------------------------------
# Ajout du dossier parent (APP/) au PYTHONPATH pour les imports relatifs
# ------------------------------------------------------------------
APP_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if APP_DIR not in sys.path:
    sys.path.insert(0, APP_DIR)

# Import du module principal d'extraction
from src.extraction.main_extraction import extract_text, METHODS

# ------------------------------------------------------------------
# Dossier des ressources (CVs)
# ------------------------------------------------------------------
RESSOURCE_DIR = os.path.join(APP_DIR, "ressource")


# ==================================================================
#  CONFIGURATION DE LA PAGE STREAMLIT
# ==================================================================
st.set_page_config(
    page_title="CV Debug Tool — Extraction & Classification",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ------------------------------------------------------------------
# CSS personnalisé : design clair et propre (thème blanc)
# ------------------------------------------------------------------
st.markdown(
    """
    <style>
    /* ---- Import police Google Fonts ---- */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    /* ---- Variables de couleurs (thème clair) ---- */
    :root {
        --bg-main:      #ffffff;
        --bg-card:      #f8fafc;
        --bg-card2:     #f1f5f9;
        --accent-blue:  #2563eb;
        --accent-purple:#7c3aed;
        --accent-green: #059669;
        --text-primary: #0f172a;
        --text-muted:   #64748b;
        --border:       #e2e8f0;
        --shadow:       0 2px 12px rgba(0,0,0,0.07);
    }

    /* ---- Corps principal ---- */
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif !important;
        background-color: #ffffff !important;
        color: var(--text-primary) !important;
    }

    .stApp {
        background-color: #ffffff !important;
    }

    /* ---- En-tête principal ---- */
    .hero-header {
        text-align: center;
        padding: 2rem 1rem 1.25rem;
        margin-bottom: 0.5rem;
    }

    .hero-header h1 {
        font-size: 2.2rem;
        font-weight: 700;
        background: linear-gradient(90deg, #2563eb, #7c3aed);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 0.4rem;
    }

    .hero-header p {
        color: var(--text-muted);
        font-size: 0.97rem;
        font-weight: 400;
    }

    /* ---- Badges de méthode ---- */
    .method-badge {
        display: inline-block;
        padding: 0.22rem 0.7rem;
        border-radius: 9999px;
        font-size: 0.72rem;
        font-weight: 600;
        letter-spacing: 0.04em;
        text-transform: uppercase;
        margin-bottom: 0.5rem;
    }
    .badge-blue   { background: #eff6ff; color: #1d4ed8; border: 1px solid #bfdbfe; }
    .badge-purple { background: #f5f3ff; color: #6d28d9; border: 1px solid #ddd6fe; }
    .badge-green  { background: #ecfdf5; color: #065f46; border: 1px solid #a7f3d0; }

    /* ---- Titre de section ---- */
    .section-title {
        font-size: 1.1rem;
        font-weight: 600;
        color: var(--text-primary);
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }

    /* ---- Boîte résultat ---- */
    .result-box {
        background: #f8fafc;
        border: 1px solid var(--border);
        border-radius: 10px;
        padding: 1.25rem;
        font-family: 'Courier New', monospace;
        font-size: 0.82rem;
        line-height: 1.65;
        color: #1e293b;
        white-space: pre-wrap;
        max-height: 520px;
        overflow-y: auto;
    }

    /* ---- Métriques ---- */
    .metric-row {
        display: flex;
        gap: 0.75rem;
        margin: 1rem 0;
        flex-wrap: wrap;
    }

    .metric-item {
        background: #f1f5f9;
        border: 1px solid var(--border);
        border-radius: 10px;
        padding: 0.7rem 1.1rem;
        flex: 1;
        min-width: 110px;
        text-align: center;
    }

    .metric-value {
        font-size: 1.4rem;
        font-weight: 700;
        color: var(--accent-blue);
    }

    .metric-label {
        font-size: 0.7rem;
        color: var(--text-muted);
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-top: 0.2rem;
    }

    /* ---- Section vide (Classification) ---- */
    .coming-soon {
        text-align: center;
        padding: 3rem 1rem;
        color: var(--text-muted);
    }

    .coming-soon .icon { font-size: 3rem; margin-bottom: 0.75rem; }
    .coming-soon h3 { font-size: 1.05rem; font-weight: 500; color: #475569; }
    .coming-soon p  { font-size: 0.85rem; color: #94a3b8; margin-top: 0.4rem; }

    /* ---- Onglets ---- */
    [data-testid="stTabs"] [role="tab"] {
        font-family: 'Inter', sans-serif !important;
        font-weight: 500 !important;
        font-size: 0.97rem !important;
        color: var(--text-muted) !important;
    }

    /* ---- Scrollbar ---- */
    .result-box::-webkit-scrollbar { width: 5px; }
    .result-box::-webkit-scrollbar-track { background: #f1f5f9; }
    .result-box::-webkit-scrollbar-thumb { background: #cbd5e1; border-radius: 3px; }

    /* ---- Bouton principal ---- */
    .stButton > button {
        background: linear-gradient(135deg, #2563eb, #4f46e5) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        font-family: 'Inter', sans-serif !important;
        font-size: 0.93rem !important;
        padding: 0.5rem 1.75rem !important;
        transition: all 0.2s ease !important;
        box-shadow: 0 2px 8px rgba(37,99,235,0.25) !important;
    }

    .stButton > button:hover {
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 14px rgba(37,99,235,0.35) !important;
    }

    /* ---- Alerts ---- */
    .stAlert {
        border-radius: 8px !important;
        font-family: 'Inter', sans-serif !important;
    }

    /* ---- Séparateur ---- */
    hr { border-color: var(--border) !important; }

    /* ---- Masquer menu hamburger et footer Streamlit ---- */
    #MainMenu, footer { visibility: hidden; }
    header { background: transparent !important; }
    </style>
    """,
    unsafe_allow_html=True,
)


# ==================================================================
#  FONCTIONS UTILITAIRES
# ==================================================================

def lister_cvs(dossier: str) -> list[str]:
    """
    Liste tous les fichiers PDF présents dans le dossier ressource.

    Args:
        dossier (str): Chemin vers le dossier contenant les CVs.

    Returns:
        list[str]: Liste des noms de fichiers PDF trouvés.
    """
    if not os.path.isdir(dossier):
        return []
    return sorted(
        f for f in os.listdir(dossier) if f.lower().endswith(".pdf")
    )


def afficher_metriques(texte: str, duree: float) -> None:
    """
    Affiche les métriques d'extraction sous forme de cards HTML.

    Args:
        texte (str): Texte extrait.
        duree (float): Durée de l'extraction en secondes.
    """
    nb_mots = len(texte.split())
    nb_chars = len(texte)
    nb_lignes = texte.count("\n") + 1

    st.markdown(
        f"""
        <div class="metric-row">
            <div class="metric-item">
                <div class="metric-value">{nb_mots:,}</div>
                <div class="metric-label">Mots</div>
            </div>
            <div class="metric-item">
                <div class="metric-value">{nb_chars:,}</div>
                <div class="metric-label">Caractères</div>
            </div>
            <div class="metric-item">
                <div class="metric-value">{nb_lignes:,}</div>
                <div class="metric-label">Lignes</div>
            </div>
            <div class="metric-item">
                <div class="metric-value">{duree:.1f}s</div>
                <div class="metric-label">Durée</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def description_methode(method_key: str) -> tuple[str, str]:
    """
    Retourne le badge HTML et une courte description pour une méthode.

    Returns:
        tuple[badge_html, description_texte]
    """
    infos = {
        "markitdown": (
            '<span class="method-badge badge-green">⚡ Local · Rapide</span>',
            "Idéal pour les **PDFs numériques** (non scannés). "
            "Convertit en Markdown sans IA. Très rapide.",
        ),
        "rapidocr": (
            '<span class="method-badge badge-blue">🔒 Local · Hors-ligne</span>',
            "Idéal pour les **PDFs scannés**. "
            "OCR local via réseau de neurones ONNX. Aucun appel API.",
        ),
        "llmwhisperer": (
            '<span class="method-badge badge-purple">☁️ Cloud · Haute qualité</span>',
            "**Meilleure précision** pour les documents complexes. "
            "Requiert une connexion internet et une clé API Unstract.",
        ),
    }
    return infos.get(method_key, ("", ""))


# ==================================================================
#  EN-TÊTE PRINCIPAL
# ==================================================================
st.markdown(
    """
    <div class="hero-header">
        <h1>📋 CV Debug Tool</h1>
        <p>Outil de débogage pour l'extraction de texte et la classification des CV</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# Ligne de séparation
st.markdown("---")


# ==================================================================
#  ONGLETS PRINCIPAUX : Extraction | Classification
# ==================================================================
tab_extraction, tab_classification = st.tabs(
    ["  📄  Extraction  ", "  🏷️  Classification  "]
)


# ==================================================================
#  ONGLET 1 — EXTRACTION
# ==================================================================
with tab_extraction:
    st.markdown("<br>", unsafe_allow_html=True)

    # ---- Colonne de configuration (gauche) et résultat (droite) ----
    col_config, col_result = st.columns([1, 2], gap="large")

    with col_config:
        st.markdown(
            '<div class="section-title">⚙️ Configuration</div>',
            unsafe_allow_html=True,
        )

        # --- Champ 1 : Choix du CV depuis app/ressource ---
        cvs_disponibles = lister_cvs(RESSOURCE_DIR)

        if not cvs_disponibles:
            st.warning(
                f"⚠️ Aucun PDF trouvé dans `APP/ressource/`.\n\n"
                f"Déposez vos fichiers CV dans ce dossier puis rechargez la page."
            )
            cv_selectionne = None
        else:
            cv_selectionne = st.selectbox(
                "📂 CV à analyser",
                options=cvs_disponibles,
                help=f"Fichiers PDF lus depuis : {RESSOURCE_DIR}",
            )

        st.markdown("<br>", unsafe_allow_html=True)

        # --- Champ 2 : Choix de la méthode d'extraction ---
        methode_labels = {
            "markitdown":   "⚡ MarkItDown — Local, rapide (PDF numérique)",
            "rapidocr":     "🔒 RapidOCR   — Local, hors-ligne (PDF scanné)",
            "llmwhisperer": "☁️ LLMWhisperer — Cloud, haute qualité",
        }

        methode_choisie = st.selectbox(
            "🔧 Méthode d'extraction",
            options=list(methode_labels.keys()),
            format_func=lambda k: methode_labels[k],
            help="Chaque méthode a ses avantages selon le type de PDF.",
        )

        # Affichage du badge et de la description de la méthode
        badge, description = description_methode(methode_choisie)
        st.markdown(badge, unsafe_allow_html=True)
        st.markdown(description)

        st.markdown("<br>", unsafe_allow_html=True)

        # --- Bouton d'exécution ---
        lancer = st.button(
            "🚀 Lancer l'extraction",
            disabled=(cv_selectionne is None),
            use_container_width=True,
        )

    # ---- Zone d'affichage du résultat (droite) ----
    with col_result:
        st.markdown(
            '<div class="section-title">📝 Résultat de l\'extraction</div>',
            unsafe_allow_html=True,
        )

        # Placeholder pour le résultat
        result_placeholder = st.empty()

        if lancer and cv_selectionne:
            pdf_path = os.path.join(RESSOURCE_DIR, cv_selectionne)

            with st.spinner(f"Extraction en cours avec **{methode_choisie}**..."):
                debut = time.perf_counter()
                try:
                    texte_extrait = extract_text(pdf_path, method=methode_choisie)
                    duree = time.perf_counter() - debut

                    # Métriques
                    afficher_metriques(texte_extrait, duree)

                    # Message de succès
                    st.success(
                        f"✅ Extraction réussie en {duree:.2f}s "
                        f"avec la méthode **{methode_choisie}**."
                    )

                    # Affichage du texte extrait
                    st.markdown(
                        f'<div class="result-box">{texte_extrait}</div>',
                        unsafe_allow_html=True,
                    )

                    # Bouton de téléchargement du résultat
                    st.download_button(
                        label="⬇️ Télécharger le texte extrait (.txt)",
                        data=texte_extrait.encode("utf-8"),
                        file_name=f"{os.path.splitext(cv_selectionne)[0]}_{methode_choisie}.txt",
                        mime="text/plain",
                        use_container_width=True,
                    )

                except FileNotFoundError as e:
                    st.error(f"❌ Fichier introuvable : {e}")
                except RuntimeError as e:
                    st.warning(f"⚠️ Extraction vide ou échouée : {e}")
                except Exception as e:
                    st.error(f"❌ Erreur inattendue :\n\n```\n{traceback.format_exc()}\n```")
        else:
            # État initial : aucune extraction lancée
            result_placeholder.markdown(
                """
                <div style="
                    text-align: center;
                    padding: 4rem 2rem;
                    color: #64748b;
                    border: 2px dashed #e2e8f0;
                    border-radius: 12px;
                    margin-top: 0.5rem;
                    background: #f8fafc;
                ">
                    <div style="font-size: 3rem; margin-bottom: 1rem;">📄</div>
                    <div style="font-size: 1rem; font-weight: 500; color: #475569;">
                        Sélectionnez un CV et une méthode,<br>puis cliquez sur <strong>Lancer l'extraction</strong>.
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )


# ==================================================================
#  ONGLET 2 — CLASSIFICATION (en cours de développement)
# ==================================================================
with tab_classification:
    st.markdown("<br>", unsafe_allow_html=True)

    # Colonnes pour la configuration (même layout que Extraction)
    col_cfg2, col_res2 = st.columns([1, 2], gap="large")

    with col_cfg2:
        st.markdown(
            '<div class="section-title">⚙️ Configuration</div>',
            unsafe_allow_html=True,
        )

        # --- Champ 1 : Choix du CV ---
        cvs_class = lister_cvs(RESSOURCE_DIR)

        if not cvs_class:
            st.warning("⚠️ Aucun PDF dans `APP/ressource/`.")
            cv_class = None
        else:
            cv_class = st.selectbox(
                "📂 CV à classifier",
                options=cvs_class,
                key="cv_classification",
                help="Sélectionnez le CV à soumettre au modèle de classification.",
            )

        st.markdown("<br>", unsafe_allow_html=True)

        # --- Champ 2 : Méthode d'extraction pour la classification ---
        methode_class = st.selectbox(
            "🔧 Méthode d'extraction (pré-traitement)",
            options=list(methode_labels.keys()),
            format_func=lambda k: methode_labels[k],
            key="methode_classification",
            help="Méthode utilisée pour extraire le texte avant classification.",
        )

        st.markdown("<br>", unsafe_allow_html=True)

        # --- Bouton d'exécution (désactivé — à venir) ---
        st.button(
            "🚀 Lancer la classification",
            disabled=True,
            use_container_width=True,
            help="La classification sera disponible prochainement.",
        )

    with col_res2:
        st.markdown(
            '<div class="section-title">🏷️ Résultat de la classification</div>',
            unsafe_allow_html=True,
        )

        # Placeholder "en construction"
        st.markdown(
            """
            <div class="coming-soon">
                <div class="icon">🚧</div>
                <h3>Module en cours de développement</h3>
                <p>
                    La classification automatique des CV sera intégrée ici.<br>
                    Elle utilisera le texte extrait par la méthode sélectionnée<br>
                    pour catégoriser et scorer les candidats.
                </p>
                <br>
                <p style="color:#94a3b8; font-size:0.8rem;">
                    Fonctionnalités prévues : matching poste/CV · scoring · extraction d'entités
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )


# ==================================================================
#  PIED DE PAGE
# ==================================================================
st.markdown("---")
st.markdown(
    """
    <div style="text-align:center; color:#94a3b8; font-size:0.78rem; padding: 0.5rem;">
        CV Debug Tool · Data Team · 2026
        &nbsp;|&nbsp;
        Méthodes : MarkItDown · RapidOCR · LLMWhisperer
    </div>
    """,
    unsafe_allow_html=True,
)

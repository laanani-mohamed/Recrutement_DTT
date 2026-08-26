"""
debug.py
=========
Interface Streamlit — Pipeline CV en 4 sections verticales.
-------------------------------------------------------------
Lancement :
    cd APP/
    streamlit run src/debug.py

Sections :
    1. 📤 Upload du CV     — Upload + aperçu PDF
    2. 📄 Extraction       — Extraction du texte brut
    3. 🔄 Conversion JSON  — LLM → JSON structuré
    4. 🎯 Scoring          — Matching CV / Poste (à venir)
"""

import os
import sys
import time
import json
import base64
import traceback

import streamlit as st

# ------------------------------------------------------------------
# Chemin APP/ pour imports relatifs
# ------------------------------------------------------------------
APP_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if APP_DIR not in sys.path:
    sys.path.insert(0, APP_DIR)

from src.extraction.main_extraction import extract_text, METHODS

RESSOURCE_DIR = os.path.join(APP_DIR, "ressource")


# ==================================================================
#  CONFIG PAGE
# ==================================================================
st.set_page_config(
    page_title="CV Pipeline — Upload · Extract · JSON · Score",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ==================================================================
#  CSS
# ==================================================================
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    :root {
        --bg-main:      #ffffff;
        --bg-card:      #f8fafc;
        --accent-blue:  #2563eb;
        --accent-purple:#7c3aed;
        --accent-green: #059669;
        --accent-amber: #d97706;
        --text-primary: #0f172a;
        --text-muted:   #64748b;
        --border:       #e2e8f0;
    }

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif !important;
        background-color: #ffffff !important;
        color: var(--text-primary) !important;
    }
    .stApp { background-color: #ffffff !important; }

    /* ---- Hero ---- */
    .hero-header {
        text-align: center;
        padding: 1.5rem 1rem 1rem;
    }
    .hero-header h1 {
        font-size: 2rem;
        font-weight: 700;
        background: linear-gradient(90deg, #2563eb, #7c3aed);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 0.3rem;
    }
    .hero-header p { color: var(--text-muted); font-size: 0.92rem; }

    /* ---- Section header ---- */
    .section-header {
        display: flex;
        align-items: center;
        gap: 0.6rem;
        margin: 1.5rem 0 0.75rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid var(--border);
    }
    .section-number {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 32px; height: 32px;
        border-radius: 50%;
        font-size: 0.85rem;
        font-weight: 700;
        color: white;
        flex-shrink: 0;
    }
    .section-title-text {
        font-size: 1.15rem;
        font-weight: 600;
        color: var(--text-primary);
    }
    .bg-blue   { background: var(--accent-blue); }
    .bg-green  { background: var(--accent-green); }
    .bg-purple { background: var(--accent-purple); }
    .bg-amber  { background: var(--accent-amber); }

    /* ---- Metric cards ---- */
    .metric-row { display: flex; gap: 0.75rem; margin: 0.75rem 0; flex-wrap: wrap; }
    .metric-item {
        background: #f1f5f9; border: 1px solid var(--border);
        border-radius: 10px; padding: 0.65rem 1rem;
        flex: 1; min-width: 100px; text-align: center;
    }
    .metric-value { font-size: 1.3rem; font-weight: 700; color: var(--accent-blue); }
    .metric-label {
        font-size: 0.68rem; color: var(--text-muted);
        text-transform: uppercase; letter-spacing: 0.05em; margin-top: 0.15rem;
    }

    /* ---- Result box ---- */
    .result-box {
        background: #f8fafc; border: 1px solid var(--border);
        border-radius: 10px; padding: 1.2rem;
        font-family: 'Courier New', monospace; font-size: 0.8rem;
        line-height: 1.6; color: #1e293b;
        white-space: pre-wrap; max-height: 450px; overflow-y: auto;
    }
    .result-box::-webkit-scrollbar { width: 5px; }
    .result-box::-webkit-scrollbar-track { background: #f1f5f9; }
    .result-box::-webkit-scrollbar-thumb { background: #cbd5e1; border-radius: 3px; }

    /* ---- Placeholder ---- */
    .empty-state {
        text-align: center; padding: 2.5rem 1.5rem; color: #94a3b8;
        border: 2px dashed #e2e8f0; border-radius: 12px; background: #f8fafc;
    }
    .empty-state .icon { font-size: 2.2rem; margin-bottom: 0.6rem; }
    .empty-state .msg { font-size: 0.9rem; font-weight: 500; color: #475569; }
    .empty-state .hint { font-size: 0.78rem; color: #94a3b8; margin-top: 0.5rem; }

    /* ---- Buttons ---- */
    .stButton > button {
        background: linear-gradient(135deg, #2563eb, #4f46e5) !important;
        color: white !important; border: none !important;
        border-radius: 8px !important; font-weight: 600 !important;
        font-family: 'Inter', sans-serif !important;
        font-size: 0.9rem !important; padding: 0.45rem 1.5rem !important;
        transition: all 0.2s ease !important;
        box-shadow: 0 2px 8px rgba(37,99,235,0.25) !important;
    }
    .stButton > button:hover {
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 14px rgba(37,99,235,0.35) !important;
    }

    /* ---- Badges ---- */
    .method-badge {
        display: inline-block; padding: 0.2rem 0.65rem;
        border-radius: 9999px; font-size: 0.7rem;
        font-weight: 600; letter-spacing: 0.04em; text-transform: uppercase;
    }
    .badge-blue   { background: #eff6ff; color: #1d4ed8; border: 1px solid #bfdbfe; }
    .badge-purple { background: #f5f3ff; color: #6d28d9; border: 1px solid #ddd6fe; }
    .badge-green  { background: #ecfdf5; color: #065f46; border: 1px solid #a7f3d0; }

    .stAlert { border-radius: 8px !important; font-family: 'Inter', sans-serif !important; }
    hr { border-color: var(--border) !important; }
    #MainMenu, footer { visibility: hidden; }
    header { background: transparent !important; }
    </style>
    """,
    unsafe_allow_html=True,
)


# ==================================================================
#  UTILITAIRES
# ==================================================================

def section_header(num: int, icon: str, title: str, color: str):
    """Affiche un en-tête de section numéroté."""
    st.markdown(
        f"""<div class="section-header">
            <div class="section-number bg-{color}">{num}</div>
            <div class="section-title-text">{icon} {title}</div>
        </div>""",
        unsafe_allow_html=True,
    )


def empty_state(icon: str, msg: str, hint: str = ""):
    """Affiche un placeholder vide."""
    hint_html = f'<div class="hint">{hint}</div>' if hint else ""
    st.markdown(
        f"""<div class="empty-state">
            <div class="icon">{icon}</div>
            <div class="msg">{msg}</div>
            {hint_html}
        </div>""",
        unsafe_allow_html=True,
    )


methode_labels = {
    "markitdown":   "⚡ MarkItDown — Local, rapide (PDF numérique)",
    "rapidocr":     "🔒 RapidOCR   — Local, hors-ligne (PDF scanné)",
    "llmwhisperer": "☁️ LLMWhisperer — Cloud, haute qualité",
}


# ==================================================================
#  EN-TÊTE
# ==================================================================
st.markdown(
    """
    <div class="hero-header">
        <h1>📋 CV Pipeline</h1>
        <p>Upload → Extraction → JSON → Scoring</p>
    </div>
    """,
    unsafe_allow_html=True,
)
st.markdown("---")


# ==================================================================
#  SECTION 1 — UPLOAD DU CV
# ==================================================================
section_header(1, "📤", "Upload du CV", "blue")

col_upload, col_preview = st.columns([1, 2], gap="large")

with col_upload:
    uploaded_file = st.file_uploader(
        "Déposez votre CV ici (PDF)",
        type=["pdf"],
        help="Le fichier sera utilisé pour toutes les étapes suivantes.",
        key="cv_upload",
    )

    # Alternative : sélectionner un CV existant depuis ressource/
    cvs_locaux = sorted(
        f for f in os.listdir(RESSOURCE_DIR) if f.lower().endswith(".pdf")
    ) if os.path.isdir(RESSOURCE_DIR) else []

    if cvs_locaux:
        st.markdown(
            '<div style="text-align:center;color:#94a3b8;font-size:0.75rem;margin:0.5rem 0;">— ou —</div>',
            unsafe_allow_html=True,
        )
        cv_local = st.selectbox(
            "📂 Choisir un CV existant",
            options=[""] + cvs_locaux,
            format_func=lambda x: "Sélectionner..." if x == "" else x,
            key="cv_local_select",
        )
    else:
        cv_local = ""

# Déterminer le PDF actif (uploaded en priorité)
pdf_bytes = None
pdf_name = None

if uploaded_file:
    pdf_bytes = uploaded_file.read()
    pdf_name = uploaded_file.name
    uploaded_file.seek(0)
elif cv_local:
    path = os.path.join(RESSOURCE_DIR, cv_local)
    with open(path, "rb") as f:
        pdf_bytes = f.read()
    pdf_name = cv_local

# Stocker dans session_state
if pdf_bytes:
    st.session_state["pdf_bytes"] = pdf_bytes
    st.session_state["pdf_name"] = pdf_name

with col_preview:
    if pdf_bytes:
        st.success(f"✅ **{pdf_name}** chargé ({len(pdf_bytes) / 1024:.0f} Ko)")
        # Aperçu PDF inline via iframe base64
        b64 = base64.b64encode(pdf_bytes).decode("utf-8")
        st.markdown(
            f'<iframe src="data:application/pdf;base64,{b64}" '
            f'width="100%" height="500" style="border:1px solid #e2e8f0;border-radius:10px;"></iframe>',
            unsafe_allow_html=True,
        )
    else:
        empty_state("📤", "Aucun CV chargé", "Uploadez un fichier ou sélectionnez-en un à gauche.")


st.markdown("---")


# ==================================================================
#  SECTION 2 — EXTRACTION DU TEXTE
# ==================================================================
section_header(2, "📄", "Extraction du texte", "green")

if not pdf_bytes:
    empty_state("📄", "Chargez d'abord un CV dans la section 1.")
else:
    col_ext_cfg, col_ext_res = st.columns([1, 2], gap="large")

    with col_ext_cfg:
        methode_choisie = st.selectbox(
            "🔧 Méthode d'extraction",
            options=list(methode_labels.keys()),
            format_func=lambda k: methode_labels[k],
            key="methode_extraction",
        )

        # Badge info
        badge_map = {
            "markitdown":   ('<span class="method-badge badge-green">⚡ Local · Rapide</span>',
                             "Idéal pour les **PDFs numériques** (non scannés)."),
            "rapidocr":     ('<span class="method-badge badge-blue">🔒 Local · Hors-ligne</span>',
                             "Idéal pour les **PDFs scannés** via OCR local ONNX."),
            "llmwhisperer": ('<span class="method-badge badge-purple">☁️ Cloud · Haute qualité</span>',
                             "**Meilleure précision** pour les documents complexes."),
        }
        badge, desc = badge_map[methode_choisie]
        st.markdown(badge, unsafe_allow_html=True)
        st.markdown(desc)

        st.markdown("<br>", unsafe_allow_html=True)

        lancer_extract = st.button(
            "🚀 Extraire le texte",
            use_container_width=True,
            key="btn_extract",
        )

    with col_ext_res:
        if lancer_extract:
            # Écrire le PDF temporairement pour les extracteurs qui ont besoin d'un chemin
            import tempfile
            with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
                tmp.write(pdf_bytes)
                tmp_path = tmp.name

            with st.spinner(f"Extraction en cours avec **{methode_choisie}**..."):
                debut = time.perf_counter()
                try:
                    texte_extrait = extract_text(tmp_path, method=methode_choisie)
                    duree = time.perf_counter() - debut

                    # Sauvegarder dans session_state
                    st.session_state["texte_extrait"] = texte_extrait
                    st.session_state["methode_extract"] = methode_choisie

                    # Métriques
                    nb_mots = len(texte_extrait.split())
                    nb_chars = len(texte_extrait)
                    nb_lignes = texte_extrait.count("\n") + 1
                    st.markdown(
                        f"""<div class="metric-row">
                            <div class="metric-item"><div class="metric-value">{nb_mots:,}</div><div class="metric-label">Mots</div></div>
                            <div class="metric-item"><div class="metric-value">{nb_chars:,}</div><div class="metric-label">Caractères</div></div>
                            <div class="metric-item"><div class="metric-value">{nb_lignes:,}</div><div class="metric-label">Lignes</div></div>
                            <div class="metric-item"><div class="metric-value">{duree:.1f}s</div><div class="metric-label">Durée</div></div>
                        </div>""",
                        unsafe_allow_html=True,
                    )
                    st.success(f"✅ Extraction réussie avec **{methode_choisie}**.")
                    st.markdown(f'<div class="result-box">{texte_extrait}</div>', unsafe_allow_html=True)

                    st.download_button(
                        "⬇️ Télécharger le texte (.txt)",
                        data=texte_extrait.encode("utf-8"),
                        file_name=f"{os.path.splitext(pdf_name)[0]}_{methode_choisie}.txt",
                        mime="text/plain",
                        use_container_width=True,
                    )

                except Exception as e:
                    st.error(f"❌ Erreur d'extraction :\n\n```\n{traceback.format_exc()}\n```")

            # Nettoyage fichier temp
            try:
                os.unlink(tmp_path)
            except Exception:
                pass

        elif "texte_extrait" in st.session_state:
            # Afficher le résultat précédent
            texte = st.session_state["texte_extrait"]
            nb_mots = len(texte.split())
            st.info(f"📄 Texte déjà extrait ({nb_mots:,} mots) — Relancez pour ré-extraire.")
            st.markdown(f'<div class="result-box">{texte}</div>', unsafe_allow_html=True)
        else:
            empty_state("📄", "Choisissez une méthode et cliquez sur Extraire.")


st.markdown("---")


# ==================================================================
#  SECTION 3 — CONVERSION JSON (LLM)
# ==================================================================
section_header(3, "🔄", "Conversion JSON (via LLM)", "purple")

texte_dispo = st.session_state.get("texte_extrait", None)

if not texte_dispo:
    empty_state("🔄", "Extrayez d'abord le texte dans la section 2.")
else:
    # Import provider
    try:
        from src.convert_json import convert_cv, PROVIDERS
        providers_ok = True
    except ImportError as e:
        providers_ok = False
        st.error(f"Module src.convert_json introuvable : {e}")

    if providers_ok:
        col_json_cfg, col_json_res = st.columns([1, 2], gap="large")

        with col_json_cfg:
            provider_labels_map = {
                k: f"{v['badge']} {v['label']}" for k, v in PROVIDERS.items()
            }

            provider_choisi = st.selectbox(
                "🤖 Provider LLM",
                options=list(PROVIDERS.keys()),
                format_func=lambda k: provider_labels_map[k],
                key="provider_json",
            )

            info_prov = PROVIDERS[provider_choisi]
            st.caption(info_prov["description"])
            if provider_choisi != "ollama":
                st.markdown(f"🔑 [Clé gratuite]({info_prov['signup_url']})")

            st.markdown("<br>", unsafe_allow_html=True)

            if provider_choisi == "ollama":
                api_key_input = st.text_input(
                    "🦙 Modèle Ollama",
                    value="qwen2.5:14b",
                    help="Le nom du modèle Ollama (ex: qwen2.5:14b, llama3.1). Il doit être installé localement (ollama run model_name).",
                    key="api_key_json",
                )
            else:
                api_key_input = st.text_input(
                    f"🗝️ Clé API — {info_prov['env_key']}",
                    type="password",
                    placeholder=f"Collez votre {info_prov['env_key']} ici...",
                    help="Optionnel si la clé est déjà intégrée dans le code.",
                    key="api_key_json",
                )

            st.markdown("<br>", unsafe_allow_html=True)

            lancer_json = st.button(
                "🔄 Convertir en JSON",
                use_container_width=True,
                key="btn_json",
            )

        with col_json_res:
            if lancer_json:
                with st.spinner(f"🤖 Conversion avec **{PROVIDERS[provider_choisi]['label']}**..."):
                    debut_llm = time.perf_counter()
                    try:
                        cle = api_key_input.strip() if api_key_input else None
                        result_json = convert_cv(
                            texte_dispo,
                            provider=provider_choisi,
                            api_key=cle if cle else None,
                        )
                        duree_llm = time.perf_counter() - debut_llm

                        # Sauvegarder
                        st.session_state["result_json"] = result_json

                        st.success(f"✅ Conversion réussie en {duree_llm:.1f}s")

                        # Cards résumé
                        nom   = result_json.get("nom_complet", "—")
                        titre = result_json.get("titre_poste", "—")
                        lieu  = result_json.get("localisation", "—")
                        email = result_json.get("email", "—")
                        nb_sk = len(result_json.get("competences", []))
                        nb_ex = len(result_json.get("experience", []))

                        st.markdown(
                            f"""<div class="metric-row">
                                <div class="metric-item" style="flex:2;text-align:left;padding:0.7rem 1rem;">
                                    <div style="font-size:1.05rem;font-weight:700;color:#0f172a;">{nom}</div>
                                    <div style="font-size:0.82rem;color:#64748b;margin-top:0.15rem;">{titre}</div>
                                    <div style="font-size:0.72rem;color:#94a3b8;margin-top:0.1rem;">📍 {lieu} · ✉️ {email}</div>
                                </div>
                                <div class="metric-item">
                                    <div class="metric-value">{nb_sk}</div>
                                    <div class="metric-label">Compétences</div>
                                </div>
                                <div class="metric-item">
                                    <div class="metric-value">{nb_ex}</div>
                                    <div class="metric-label">Expériences</div>
                                </div>
                            </div>""",
                            unsafe_allow_html=True,
                        )

                        # Résumé profil
                        resume_profil = result_json.get("resume", "")
                        if resume_profil:
                            st.markdown(
                                f"""<div style="background:#f0f9ff;border-left:3px solid #2563eb;
                                border-radius:0 8px 8px 0;padding:0.7rem 1rem;margin-bottom:0.75rem;
                                font-size:0.85rem;color:#1e40af;font-style:italic;">{resume_profil}</div>""",
                                unsafe_allow_html=True,
                            )

                        # JSON complet
                        json_str = json.dumps(result_json, ensure_ascii=False, indent=2)
                        with st.expander("📋 JSON complet", expanded=True):
                            st.code(json_str, language="json")

                        nom_fich = os.path.splitext(pdf_name or "cv")[0]
                        st.download_button(
                            "⬇️ Télécharger le JSON (.json)",
                            data=json_str.encode("utf-8"),
                            file_name=f"{nom_fich}_{provider_choisi}.json",
                            mime="application/json",
                            use_container_width=True,
                        )

                    except ValueError as e:
                        st.error(f"❌ Clé API manquante :\n\n{e}")
                    except RuntimeError as e:
                        st.error(f"❌ Erreur LLM :\n\n{e}")
                    except Exception as e:
                        st.error(f"❌ Erreur inattendue :\n\n```\n{traceback.format_exc()}\n```")

            elif "result_json" in st.session_state:
                # Afficher le résultat précédent
                rj = st.session_state["result_json"]
                nom = rj.get("nom_complet", "—")
                titre = rj.get("titre_poste", "—")
                st.info(f"🔄 JSON déjà généré pour **{nom}** — *{titre}*")
                json_str = json.dumps(rj, ensure_ascii=False, indent=2)
                with st.expander("📋 JSON complet", expanded=False):
                    st.code(json_str, language="json")
            else:
                empty_state("🔄", "Choisissez un provider LLM et lancez la conversion.")


st.markdown("---")


# ==================================================================
#  SECTION 4 — SCORING (À VENIR)
# ==================================================================
section_header(4, "🎯", "Scoring — Matching CV / Poste", "amber")

result_json_dispo = st.session_state.get("result_json", None)

if not result_json_dispo:
    empty_state(
        "🎯",
        "Convertissez d'abord le CV en JSON (section 3).",
        "Le scoring comparera le profil du candidat avec une description de poste."
    )
else:
    try:
        from src.scoring import score_cv, PROVIDERS as SCORING_PROVIDERS
        scoring_ok = True
    except ImportError as e:
        scoring_ok = False
        st.error(f"Module src.scoring introuvable : {e}")

    if scoring_ok:
        col_score_cfg, col_score_res = st.columns([1, 2], gap="large")

        with col_score_cfg:
            job_desc = st.text_area(
                "📝 Description du poste (Job Description)",
                height=250,
                placeholder="Collez ici l'offre d'emploi complète...",
                key="job_desc_input",
            )

            st.markdown("<br>", unsafe_allow_html=True)

            provider_labels_map = {
                k: f"{v['badge']} {v['label']}" for k, v in SCORING_PROVIDERS.items()
            }

            provider_choisi_score = st.selectbox(
                "🤖 Provider LLM (Scoring)",
                options=list(SCORING_PROVIDERS.keys()),
                format_func=lambda k: provider_labels_map[k],
                key="provider_score",
            )

            info_prov_score = SCORING_PROVIDERS[provider_choisi_score]
            
            if provider_choisi_score == "ollama":
                api_key_score = st.text_input(
                    "🦙 Modèle Ollama (Scoring)",
                    value="qwen2.5:14b",
                    help="Le nom du modèle Ollama (ex: qwen2.5:14b).",
                    key="api_key_score",
                )
            else:
                api_key_score = st.text_input(
                    f"🗝️ Clé API — {info_prov_score['env_key']}",
                    type="password",
                    placeholder=f"Collez votre {info_prov_score['env_key']} ici...",
                    help="Optionnel si la clé est déjà intégrée dans le code.",
                    key="api_key_score",
                )

            st.markdown("<br>", unsafe_allow_html=True)

            lancer_scoring = st.button(
                "🎯 Évaluer le profil",
                disabled=not job_desc.strip(),
                use_container_width=True,
                key="btn_score",
            )

        with col_score_res:
            if lancer_scoring and job_desc.strip():
                with st.spinner(f"🎯 Évaluation avec **{SCORING_PROVIDERS[provider_choisi_score]['label']}**..."):
                    debut_score = time.perf_counter()
                    try:
                        cle_score = api_key_score.strip() if api_key_score else None
                        
                        result_score = score_cv(
                            result_json_dispo,
                            job_desc.strip(),
                            provider=provider_choisi_score,
                            api_key=cle_score if cle_score else None,
                        )
                        duree_score = time.perf_counter() - debut_score
                        
                        st.session_state["result_score"] = result_score
                        st.success(f"✅ Scoring terminé en {duree_score:.1f}s")
                        
                        # Affichage du score global
                        score_global = result_score.get("score_global", 0)
                        
                        # Choix de la couleur selon le score
                        if score_global >= 80:
                            color_score = "green"
                        elif score_global >= 50:
                            color_score = "amber"
                        else:
                            color_score = "red"
                            
                        st.markdown(
                            f'''<div style="text-align: center; margin-bottom: 1.5rem;">
                                <div style="font-size: 3.5rem; font-weight: 800; color: var(--accent-{color_score});">{score_global}%</div>
                                <div style="font-size: 1rem; color: var(--text-muted); font-weight: 600; text-transform: uppercase; letter-spacing: 0.1em;">Score global d'adéquation</div>
                            </div>''',
                            unsafe_allow_html=True
                        )
                        
                        # Détails des scores
                        s_comp = result_score.get("score_competences", 0)
                        s_exp = result_score.get("score_experience", 0)
                        s_form = result_score.get("score_formation", 0)
                        
                        st.markdown(
                            f"""<div class="metric-row">
                                <div class="metric-item"><div class="metric-value" style="font-size: 1.1rem;">{s_comp}%</div><div class="metric-label">Compétences</div></div>
                                <div class="metric-item"><div class="metric-value" style="font-size: 1.1rem;">{s_exp}%</div><div class="metric-label">Expérience</div></div>
                                <div class="metric-item"><div class="metric-value" style="font-size: 1.1rem;">{s_form}%</div><div class="metric-label">Formation</div></div>
                            </div>""",
                            unsafe_allow_html=True,
                        )
                        
                        # Affichage des explications si elles existent
                        has_expl = any(k in result_score for k in ["explication_competences", "explication_experience", "explication_formation"])
                        if has_expl:
                            with st.expander("📊 Explications détaillées des scores", expanded=True):
                                if "explication_competences" in result_score:
                                    st.markdown(f"**Compétences ({s_comp}%) :** {result_score['explication_competences']}")
                                if "explication_experience" in result_score:
                                    st.markdown(f"**Expérience ({s_exp}%) :** {result_score['explication_experience']}")
                                if "explication_formation" in result_score:
                                    st.markdown(f"**Formation ({s_form}%) :** {result_score['explication_formation']}")
                                    
                        # Recommandation
                        reco = result_score.get("recommandation", "")
                        if reco:
                            st.markdown(
                                f"""<div style="background:#fefce8;border-left:3px solid #ca8a04;
                                border-radius:0 8px 8px 0;padding:0.7rem 1rem;margin:1rem 0;
                                font-size:0.9rem;color:#854d0e;"><strong>💡 Évaluation :</strong> {reco}</div>""",
                                unsafe_allow_html=True,
                            )
                            
                        # Points forts et lacunes
                        col_pf, col_lac = st.columns(2)
                        with col_pf:
                            st.markdown("#### ✅ Points forts")
                            pf_list = result_score.get("points_forts", [])
                            for pf in pf_list:
                                st.markdown(f"- {pf}")
                                
                        with col_lac:
                            st.markdown("#### ⚠️ Lacunes")
                            lac_list = result_score.get("lacunes", [])
                            for lac in lac_list:
                                st.markdown(f"- {lac}")

                        # JSON complet
                        import json as _json
                        score_json_str = _json.dumps(result_score, ensure_ascii=False, indent=2)
                        with st.expander("📋 JSON détaillé", expanded=False):
                            st.code(score_json_str, language="json")
                            
                    except Exception as e:
                        st.error(f"❌ Erreur lors du scoring :\n\n```\n{traceback.format_exc()}\n```")
                        
            elif "result_score" in st.session_state:
                # Afficher le résultat précédent
                rs = st.session_state["result_score"]
                st.info(f"🎯 Score déjà calculé : **{rs.get('score_global', 0)}%**")
                
                score_json_str = json.dumps(rs, ensure_ascii=False, indent=2)
                with st.expander("📋 Afficher les détails de l'évaluation", expanded=True):
                    st.code(score_json_str, language="json")
            else:
                if not job_desc.strip():
                    empty_state("📝", "Veuillez coller une description de poste à gauche.")
                else:
                    empty_state("🎯", "Cliquez sur Évaluer le profil pour lancer le matching.")


# ==================================================================
#  PIED DE PAGE
# ==================================================================
st.markdown("---")
st.markdown(
    """
    <div style="text-align:center;color:#94a3b8;font-size:0.75rem;padding:0.5rem;">
        CV Pipeline · Data Team · 2026
        &nbsp;|&nbsp;
        Extraction : MarkItDown · RapidOCR · LLMWhisperer
        &nbsp;|&nbsp;
        JSON : Groq · Gemini · OpenRouter
    </div>
    """,
    unsafe_allow_html=True,
)

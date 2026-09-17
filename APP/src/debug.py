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
        --accent-rose:  #db2777;
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
    .bg-rose   { background: var(--accent-rose); }

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
        <p>Upload → Extraction → JSON → Scoring → Entretien</p>
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
#  SECTION 4 — SCORING (verdict par exigence, score calculé en Python)
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
            st.caption(info_prov_score["description"])

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
                barre_score = st.progress(0.0, text="Démarrage…")

                def _sur_progression_score(etape: str, fraction: float):
                    barre_score.progress(min(max(fraction, 0.0), 1.0), text=etape)

                debut_score = time.perf_counter()
                try:
                    cle_score = api_key_score.strip() if api_key_score else None
                    est_ollama_score = provider_choisi_score == "ollama"

                    result_score = score_cv(
                        result_json_dispo,
                        job_desc.strip(),
                        provider=provider_choisi_score,
                        api_key=None if est_ollama_score else (cle_score or None),
                        model=cle_score if est_ollama_score else None,
                        on_progress=_sur_progression_score,
                    )
                    st.session_state["result_score"] = result_score
                    barre_score.empty()
                    st.success(
                        f"✅ Scoring terminé en {time.perf_counter() - debut_score:.1f}s "
                        f"({len(result_score.verdicts)} exigences évaluées)"
                    )
                except ValueError as e:
                    barre_score.empty()
                    st.error(f"❌ Clé API manquante :\n\n{e}")
                except Exception:
                    barre_score.empty()
                    st.error(f"❌ Erreur lors du scoring :\n\n```\n{traceback.format_exc()}\n```")

            carte_score = st.session_state.get("result_score", None)

            if carte_score is None:
                if not job_desc.strip():
                    empty_state("📝", "Veuillez coller une description de poste à gauche.")
                else:
                    empty_state("🎯", "Cliquez sur Évaluer le profil pour lancer le matching.")
            else:
                if not lancer_scoring:
                    st.info(f"🎯 Score en mémoire — **{carte_score.candidat}** · *{carte_score.poste}*")

                score_global = carte_score.score_global
                color_score = "green" if score_global >= 70 else "amber" if score_global >= 40 else "rose"

                st.markdown(
                    f'''<div style="text-align: center; margin-bottom: 1rem;">
                        <div style="font-size: 3.5rem; font-weight: 800; color: var(--accent-{color_score});">{score_global}%</div>
                        <div style="font-size: 1rem; color: var(--text-muted); font-weight: 600; text-transform: uppercase; letter-spacing: 0.1em;">Score global d'adéquation</div>
                    </div>''',
                    unsafe_allow_html=True
                )

                nb_verdicts = len(carte_score.verdicts)
                nb_satisfait = sum(1 for v in carte_score.verdicts if v.status == "satisfait")
                nb_verifiees = sum(1 for v in carte_score.verdicts if v.evidence_verifiee)
                st.markdown(
                    f"""<div class="metric-row">
                        <div class="metric-item"><div class="metric-value">{nb_satisfait}/{nb_verdicts}</div><div class="metric-label">Exigences satisfaites</div></div>
                        <div class="metric-item"><div class="metric-value">{len(carte_score.job.must_have)}</div><div class="metric-label">Indispensables</div></div>
                        <div class="metric-item"><div class="metric-value">{nb_verifiees}/{nb_verdicts}</div><div class="metric-label">Preuves vérifiées</div></div>
                    </div>""",
                    unsafe_allow_html=True,
                )

                if carte_score.recommandation:
                    st.markdown(
                        f"""<div style="background:#fefce8;border-left:3px solid #ca8a04;
                        border-radius:0 8px 8px 0;padding:0.7rem 1rem;margin:1rem 0;
                        font-size:0.9rem;color:#854d0e;"><strong>💡 Synthèse :</strong> {carte_score.recommandation}
                        <br><span style="font-size:0.75rem;font-style:italic;">Cette synthèse est une aide à la décision, pas une décision — l'embauche reste une décision humaine.</span>
                        </div>""",
                        unsafe_allow_html=True,
                    )

                BADGE_STATUT = {
                    "satisfait": ("✅", "#059669"),
                    "partiel": ("🟡", "#d97706"),
                    "absent": ("🔴", "#dc2626"),
                }
                st.markdown("#### 📋 Détail par exigence")
                for v in carte_score.verdicts:
                    icone, couleur = BADGE_STATUT[v.status]
                    cat_badge = "🔒 indispensable" if v.categorie == "must_have" else "➕ souhaitable"
                    with st.expander(f"{icone} {v.requirement} — {cat_badge}", expanded=(v.status == "absent")):
                        st.markdown(
                            f'<span style="color:{couleur};font-weight:700;text-transform:uppercase;'
                            f'font-size:0.75rem;">{v.status}</span>',
                            unsafe_allow_html=True,
                        )
                        if v.raisonnement:
                            st.caption(v.raisonnement)
                        if v.evidence:
                            badge_preuve = "✅ citation vérifiée" if v.evidence_verifiee else "⚠️ citation non retrouvée dans le CV"
                            st.markdown(f"**Preuve** ({badge_preuve}) : *« {v.evidence} »*")
                        else:
                            st.caption("Aucune preuve trouvée dans le CV.")

                col_pf, col_lac = st.columns(2)
                with col_pf:
                    st.markdown("#### ✅ Points forts")
                    for pf in carte_score.points_forts:
                        st.markdown(f"- {pf}")
                with col_lac:
                    st.markdown("#### ⚠️ Lacunes")
                    for lac in carte_score.lacunes:
                        st.markdown(f"- {lac}")

                with st.expander("📋 JSON détaillé", expanded=False):
                    st.code(carte_score.model_dump_json(indent=2), language="json")

                st.download_button(
                    "⬇️ Télécharger le score (.json)",
                    data=carte_score.model_dump_json(indent=2).encode("utf-8"),
                    file_name=f"score_{carte_score.candidat.replace(' ', '_').lower()}.json",
                    mime="application/json",
                    use_container_width=True,
                )


st.markdown("---")


# ==================================================================
#  SECTION 5 — PRÉPARATION DE L'ENTRETIEN
# ==================================================================
section_header(5, "🎤", "Préparation de l'entretien", "rose")

cv_pour_entretien = st.session_state.get("result_json", None)

if not cv_pour_entretien:
    empty_state(
        "🎤",
        "Convertissez d'abord le CV en JSON (section 3).",
        "Le plan génère des questions ancrées dans le CV, chacune avec son barème de notation.",
    )
else:
    try:
        from src.entretien.contracts import LIBELLES_SECTION, SECTIONS, QuestionPlan
        from src.entretien.question import PROVIDERS as ENTRETIEN_PROVIDERS
        from src.entretien.question import generate_question_plan
        entretien_ok = True
    except ImportError as e:
        entretien_ok = False
        st.error(f"Module src.entretien introuvable : {e}")

    if entretien_ok:
        col_ent_cfg, col_ent_res = st.columns([1, 2], gap="large")

        with col_ent_cfg:
            provider_labels_ent = {
                k: f"{v['badge']} {v['label']}" for k, v in ENTRETIEN_PROVIDERS.items()
            }

            provider_entretien = st.selectbox(
                "🤖 Provider LLM (Entretien)",
                options=list(ENTRETIEN_PROVIDERS.keys()),
                format_func=lambda k: provider_labels_ent[k],
                key="provider_entretien",
            )

            info_ent = ENTRETIEN_PROVIDERS[provider_entretien]
            st.caption(info_ent["description"])

            if provider_entretien == "ollama":
                cle_entretien = st.text_input(
                    "🦙 Modèle Ollama (Entretien)",
                    value="qwen2.5:14b",
                    help="Le plan d'entretien est exigeant : préférez un modèle ≥ 14B.",
                    key="api_key_entretien",
                )
            else:
                cle_entretien = st.text_input(
                    f"🗝️ Clé API — {info_ent['env_key']}",
                    type="password",
                    placeholder=f"Collez votre {info_ent['env_key']} ici...",
                    help=(
                        "Obligatoire : ce module n'embarque aucune clé par défaut, "
                        "contrairement aux sections 3 et 4."
                    ),
                    key="api_key_entretien",
                )

            job_desc_entretien = (st.session_state.get("job_desc_input") or "").strip()
            carte_score_entretien = st.session_state.get("result_score", None)
            # generate_question_plan attend un dict (lacunes/points_forts) : ScoreCard
            # expose ces deux champs comme des listes calculées en Python, pas hallucinées.
            score_entretien = carte_score_entretien.model_dump() if carte_score_entretien else None

            if score_entretien:
                st.success("✅ Scoring détecté — ses lacunes deviennent les points à sonder.")
            else:
                st.info("ℹ️ Sans scoring (section 4), les questions ne cibleront pas les écarts.")

            if not job_desc_entretien:
                st.warning("⚠️ Renseignez la description du poste en section 4.")

            st.markdown("<br>", unsafe_allow_html=True)

            lancer_entretien = st.button(
                "🎤 Générer le plan d'entretien",
                disabled=not job_desc_entretien,
                use_container_width=True,
                key="btn_entretien",
            )

            st.markdown("<br>", unsafe_allow_html=True)

            plan_importe = st.file_uploader(
                "📂 Ou réimporter un plan (.json)",
                type=["json"],
                help="Un plan téléchargé précédemment, pour reprendre sans régénérer.",
                key="upload_plan",
            )
            if plan_importe is not None:
                try:
                    st.session_state["plan_entretien"] = QuestionPlan.model_validate_json(
                        plan_importe.read().decode("utf-8")
                    )
                    st.success("✅ Plan réimporté.")
                except Exception as e:
                    st.error(f"❌ Plan invalide :\n\n{e}")

        with col_ent_res:
            if lancer_entretien and job_desc_entretien:
                barre = st.progress(0.0, text="Démarrage…")

                def _sur_progression(etape: str, fraction: float):
                    barre.progress(min(max(fraction, 0.0), 1.0), text=etape)

                debut_ent = time.perf_counter()
                try:
                    saisie = cle_entretien.strip() if cle_entretien else None
                    est_ollama = provider_entretien == "ollama"

                    plan_genere = generate_question_plan(
                        cv_pour_entretien,
                        job_desc_entretien,
                        provider=provider_entretien,
                        api_key=None if est_ollama else (saisie or None),
                        model=saisie if est_ollama else None,
                        scoring_json=score_entretien,
                        on_progress=_sur_progression,
                    )
                    st.session_state["plan_entretien"] = plan_genere
                    barre.empty()
                    st.success(
                        f"✅ Plan généré en {time.perf_counter() - debut_ent:.1f}s "
                        f"({len(plan_genere.questions)} questions)"
                    )
                except ValueError as e:
                    barre.empty()
                    st.error(f"❌ Clé API manquante :\n\n{e}")
                except Exception:
                    barre.empty()
                    st.error(f"❌ Erreur inattendue :\n\n```\n{traceback.format_exc()}\n```")

            plan = st.session_state.get("plan_entretien", None)

            if plan is None:
                empty_state(
                    "🎤",
                    "Choisissez un provider et lancez la génération.",
                    "Environ 11 questions réparties en 5 sections, barème compris.",
                )
            else:
                if not lancer_entretien:
                    st.info(f"🎤 Plan en mémoire — **{plan.candidat}** · *{plan.poste}*")

                nb_q = len(plan.questions)
                nb_ancres = sum(1 for q in plan.questions if q.ancrage_verifie)
                nb_criteres = sum(len(q.rubric) for q in plan.questions)
                nb_relances = sum(len(q.followups) for q in plan.questions)

                st.markdown(
                    f"""<div class="metric-row">
                        <div class="metric-item"><div class="metric-value">{nb_q}</div><div class="metric-label">Questions</div></div>
                        <div class="metric-item"><div class="metric-value">{nb_ancres}/{nb_q}</div><div class="metric-label">Ancrages vérifiés</div></div>
                        <div class="metric-item"><div class="metric-value">{nb_criteres}</div><div class="metric-label">Critères</div></div>
                        <div class="metric-item"><div class="metric-value">{nb_relances}</div><div class="metric-label">Relances</div></div>
                    </div>""",
                    unsafe_allow_html=True,
                )

                if plan.sections_echouees:
                    tout_echoue = not plan.questions
                    raisons = plan.erreurs or {}
                    causes = set(raisons.values())

                    titre = (
                        "❌ Aucune section n'a abouti."
                        if tout_echoue
                        else f"⚠️ Sections non générées : **{', '.join(plan.sections_echouees)}**"
                    )
                    if not raisons:
                        corps = ""
                    elif len(causes) == 1:
                        corps = f"\n\nCause : {next(iter(causes))}"
                    else:
                        corps = "\n\n" + "\n".join(
                            f"- **{s}** : {r}" for s, r in raisons.items()
                        )

                    (st.error if tout_echoue else st.warning)(titre + corps)

                if nb_ancres < nb_q:
                    st.info(
                        f"ℹ️ {nb_q - nb_ancres} question(s) portent un ancrage introuvable dans le CV "
                        "(badge ⚠️) : à relire avant l'entretien."
                    )

                exigences = plan.brief.job.must_have
                if exigences:
                    st.markdown(
                        f"""<div style="background:#fdf2f8;border-left:3px solid #db2777;
                        border-radius:0 8px 8px 0;padding:0.7rem 1rem;margin:0.75rem 0;
                        font-size:0.85rem;color:#9d174d;"><strong>Exigences ciblées :</strong>
                        {" · ".join(exigences)}</div>""",
                        unsafe_allow_html=True,
                    )

                for section in SECTIONS:
                    lot = plan.par_section(section)
                    if not lot:
                        continue

                    libelle = LIBELLES_SECTION.get(section, section)
                    with st.expander(
                        f"{libelle} — {len(lot)} question(s)",
                        expanded=(section == "technique"),
                    ):
                        for q in lot:
                            badge = "✅" if q.ancrage_verifie else "⚠️"
                            st.markdown(
                                f"`{q.id}` · **{q.target_competency}** · difficulté {q.difficulty}/5"
                            )
                            st.markdown(f"> {q.question}")
                            st.caption(f"{badge} Ancrage CV : {q.ancrage_cv or '—'}")

                            st.markdown("**Barème de notation**")
                            for critere in q.rubric:
                                st.markdown(
                                    f"- `{critere.weight:.2f}` **{critere.criterion}** — {critere.description}"
                                )

                            if q.followups:
                                st.markdown("**Relances**")
                                for relance in q.followups:
                                    st.markdown(f"- {relance}")

                            st.markdown("---")

                nom_plan = (plan.candidat or "candidat").replace(" ", "_").lower()
                st.download_button(
                    "⬇️ Télécharger le plan (.json)",
                    data=plan.model_dump_json(indent=2).encode("utf-8"),
                    file_name=f"plan_entretien_{nom_plan}.json",
                    mime="application/json",
                    use_container_width=True,
                )


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
        &nbsp;|&nbsp;
        Entretien : plan structuré, barème inclus
    </div>
    """,
    unsafe_allow_html=True,
)

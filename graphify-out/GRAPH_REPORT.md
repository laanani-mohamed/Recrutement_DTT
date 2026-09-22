# Graph Report - 2-Recrutement  (2026-09-22)

## Corpus Check
- 51 files · ~66,123 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 352 nodes · 408 edges · 47 communities (31 shown, 16 thin omitted)
- Extraction: 85% EXTRACTED · 15% INFERRED · 0% AMBIGUOUS · INFERRED: 62 edges (avg confidence: 0.8)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `7eacfb8d`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- pipeline.py
- main_extraction.py
- parse_json_block
- pipeline.py
- main_scoring.py
- pipeline.py
- CleApiManquante
- __init__.py
- debug.py
- __init__.py
- 🌿 GreenHire AI — Architecture Technique Complète
- Module 2 — Matching Sémantique CV/Offre
- Module 7 — Entretien LIVE avec IA Générant Questions
- Module 1 — Upload CV + Parsing IA
- Module 3 — Score & Classement Automatique
- Module 8 — Vérification Faciale en Temps Réel
- Sécurité & RGPD
- Module 5 — Entretien Vidéo Asynchrone par IA
- Module 9 — Green Score / ESG
- Module 4 — Résumé IA du CV
- Module 6 — Proctoring (Caméra, Anti-Copier, Anti-IA)
- ollama_provider.py
- ollama_provider.py
- ollama_provider.py
- contracts.py
- Module 10 — Notification Service
- Différenciation Concurrentielle
- prompt_fragments.py
- __init__.py
- __init__.py
- __init__.py
- __init__.py
- __init__.py
- Progression
- AppelLLM
- Progression
- Progression
- BaseModel
- Progression
- AppelLLM
- Progression
- BaseModel
- AppelLLM

## God Nodes (most connected - your core abstractions)
1. `🌿 GreenHire AI — Architecture Technique Complète` - 20 edges
2. `run()` - 13 edges
3. `CleApiManquante` - 12 edges
4. `_evaluer_question()` - 10 edges
5. `run()` - 10 edges
6. `parse_json_block()` - 10 edges
7. `run()` - 9 edges
8. `convert_cv()` - 8 edges
9. `Question` - 8 edges
10. `_generer_section()` - 8 edges

## Surprising Connections (you probably didn't know these)
- `soumettre_reponse()` --calls--> `AnswerRecord`  [INFERRED]
  src/entretien/live/moteur.py → APP/src/entretien/contracts.py
- `_build_brief()` --calls--> `build_job_spec()`  [INFERRED]
  APP/src/entretien/question/pipeline.py → src/shared/job_spec.py
- `_parser_questions()` --calls--> `parse_json_block()`  [INFERRED]
  APP/src/entretien/question/pipeline.py → src/shared/json_utils.py
- `_assembler()` --calls--> `citation_est_verifiee()`  [INFERRED]
  APP/src/entretien/question/pipeline.py → src/shared/sanitize.py
- `run()` --calls--> `sanitize_cv()`  [INFERRED]
  APP/src/entretien/question/pipeline.py → src/shared/sanitize.py

## Import Cycles
- None detected.

## Communities (47 total, 16 thin omitted)

### Community 0 - "pipeline.py"
Cohesion: 0.08
Nodes (34): AnswerRecord, EvaluatedAnswer, InterviewBrief, InterviewEvaluation, InterviewSession, BaseModel, Question, QuestionPlan (+26 more)

### Community 1 - "main_extraction.py"
Cohesion: 0.11
Nodes (15): ExtractionMethod, extract_with_llmwhisperer(), _ocr_page(), llmwhisperer_ocr.py ==================== Méthode d'extraction : LLMWhisperer (AP, Extrait le texte d'une page spécifique d'un PDF via LLMWhisperer.      Args:, Extrait le texte complet d'un PDF via LLMWhisperer, page par page.      Le résul, extract_text(), main_extraction.py =================== Module principal d'orchestration de l'ext (+7 more)

### Community 2 - "parse_json_block"
Cohesion: 0.08
Nodes (22): ProviderName, classify_with_gemini(), gemini_provider.py =================== Provider LLM : Google Gemini Flash 2.0 --, Analyse un texte de CV via l'API Google Gemini et retourne un dict JSON structur, classify_with_groq(), groq_provider.py ================= Provider LLM : Groq (llama-3.3-70b-versatile), Analyse un texte de CV via l'API Groq et retourne un dict JSON structuré.      A, convert_cv() (+14 more)

### Community 3 - "pipeline.py"
Cohesion: 0.05
Nodes (30): call_llm(), Provider Google Gemini pour l'évaluation des réponses d'entretien., Appelle Gemini et retourne le texte brut de la réponse., call_llm(), Provider Groq pour l'évaluation des réponses d'entretien., Appelle Groq et retourne le texte brut de la réponse., call_llm(), Provider OpenRouter pour l'évaluation des réponses d'entretien. (+22 more)

### Community 4 - "main_scoring.py"
Cohesion: 0.09
Nodes (23): Contrats de données pour le scoring CV / fiche de poste.  Principe directeur : l, Verdict du LLM sur UNE exigence du poste, jamais un score global., Évaluation complète d'un CV face à un poste, exigence par exigence., Score 0-100, pondéré must_have > nice_to_have. Calcul Python pur., RequirementVerdict, ScoreCard, main_scoring.py ================ Module principal d'orchestration des providers, Évalue un CV (JSON) face à une fiche de poste, exigence par exigence.      Args: (+15 more)

### Community 5 - "pipeline.py"
Cohesion: 0.11
Nodes (24): CriterionVerdict, Verdict du LLM sur UN critère du barème d'une question, jamais un score., _avancer(), _completer_criteres_manquants(), _evaluer_avec_isolation(), _evaluer_question(), _maintenant(), _parser_criteres() (+16 more)

### Community 6 - "CleApiManquante"
Cohesion: 0.15
Nodes (17): demarrer(), _duree_secondes(), formater_duree(), formater_horodatage(), _maintenant(), question_courante(), Moteur de conduite de l'entretien : déroule le QuestionPlan, ne réfléchit jamais, Enregistre la réponse du candidat, décide relance ou avance le curseur.      Une (+9 more)

### Community 7 - "__init__.py"
Cohesion: 0.20
Nodes (13): citation_est_verifiee(), _degager(), _nettoyer(), Neutralisation des contenus non fiables (CV, fiche de poste) avant envoi à un LL, Retire caractères invisibles et balises de délimitation, normalise, tronque., Reconstruit un CV réduit aux champs utiles à la rédaction de questions ou au sco, Assainit un texte libre (fiche de poste) sans le tronquer au format court., Ensemble de mots normalisés (minuscules, sans accent, >2 lettres).      Public : (+5 more)

### Community 8 - "debug.py"
Cohesion: 0.20
Nodes (10): Any, build_job_spec(), Structuration d'une fiche de poste en exigences (JobSpec).  Étape commune à la p, Structure une fiche de poste assainie en JobSpec.      Ne lève que CleApiManquan, user_brief(), extract_json_block(), parse_json_block(), Extraction d'un bloc JSON dans une réponse LLM non contrainte. (+2 more)

### Community 9 - "__init__.py"
Cohesion: 0.22
Nodes (5): empty_state(), debug.py ========= Interface Streamlit — Pipeline CV en 4 sections verticales. -, Affiche un en-tête de section numéroté., Affiche un placeholder vide., section_header()

### Community 10 - "🌿 GreenHire AI — Architecture Technique Complète"
Cohesion: 0.22
Nodes (8): 1. Vision du Projet, 2. Stack Technique Global, 3. Architecture en 5 Couches, Flux de Données Typique, 🌿 GreenHire AI — Architecture Technique Complète, Planning de Réalisation (Méthodologie Agile), Récapitulatif des Verdicts, 📋 Table des Matières

### Community 11 - "Module 2 — Matching Sémantique CV/Offre"
Cohesion: 0.29
Nodes (7): Approche technique, Module 2 — Matching Sémantique CV/Offre, Objectif, Score composite pondéré, Seuils configurables, Technologies, Verdict

### Community 12 - "Module 7 — Entretien LIVE avec IA Générant Questions"
Cohesion: 0.29
Nodes (7): Architecture, Défi principal : La latence, Module 7 — Entretien LIVE avec IA Générant Questions, Objectif *(Cœur du projet)*, Solutions, Technologies, Verdict

### Community 13 - "Module 1 — Upload CV + Parsing IA"
Cohesion: 0.29
Nodes (7): Export Excel (multi-onglets), Flux de données, Module 1 — Upload CV + Parsing IA, Objectif, Schema JSON de sortie (extraction), Technologies, Verdict

### Community 14 - "Module 3 — Score & Classement Automatique"
Cohesion: 0.33
Nodes (6): Classement, Explicabilité (XAI — Explainable AI), Module 3 — Score & Classement Automatique, Objectif, Technologies, Verdict

### Community 15 - "Module 8 — Vérification Faciale en Temps Réel"
Cohesion: 0.40
Nodes (5): Approche, Module 8 — Vérification Faciale en Temps Réel, Objectif, RGPD — Données biométriques, Verdict

### Community 16 - "Sécurité & RGPD"
Cohesion: 0.40
Nodes (5): Audit de biais IA, Authentification & Autorisation, Protection des données, RGPD — Points clés, Sécurité & RGPD

### Community 17 - "Module 5 — Entretien Vidéo Asynchrone par IA"
Cohesion: 0.40
Nodes (5): Flux, Module 5 — Entretien Vidéo Asynchrone par IA, Objectif, Technologies, ⚠️ Verdict

### Community 18 - "Module 9 — Green Score / ESG"
Cohesion: 0.40
Nodes (5): Fonctionnalités, Formule de calcul, Module 9 — Green Score / ESG, Objectif *(Votre arme secrète)*, Verdict

### Community 19 - "Module 4 — Résumé IA du CV"
Cohesion: 0.40
Nodes (5): Module 4 — Résumé IA du CV, Objectif, Prompt structuré (LangChain), Sortie, Verdict

### Community 20 - "Module 6 — Proctoring (Caméra, Anti-Copier, Anti-IA)"
Cohesion: 0.40
Nodes (5): Module 6 — Proctoring (Caméra, Anti-Copier, Anti-IA), Objectif, Règle d'or, Tableau des détections, Verdict

### Community 21 - "ollama_provider.py"
Cohesion: 0.50
Nodes (3): call_llm(), Provider Ollama (local) pour l'évaluation des réponses d'entretien., Appelle Ollama en local et retourne le texte brut de la réponse.      api_key es

### Community 22 - "ollama_provider.py"
Cohesion: 0.50
Nodes (3): call_llm(), Provider Ollama (local) pour la génération du plan d'entretien., Appelle Ollama en local et retourne le texte brut de la réponse.      api_key es

### Community 23 - "ollama_provider.py"
Cohesion: 0.50
Nodes (3): call_llm(), Provider Ollama (local) pour le scoring CV / fiche de poste., Appelle Ollama en local et retourne le texte brut de la réponse.      api_key es

### Community 24 - "contracts.py"
Cohesion: 0.50
Nodes (3): JobSpec, Contrats de données partagés par les modules entretien et scoring., Fiche de poste structurée en exigences.

### Community 25 - "Module 10 — Notification Service"
Cohesion: 0.50
Nodes (4): Canaux, Module 10 — Notification Service, Objectif, Verdict

### Community 26 - "Différenciation Concurrentielle"
Cohesion: 0.50
Nodes (4): Ce que personne ne fait (votre territoire), Ce qui existe déjà (saturé), Différenciation Concurrentielle, Pitch final ajusté

## Knowledge Gaps
- **60 isolated node(s):** `📋 Table des Matières`, `1. Vision du Projet`, `2. Stack Technique Global`, `3. Architecture en 5 Couches`, `Objectif` (+55 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **16 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `CleApiManquante` connect `pipeline.py` to `parse_json_block`?**
  _High betweenness centrality (0.129) - this node is a cross-community bridge._
- **Why does `run()` connect `main_scoring.py` to `debug.py`, `__init__.py`?**
  _High betweenness centrality (0.072) - this node is a cross-community bridge._
- **Why does `_parser_questions()` connect `pipeline.py` to `debug.py`, `parse_json_block`?**
  _High betweenness centrality (0.067) - this node is a cross-community bridge._
- **Are the 13 inferred relationships involving `ValueError` (e.g. with `_parser_questions()` and `classify_with_gemini()`) actually correct?**
  _`ValueError` has 13 INFERRED edges - model-reasoned connections that need verification._
- **Are the 7 inferred relationships involving `run()` (e.g. with `score_cv()` and `system_verdict()`) actually correct?**
  _`run()` has 7 INFERRED edges - model-reasoned connections that need verification._
- **Are the 9 inferred relationships involving `CleApiManquante` (e.g. with `call_llm()` and `call_llm()`) actually correct?**
  _`CleApiManquante` has 9 INFERRED edges - model-reasoned connections that need verification._
- **Are the 5 inferred relationships involving `_evaluer_question()` (e.g. with `criteres_avec_id()` and `system_evaluation_question()`) actually correct?**
  _`_evaluer_question()` has 5 INFERRED edges - model-reasoned connections that need verification._
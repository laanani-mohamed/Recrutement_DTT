# Graph Report - APP  (2026-09-21)

## Corpus Check
- 49 files · ~18,047 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 278 nodes · 577 edges · 10 communities (9 shown, 1 thin omitted)
- Extraction: 98% EXTRACTED · 2% INFERRED · 0% AMBIGUOUS · INFERRED: 14 edges (avg confidence: 0.78)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `38d5c4f7`
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
- debug.py
- __init__.py

## God Nodes (most connected - your core abstractions)
1. `CleApiManquante` - 25 edges
2. `Question` - 20 edges
3. `run()` - 17 edges
4. `InterviewSession` - 16 edges
5. `parse_json_block()` - 14 edges
6. `QuestionPlan` - 13 edges
7. `_evaluer_question()` - 13 edges
8. `run()` - 13 edges
9. `run()` - 12 edges
10. `convert_cv()` - 10 edges

## Surprising Connections (you probably didn't know these)
- `question_courante()` --references--> `Question`  [EXTRACTED]
  APP/src/entretien/live/moteur.py → APP/src/entretien/contracts.py
- `reponse_semble_superficielle()` --references--> `Question`  [EXTRACTED]
  APP/src/entretien/live/moteur.py → APP/src/entretien/contracts.py
- `_generer_section()` --references--> `Question`  [EXTRACTED]
  APP/src/entretien/question/pipeline.py → APP/src/entretien/contracts.py
- `_parser_questions()` --references--> `Question`  [EXTRACTED]
  APP/src/entretien/question/pipeline.py → APP/src/entretien/contracts.py
- `demarrer()` --references--> `QuestionPlan`  [EXTRACTED]
  APP/src/entretien/live/moteur.py → APP/src/entretien/contracts.py

## Import Cycles
- None detected.

## Communities (10 total, 1 thin omitted)

### Community 0 - "pipeline.py"
Cohesion: 0.12
Nodes (25): InterviewBrief, QuestionPlan, Ce que le planificateur doit savoir avant de rédiger les questions., Plan d'entretien complet, prêt à être déroulé sans nouvel appel LLM., Phase de préparation : génération du plan d'entretien à partir du CV et du poste, generate_question_plan(), Progression, Construit un plan d'entretien structuré à partir du CV et de la fiche de poste. (+17 more)

### Community 1 - "main_extraction.py"
Cohesion: 0.14
Nodes (15): ExtractionMethod, extract_with_llmwhisperer(), _ocr_page(), llmwhisperer_ocr.py ==================== Méthode d'extraction : LLMWhisperer (AP, Extrait le texte d'une page spécifique d'un PDF via LLMWhisperer.      Args:, Extrait le texte complet d'un PDF via LLMWhisperer, page par page.      Le résul, extract_text(), main_extraction.py =================== Module principal d'orchestration de l'ext (+7 more)

### Community 2 - "parse_json_block"
Cohesion: 0.10
Nodes (24): Any, ProviderName, classify_with_gemini(), gemini_provider.py =================== Provider LLM : Google Gemini Flash 2.0 --, Analyse un texte de CV via l'API Google Gemini et retourne un dict JSON structur, classify_with_groq(), groq_provider.py ================= Provider LLM : Groq (llama-3.3-70b-versatile), Analyse un texte de CV via l'API Groq et retourne un dict JSON structuré.      A (+16 more)

### Community 3 - "pipeline.py"
Cohesion: 0.08
Nodes (46): CriterionVerdict, EvaluatedAnswer, InterviewEvaluation, InterviewSession, BaseModel, Question, Contrats de données partagés par les phases préparation, entretien et évaluation, État de la conduite d'un entretien : progression dans le plan + réponses collect (+38 more)

### Community 4 - "main_scoring.py"
Cohesion: 0.13
Nodes (14): BaseModel, Contrats de données pour le scoring CV / fiche de poste.  Principe directeur : l, Verdict du LLM sur UNE exigence du poste, jamais un score global., Évaluation complète d'un CV face à un poste, exigence par exigence., Score 0-100, pondéré must_have > nice_to_have. Calcul Python pur., RequirementVerdict, ScoreCard, Progression (+6 more)

### Community 5 - "pipeline.py"
Cohesion: 0.08
Nodes (36): _avancer(), _completer_verdicts_manquants(), _exigences_avec_id(), AppelLLM, Progression, Pipeline de scoring : JobSpec → verdict par exigence → score calculé en Python., Produit une ScoreCard. Ne lève que CleApiManquante (erreur de configuration)., Numérote les exigences : un requirement_id explicite évite au modèle de devoir (+28 more)

### Community 6 - "CleApiManquante"
Cohesion: 0.07
Nodes (34): call_llm(), Provider Google Gemini pour l'évaluation des réponses d'entretien., Appelle Gemini et retourne le texte brut de la réponse., call_llm(), Provider Groq pour l'évaluation des réponses d'entretien., Appelle Groq et retourne le texte brut de la réponse., call_llm(), Provider OpenRouter pour l'évaluation des réponses d'entretien. (+26 more)

### Community 8 - "debug.py"
Cohesion: 0.10
Nodes (27): empty_state(), debug.py ========= Interface Streamlit — Pipeline CV en 4 sections verticales. -, Affiche un en-tête de section numéroté., Affiche un placeholder vide., section_header(), AnswerRecord, Une réponse du candidat, horodatée — à une question principale ou à une relance., Phase live : conduite de l'entretien. Déroule le QuestionPlan, ne réfléchit jama (+19 more)

## Knowledge Gaps
- **1 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `CleApiManquante` connect `CleApiManquante` to `pipeline.py`, `parse_json_block`, `pipeline.py`, `pipeline.py`?**
  _High betweenness centrality (0.164) - this node is a cross-community bridge._
- **Why does `score_cv()` connect `main_scoring.py` to `debug.py`, `parse_json_block`, `pipeline.py`?**
  _High betweenness centrality (0.067) - this node is a cross-community bridge._
- **Why does `extract_text()` connect `main_extraction.py` to `debug.py`, `parse_json_block`?**
  _High betweenness centrality (0.067) - this node is a cross-community bridge._
- **Are the 13 inferred relationships involving `ValueError` (e.g. with `classify_with_gemini()` and `classify_with_groq()`) actually correct?**
  _`ValueError` has 13 INFERRED edges - model-reasoned connections that need verification._
- **What connects `gemini_provider.py =================== Provider LLM : Google Gemini Flash 2.0 --`, `Analyse un texte de CV via l'API Google Gemini et retourne un dict JSON structur`, `groq_provider.py ================= Provider LLM : Groq (llama-3.3-70b-versatile)` to the rest of the system?**
  _115 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `pipeline.py` be split into smaller, more focused modules?**
  _Cohesion score 0.11822660098522167 - nodes in this community are weakly interconnected._
- **Should `main_extraction.py` be split into smaller, more focused modules?**
  _Cohesion score 0.14210526315789473 - nodes in this community are weakly interconnected._
# Graph Report - APP  (2026-09-15)

## Corpus Check
- Corpus is ~11,850 words - fits in a single context window. You may not need a graph.

## Summary
- 154 nodes · 278 edges · 8 communities
- Extraction: 95% EXTRACTED · 5% INFERRED · 0% AMBIGUOUS · INFERRED: 14 edges (avg confidence: 0.78)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- Contrats Pydantic Entretien
- Interface Streamlit & OCR
- Conversion CV vers JSON
- Pipeline Génération Questions
- Scoring CV / Poste
- Utilitaires JSON & API Entretien
- Providers LLM Entretien

## God Nodes (most connected - your core abstractions)
1. `run()` - 12 edges
2. `QuestionPlan` - 11 edges
3. `convert_cv()` - 10 edges
4. `InterviewBrief` - 10 edges
5. `CleApiManquante` - 10 edges
6. `score_cv()` - 10 edges
7. `Question` - 9 edges
8. `_generer_section()` - 9 edges
9. `extract_text()` - 9 edges
10. `parse_json_block()` - 8 edges

## Surprising Connections (you probably didn't know these)
- `_parser_questions()` --references--> `Question`  [EXTRACTED]
  src/entretien/question/pipeline.py → src/entretien/contracts.py
- `_assembler()` --references--> `InterviewBrief`  [EXTRACTED]
  src/entretien/question/pipeline.py → src/entretien/contracts.py
- `generate_question_plan()` --references--> `QuestionPlan`  [EXTRACTED]
  src/entretien/question/main_question.py → src/entretien/contracts.py
- `_build_brief()` --calls--> `parse_json_block()`  [EXTRACTED]
  src/entretien/question/pipeline.py → src/entretien/json_utils.py
- `generate_question_plan()` --calls--> `run()`  [EXTRACTED]
  src/entretien/question/main_question.py → src/entretien/question/pipeline.py

## Import Cycles
- None detected.

## Communities (8 total, 0 thin omitted)

### Community 0 - "Contrats Pydantic Entretien"
Cohesion: 0.13
Nodes (24): AppelLLM, BaseModel, InterviewBrief, JobSpec, Question, Contrats de données partagés par les phases préparation, entretien et évaluation, Un critère observable du barème de notation d'une question., Une question d'entretien, indissociable de son barème et de ses relances. (+16 more)

### Community 1 - "Interface Streamlit & OCR"
Cohesion: 0.10
Nodes (20): ExtractionMethod, empty_state(), debug.py ========= Interface Streamlit — Pipeline CV en 4 sections verticales. -, Affiche un en-tête de section numéroté., Affiche un placeholder vide., section_header(), extract_with_llmwhisperer(), _ocr_page() (+12 more)

### Community 2 - "Conversion CV vers JSON"
Cohesion: 0.14
Nodes (15): classify_with_gemini(), gemini_provider.py =================== Provider LLM : Google Gemini Flash 2.0 --, Analyse un texte de CV via l'API Google Gemini et retourne un dict JSON structur, classify_with_groq(), groq_provider.py ================= Provider LLM : Groq (llama-3.3-70b-versatile), Analyse un texte de CV via l'API Groq et retourne un dict JSON structuré.      A, convert_cv(), ProviderName (+7 more)

### Community 3 - "Pipeline Génération Questions"
Cohesion: 0.15
Nodes (19): QuestionPlan, Plan d'entretien complet, prêt à être déroulé sans nouvel appel LLM., _assembler(), _avancer(), Progression, Produit un plan d'entretien.      Une section ratée est signalée dans le plan, j, run(), ancrage_est_verifie() (+11 more)

### Community 4 - "Scoring CV / Poste"
Cohesion: 0.18
Nodes (13): clean_json_response(), score_with_gemini(), clean_json_response(), score_with_groq(), ProviderName, main_scoring.py ================ Module principal d'orchestration des providers, Analyse un CV (format JSON) et une description de poste avec le provider LLM spé, score_cv() (+5 more)

### Community 5 - "Utilitaires JSON & API Entretien"
Cohesion: 0.12
Nodes (15): Any, extract_json_block(), parse_json_block(), Extraction d'un bloc JSON dans une réponse LLM non contrainte., Isole le premier objet ou tableau JSON complet du texte.      Tolère un préambul, Parse le premier bloc JSON d'une réponse LLM., Phase de préparation : génération du plan d'entretien à partir du CV et du poste, generate_question_plan() (+7 more)

### Community 6 - "Providers LLM Entretien"
Cohesion: 0.18
Nodes (13): CleApiManquante, Erreurs du domaine entretien., Aucune clé API utilisable pour ce provider.      C'est une erreur de configurati, call_llm(), Provider Google Gemini pour la génération du plan d'entretien., Appelle Gemini et retourne le texte brut de la réponse., call_llm(), Provider Groq pour la génération du plan d'entretien. (+5 more)

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `CleApiManquante` connect `Providers LLM Entretien` to `Contrats Pydantic Entretien`, `Utilitaires JSON & API Entretien`?**
  _High betweenness centrality (0.124) - this node is a cross-community bridge._
- **Why does `extract_text()` connect `Interface Streamlit & OCR` to `Utilitaires JSON & API Entretien`?**
  _High betweenness centrality (0.124) - this node is a cross-community bridge._
- **Why does `convert_cv()` connect `Conversion CV vers JSON` to `Interface Streamlit & OCR`, `Utilitaires JSON & API Entretien`?**
  _High betweenness centrality (0.102) - this node is a cross-community bridge._
- **Are the 13 inferred relationships involving `ValueError` (e.g. with `classify_with_gemini()` and `classify_with_groq()`) actually correct?**
  _`ValueError` has 13 INFERRED edges - model-reasoned connections that need verification._
- **Are the 2 inferred relationships involving `convert_cv()` (e.g. with `main_convert_json.py` and `ValueError`) actually correct?**
  _`convert_cv()` has 2 INFERRED edges - model-reasoned connections that need verification._
- **What connects `gemini_provider.py =================== Provider LLM : Google Gemini Flash 2.0 --`, `Analyse un texte de CV via l'API Google Gemini et retourne un dict JSON structur`, `groq_provider.py ================= Provider LLM : Groq (llama-3.3-70b-versatile)` to the rest of the system?**
  _57 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Contrats Pydantic Entretien` be split into smaller, more focused modules?**
  _Cohesion score 0.1310344827586207 - nodes in this community are weakly interconnected._
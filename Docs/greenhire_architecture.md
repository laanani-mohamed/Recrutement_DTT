# 🌿 GreenHire AI — Architecture Technique Complète

> **Plateforme de Recrutement Intelligent & Durable**
> 
> Projet de fin d'études / Stage — Juillet 2026

---

## 📋 Table des Matières

1. [Vision du Projet](#1-vision-du-projet)
2. [Stack Technique Global](#2-stack-technique-global)
3. [Architecture en 5 Couches](#3-architecture-en-5-couches)
4. [Module 1 — Upload CV + Parsing IA](#module-1--upload-cv--parsing-ia)
5. [Module 2 — Matching Sémantique](#module-2--matching-sémantique-cvoffre)
6. [Module 3 — Score & Classement](#module-3--score--classement-automatique)
7. [Module 4 — Résumé IA du CV](#module-4--résumé-ia-du-cv)
8. [Module 5 — Entretien Vidéo Asynchrone](#module-5--entretien-vidéo-asynchrone-par-ia)
9. [Module 6 — Proctoring](#module-6--proctoring-caméra-anti-copier-anti-ia)
10. [Module 7 — Entretien LIVE avec IA](#module-7--entretien-live-avec-ia-générant-questions)
11. [Module 8 — Vérification Faciale Temps Réel](#module-8--vérification-faciale-en-temps-réel)
12. [Module 9 — Green Score / ESG](#module-9--green-score--esg)
13. [Module 10 — Notification](#module-10--notification-service)
14. [Flux de Données Typique](#flux-de-données-typique)
15. [Sécurité & RGPD](#sécurité--rgpd)
16. [Planning de Réalisation](#planning-de-réalisation)
17. [Différenciation Concurrentielle](#différenciation-concurrentielle)

---

## 1. Vision du Projet

**GreenHire AI** est une plateforme de recrutement nouvelle génération qui révolutionne le processus RH en combinant intelligence artificielle, sécurité biométrique et responsabilité environnementale. Le projet vise à dématérialiser totalement le recrutement — éliminant le papier, les déplacements physiques et les biais humains — tout en garantissant l'authenticité des candidats grâce à une vérification faciale en temps réel et une détection de fraude comportementale.

> *« Le seul ATS IA au monde qui mesure et certifie l'impact carbone de chaque recrutement dématérialisé. »*

---

## 2. Stack Technique Global

| Couche | Technologie |
|--------|-------------|
| **Frontend** | React 19 + Next.js 15 + Tailwind CSS |
| **Backend** | FastAPI (Python) + Node.js (microservices temps réel) |
| **Base de données** | PostgreSQL 16 (relationnel) + Pinecone/Milvus (vecteurs) |
| **Cache & Queue** | Redis 7 |
| **LLM / NLP** | OpenAI GPT-4o / Claude 3.5 + LangChain |
| **Embeddings** | OpenAI `text-embedding-3-large` ou `sentence-transformers` |
| **Parsing CV** | PyPDF2 / pdfplumber + Tesseract OCR |
| **Vidéo Live** | WebRTC (PeerJS) + Socket.io |
| **Facial Recognition** | FaceAPI.js (browser) + AWS Rekognition (API) |
| **Speech-to-Text** | OpenAI Whisper |
| **Stockage fichiers** | MinIO / AWS S3 |
| **Monitoring** | Prometheus + Grafana + ELK Stack |
| **DevOps** | Docker + Docker Compose + Kubernetes |
| **CI/CD** | GitHub Actions |
| **Auth** | Keycloak (OIDC) |

---

## 3. Architecture en 5 Couches

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  LAYER 1 — FRONTEND (React 19 + Next.js 15 + Tailwind)                     │
│  Upload CV │ Fiche Poste │ Dashboard RH │ Live Interview │ Green Score      │
├─────────────────────────────────────────────────────────────────────────────┤
│  LAYER 2 — API GATEWAY & AUTH (FastAPI + Keycloak)                         │
│  JWT Auth │ RBAC │ Rate Limiting │ Request Logging │ OpenAPI/Swagger       │
├─────────────────────────────────────────────────────────────────────────────┤
│  LAYER 3 — BACKEND MICROSERVICES (10 modules)                              │
│  M1:CV │ M2:Matching │ M3:Ranking │ M4:ResumeAI │ M5:Async │ M6:Proctoring │
│  M7:LiveAI │ M8:FaceVerify │ M9:GreenESG │ M10:Notification               │
├─────────────────────────────────────────────────────────────────────────────┤
│  LAYER 4 — DATA & STORAGE                                                  │
│  PostgreSQL │ Pinecone/Milvus │ MinIO/S3 │ Redis │ Elasticsearch │ Excel   │
├─────────────────────────────────────────────────────────────────────────────┤
│  LAYER 5 — INFRA & DEVOPS                                                  │
│  Docker │ Kubernetes │ GitHub Actions │ Prometheus │ AWS/Azure │ Vault     │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Module 1 — Upload CV + Parsing IA

### Objectif
Permettre au candidat d'uploader son CV (PDF, DOCX, ou image scannée) et en extraire automatiquement les informations structurées.

### Flux de données
```
Upload (PDF/DOCX/Image) → Parsing → Extraction structurée (JSON) → Export Excel
```

### Technologies
- **Extraction texte natif** : `PyPDF2`, `pdfplumber`
- **OCR (PDF scannés)** : `Tesseract` (local) ou `Azure Document Intelligence` (cloud)
- **Extraction structurée** : LLM avec **function calling** (schema JSON strict)
- **Export Excel** : `openpyxl` ou `xlsxwriter`

### Schema JSON de sortie (extraction)
```json
{
  "nom": "Jean Dupont",
  "email": "jean.dupont@email.com",
  "telephone": "+33 6 12 34 56 78",
  "competences": ["Python", "Django", "React", "PostgreSQL"],
  "experiences": [
    {
      "poste": "Développeur Full-Stack",
      "entreprise": "TechCorp",
      "duree_mois": 24,
      "description": "Développement d'applications web..."
    }
  ],
  "formation": [
    {
      "diplome": "Master Informatique",
      "ecole": "Université Paris-Saclay",
      "annee": 2024
    }
  ],
  "langues": ["Français (C2)", "Anglais (B2)"]
}
```

### Export Excel (multi-onglets)
| Onglet | Contenu |
|--------|---------|
| **Candidats** | Infos générales, contact, date d'upload |
| **Compétences** | Matrice candidat × compétence (Oui/Non) |
| **Expériences** | Poste, entreprise, durée, description |
| **Matching** | Scores par offre, classement |

### Verdict
✅ **DO IT** — Faisable et rapide. C'est la fondation du projet.

---

## Module 2 — Matching Sémantique CV/Offre

### Objectif
Comparer sémantiquement le contenu d'un CV avec la description d'un poste et retourner un score de correspondance.

### Approche technique
```
CV (texte) ──embed──→ Vector [1536-dim]
                           ↓
                    FAISS Index (top-k search)
                           ↓
Offre (texte) ──embed──→ Vector [1536-dim]
                           ↓
                    Cosine Similarity
                           ↓
                    Score composite pondéré
```

### Technologies
- **Embeddings** : `OpenAI text-embedding-3-large` (1536-dim) ou `sentence-transformers/all-MiniLM-L6-v2` (gratuit, local)
- **Vector DB** : `Pinecone` (cloud) ou `Milvus` (self-hosted) ou `pgvector` (PostgreSQL extension)
- **Similarity** : Cosine similarity ou Euclidean distance

### Score composite pondéré
```
Score_final = (matching_competences * 0.40)
            + (experience_pertinente * 0.30)
            + (formation * 0.15)
            + (soft_skills * 0.10)
            + (localisation * 0.05)
```

### Seuils configurables
| Seuil | Couleur | Action |
|-------|---------|--------|
| > 70% | 🟢 Vert | Candidat prioritaire |
| 50-70% | 🟠 Orange | À étudier |
| < 50% | 🔴 Rouge | Non retenu |

### Verdict
✅ **DO IT** — Mature et standard. Utiliser `text-embedding-3-large` pour la qualité.

---

## Module 3 — Score & Classement Automatique

### Objectif
Classer automatiquement les candidats par pertinence et fournir une explication du score.

### Classement
- Tri décroissant par `Score_final`
- Pagination (20 candidats par page)
- Filtres dynamiques (seuil minimum, compétence requise, etc.)

### Explicabilité (XAI — Explainable AI)
Chaque score est justifié par un résumé généré :
> *"Score 82% : ✅ Python (3 ans d'expérience), ✅ Django (2 ans), ❌ AWS (manquant), ✅ Anglais B2"*

### Technologies
- **Règles métier** : Poids configurables par le RH
- **XAI** : `SHAP` ou templates LLM pour la justification

### Verdict
✅ **DO IT** — Standard, mais **obligatoire** d'ajouter l'explicabilité pour éviter les biais.

---

## Module 4 — Résumé IA du CV

### Objectif
Générer un résumé exécutif du CV adapté au poste visé.

### Prompt structuré (LangChain)
```
Résume ce CV pour le poste de [TITRE_POSTE]. Format JSON :
{
  "forces": ["3 bullets de forces clés"],
  "faiblesses": ["2 bullets de gaps ou manques"],
  "recommandation": "Oui/Non avec justification",
  "score_pertinence": "0-100"
}
Contrainte : ne cite que des faits présents dans le CV. Aucune supposition.
```

### Sortie
- JSON structuré stocké en base
- Affichage dans le dashboard RH sous forme de carte résumée

### Verdict
✅ **DO IT** — Trivial avec un LLM moderne. Attention aux hallucinations (prompt strict).

---

## Module 5 — Entretien Vidéo Asynchrone par IA

### Objectif
Générer des questions personnalisées selon le CV et l'offre, enregistrer les réponses vidéo du candidat, puis les analyser.

### Flux
```
CV + Offre → LLM génère 5 questions → Candidat enregistre réponses (vidéo)
→ Upload S3 → Whisper transcription → LLM analyse réponse → Score
```

### Technologies
- **Questions IA** : GPT-4o avec contexte CV + Offre
- **Enregistrement** : `MediaRecorder API` (browser)
- **Stockage vidéo** : `MinIO` / `AWS S3`
- **Transcription** : `OpenAI Whisper`
- **Analyse** : LLM évalue pertinence, clarté, profondeur

### ⚠️ Verdict
⚠️ **OPTIONNEL** — Si vous implémentez le Module 7 (Live), l'asynchrone devient redondant. **Concentrez-vous sur le LIVE.**

---

## Module 6 — Proctoring (Caméra, Anti-Copier, Anti-IA)

### Objectif
Détecter et prévenir la fraude pendant l'entretien (copier-coller, changement d'onglet, assistance IA externe).

### Tableau des détections
| Détection | Technique | Tolérance |
|-----------|-----------|-----------|
| **Copier-coller** | `document.addEventListener('paste', ...)` + `beforeinput` | 3 strikes |
| **Changement d'onglet** | `document.visibilitychange` + `window.blur` | 3 strikes |
| **Keystroke dynamics** | Analyse vitesse de frappe (WPM + régularité) | Anomalie = flag |
| **Multi-écran** | `window.screen` + `screen.width` (heuristique) | Alert |
| **Snapshots webcam** | `canvas.drawImage(video)` toutes les 10s | Comparaison faciale |

### Règle d'or
> **Jamais de kill automatique.** Système de 3 strikes :
> 1. 🟡 Alerte visuelle (jaune)
> 2. 🟠 Alerte RH (orange)
> 3. 🔴 Session terminée (rouge) — **décision humaine**

### Verdict
✅ **DO IT** — Mature côté technique. Soyez humain dans la tolérance.

---

## Module 7 — Entretien LIVE avec IA Générant Questions

### Objectif *(Cœur du projet)*
Mener un entretien vidéo **en temps réel** où une IA pose des questions personnalisées, adapte le fil de la conversation selon les réponses, et analyse la performance du candidat.

### Architecture
```
Candidat ──WebRTC──→ Serveur Signaling (Socket.io)
                          ↓
                    IA génère question (GPT-4o streaming)
                          ↓
                    Candidat répond (micro + caméra)
                          ↓
                    Whisper STT → Transcription temps réel
                          ↓
                    LLM analyse → Score + Question suivante
                          ↓
                    Rapport final (audio + texte + score)
```

### Technologies
- **Vidéo temps réel** : `PeerJS` (WebRTC simple) ou `Mediasoup` (scalable)
- **Streaming LLM** : `stream=true` sur OpenAI API (latence < 1s)
- **Arbre de questions** (optimisation) : Pré-générer un arbre de décision plutôt que générer à la volée
- **Transcription temps réel** : `Whisper` en mode segment par segment

### Défi principal : La latence
Un entretien où le candidat attend 3s entre chaque question est insupportable.

### Solutions
1. **Pré-génération** : Arbre de questions avec 3 branches par nœud
2. **LLM local rapide** : `Llama 3.1 8B` sur GPU (RTX 4090 ou cloud GPU)
3. **Streaming** : Afficher la question mot par mot pendant la génération

### Verdict
🌟 **C'EST VOTRE CŒUR DE PROJET** — Différenciant mais difficile. Investissez ici.

---

## Module 8 — Vérification Faciale en Temps Réel

### Objectif
Vérifier que la personne qui passe l'entretien correspond bien au candidat déclaré (photo CV / pièce d'identité).

### Approche
1. **Vérification initiale** (début de session) :
   - Snapshot via webcam
   - Comparaison avec photo CV / ID
   - `FaceAPI.js` (browser) pour détection
   - `AWS Rekognition` (API) pour comparaison faciale (plus précis)

2. **Surveillance passive** (pendant l'entretien) :
   - Snapshots toutes les 10-15 secondes
   - Détection de visage (pas de comparaison continue — trop lourd)
   - Si pas de visage détecté → alerte

3. **Alerte** :
   - Si mismatch ou absence de visage → notification WebSocket au RH
   - Flag sur le rapport final
   - **Jamais de kill automatique**

### RGPD — Données biométriques
- Photos chiffrées (`AES-256`)
- Conservation limitée (30 jours maximum)
- Consentement explicite du candidat
- Droit à l'oubli (suppression automatique post-recrutement)

### Verdict
⚠️ **FAISABLE MAIS RISQUÉ** — Adoucissez l'approche. Snapshots + alertes, pas kill auto.

---

## Module 9 — Green Score / ESG

### Objectif *(Votre arme secrète)*
Mesurer et certifier l'impact carbone évité par chaque recrutement dématérialisé.

### Formule de calcul
```
CO₂_physique = 5.0 kg  (déplacement + papier + salle de réunion)
CO₂_digital  = 0.05 kg (serveur + streaming vidéo)
CO₂_evite    = CO₂_physique - CO₂_digital = 4.95 kg
```

> Basé sur les facteurs d'émission ADEME / GHG Protocol.

### Fonctionnalités
| Feature | Description |
|---------|-------------|
| **Badge candidat** | *"🌿 Ce recrutement a évité 4.95 kg de CO₂"* |
| **Dashboard ESG** | Cumul mensuel/annuel par entreprise |
| **Rapport PDF** | Export mensuel pour la direction RSE |
| **Comparaison** | *"Équivalent à 25 km en voiture évités"* |

### Verdict
🌟 **OBLIGATOIRE** — C'est votre seule vraie différenciation. Zéro difficulté technique.

---

## Module 10 — Notification Service

### Objectif
Gérer toutes les communications automatisées avec les candidats et les RH.

### Canaux
| Canal | Usage | Technologie |
|-------|-------|-------------|
| **Email** | Confirmation upload, invitation entretien, résultat | `SendGrid` / `Mailgun` / `AWS SES` |
| **Rappels** | 24h avant l'entretien | `Celery Beat` (cron) |
| **Push temps réel** | Alertes proctoring, visiteur en live | `WebSocket` (Socket.io) |
| **SMS** | Rappel urgent (optionnel) | `Twilio` |

### Verdict
✅ **DO IT** — Standard, nécessaire pour l'UX.

---

## Flux de Données Typique

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  Candidat   │───→│   Upload    │───→│  Parsing    │───→│  Matching   │
│  (Frontend) │    │   CV (S3)   │    │   (M1)      │    │   (M2+M3)   │
└─────────────┘    └─────────────┘    └─────────────┘    └──────┬──────┘
                                                                  │
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌──────▼──────┐
│   Décision  │←───│   Rapport   │←───│   Live AI   │←───│  Invitation │
│     RH      │    │   Final     │    │  (M7+M8)    │    │  (M10)      │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
       ↑
       └──────────────────────────────────────────────────────────┐
                                                                  │
                    ┌─────────────┐    ┌─────────────┐
                    │ Green Score │←───│  Proctoring │
                    │   (M9)      │    │   (M6)      │
                    └─────────────┘    └─────────────┘
```

---

## Sécurité & RGPD

### Authentification & Autorisation
- **OIDC** via Keycloak
- **JWT** stateless avec refresh tokens
- **RBAC** : `candidat`, `rh`, `admin`, `super_admin`

### Protection des données
- **Chiffrement au repos** : `AES-256` pour les fichiers S3
- **Chiffrement en transit** : TLS 1.3
- **Hashing mots de passe** : `bcrypt` (cost=12)
- **Secrets** : HashiCorp Vault

### RGPD — Points clés
| Principe | Mise en œuvre |
|----------|---------------|
| **Consentement** | Case à cocher explicite avant upload CV |
| **Minimisation** | Données biométriques supprimées après 30j |
| **Droit à l'oubli** | Endpoint `/api/me/delete` — suppression complète |
| **Portabilité** | Export données personnelles (JSON) |
| **Audit** | Logs Elasticsearch traçant chaque accès |

### Audit de biais IA
- Tableau de bord vérifiant que le matching ne discrimine pas (genre, âge, origine)
- Rapport mensuel de fairness

---

## Planning de Réalisation (Méthodologie Agile)

| Sprint | Durée | Livrable | Modules |
|--------|-------|----------|---------|
| **Sprint 0** | 1 semaine | Cahier des charges, maquettes Figma, architecture | — |
| **Sprint 1** | 2 semaines | Upload CV + Parsing + Base de données | M1 |
| **Sprint 2** | 2 semaines | Matching IA + Résumé + Classement | M2, M3, M4 |
| **Sprint 3** | 2 semaines | Interface RH (Dashboard) | Frontend |
| **Sprint 4** | 2 semaines | WebRTC + Session vidéo live | M7 (partie vidéo) |
| **Sprint 5** | 2 semaines | Facial recognition + Anti-copier-coller | M6, M8 |
| **Sprint 6** | 2 semaines | Génération questions IA + Analyse réponses | M7 (partie IA) |
| **Sprint 7** | 2 semaines | Green Score + Notifications + Auth | M9, M10, M2-Auth |
| **Sprint 8** | 1 semaine | Tests E2E, correction bugs, documentation | QA |
| **Sprint 9** | 1 semaine | Déploiement + Présentation finale | DevOps |

**Total : ~17 semaines (~4 mois)**

---

## Différenciation Concurrentielle

### Ce qui existe déjà (saturé)
| Fonction | Acteurs |
|----------|---------|
| Parsing CV + Matching | HireVue, Manatal, Eightfold, Truffle |
| Entretien asynchrone | HireVue, TestGorilla, Manatal AI Interviewer |
| Proctoring | Testlify, TestTrick, Talview |
| Entretien live (partiel) | Fabric, Sherlock AI |

### Ce que personne ne fait (votre territoire)
| Fonction | Statut |
|----------|--------|
| **Score carbone par recrutement** | ❌ Aucun concurrent |
| **Rapport ESG mensuel** | ❌ Aucun concurrent |
| **Certification verte du processus** | ❌ Aucun concurrent |

### Pitch final ajusté
> *« GreenHire AI ne se contente pas d'automatiser le recrutement — ça, HireVue le fait déjà. Notre projet combine un moteur de matching IA classique avec un entretien live généré par IA et un proctoring intelligent. Mais surtout, nous sommes les seuls à certifier l'impact carbone de chaque recrutement dématérialisé, répondant à l'urgence ESG des entreprises. Nous ne réinventons pas la roue : nous l'améliorons avec une vision responsable. »*

---

## Récapitulatif des Verdicts

| # | Module | Priorité | Complexité |
|---|--------|----------|------------|
| 1 | Upload CV + Parsing | **P0 — Obligatoire** | ⭐ Basse |
| 2 | Matching Sémantique | **P0 — Obligatoire** | ⭐⭐ Moyenne |
| 3 | Score & Classement | **P0 — Obligatoire** | ⭐⭐ Moyenne |
| 4 | Résumé IA | **P0 — Obligatoire** | ⭐ Basse |
| 5 | Async Interview | **P4 — À éviter** | ⭐⭐⭐ Élevée |
| 6 | Proctoring | **P1 — Important** | ⭐⭐⭐ Élevée |
| 7 | Live Interview AI | **P2 — Le "Wow"** | ⭐⭐⭐⭐ Très élevée |
| 8 | Face Verify Live | **P3 — Optionnel** | ⭐⭐⭐⭐ Très élevée |
| 9 | Green Score | **P0 — Obligatoire** | ⭐ Basse |
| 10 | Notification | **P1 — Important** | ⭐ Basse |

---

*Document généré le 29 Juillet 2026 — GreenHire AI Project*

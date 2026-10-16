"""
nuextract_provider.py
=====================
Provider local NuExtract3 (GGUF, llama-cpp-python) : texte de CV -> JSON structuré.
Metal (GPU Apple) par défaut, repli automatique sur CPU si le chargement échoue.

Variables d'environnement (optionnelles) :
    NUEXTRACT_REPO        dépôt HuggingFace      (défaut numind/NuExtract3-GGUF)
    NUEXTRACT_FILE        fichier GGUF           (défaut NuExtract3-Q4_K_M.gguf)
    NUEXTRACT_CTX         fenêtre de contexte    (défaut 8192)
    NUEXTRACT_GPU_LAYERS  -1 = Metal, 0 = CPU pur (défaut -1)
    NUEXTRACT_THREADS     threads CPU            (défaut 4)
    NUEXTRACT_BATCH       taille de lot = prompt max sous Metal (défaut 4096)
"""

import json
import os
import re
import sys
import time

REPO_ID = os.environ.get("NUEXTRACT_REPO", "numind/NuExtract3-GGUF")
FICHIER = os.environ.get("NUEXTRACT_FILE", "NuExtract3-Q4_K_M.gguf")
N_CTX = int(os.environ.get("NUEXTRACT_CTX", "8192"))
GPU_LAYERS = int(os.environ.get("NUEXTRACT_GPU_LAYERS", "-1"))
N_THREADS = int(os.environ.get("NUEXTRACT_THREADS", "4"))
# Metal : llama_decode échoue (-3) quand le prompt est découpé en plusieurs lots.
# On force donc un lot unique assez grand pour tout le prompt.
N_BATCH = int(os.environ.get("NUEXTRACT_BATCH", "4096"))
MAX_TOKENS = 3072

# Même structure que les autres providers (consommée par debug.py / scoring).
# "description" = citation verbatim du CV ; "resume" = synthèse du modèle.
SCHEMA = {
    "nom_complet": "verbatim-string",
    "email": "email",
    "telephone": "verbatim-string",
    "localisation": "string",
    "titre_poste": "string",
    "resume": "string",
    "competences": ["string"],
    "langues": [{"langue": "string", "niveau": "string"}],
    "experience": [{
        "poste": "verbatim-string",
        "entreprise": "verbatim-string",
        "debut": "date",
        "fin": "date",
        "resume": "string",
        "description": "verbatim-string",
    }],
    "formation": [{
        "diplome": "verbatim-string",
        "etablissement": "verbatim-string",
        "annee": "string",
    }],
    "certifications": ["verbatim-string"],
    "liens": {
        "linkedin": "verbatim-string",
        "github": "verbatim-string",
        "portfolio": "verbatim-string",
    },
}

_TYPES = {"verbatim-string", "string", "integer", "number", "date", "date-time",
          "time", "country", "currency", "email", "boolean"}

_llm = None
_chat_tpl = None
LAST_STATS: dict = {}


def _to_schema(t):
    """Gabarit NuExtract -> JSON Schema (pour la grammaire de sortie)."""
    if isinstance(t, dict):
        return {"type": "object",
                "properties": {k: _to_schema(v) for k, v in t.items()},
                "required": list(t.keys()), "additionalProperties": False}
    if isinstance(t, list):
        if len(t) == 1 and (isinstance(t[0], dict) or t[0] in _TYPES):
            return {"type": "array", "items": _to_schema(t[0])}
        return {"enum": t + [None]}
    base = {"integer": "integer", "number": "number", "boolean": "boolean"}.get(t, "string")
    return {"type": [base, "null"]}


def _ram_mo() -> float:
    import psutil
    return psutil.Process(os.getpid()).memory_info().rss / 1024**2


def _charger():
    """Charge le modèle une seule fois (Metal, sinon CPU) et prépare le template."""
    global _llm, _chat_tpl
    if _llm is not None:
        return _llm

    from huggingface_hub import hf_hub_download
    from jinja2.sandbox import ImmutableSandboxedEnvironment
    from llama_cpp import Llama

    print(f"[NuExtract] Téléchargement/lecture du modèle {FICHIER}...", file=sys.stderr)
    chemin = hf_hub_download(repo_id=REPO_ID, filename=FICHIER)

    def _llama(n_gpu):
        return Llama(model_path=chemin, n_ctx=N_CTX, n_gpu_layers=n_gpu,
                     n_threads=N_THREADS, n_batch=N_BATCH, n_ubatch=N_BATCH, use_mmap=True, verbose=False)

    t0 = time.perf_counter()
    mode = "Metal" if GPU_LAYERS != 0 else "CPU"
    try:
        _llm = _llama(GPU_LAYERS)
    except Exception as e:
        if GPU_LAYERS == 0:
            raise RuntimeError(f"Chargement NuExtract impossible : {e}")
        print(f"[NuExtract] Metal indisponible ({e}) -> repli CPU", file=sys.stderr)
        mode = "CPU (repli)"
        _llm = _llama(0)
    LAST_STATS["mode"] = mode
    LAST_STATS["chargement_s"] = round(time.perf_counter() - t0, 1)

    # Les balises {% generation %} sont propres à transformers : on les retire.
    src = re.sub(r"\{%-?\s*(end)?generation\s*-?%\}", "",
                 _llm.metadata["tokenizer.chat_template"])
    env = ImmutableSandboxedEnvironment(trim_blocks=True, lstrip_blocks=True,
                                        extensions=["jinja2.ext.loopcontrols"])
    env.globals["raise_exception"] = lambda m: (_ for _ in ()).throw(Exception(m))
    _chat_tpl = env.from_string(src)
    return _llm


def _parse_json(txt: str) -> dict:
    txt = txt.strip().strip("`").removeprefix("json").strip()
    try:
        return json.loads(txt)
    except json.JSONDecodeError:
        return json.loads(txt[txt.find("{"):txt.rfind("}") + 1])


def classify_with_nuextract(cv_text: str, model: str = None) -> dict:
    """Extrait le JSON du CV avec NuExtract3 en local. `model` est ignoré (compat. API)."""
    from llama_cpp import LlamaGrammar

    llm = _charger()
    prompt = _chat_tpl.render(
        messages=[{"role": "user", "content": [{"type": "text", "text": cv_text}]}],
        template=json.dumps(SCHEMA, indent=4, ensure_ascii=False),
        enable_thinking=False,
        add_generation_prompt=True,
    )
    n_prompt = len(llm.tokenize(prompt.encode("utf-8")))
    if "Metal" in LAST_STATS.get("mode", "") and n_prompt > N_BATCH:
        raise RuntimeError(f"Prompt de {n_prompt} tokens > lot Metal {N_BATCH} "
                           f"(augmenter NUEXTRACT_BATCH ou utiliser NUEXTRACT_GPU_LAYERS=0).")
    if n_prompt + MAX_TOKENS > llm.n_ctx():
        raise RuntimeError(f"CV trop long : {n_prompt} tokens + {MAX_TOKENS} de sortie "
                           f"> contexte {llm.n_ctx()} (augmenter NUEXTRACT_CTX).")

    grammar = LlamaGrammar.from_json_schema(json.dumps(_to_schema(SCHEMA)), verbose=False)
    t0 = time.perf_counter()
    out = llm.create_completion(prompt, max_tokens=MAX_TOKENS, temperature=0.2, grammar=grammar)
    duree = time.perf_counter() - t0

    n_out = out["usage"]["completion_tokens"]
    LAST_STATS.update({
        "tokens_prompt": n_prompt, "tokens_sortie": n_out,
        "generation_s": round(duree, 1),
        "vitesse_tok_s": round(n_out / duree, 1) if duree else None,
        "ram_mo": round(_ram_mo()),
    })
    try:
        return _parse_json(out["choices"][0]["text"])
    except json.JSONDecodeError as e:
        raise RuntimeError(f"NuExtract a retourné un JSON invalide : {e}")

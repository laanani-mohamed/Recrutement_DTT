"""
run_eval.py — précision / métriques d'un provider de conversion CV -> JSON.

Usage (depuis APP/) :
    python eval/run_eval.py                       # nuextract sur tous les CV de eval/gold/
    python eval/run_eval.py nuextract groq        # compare plusieurs providers
    python eval/run_eval.py nuextract --cv cv1

Un CV `ressource/<nom>.pdf` est évalué s'il a une référence `eval/gold/<nom>.json`.
Sorties : eval/results/<provider>_<nom>.json (+ résumé affiché et eval/results/summary.json).

Métriques :
  - Champs simples (nom, email, tel, localisation, titre) : exact (normalisé) + similarité.
  - Listes (compétences, certifications, expériences, formations, langues) :
    précision / rappel / F1 avec appariement flou glouton.
  - Dates des expériences : exactitude début / fin sur les expériences appariées.
  - Ancrage (hallucination) : part des valeurs "verbatim" retrouvées dans le texte source.
  - Opérationnel : JSON valide, latence, tokens/s et RAM (NuExtract).
"""
import json
import os
import re
import sys
import time
import unicodedata
from difflib import SequenceMatcher

APP = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, APP)

SEUIL_ITEM = 0.85   # appariement des éléments de listes courtes
SEUIL_EXP = 0.55    # appariement des expériences / formations


# ------------------------------------------------------------------ normalisation
def norm(s) -> str:
    if s is None:
        return ""
    s = unicodedata.normalize("NFKD", str(s)).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", " ", s).strip()


def compact(s) -> str:
    return norm(s).replace(" ", "")


def sim(a, b) -> float:
    a, b = norm(a), norm(b)
    if not a and not b:
        return 1.0
    return SequenceMatcher(None, a, b).ratio()


def norm_date(d):
    """'05/2026' | '2026-05' | '2026' -> 'YYYY-MM' / 'YYYY' ; présent/vide -> None."""
    if d is None:
        return None
    s = str(d).strip().lower()
    if not s or re.search(r"aujourd|pr[ée]sent|en cours|now|current", s):
        return None
    m = re.search(r"(\d{1,2})\s*[/.-]\s*(\d{4})", s)
    if m:
        return f"{m.group(2)}-{int(m.group(1)):02d}"
    m = re.search(r"(\d{4})\s*-\s*(\d{1,2})\b", s)
    if m:
        return f"{m.group(1)}-{int(m.group(2)):02d}"
    m = re.search(r"\d{4}", s)
    return m.group(0) if m else None


# ------------------------------------------------------------------ appariement
def apparier(gold, pred, score_fn, seuil):
    """Appariement glouton 1-1 : renvoie [(i_gold, j_pred, score)]."""
    paires = sorted(((score_fn(g, p), i, j) for i, g in enumerate(gold)
                     for j, p in enumerate(pred)), reverse=True)
    ug, up, res = set(), set(), []
    for sc, i, j in paires:
        if sc >= seuil and i not in ug and j not in up:
            ug.add(i); up.add(j); res.append((i, j, sc))
    return res


def prf(n_gold, n_pred, n_ok):
    p = n_ok / n_pred if n_pred else (1.0 if not n_gold else 0.0)
    r = n_ok / n_gold if n_gold else (1.0 if not n_pred else 0.0)
    f = 2 * p * r / (p + r) if p + r else 0.0
    return {"precision": round(p, 3), "rappel": round(r, 3), "f1": round(f, 3),
            "n_gold": n_gold, "n_pred": n_pred, "n_ok": n_ok}


def _liste(x):
    return x if isinstance(x, list) else []


def _dict_items(x):
    return [e for e in _liste(x) if isinstance(e, dict)]


# ------------------------------------------------------------------ métriques
def eval_cv(gold: dict, pred: dict, source: str) -> dict:
    m = {}

    # champs simples
    champs = {}
    for k in ("nom_complet", "email", "telephone", "localisation", "titre_poste"):
        g, p = gold.get(k), pred.get(k)
        if k == "telephone":
            exact = compact(g) == compact(p)
        else:
            exact = norm(g) == norm(p)
        champs[k] = {"exact": exact, "similarite": round(sim(g, p), 3)}
    m["champs"] = champs
    m["champs_exact_pct"] = round(100 * sum(c["exact"] for c in champs.values()) / len(champs), 1)

    # listes de chaînes
    for k in ("competences", "certifications"):
        g, p = _liste(gold.get(k)), _liste(pred.get(k))
        ok = len(apparier(g, p, sim, SEUIL_ITEM))
        m[k] = prf(len(g), len(p), ok)

    # langues (appariées sur la langue ; niveau évalué ensuite)
    g, p = _dict_items(gold.get("langues")), _dict_items(pred.get("langues"))
    pa = apparier(g, p, lambda a, b: sim(a.get("langue"), b.get("langue")), SEUIL_ITEM)
    m["langues"] = prf(len(g), len(p), len(pa))
    m["langues"]["niveau_ok"] = sum(sim(g[i].get("niveau"), p[j].get("niveau")) >= 0.7 for i, j, _ in pa)

    # expériences
    def s_exp(a, b):
        return (0.4 * sim(a.get("poste"), b.get("poste")) + 0.4 * sim(a.get("entreprise"), b.get("entreprise"))
                + 0.2 * (norm_date(a.get("debut")) == norm_date(b.get("debut"))))
    g, p = _dict_items(gold.get("experience")), _dict_items(pred.get("experience"))
    pa = apparier(g, p, s_exp, SEUIL_EXP)
    m["experience"] = prf(len(g), len(p), len(pa))
    if pa:
        m["experience"]["debut_ok"] = sum(norm_date(g[i].get("debut")) == norm_date(p[j].get("debut")) for i, j, _ in pa)
        m["experience"]["fin_ok"] = sum(norm_date(g[i].get("fin")) == norm_date(p[j].get("fin")) for i, j, _ in pa)
        m["experience"]["dates_acc"] = round((m["experience"]["debut_ok"] + m["experience"]["fin_ok"]) / (2 * len(pa)), 3)

    # formations
    def s_form(a, b):
        return 0.6 * sim(a.get("diplome"), b.get("diplome")) + 0.4 * sim(a.get("etablissement"), b.get("etablissement"))
    g, p = _dict_items(gold.get("formation")), _dict_items(pred.get("formation"))
    m["formation"] = prf(len(g), len(p), len(apparier(g, p, s_form, SEUIL_EXP)))

    # ancrage : valeurs "verbatim" retrouvées dans le source
    src = compact(source)
    vals = [pred.get(k) for k in ("nom_complet", "email", "telephone")]
    for e in _dict_items(pred.get("experience")):
        vals += [e.get("poste"), e.get("entreprise"), e.get("description")]
    for e in _dict_items(pred.get("formation")):
        vals += [e.get("diplome"), e.get("etablissement")]
    vals += _liste(pred.get("certifications"))
    vals = [v for v in vals if isinstance(v, str) and compact(v)]
    ancres = sum(compact(v) in src for v in vals)
    m["ancrage"] = {"valeurs": len(vals), "retrouvees": ancres,
                    "taux": round(ancres / len(vals), 3) if vals else None}

    # F1 global (micro) sur les listes
    tot = {"ok": 0, "g": 0, "p": 0}
    for k in ("competences", "certifications", "langues", "experience", "formation"):
        tot["ok"] += m[k]["n_ok"]; tot["g"] += m[k]["n_gold"]; tot["p"] += m[k]["n_pred"]
    m["f1_listes_micro"] = prf(tot["g"], tot["p"], tot["ok"])["f1"]
    return m


# ------------------------------------------------------------------ exécution
def main():
    args = sys.argv[1:]
    cvs = None
    if "--cv" in args:
        i = args.index("--cv")
        cvs = [args[i + 1]]
        del args[i:i + 2]
    providers = args or ["nuextract"]

    from src.extraction.main_extraction import extract_text
    from src.convert_json import convert_cv

    gold_dir = os.path.join(APP, "eval", "gold")
    out_dir = os.path.join(APP, "eval", "results")
    os.makedirs(out_dir, exist_ok=True)
    noms = cvs or sorted(f[:-5] for f in os.listdir(gold_dir) if f.endswith(".json"))

    textes = {n: extract_text(os.path.join(APP, "ressource", f"{n}.pdf"), method="markitdown") for n in noms}
    golds = {n: json.load(open(os.path.join(gold_dir, f"{n}.json"), encoding="utf-8")) for n in noms}

    summary = {}
    for prov in providers:
        for n in noms:
            t0 = time.perf_counter()
            rec = {"provider": prov, "cv": n}
            try:
                pred = convert_cv(textes[n], provider=prov)
                rec["latence_s"] = round(time.perf_counter() - t0, 1)
                rec["json_valide"] = isinstance(pred, dict)
                if prov == "nuextract":
                    from src.convert_json.nuextract_provider import LAST_STATS
                    rec["stats_nuextract"] = dict(LAST_STATS)
                rec["metriques"] = eval_cv(golds[n], pred, textes[n])
                rec["prediction"] = pred
            except Exception as e:
                rec.update(json_valide=False, erreur=str(e)[:300],
                           latence_s=round(time.perf_counter() - t0, 1))
            json.dump(rec, open(os.path.join(out_dir, f"{prov}_{n}.json"), "w"),
                      ensure_ascii=False, indent=1)
            summary[f"{prov}/{n}"] = {k: v for k, v in rec.items() if k != "prediction"}

    json.dump(summary, open(os.path.join(out_dir, "summary.json"), "w"), ensure_ascii=False, indent=1)
    afficher(summary)


def afficher(summary):
    print(f"\n{'run':<16}{'valide':>7}{'temps':>8}{'champs%':>9}{'F1 skills':>10}{'F1 exp':>8}"
          f"{'F1 form':>8}{'F1 lang':>8}{'dates':>7}{'ancrage':>9}{'F1 glob':>9}")
    for run, r in summary.items():
        if "metriques" not in r:
            print(f"{run:<16}{'ERR':>7}  {r.get('erreur', '')[:90]}")
            continue
        m = r["metriques"]
        print(f"{run:<16}{'oui':>7}{r['latence_s']:>8}{m['champs_exact_pct']:>9}{m['competences']['f1']:>10}"
              f"{m['experience']['f1']:>8}{m['formation']['f1']:>8}{m['langues']['f1']:>8}"
              f"{m['experience'].get('dates_acc', '-'):>7}{m['ancrage']['taux']:>9}{m['f1_listes_micro']:>9}")


if __name__ == "__main__":
    main()

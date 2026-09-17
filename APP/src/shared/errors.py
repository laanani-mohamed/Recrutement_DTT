"""Erreurs communes aux modules LLM (entretien, scoring)."""


class CleApiManquante(ValueError):
    """Aucune clé API utilisable pour ce provider.

    C'est une erreur de configuration, pas un aléa de génération : elle remonte
    au lieu d'être dégradée en section/exigence échouée, sinon l'utilisateur ne
    voit qu'un résultat vide sans jamais en connaître la cause.
    """

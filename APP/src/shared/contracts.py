"""Contrats de données partagés par les modules entretien et scoring."""

from pydantic import BaseModel, Field


class JobSpec(BaseModel):
    """Fiche de poste structurée en exigences."""

    titre: str = "Poste"
    must_have: list[str] = Field(default_factory=list)
    nice_to_have: list[str] = Field(default_factory=list)

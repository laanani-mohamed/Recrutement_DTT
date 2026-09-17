# src/__init__.py
# Rend le dossier src importable comme package Python

# Charge APP/.env avant tout accès à os.environ par les providers.
# Chemin explicite : le .env doit être trouvé quel que soit le répertoire courant.
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    DATA_DIR = os.environ.get(
        "DATA_DIR",
        os.path.join(os.path.dirname(os.path.dirname(__file__)), "data"),
    )
    OUTPUT_DIR = os.environ.get(
        "OUTPUT_DIR",
        os.path.join(os.path.dirname(os.path.dirname(__file__)), "outputs"),
    )

    @property
    def FACEBOOK_DB(self):
        return os.environ.get("FACEBOOK_DB") or os.path.join(self.DATA_DIR, "facebook.db")

    @property
    def TIKTOK_DB(self):
        return os.environ.get("TIKTOK_DB") or os.path.join(self.DATA_DIR, "tiktok.db")

    @property
    def EXTERNOS_DB(self):
        return os.environ.get("EXTERNOS_DB") or os.path.join(self.DATA_DIR, "externos.db")

    # -- Constantes de clasificación (SSOT) --
    FB_PAGES_OFICIALES = [
        "Alcaldía de Santa Ana",
        "Gustavo Acevedo",
    ]

    FB_REACTIONS = [
        "likes_count", "loves_count", "cares_count",
        "hahas_count", "wows_count", "sads_count", "angrys_count",
    ]

    TK_ENGAGEMENT = ["views", "likes", "shares", "favorites_count", "comments_count"]

    TK_ACCOUNTS = {
        1: "Alcaldía de Santa Ana",
        3: "Gustavo Acevedo",
    }

    MIN_COMENTARIOS_MUESTRA = 15


def ensure_dirs(cfg=None):
    """Crea DATA_DIR y OUTPUT_DIR si no existen. Llamar explícitamente."""
    cfg = cfg or Config()
    os.makedirs(cfg.DATA_DIR, exist_ok=True)
    os.makedirs(cfg.OUTPUT_DIR, exist_ok=True)

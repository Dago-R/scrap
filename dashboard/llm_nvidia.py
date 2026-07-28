"""
llm_nvidia.py — Módulo de integración con IA externa (ELIMINADO).

La extracción de datos desde capturas/PDF se hace ahora con una IA externa
(ej. Claude en claude.ai). El JSON resultante se importa en el panel de carga
usando la sección "Importar JSON extraído externamente" en dash_ingesta.py.

Este módulo se mantiene como stub para no romper imports existentes.
"""


def llm_disponible() -> bool:
    """Siempre devuelve False: la integración con IA local fue eliminada."""
    return False


def chat_vision(prompt: str, paginas: list, max_tokens: int = 8192, model=None) -> str:
    """Stub: lanza error informativo si se llama directamente."""
    raise RuntimeError(
        "La integración con IA local fue eliminada. "
        "Usa la sección 'Importar JSON' del panel de carga."
    )

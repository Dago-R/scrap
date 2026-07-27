"""Helper para registrar propuestas nuevas en taxonomias_pendientes.json.

Usado por emotion.py, topic.py, zona.py y dash_temas.py cuando detectan una
categoría, zona o entidad que no existe en el catálogo actual.

Tipos soportados: "emocion", "tema", "zona", "entidad".
"""
import json
import os
from datetime import datetime, timezone


_TAXONOMIAS_PATH = os.path.join(
    os.path.dirname(__file__), os.pardir, "data", "taxonomias_pendientes.json"
)


def _registrar_propuesta(
    clave_propuesta: str,
    ejemplo_texto: str,
    tipo: str,
    familia_mas_cercana: str = "",
) -> None:
    """Append una propuesta a taxonomias_pendientes.json con lock de archivo.

    Si ya existe una entrada pendiente con la misma clave+tipo, incrementa
    n_ocurrencias y actualiza fecha en vez de crear entrada duplicada.

    Args:
        clave_propuesta: nombre propuesto (ej. "nueva_emocion" o "zona_xyz")
        ejemplo_texto: fragmento del texto que motivó la propuesta
        tipo: "emocion", "tema", o "zona"
        familia_mas_cercana: familia o categoría más cercana (vacío si no aplica)
    """
    path = os.path.normpath(_TAXONOMIAS_PATH)

    try:
        # Crear archivo si no existe
        if not os.path.exists(path):
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "w", encoding="utf-8") as f:
                json.dump([], f)

        with open(path, "r+", encoding="utf-8") as f:
            try:
                import fcntl
                fcntl.flock(f, fcntl.LOCK_EX)
            except (ImportError, OSError):
                fcntl = None  # Windows or unavailable

            try:
                f.seek(0)
                try:
                    data = json.load(f)
                except json.JSONDecodeError:
                    data = []

                # Deduplicar
                found = False
                for entry in data:
                    if (entry.get("clave_propuesta") == clave_propuesta
                            and entry.get("tipo") == tipo
                            and entry.get("estado") == "pendiente"):
                        entry["n_ocurrencias"] = entry.get("n_ocurrencias", 1) + 1
                        entry["fecha"] = datetime.now(timezone.utc).isoformat()
                        found = True
                        break

                if not found:
                    data.append({
                        "clave_propuesta": clave_propuesta,
                        "ejemplo_texto": ejemplo_texto[:200],
                        "tipo": tipo,
                        "familia_mas_cercana": familia_mas_cercana,
                        "fecha": datetime.now(timezone.utc).isoformat(),
                        "estado": "pendiente",
                        "n_ocurrencias": 1,
                    })

                f.seek(0)
                f.truncate()
                json.dump(data, f, ensure_ascii=False, indent=2)
            finally:
                if fcntl is not None:
                    try:
                        fcntl.flock(f, fcntl.LOCK_UN)
                    except OSError:
                        pass

    except OSError:
        # Fallback without lock (Windows or other OS issues)
        _registrar_propuesta_sin_lock(
            clave_propuesta, ejemplo_texto, tipo, familia_mas_cercana
        )


def _registrar_propuesta_sin_lock(
    clave_propuesta: str,
    ejemplo_texto: str,
    tipo: str,
    familia_mas_cercana: str,
) -> None:
    """Fallback sin lock para entornos sin fcntl (Windows).

    Usa rename atómico (tmp → destino) para minimizar riesgo de corrupción
    en escrituras concurrentes. No es completamente atómico en todos los SO,
    pero es significativamente más seguro que write directo.
    """
    import tempfile
    path = os.path.normpath(_TAXONOMIAS_PATH)
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        data = []

    found = False
    for entry in data:
        if (entry.get("clave_propuesta") == clave_propuesta
                and entry.get("tipo") == tipo
                and entry.get("estado") == "pendiente"):
            entry["n_ocurrencias"] = entry.get("n_ocurrencias", 1) + 1
            entry["fecha"] = datetime.now(timezone.utc).isoformat()
            found = True
            break

    if not found:
        data.append({
            "clave_propuesta": clave_propuesta,
            "ejemplo_texto": ejemplo_texto[:200],
            "tipo": tipo,
            "familia_mas_cercana": familia_mas_cercana,
            "fecha": datetime.now(timezone.utc).isoformat(),
            "estado": "pendiente",
            "n_ocurrencias": 1,
        })

    dir_path = os.path.dirname(path)
    os.makedirs(dir_path, exist_ok=True)
    try:
        fd, tmp_path = tempfile.mkstemp(dir=dir_path, suffix=".tmp")
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as tmp_f:
                json.dump(data, tmp_f, ensure_ascii=False, indent=2)
            os.replace(tmp_path, path)  # rename atómico
        except Exception:
            try:
                os.unlink(tmp_path)
            except OSError:
                pass
            raise
    except Exception:
        # Último recurso: write directo (comportamiento original)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

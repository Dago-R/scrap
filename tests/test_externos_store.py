"""Tests para dashboard/externos_store.py — persistencia de reacciones Externos (17.1.14)."""
import sqlite3
import tempfile
import os

from dashboard.externos_store import (
    asegurar_tablas_externas,
    insertar_post_externo,
    _total_reacciones,
)


def _db():
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    db = path
    asegurar_tablas_externas(db)
    conn = sqlite3.connect(db)
    return conn, db


def test_total_reacciones_desde_contrato_anidado():
    """17.1.14: el contrato trae reacciones como {clave: {valor, confianza}};
    el total debe extraerse (o sumarse) en vez de guardar 0."""
    datos = {
        "reacciones": {
            "likes": {"valor": 40, "confianza": "seguro"},
            "loves": {"valor": 5, "confianza": "seguro"},
            "cares": {"valor": 2, "confianza": "dudoso"},
            "hahas": {"valor": 1, "confianza": "seguro"},
            "sads": {"valor": 0, "confianza": "seguro"},
            "wows": {"valor": 3, "confianza": "seguro"},
            "angrys": {"valor": 1, "confianza": "seguro"},
            "total": {"valor": None, "confianza": "dudoso"},
        },
    }
    assert _total_reacciones(datos) == 52


def test_total_reacciones_usa_total_explicito():
    datos = {"reacciones": {"total": {"valor": 99, "confianza": "seguro"}}}
    assert _total_reacciones(datos) == 99


def test_total_reacciones_flat_prioritario():
    datos = {"total_reactions": 123, "reacciones": {"likes": {"valor": 1}}}
    assert _total_reacciones(datos) == 123


def test_insertar_post_externo_persiste_reacciones():
    """17.1.14: el post externo se guarda con total_reactions real del contrato."""
    conn, db = _db()
    try:
        insertar_post_externo(conn, {
            "page_name": "Prensa Prueba",
            "message": "Nota de prueba",
            "reacciones": {
                "likes": {"valor": 10, "confianza": "seguro"},
                "loves": {"valor": 2, "confianza": "seguro"},
                "cares": {"valor": 0, "confianza": "seguro"},
                "hahas": {"valor": 0, "confianza": "seguro"},
                "sads": {"valor": 0, "confianza": "seguro"},
                "wows": {"valor": 0, "confianza": "seguro"},
                "angrys": {"valor": 0, "confianza": "seguro"},
                "total": {"valor": None, "confianza": "dudoso"},
            },
            "post_url": "https://example.com/nota",
        }, "ext_1")
        conn.commit()
        fila = conn.execute(
            "SELECT page_name, total_reactions, post_url FROM external_posts WHERE post_id='ext_1'"
        ).fetchone()
        assert fila[0] == "Prensa Prueba"
        assert fila[1] == 12
        assert fila[2] == "https://example.com/nota"
    finally:
        conn.close()
        os.remove(db)

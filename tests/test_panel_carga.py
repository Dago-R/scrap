"""Tests para dashboard/panel_carga.py — pestañas (sin aprobación manual)."""
import inspect
import os
import re

import pytest


def _leer_fuente():
    """Lee el fuente de panel_carga.py como string."""
    path = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                        "dashboard", "panel_carga.py")
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def test_panel_carga_no_tiene_pestanas_aprobacion():
    """panel_carga.py ya NO define pestañas de aprobación manual."""
    src = _leer_fuente()
    assert "Aprobar temas" not in src


def test_panel_carga_importa_render_revisor():
    """panel_carga.py importa render_revisor_temas (WARN-01)."""
    src = _leer_fuente()
    assert "render_revisor_temas" in src


def test_panel_carga_pestanas_revision_tres_plataformas():
    """17.1.1: la revisión de temas tiene una pestaña por plataforma
    (Facebook, TikTok, Externos) con contador de pendientes."""
    src = _leer_fuente()
    assert "Revisión de Temas" in src
    assert "fb_comments" in src
    assert "comment_id" in src
    assert "external_comments" in src
    assert "pend." in src


def test_panel_carga_revision_pasa_tabla_y_columna():
    """17.1.1: cada pestaña de revisión pasa tabla/col_id/col_texto a
    render_revisor_temas para la escritura de vuelta en la plataforma."""
    src = _leer_fuente()
    assert "tabla=" in src
    assert "col_id=" in src
    assert "col_texto=" in src


def test_panel_carga_tres_pestanas():
    """panel_carga.py define exactamente 3 pestañas: cargar, JSON, editor."""
    src = _leer_fuente()
    assert "Cargar contenido" in src
    assert "Importar JSON" in src
    assert "Editar base de datos" in src


def test_panel_carga_importa_config():
    """panel_carga.py importa TIKTOK_DB y EXTERNOS_DB de Config."""
    src = _leer_fuente()
    assert "TIKTOK_DB" in src
    assert "EXTERNOS_DB" in src


def test_panel_carga_orden_pestanas():
    """Las pestañas están en el orden: cargar, JSON, editor."""
    src = _leer_fuente()
    idx_cargar = src.index("Cargar contenido")
    idx_json = src.index("Importar JSON")
    idx_editar = src.index("Editar base de datos")
    assert idx_cargar < idx_json < idx_editar

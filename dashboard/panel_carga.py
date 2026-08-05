"""PANEL DE CARGA — Analista (app separada, SOLO LOCAL).

App Streamlit independiente del dashboard del alcalde. Aquí el analista carga
informes, evidencia y briefings hacia el pipeline de inteligencia. NO se expone
públicamente: se ejecuta en local y opera sobre la misma base de datos local que
el resto del proyecto (config.py).

Ejecutar:
    streamlit run dashboard/panel_carga.py

Mantener este panel separado de app.py asegura que el alcalde nunca vea la
opción de "cargar contenido" en su dashboard.
"""

import streamlit as st
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # path-hack para imports de src/
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "dashboard"))  # path-hack para imports de dashboard/ hermanos

from dashboard.estilos import CSS
from dashboard.estilos_override import CSS_OVERRIDE
from dashboard.dash_ui import _page_head
from dashboard.dash_ingesta import seccion_cargar_contenido, seccion_importar_json
from dashboard.editor_db import seccion_editar_db
from dashboard.dash_temas import render_revisor_temas
from dashboard.tema_aprobaciones import (
    asegurar_tabla_en_tiktok,
    asegurar_computed_tiktok,
    asegurar_computed_externos,
)
from src.config import Config, ensure_dirs
_cfg = Config()
FACEBOOK_DB = _cfg.FACEBOOK_DB
TIKTOK_DB = _cfg.TIKTOK_DB
EXTERNOS_DB = _cfg.EXTERNOS_DB
ensure_dirs(_cfg)

from config.logging_config import configurar_logging
configurar_logging()

# ─── Migraciones estructurales 8.3 ─────
asegurar_tabla_en_tiktok(TIKTOK_DB)
asegurar_computed_tiktok(TIKTOK_DB)
asegurar_computed_externos(EXTERNOS_DB)

# ─── Estado de sesión ────────────────
if "lote_ingreso" not in st.session_state:
    st.session_state["lote_ingreso"] = []

st.set_page_config(
    page_title="PANEL DE CARGA — Analista",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown(CSS, unsafe_allow_html=True)
st.markdown(CSS_OVERRIDE, unsafe_allow_html=True)

# ─── Topbar (uso interno del analista) ─────
st.markdown("""
<div class="topbar">
    <div class="topbar-brand">PANEL DE CARGA <span class="sep">/</span> <span class="who">Analista</span></div>
    <div class="topbar-meta">USO INTERNO <span class="acc">·</span> LOCAL</div>
</div>
""", unsafe_allow_html=True)

_page_head(
    "OPERACIÓN / CARGA DE CONTENIDO",
    "Centro de ingesta de informes y evidencia",
    "Cargue informes consolidados, evidencia documental y briefings diarios. Cada documento se incorpora al pipeline de inteligencia."
)

tab_carga, tab_json, tab_editor = st.tabs([
    "📥 Cargar contenido", "📥 Importar JSON", "🛠️ Editar base de datos",
])
with tab_carga:
    seccion_cargar_contenido()
with tab_json:
    seccion_importar_json()
with tab_editor:
    seccion_editar_db()

# ── Revisión manual de temas ──────────────────────────────────────────
st.markdown("---")
st.subheader("Revisión de Temas")
from src.config import Config as _Cfg
_cfg_temas = _Cfg()


def _pendientes_plataforma(db_path, tabla, col_id, col_texto):
    """Contador real de comentarios sin aprobación para una plataforma."""
    import sqlite3
    try:
        conn = sqlite3.connect(db_path)
        try:
            n = conn.execute(
                f"SELECT COUNT(*) FROM {tabla} "
                f"WHERE {col_texto} IS NOT NULL AND {col_texto} != ''"
            ).fetchone()[0]
        finally:
            conn.close()
    except Exception:
        n = 0
    from dashboard.tema_aprobaciones import ids_aprobados
    try:
        aprobados = ids_aprobados(db_path)
    except Exception:
        aprobados = set()
    return max(0, n - len(aprobados))


_PLATAFORMAS_REVISION = [
    {
        "label": "Facebook",
        "db": _cfg_temas.FACEBOOK_DB,
        "tabla": "fb_comments",
        "col_id": "comment_id",
        "col_texto": "message",
        "col_parent": "parent_comment_id",
    },
    {
        "label": "TikTok",
        "db": _cfg_temas.TIKTOK_DB,
        "tabla": "comments",
        "col_id": "id",
        "col_texto": "text",
        "col_parent": None,
    },
    {
        "label": "Externos",
        "db": _cfg_temas.EXTERNOS_DB,
        "tabla": "external_comments",
        "col_id": "comment_id",
        "col_texto": "message",
        "col_parent": None,
    },
]

if len(_PLATAFORMAS_REVISION) > 1:
    tabs_revision = st.tabs([
        f"{p['label']} ({_pendientes_plataforma(p['db'], p['tabla'], p['col_id'], p['col_texto'])} pend.)"
        for p in _PLATAFORMAS_REVISION
    ])
    for tab, p in zip(tabs_revision, _PLATAFORMAS_REVISION):
        with tab:
            render_revisor_temas(
                db_path=p["db"],
                tabla=p["tabla"],
                col_id=p["col_id"],
                col_texto=p["col_texto"],
                col_parent=p["col_parent"],
            )
else:
    p = _PLATAFORMAS_REVISION[0]
    render_revisor_temas(
        db_path=p["db"],
        tabla=p["tabla"],
        col_id=p["col_id"],
        col_texto=p["col_texto"],
        col_parent=p["col_parent"],
    )

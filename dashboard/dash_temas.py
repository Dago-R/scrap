"""UI de aprobación manual de temas (100% manual, sin IA).

Cada comentario se revisa uno por uno: el analista selecciona un tema
englobante y aprueba. La postura se deriva automáticamente de la emoción
(clasificada fuera del panel por el usuario usando colores en capturas).

Solo los comentarios aprobados cuentan en las tarjetas de Temas Emergentes.
"""

import json

from analytics.topic import classify_topic
from dashboard.tema_aprobaciones import (
    guardar_aprobacion,
    resumen_revision,
)
from dashboard.tema_taxonomia import (
    TEMAS_VISIBLES,
    TEMA_LABELS,
    EMOCIONES,
    EMOCION_LABELS,
    EMOCION_DEFAULT,
    EMOCIONES_VALIDAS,
    INTENSIDADES_POSTURA,
    INTENSIDAD_POSTURA_DEFAULT,
)

# Opciones del selector de tema: temas englobantes + 'sin tema'.
_OPCIONES = list(TEMAS_VISIBLES) + ["no_aplica"]

# Emociones agrupadas para el selector (subconjunto legible de las ~50 disponibles)
_EMOCIONES_SELECTOR = [
    # Positivas
    "serenidad", "alegria", "euforia",
    "confianza", "admiracion", "reconocimiento", "satisfaccion",
    "optimismo", "esperanza", "amor_civico",
    # Neutras / cívicas
    "calma", "interes", "expectativa", "objecion", "curiosidad",
    # Negativas leves
    "preocupacion", "aprension", "fastidio", "molestia", "melancolia",
    # Negativas fuertes
    "enojo", "furia", "ira", "reclamo",
    "desagrado", "repulsion", "indignacion_moral", "indignacion",
    "tristeza", "dolor", "ironia", "incredulidad", "ansiedad",
    "vigilancia", "agresividad", "desprecio",
]
_EMOCIONES_SELECTOR_LABELS = {k: EMOCION_LABELS.get(k, k) for k in _EMOCIONES_SELECTOR}


def _label_opcion(clave):
    if clave == "no_aplica":
        return "— Sin tema / descartar —"
    return TEMA_LABELS.get(clave, clave)


def _ids_aprobados_en_periodo(db_path):
    """IDs de comentarios que ya tienen aprobación."""
    from dashboard.tema_aprobaciones import ids_aprobados
    return ids_aprobados(db_path)


def _obtener_texto_padre(db_path, parent_comment_id, tabla="fb_comments"):
    """Obtiene el texto de un comentario padre (solo Facebook tiene parent_comment_id)."""
    if not parent_comment_id:
        return None
    try:
        import sqlite3
        conn = sqlite3.connect(db_path)
        row = conn.execute(
            f"SELECT message FROM {tabla} WHERE comment_id = ?",
            (parent_comment_id,)
        ).fetchone()
        conn.close()
        return row[0] if row else None
    except Exception:
        return None


def render_revisor_temas(db_path, tabla="fb_comments", col_id="comment_id",
                          col_texto="message", col_parent=None):
    """Renderiza la interfaz de revisión y aprobación de un comentario.

    Args:
        db_path: ruta a la base de datos.
        tabla: nombre de la tabla de comentarios.
        col_id: columna del ID del comentario.
        col_texto: columna del texto del comentario.
        col_parent: columna del comment_id padre (solo Facebook tiene
            parent_comment_id). Si es None, no se busca contexto padre.
    """
    import streamlit as st

    tiene_padre = col_parent is not None

    with st.expander("✍️ Revisar y aprobar temas", expanded=False):
        import sqlite3
        ids_ok = _ids_aprobados_en_periodo(db_path)
        try:
            conn = sqlite3.connect(db_path)
            if tiene_padre:
                rows = conn.execute(
                    f"SELECT {col_id}, {col_texto}, {col_parent}, emocion FROM {tabla} "
                    f"WHERE {col_texto} IS NOT NULL AND {col_texto} != ''"
                ).fetchall()
            else:
                rows_raw = conn.execute(
                    f"SELECT {col_id}, {col_texto}, emocion FROM {tabla} "
                    f"WHERE {col_texto} IS NOT NULL AND {col_texto} != ''"
                ).fetchall()
                rows = [(cid, msg, None, emocion) for cid, msg, emocion in rows_raw]
            conn.close()
        except Exception:
            rows = []
        pendientes = [(cid, msg, parent, emocion) for cid, msg, parent, emocion in rows
                      if cid not in ids_ok]

        st.markdown(
            f'<p style="font-size:11px;color:var(--fg-muted)">'
            f'{len(pendientes)} pendientes · {len(ids_ok)} aprobados.</p>',
            unsafe_allow_html=True,
        )

        if not pendientes:
            st.markdown(
                '<div class="status-info">No hay comentarios pendientes de revisión.</div>',
                unsafe_allow_html=True,
            )
        else:
            for cid, texto, parent_id, emocion_guardada in pendientes:
                _render_item_aprobacion(
                    db_path, tabla, col_id, col_texto, col_parent,
                    cid, texto, parent_id, emocion_guardada,
                    titulo_accion="Aprobar",
                )

    # ── Vista de aprobados: modificar tema/emoción ya guardados ──
    from dashboard.tema_aprobaciones import obtener_aprobaciones
    aprobaciones = obtener_aprobaciones(db_path)
    if aprobaciones:
        with st.expander("✅ Aprobados — modificar", expanded=False):
            st.markdown(
                '<p style="font-size:11px;color:var(--fg-muted)">'
                'Los aprobados ya cuentan en la evidencia del período. '
                'Puedes corregir el tema, la emoción o la intensidad; '
                'la reescritura es un UPDATE (INSERT OR REPLACE) sobre la misma '
                f'aprobación y vuelve a escribir el tema en la tabla {tabla}.</p>',
                unsafe_allow_html=True,
            )
            _render_aprobados(
                db_path, tabla, col_id, col_texto, col_parent,
                rows, aprobaciones,
            )


def _render_item_aprobacion(db_path, tabla, col_id, col_texto, col_parent,
                            cid, texto, parent_id, emocion_guardada,
                            titulo_accion="Aprobar", previo=None):
    """Renderiza un comentario con selectores de tema/emoción/intensidad y su botón.

    `previo` (dict de obtener_aprobaciones) precarga los valores guardados cuando
    el comentario ya está aprobado (vista de modificación).
    """
    import streamlit as st
    from dashboard.html_safety import safe_text

    texto_clean = safe_text(texto)
    st.markdown(
        f'<div style="font-size:13px;padding:8px 10px;margin:8px 0 4px 0;'
        f'background:var(--bg-elevated);border-radius:6px;border-left:3px solid var(--accent)">'
        f'«{texto_clean}»</div>',
        unsafe_allow_html=True,
    )

    if col_parent and parent_id:
        texto_padre = _obtener_texto_padre(db_path, parent_id, tabla)
        if texto_padre:
            padre_clean = safe_text(str(texto_padre))
            st.markdown(
                f'<div style="font-size:11px;padding:4px 8px;margin:0 0 6px 12px;'
                f'color:var(--fg-muted);border-left:2px solid var(--border-default)">'
                f'↩ Respondiendo a: «{padre_clean[:200]}»</div>',
                unsafe_allow_html=True,
            )

    resultado_tema = classify_topic(texto)
    tema_contado = resultado_tema.tema if resultado_tema.tema in _OPCIONES else "no_aplica"
    default_idx_tema = _OPCIONES.index(tema_contado)
    if previo and previo.get("tema") in _OPCIONES:
        default_idx_tema = _OPCIONES.index(previo["tema"])

    emo_default = emocion_guardada if emocion_guardada in _EMOCIONES_SELECTOR else EMOCION_DEFAULT
    if previo and previo.get("emocion") in _EMOCIONES_SELECTOR:
        emo_default = previo["emocion"]
    default_idx_emo = _EMOCIONES_SELECTOR.index(emo_default) if emo_default in _EMOCIONES_SELECTOR else 0

    int_default = (previo or {}).get("intensidad_postura") or INTENSIDAD_POSTURA_DEFAULT
    int_opciones = ["leve", "moderada", "fuerte"]
    default_idx_int = int_opciones.index(int_default) if int_default in int_opciones else 1

    c1, c2, c3, c4 = st.columns([4, 3, 2, 1])
    with c1:
        sel_tema = st.selectbox(
            "Tema",
            _OPCIONES,
            format_func=_label_opcion,
            key=f"sel_tema_{cid}",
            label_visibility="collapsed",
            index=default_idx_tema,
        )
    with c2:
        sel_emo = st.selectbox(
            "Emoción",
            _EMOCIONES_SELECTOR,
            format_func=lambda k: _EMOCIONES_SELECTOR_LABELS.get(k, k),
            key=f"sel_emo_{cid}",
            label_visibility="collapsed",
            index=default_idx_emo,
        )
    with c3:
        sel_intensidad = st.selectbox(
            "Intensidad",
            int_opciones,
            index=default_idx_int,
            key=f"sel_int_{cid}",
            label_visibility="collapsed",
        )
    with c4:
        if st.button(titulo_accion, key=f"ap_{cid}"):
            guardar_aprobacion(
                db_path, cid, sel_tema, texto=texto,
                tema_sugerido=tema_contado,
                tono=None, confianza=None,
                emocion=sel_emo,
                intensidad_postura=sel_intensidad,
                tabla=tabla, col_id=col_id,
            )
            st.rerun()

    if resultado_tema.n_coincidencias:
        st.caption(
            f"Léxico: {_label_opcion(tema_contado)} "
            f"({resultado_tema.n_coincidencias} coincidencia(s): "
            f"{', '.join(resultado_tema.evidence[:5])})"
        )


def _render_aprobados(db_path, tabla, col_id, col_texto, col_parent,
                      rows, aprobaciones):
    """Vista de aprobados con selectores precargados y botón de actualizar.

    Permite corregir un tema/emoción ya aprobados y filtrar por tema para
    revisar en lote.
    """
    import streamlit as st

    if not rows:
        return

    # Filtrar por tema (precargado al valor guardado)
    temas_guardados = sorted({ap.get("tema") for ap in aprobaciones.values() if ap.get("tema")})
    filtro = st.selectbox(
        "Filtrar por tema aprobado",
        ["— todos —"] + temas_guardados,
        key=f"filtro_tema_{col_id}",
    )

    for cid, msg, parent_id, emocion_guardada in rows:
        ap = aprobaciones.get(cid)
        if ap is None:
            continue
        if filtro != "— todos —" and ap.get("tema") != filtro:
            continue
        _render_item_aprobacion(
            db_path, tabla, col_id, col_texto, col_parent,
            cid, msg, parent_id, emocion_guardada,
            titulo_accion="Actualizar",
            previo=ap,
        )

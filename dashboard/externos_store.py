"""Persistencia de paginas externas y guardado de posts externos.

Modulo independiente (no toca modulo5_externos.py) para:
  - Recordar nombres de paginas externas y reusarlos en futuras cargas.
  - Insertar posts y comentarios externos reales en externos.db.

Las tablas externas (external_posts, external_comments, external_sentimiento)
usan el MISMO esquema que dashboard/modulo5_externos.py para que el dashboard
(cargar_externos en app.py) las lea sin cambios. external_pages es la lista
persistente de paginas externas que el operador reutiliza al cargar contenido.
"""

import os
import sqlite3

from src.config import Config
_cfg = Config()
EXTERNOS_DB = _cfg.EXTERNOS_DB

from dashboard._generar_id import generar_id_post


def _resolver_db(db_path=None):
    """Permite override por argumento o env var (modo prueba usa externos_test.db)."""
    return db_path or os.getenv("EXTERNOS_DB", EXTERNOS_DB)


def asegurar_tablas_externas(db_path=None):
    """Crea las tablas externas si no existen (idempotente).

    Tambien migra external_comments con columnas computed
    (sentiment, sentiment_score, topic_category, zona) para cerrar
    la brecha estructural con fb_comments (Bloque 8.3).
    """
    db = _resolver_db(db_path)
    conn = sqlite3.connect(db)
    try:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS external_posts (
                post_id TEXT PRIMARY KEY,
                page_name TEXT,
                page_url TEXT,
                message TEXT,
                created_time DATETIME,
                total_reactions INTEGER DEFAULT 0,
                comments_count INTEGER DEFAULT 0,
                post_url TEXT,
                source TEXT DEFAULT 'manual_externo',
                scraped_at DATETIME DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS external_comments (
                comment_id TEXT PRIMARY KEY,
                post_id TEXT,
                message TEXT,
                author_name TEXT DEFAULT 'Anonymous',
                created_time DATETIME,
                scraped_at DATETIME DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS external_sentimiento (
                post_id TEXT PRIMARY KEY,
                total_comentarios INTEGER,
                pct_positivo REAL,
                pct_negativo REAL,
                pct_neutral REAL,
                score_sentimiento REAL,
                comentario_mas_negativo TEXT,
                comentario_mas_positivo TEXT
            );

            CREATE TABLE IF NOT EXISTS external_pages (
                name TEXT PRIMARY KEY,
                added_at DATETIME DEFAULT CURRENT_TIMESTAMP
            );
        """)
        # Migrar columnas computed en external_comments
        from dashboard.tema_aprobaciones import _asegurar_columnas_computed
        _asegurar_columnas_computed(conn, "external_comments")
        # Migrar columnas emocion/intensidad/confianza_emocion/tema_sugerido
        from dashboard.tema_aprobaciones import _asegurar_columnas_emocion
        _asegurar_columnas_emocion(conn, "external_comments")
        conn.commit()
    finally:
        conn.close()


def listar_paginas_externas(db_path=None):
    """Devuelve la lista de nombres de paginas externas guardadas (orden alfabetico)."""
    db = _resolver_db(db_path)
    try:
        asegurar_tablas_externas(db)
        conn = sqlite3.connect(db)
        try:
            rows = conn.execute(
                "SELECT name FROM external_pages ORDER BY name COLLATE NOCASE"
            ).fetchall()
        finally:
            conn.close()
        return [r[0] for r in rows]
    except Exception:
        return []


def agregar_pagina_externa(nombre, db_path=None):
    """Guarda un nombre de pagina externa para reusarlo despues. Idempotente."""
    nombre = (nombre or "").strip()
    if not nombre:
        return False
    db = _resolver_db(db_path)
    try:
        asegurar_tablas_externas(db)
        conn = sqlite3.connect(db)
        try:
            conn.execute(
                "INSERT OR IGNORE INTO external_pages (name) VALUES (?)", (nombre,)
            )
            conn.commit()
        finally:
            conn.close()
        return True
    except Exception:
        return False


def obtener_ids_posts_externos(conn):
    """IDs de posts externos ya guardados (para deduplicar al generar nuevos IDs)."""
    try:
        rows = conn.execute("SELECT post_id FROM external_posts").fetchall()
        return {r[0] for r in rows}
    except Exception:
        return set()


def _valor_numero(campo) -> int:
    """Extrae un número de un campo que puede ser entero plano o el dict
    {'valor': n, 'confianza': ...} del contrato de extracción."""
    if campo is None:
        return 0
    if isinstance(campo, dict):
        return int(campo.get("valor") or 0)
    try:
        return int(campo or 0)
    except (TypeError, ValueError):
        return 0


def _total_reacciones(datos: dict) -> int:
    """Total de reacciones de un post externo.

    Prioridad: flat total_reactions > total del dict reacciones > suma del
    desglose (likes+loves+cares+hahas+sads+wows+angrys). El contrato de
    extracción trae las reacciones como {clave: {valor, confianza}}; sin
    este cálculo el total se guardaba siempre en 0 (17.1.14).
    """
    flat = datos.get("total_reactions")
    if flat is not None and str(flat).strip() != "":
        return _valor_numero(flat)
    reacciones = datos.get("reacciones") or {}
    if not isinstance(reacciones, dict):
        return 0
    total = _valor_numero(reacciones.get("total"))
    if total:
        return total
    return sum(
        _valor_numero(reacciones.get(k))
        for k in ("likes", "loves", "cares", "hahas", "sads", "wows", "angrys")
    )


def insertar_post_externo(conn, datos, post_id):
    """Inserta un post externo en external_posts."""
    comentarios = datos.get("comentarios") or []
    enlace = datos.get("enlace") or {}
    url = datos.get("post_url") or (
        enlace.get("valor") if isinstance(enlace, dict) else ""
    )
    page_name = datos.get("page_name") or datos.get("autor_pagina") or ""
    comments = datos.get("comments_count")
    conn.execute(
        """INSERT OR REPLACE INTO external_posts
            (post_id, page_name, page_url, message, created_time,
             total_reactions, comments_count, post_url, source)
            VALUES (?,?,?,?,?,?,?,?,?)""",
        (
            post_id,
            str(page_name or ""),
            str(datos.get("page_url", "") or ""),
            str(datos.get("message", "") or ""),
            datos.get("created_time"),
            _total_reacciones(datos),
            int(comments or len(comentarios)) if comments is not None else len(comentarios),
            str(url or ""),
            "manual_externo",
        ),
    )
    return True


def agregar_post_externo_manual(url, page_name="", total_reactions=0,
                                comments_count=0, message="", created_time=None,
                                db_path=None):
    """Crea (o actualiza) un post externo a partir de un enlace pegado a mano y
    devuelve su post_id, para marcarlo como réplica de la medalla.

    Pensado para el editor de la medalla: cuando un medio replica la publicación
    y esa nota no está en external_posts (no se cargó por el flujo normal), el
    analista pega el enlace y aquí se registra como página externa. Devuelve None
    si no se indicó ni enlace ni nombre del medio.
    """
    url = (url or "").strip()
    nombre = (page_name or "").strip()
    if not url and not nombre:
        return None
    db = _resolver_db(db_path)
    asegurar_tablas_externas(db)
    conn = sqlite3.connect(db)
    try:
        ids = obtener_ids_posts_externos(conn)
        base = url or f"{nombre}|{created_time or ''}|{(message or '')[:200]}"
        post_id = generar_id_post(base, ids)
        datos = {
            "page_name": nombre,
            "page_url": "",
            "message": message or "",
            "created_time": created_time,
            "total_reactions": int(total_reactions or 0),
            "comments_count": int(comments_count or 0),
            "post_url": url,
        }
        insertar_post_externo(conn, datos, post_id)
        if nombre:
            conn.execute(
                "INSERT OR IGNORE INTO external_pages (name) VALUES (?)", (nombre,)
            )
        conn.commit()
        return post_id
    finally:
        conn.close()


def insertar_comentario_externo(conn, comment_id, post_id, texto, autor=None,
                                 emocion=None, intensidad=None,
                                 confianza_emocion=None, tema_sugerido=None):
    """Inserta un comentario externo en external_comments."""
    conn.execute(
        """INSERT OR REPLACE INTO external_comments
            (comment_id, post_id, message, author_name, created_time,
             emocion, intensidad, confianza_emocion, tema_sugerido)
            VALUES (?,?,?,?,?,?,?,?,?)""",
        (comment_id, post_id, texto, (autor or "Anonymous"), None,
         emocion, intensidad, confianza_emocion, tema_sugerido),
    )
    return True

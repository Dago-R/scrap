"""Clasificar sentimiento y emoción de todos los comentarios y persistir en DB.

Uso:
    python -m scripts.clasificar_comentarios
    python -m scripts.clasificar_comentarios --plataforma externos
    python -m scripts.clasificar_comentarios --plataforma facebook
    python -m scripts.clasificar_comentarios --plataforma tiktok
    python -m scripts.clasificar_comentarios --forzar   # re-clasifica aunque ya tenga valor

Este script lee cada comentario de las tres DBs, corre classify_sentiment()
y classify_emotion() sobre el texto, y hace UPDATE de las columnas
sentiment, sentiment_score, emocion, intensidad donde estén vacías
(o en todos si --forzar).
"""
import argparse
import sqlite3

from src.config import Config
from analytics.sentiment import classify_sentiment
from analytics.emotion import classify_emotion

_cfg = Config()


def _classify_and_update(db_path: str, tabla: str, col_id: str, col_texto: str,
                          forzar: bool = False) -> dict:
    """Clasifica y actualiza una tabla de comentarios.

    Args:
        db_path: ruta a la DB SQLite.
        tabla: nombre de la tabla (fb_comments, comments, external_comments).
        col_id: nombre de la columna ID (comment_id, id).
        col_texto: nombre de la columna de texto (message, text).
        forzar: si True, re-clasifica aunque ya tenga valor.

    Returns:
        dict con {procesados, actualizados, omitidos, errores}.
    """
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row

    if forzar:
        where_clause = f"WHERE {col_texto} IS NOT NULL AND TRIM({col_texto}) != ''"
    else:
        where_clause = (
            f"WHERE {col_texto} IS NOT NULL AND TRIM({col_texto}) != '' "
            f"AND (sentiment IS NULL OR emocion IS NULL)"
        )

    rows = conn.execute(
        f"SELECT {col_id}, {col_texto} FROM {tabla} {where_clause}"
    ).fetchall()

    procesados = 0
    actualizados = 0
    omitidos = 0
    errores = 0

    for row in rows:
        cid = row[col_id]
        texto = row[col_texto] or ""
        procesados += 1

        if not texto.strip():
            omitidos += 1
            continue

        try:
            sent = classify_sentiment(texto)
            emo = classify_emotion(texto, es_oficial=False)

            conn.execute(
                f"UPDATE {tabla} SET "
                f"sentiment = ?, sentiment_score = ?, "
                f"emocion = ?, intensidad = ? "
                f"WHERE {col_id} = ?",
                (
                    sent.label,
                    float(sent.score),
                    emo.emocion,
                    emo.intensidad,
                    cid,
                ),
            )
            actualizados += 1
        except Exception as exc:
            print(f"  ERROR en {tabla} id={cid}: {exc}")
            errores += 1

    conn.commit()
    conn.close()
    return {
        "procesados": procesados,
        "actualizados": actualizados,
        "omitidos": omitidos,
        "errores": errores,
    }


PLATAFORMAS = {
    "facebook": (_cfg.FACEBOOK_DB, "fb_comments", "comment_id", "message"),
    "tiktok": (_cfg.TIKTOK_DB, "comments", "id", "text"),
    "externos": (_cfg.EXTERNOS_DB, "external_comments", "comment_id", "message"),
}


def main():
    parser = argparse.ArgumentParser(
        description="Clasificar sentimiento y emoción de comentarios y persistir en DB."
    )
    parser.add_argument(
        "--plataforma",
        choices=list(PLATAFORMAS.keys()),
        default=None,
        help="Procesar solo una plataforma. Sin valor: procesa las tres.",
    )
    parser.add_argument(
        "--forzar",
        action="store_true",
        help="Re-clasificar aunque las columnas ya tengan valor.",
    )
    args = parser.parse_args()

    targets = (
        {args.plataforma: PLATAFORMAS[args.plataforma]}
        if args.plataforma
        else PLATAFORMAS
    )

    total_procesados = 0
    total_actualizados = 0

    for nombre, (db_path, tabla, col_id, col_texto) in targets.items():
        print(f"\n[{nombre}] {db_path}")
        stats = _classify_and_update(db_path, tabla, col_id, col_texto, forzar=args.forzar)
        print(
            f"  procesados={stats['procesados']} "
            f"actualizados={stats['actualizados']} "
            f"omitidos={stats['omitidos']} "
            f"errores={stats['errores']}"
        )
        total_procesados += stats["procesados"]
        total_actualizados += stats["actualizados"]

    print(f"\nTotal: {total_procesados} procesados, {total_actualizados} actualizados.")


if __name__ == "__main__":
    main()

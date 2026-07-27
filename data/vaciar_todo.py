import sqlite3, os

DATA_DIR = os.environ.get("DATA_DIR", "data")

PLAN = {
    "facebook.db": [
        "fb_posts", "fb_comments", "fb_engagement", "fb_sentimiento",
        "item_embeddings", "post_categorias", "tema_clasificaciones_ia",
        "medalla_seleccion", "medalla_feedback", "series_facebook",
        "tema_aprobaciones", "problematicas", "insights", "nlp_results",
        "daily_metrics", "audit_log",
    ],
    "tiktok.db": [
        "videos", "comments", "tiktok_sentimiento", "tiktok_engagement",
        "series_tiktok",
    ],
    "externos.db": [
        "external_posts", "external_comments", "external_sentimiento",
        "external_pages", "tema_aprobaciones",
    ],
}

for dbname, tablas in PLAN.items():
    path = os.path.join(DATA_DIR, dbname)
    if not os.path.exists(path):
        print(f"  {dbname}: no existe, se salta")
        continue
    conn = sqlite3.connect(path)
    cur = conn.cursor()
    existentes = {r[0] for r in cur.execute(
        "SELECT name FROM sqlite_master WHERE type='table'"
    ).fetchall()}
    for t in tablas:
        if t not in existentes:
            continue
        antes = cur.execute(f'SELECT COUNT(*) FROM "{t}"').fetchone()[0]
        cur.execute(f'DELETE FROM "{t}"')
        print(f"  {dbname}::{t}: borradas {antes} filas")
    # Resetea contadores autoincrement si existen
    try:
        cur.execute("DELETE FROM sqlite_sequence")
    except sqlite3.OperationalError:
        pass
    conn.commit()
    cur.execute("VACUUM")
    conn.close()

print("Listo.")
"""Tests para analytics/emotion.py — clasificación léxica de emoción (31 categorías)."""
import pytest
from analytics.emotion import (
    classify_emotion, aggregate_emotions,
    INTENSIFICADORES, EMOTION_LEXICON, _detectar_intensidad_texto,
)


# ── Neutral / vacío ──

def test_emotion_neutral_texto_vacio():
    r = classify_emotion("")
    assert r.emocion == "calma"
    assert r.familia == "civica"


def test_emotion_neutral_texto_neutro():
    r = classify_emotion("La reunión es el lunes a las 3pm")
    # Texto real sin match léxico → clave propuesta, no "calma"
    assert r.emocion != "calma"
    assert "_nueva" in r.emocion or r.familia in (
        "civica", "joy", "trust", "fear", "surprise",
        "sadness", "disgust", "anger", "anticipation", "diada",
    )


def test_emotion_none():
    r = classify_emotion(None)
    assert r.emocion == "calma"


# ── Alegría (joy) ──

def test_alegria_basica():
    r = classify_emotion("Estoy muy contento con el resultado")
    assert r.emocion in ("alegria", "euforia", "serenidad")
    assert r.familia == "joy"


def test_serenidad():
    r = classify_emotion("Me siento en paz, tranquilo con todo")
    assert r.emocion == "serenidad"
    assert r.familia == "joy"
    assert r.intensidad == "leve"


def test_euforia():
    r = classify_emotion("Es espectacular eufórico increíble")
    assert r.emocion == "euforia"
    assert r.familia == "joy"
    assert r.intensidad == "intensa"


# ── Confianza (trust) ──

def test_confianza():
    r = classify_emotion("Confío en el gobierno local, respaldo su gestión")
    assert r.emocion in ("confianza", "aceptacion")
    assert r.familia == "trust"


def test_admiracion():
    r = classify_emotion("Admiro el trabajo de los maestros, excelentes")
    assert r.emocion == "admiracion"
    assert r.familia == "trust"


# ── Miedo (fear) ──

def test_preocupacion():
    r = classify_emotion("Me preocupa la inseguridad en la zona, hay peligro")
    assert r.emocion in ("preocupacion", "aprension")
    assert r.familia == "fear"


def test_terror():
    r = classify_emotion("Pánico total, miedo a salir a la calle, terror")
    assert r.emocion == "terror"
    assert r.familia == "fear"


# ── Sorpresa (surprise) ──

def test_sorpresa():
    r = classify_emotion("No esperaba esa noticia, sorprendido estoy")
    assert r.emocion in ("sorpresa", "distraccion", "asombro")
    assert r.familia == "surprise"


def test_asombro():
    r = classify_emotion("Asombroso e impactante, extraordinario")
    assert r.emocion in ("asombro", "sorpresa")
    assert r.familia == "surprise"


# ── Tristeza (sadness) ──

def test_tristeza():
    r = classify_emotion("Triste lo que pasó, me da pena")
    assert r.emocion in ("tristeza", "melancolia")
    assert r.familia == "sadness"


def test_dolor():
    r = classify_emotion("Dolor profundo por esta tragedia, sufrimiento")
    assert r.emocion in ("dolor", "tristeza")
    assert r.familia == "sadness"


# ── Desagrado (disgust) ──

def test_desagrado():
    r = classify_emotion("Desagradable la situación, fea y molesta")
    assert r.emocion in ("desagrado", "repulsion")
    assert r.familia == "disgust"


def test_repulsion():
    r = classify_emotion("asco da esta corrupción, indignación moral, repugnante")
    assert r.emocion == "repulsion"
    assert r.familia == "disgust"


# ── Enojo (anger) ──

def test_enojo():
    r = classify_emotion("Enojado y furioso con esta rabia, indignado")
    assert r.emocion in ("enojo", "furia")
    assert r.familia == "anger"


def test_furia():
    r = classify_emotion("Furia e ira, odio absoluto, basura de gobierno")
    assert r.emocion == "furia"
    assert r.familia == "anger"


def test_fastidio():
    r = classify_emotion("Harto y cansado de esta molestia constante")
    assert r.emocion in ("fastidio", "enojo")
    assert r.familia == "anger"


# ── Anticipación (anticipation) ──

def test_interes():
    r = classify_emotion("Me interesa saber más, curioso por la información")
    assert r.emocion in ("interes", "expectativa")
    assert r.familia == "anticipation"


def test_expectativa():
    r = classify_emotion("Espero que salga bien, estoy pendiente del estreno")
    assert r.emocion in ("expectativa", "interes", "optimismo")
    assert r.familia in ("anticipation", "diada")


# ── Díadas ──

def test_optimismo():
    r = classify_emotion("Tengo esperanza de que mejorará todo, saldrá adelante")
    assert r.emocion == "optimismo"
    assert r.familia == "diada"


def test_amor_civico():
    r = classify_emotion("Amor por nuestra comunidad, solidaridad y hermandad")
    assert r.emocion == "amor_civico"
    assert r.familia == "diada"


def test_desprecio():
    r = classify_emotion("Desprecio total, basura inútil, menosprecio")
    assert r.emocion == "desprecio"
    assert r.familia == "diada"


# ── Posturas cívicas ──

def test_reclamo():
    r = classify_emotion("Exijo que se solucione, demanda y queja formal")
    assert r.emocion == "reclamo"
    assert r.familia == "civica"


def test_satisfaccion():
    r = classify_emotion("Satisfecho y conforme, bien hecho, funciona bien")
    assert r.emocion == "satisfaccion"
    assert r.familia == "civica"


def test_reconocimiento():
    r = classify_emotion("Agradezco el excelente trabajo, gracias por todo")
    assert r.emocion == "reconocimiento"
    assert r.familia == "civica"


def test_calma():
    r = classify_emotion("Solo para informar, dato de referencia")
    assert r.emocion == "calma"
    assert r.familia == "civica"


# ── Intensidad ──

def test_intensidad_muy_enfatiza():
    r = classify_emotion("Muy contento y alegre con la nueva")
    if r.familia == "joy":
        assert r.intensidad in ("media", "intensa")


def test_intensidad_exclamaciones():
    r = classify_emotion("Excelente trabajo!!!")
    assert _detectar_intensidad_texto("Excelente trabajo!!!")


def test_intensidad_mayusculas():
    assert _detectar_intensidad_texto("EXCELENTE")


# ── Regla "me divierte" en publicaciones oficiales ──

def test_me_divierte_oficial():
    r = classify_emotion("Jaja me divierte mucho", es_oficial=True)
    assert r.emocion == "ironia"


def test_me_divierte_no_oficial():
    r = classify_emotion("Me divierte mucho jaja", es_oficial=False)
    assert r.emocion != "ironia"


# ── Léxico no vacío ──

def test_lexico_completo():
    """Cada una de las 31 emociones debe tener al menos una palabra semilla."""
    from dashboard.tema_taxonomia import EMOCIONES_VALIDAS
    for emo in EMOCIONES_VALIDAS:
        assert emo in EMOTION_LEXICON, f"Emoción '{emo}' sin léxico definido"
        assert len(EMOTION_LEXICON[emo]) > 0, f"Emoción '{emo}' con léxico vacío"


def test_intensificadores_no_vacio():
    assert len(INTENSIFICADORES) > 5


# ── Agregación batch ──

def test_aggregate_emotions_vacio():
    agg = aggregate_emotions([])
    assert agg["total"] == 0
    assert agg["dominante"] == "calma"


def test_aggregate_emotions_mixto():
    texts = [
        "Contento con el resultado",
        "Tristeza profunda por la tragedia",
        "Enojado con la corrupción",
        "Normal, solo informativo",
        "Excelente trabajo, agradezco",
    ]
    agg = aggregate_emotions(texts)
    assert agg["total"] == 5
    assert agg["dominante"] != ""
    assert isinstance(agg["conteo"], dict)
    assert isinstance(agg["pct"], dict)


def test_aggregate_emotions_porcentajes_suman_100():
    texts = ["Alegre", "Triste", "Enojado", "Normal", "Asombrado"]
    agg = aggregate_emotions(texts)
    total_pct = sum(agg["pct"].values())
    assert abs(total_pct - 100.0) < 1.0


def test_aggregate_emotions_familias():
    texts = ["Alegre", "Triste", "Enojado"]
    agg = aggregate_emotions(texts)
    assert len(agg["familias"]) > 0


def test_aggregate_emotions_es_oficial():
    texts = ["Me divierte jaja", "Triste situación"]
    agg = aggregate_emotions(texts, es_oficial=True)
    assert agg["total"] == 2


# ── 19.1: classify_emotion devuelve clave propuesta, no calma ──

def test_emotion_devuelve_propuesta_no_calma():
    """Texto con señal emocional real sin match léxico → devuelve clave propuesta."""
    r = classify_emotion("xyzzy flurb nobbat xyzzy")
    assert r.emocion != "calma"
    assert "_nueva" in r.emocion


# ── 19.2: Deduplicación en _registrar_propuesta ──

def test_deduplicacion_propuesta_emocion():
    """El mismo texto sin match clasificado dos veces → una sola entrada con n_ocurrencias==2."""
    import json
    from analytics._propuestas import _registrar_propuesta

    for _ in range(2):
        _registrar_propuesta(
            clave_propuesta="anger_nueva",
            ejemplo_texto="texto de prueba",
            tipo="emocion",
            familia_mas_cercana="anger",
        )

    from analytics._propuestas import _TAXONOMIAS_PATH
    import os
    path = os.path.normpath(_TAXONOMIAS_PATH)
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    anger_entries = [e for e in data if e["clave_propuesta"] == "anger_nueva"]
    assert len(anger_entries) == 1
    assert anger_entries[0]["n_ocurrencias"] == 2


# ── Patch 13.1: Regresión negativa — exclusiones del patch ──

def test_jose_no_en_lexicon():
    """'jose' es nombre propio ambiguo — NO debe estar en ningun set del lexicon."""
    all_words = set()
    for words in EMOTION_LEXICON.values():
        all_words.update(words)
    assert "jose" not in all_words


def test_gabi_no_en_lexicon():
    """'gabi' es nombre propio ambiguo — NO debe estar en ningun set del lexicon."""
    all_words = set()
    for words in EMOTION_LEXICON.values():
        all_words.update(words)
    assert "gabi" not in all_words


def test_vamos_no_en_lexicon():
    """'vamos' es uso neutro frecuente en ES salvadoreño — NO debe estar como token suelto."""
    all_words = set()
    for words in EMOTION_LEXICON.values():
        all_words.update(words)
    # Puede existir como parte de frase ("a ver si vamos"), pero no como token suelto
    assert "vamos" not in all_words


def test_santa_ana_solo_no_dispara_amor_civico():
    """Comentario que solo menciona el lugar NO debe clasificarse como amor_civico."""
    r = classify_emotion("en Santa Ana nunca arreglan nada")
    # 'santa ana' suelto no esta en amor_civico, asi que no debe ganar esa categoria
    # Puede caer en otra clave o propuesta, pero NO amor_civico
    assert r.emocion != "amor_civico"


# ── Patch 13.1: Tests positivos ──

def test_euforia_deportiva_gol():
    r = classify_emotion("Gol gol gol!!! Que victoria")
    assert r.emocion == "euforia"


def test_euforia_deportiva_golazo():
    r = classify_emotion("Golazo de la seleccion, que campeones")
    assert r.emocion == "euforia"


def test_euforia_deportiva_campeones():
    r = classify_emotion("Campeones del mundo, celebrando")
    assert r.emocion == "euforia"


def test_euforia_deportiva_victoria():
    r = classify_emotion("Victoria historica, ganamos la copa")
    assert r.emocion == "euforia"


def test_alegria_expresiones():
    r = classify_emotion("Que lindo, gran partido de la noche")
    assert r.emocion == "alegria"


def test_alegria_que_bien():
    r = classify_emotion("Que bien jugado, hermoso")
    assert r.emocion == "alegria"


def test_amor_civico_orgullo():
    r = classify_emotion("Orgullo santaneco, mi municipio es el mejor")
    assert r.emocion == "amor_civico"


def test_amor_civico_santaneco():
    r = classify_emotion("Santaneco de corazón, amo Santa Ana")
    assert r.emocion == "amor_civico"


def test_reconocimiento_gracias_alcalde():
    r = classify_emotion("Gracias alcalde por la iniciativa")
    assert r.emocion == "reconocimiento"


def test_reconocimiento_gracias_pantalla():
    r = classify_emotion("Gracias por la pantalla, excelente idea")
    assert r.emocion == "reconocimiento"


# ── 13.1.1: Regresión negativa — entradas ambiguas removidas de euforia ──

def test_eso_es_no_en_lexicon():
    """'eso es' es conector genérico — NO debe estar en ningun set del lexicon."""
    all_words = set()
    for words in EMOTION_LEXICON.values():
        all_words.update(words)
    assert "eso es" not in all_words


def test_arriba_no_en_lexicon():
    """'arriba' es ubicación frecuente — NO debe estar como token suelto."""
    all_words = set()
    for words in EMOTION_LEXICON.values():
        all_words.update(words)
    assert "arriba" not in all_words


def test_viva_no_en_lexicon():
    """'viva' es verbo vivir en subjuntivo — NO debe estar como token suelto."""
    all_words = set()
    for words in EMOTION_LEXICON.values():
        all_words.update(words)
    assert "viva" not in all_words


def test_vivan_no_en_lexicon():
    """'vivan' es verbo vivir en subjuntivo — NO debe estar como token suelto."""
    all_words = set()
    for words in EMOTION_LEXICON.values():
        all_words.update(words)
    assert "vivan" not in all_words


def test_eso_es_no_euforia_falso_positivo():
    r = classify_emotion("Eso es un problema que no arreglan")
    assert r.emocion != "euforia"


def test_arriba_no_euforia_falso_positivo():
    r = classify_emotion("Hay un poste dañado allá arriba")
    assert r.emocion != "euforia"


def test_viva_no_euforia_falso_positivo():
    r = classify_emotion("Necesitamos que la gente viva mejor")
    assert r.emocion != "euforia"


def test_euforia_positivos_siguen_tras_remocion():
    """Los casos positivos deben seguir clasificando como euforia."""
    assert classify_emotion("Gol gol gol!!! Que victoria").emocion == "euforia"
    assert classify_emotion("Golazo de la seleccion, que campeones").emocion == "euforia"
    assert classify_emotion("Campeones del mundo, celebrando").emocion == "euforia"
    assert classify_emotion("Victoria historica, ganamos la copa").emocion == "euforia"


def test_no_palabras_duplicadas_en_lexico():
    from collections import defaultdict
    from analytics.emotion import EMOTION_LEXICON
    word_to_cats = defaultdict(list)
    for cat, words in EMOTION_LEXICON.items():
        for w in words:
            word_to_cats[w].append(cat)
    duplicates = {w: cats for w, cats in word_to_cats.items() if len(cats) > 1}
    assert not duplicates, f"Palabras duplicadas: {duplicates}"

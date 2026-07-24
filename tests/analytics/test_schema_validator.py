"""Tests para analytics/schema_validator.py (T4.2)."""
import pytest
from analytics.schema_validator import validar, ValidationError, ValidationResult


def _base_valid():
    """analysis.json minimo que pasa todas las validaciones."""
    return {
        "meta": {
            "periodo": "2026-04",
            "fecha_datos_hasta": "2026-04-30",
            "generado_en": "2026-05-01T10:00:00",
        },
        "bloque1": {
            "clima_narrativo": {
                "narrativa": "Clima estable.",
                "enlaces_referencia": [],
            },
            "indice_emociones": {
                "emocion_dominante": "calma",
                "narrativa": "",
                "enlaces_referencia": [],
            },
            "intensidad": {"narrativa": "", "enlaces_referencia": []},
            "concentracion_tematica": {
                "ramas": [
                    {"tema": "seguridad", "share": 50.0, "emocion_dominante": "calma"},
                    {"tema": "movilidad", "share": 50.0, "emocion_dominante": "calma"},
                ],
                "narrativa": "",
                "enlaces_referencia": [],
            },
            "pulso_iq": {"narrativa": "", "enlaces_referencia": []},
            "metricas_rendimiento": {"narrativa": "", "enlaces_referencia": []},
        },
        "bloque2": {
            "voces_influencia": [
                {
                    "pagina": "Alcaldía",
                    "postura": "apoyo",
                    "engagement": 1500,
                    "reacciones_totales": 1000,
                    "comentarios_totales": 300,
                    "compartidos_totales": 200,
                    "narrativa": "",
                    "enlaces_referencia": [],
                },
            ],
        },
        "bloque3": {
            "puntos_friccion": [
                {
                    "tema": "seguridad",
                    "n_negativos": 45,
                    "emocion_dominante": "enojo",
                    "citas_moderadas": [],
                    "narrativa": "",
                    "enlaces_relacionados": [],
                },
            ],
            "autenticidad": {"narrativa": "", "enlaces_referencia": []},
            "velocidad_propagacion": {"narrativa": "", "enlaces_referencia": []},
            "nivel_alerta": {"alertas_cambridge": [], "narrativa": "", "enlaces_referencia": []},
        },
        "bloque4": {
            "eco_historico": {"narrativa": "", "enlaces_referencia": []},
            "leccion_aprendida": {"narrativa": "", "enlaces_referencia": []},
            "brecha_percepcion_realidad": {"narrativa": "", "enlaces_referencia": []},
            "contexto_no_visible": {"narrativa": "", "enlaces_referencia": []},
            "correlacion_contenido_reaccion": {"narrativa": "", "enlaces_referencia": []},
            "comparativa_sectorial": {"narrativa": "", "enlaces_referencia": []},
            "proyeccion_escenario": {"narrativa": "", "enlaces_referencia": []},
            "recomendacion_estrategica": {"narrativa": "", "enlaces_referencia": []},
        },
    }


def test_valido_base_es_publicable():
    r = validar(_base_valid())
    assert r.es_publicable
    assert len(r.bloqueantes()) == 0


def test_no_es_dict():
    r = validar("no soy dict")
    assert not r.es_publicable
    assert r.errores[0].codigo == "V00_NO_ES_DICT"


# ── V01 ──
def test_v01_engagement_sin_submetricas():
    d = _base_valid()
    d["bloque2"]["voces_influencia"][0]["reacciones_totales"] = 0
    d["bloque2"]["voces_influencia"][0]["comentarios_totales"] = 0
    d["bloque2"]["voces_influencia"][0]["compartidos_totales"] = 0
    r = validar(d)
    assert not r.es_publicable
    assert any(e.codigo == "V01_ENGAGEMENT_SIN_SUBMETRICAS" for e in r.errores)


def test_v01_engagement_ok_con_submetricas():
    d = _base_valid()
    r = validar(d)
    assert not any(e.codigo == "V01_ENGAGEMENT_SIN_SUBMETRICAS" for e in r.errores)


# ── V02 ──
def test_v02_shares_no_suman_100():
    d = _base_valid()
    d["bloque1"]["concentracion_tematica"]["ramas"][0]["share"] = 30
    d["bloque1"]["concentracion_tematica"]["ramas"][1]["share"] = 30
    r = validar(d)
    assert not r.es_publicable
    assert any(e.codigo == "V02_SHARES_TEMATICA_NO_SUMAN_100" for e in r.errores)


def test_v02_shares_suman_100():
    r = validar(_base_valid())
    assert not any(e.codigo == "V02_SHARES_TEMATICA_NO_SUMAN_100" for e in r.errores)


# ── V03 ──
def test_v03_friccion_sin_emocion():
    d = _base_valid()
    d["bloque3"]["puntos_friccion"][0]["emocion_dominante"] = ""
    r = validar(d)
    assert not r.es_publicable
    assert any(e.codigo == "V03_FRICCION_SIN_EMOCION" for e in r.errores)


# ── V04 ──
def test_v04_alerta_descripcion_dict():
    d = _base_valid()
    d["bloque3"]["nivel_alerta"]["alertas_cambridge"] = [
        {"tipo": "rumor", "descripcion": {"verdadero": True}},
    ]
    r = validar(d)
    assert not r.es_publicable
    assert any(e.codigo == "V04_ALERTA_DESCRIPCION_MAL_TIPADA" for e in r.errores)


def test_v04_alerta_ok():
    d = _base_valid()
    d["bloque3"]["nivel_alerta"]["alertas_cambridge"] = [
        {"tipo": "rumor", "descripcion": "Hay un rumor circulando."},
    ]
    r = validar(d)
    assert not any(e.codigo == "V04_ALERTA_DESCRIPCION_MAL_TIPADA" for e in r.errores)


# ── V05 ──
def test_v05_bloque4_mal_tipado():
    d = _base_valid()
    d["bloque4"]["eco_historico"] = "no soy dict"
    r = validar(d)
    assert not r.es_publicable
    assert any(e.codigo == "V05_BLOQUE4_MAL_TIPADO" for e in r.errores)


# ── V06 ──
def test_v06_meta_periodo_incompleto():
    d = _base_valid()
    d["meta"]["periodo"] = ""
    r = validar(d)
    assert not r.es_publicable
    assert any(e.codigo == "V06_META_PERIODO_INCOMPLETO" for e in r.errores)


def test_v06_meta_falta_generado_en():
    d = _base_valid()
    d["meta"]["generado_en"] = ""
    r = validar(d)
    assert not r.es_publicable


# ── V07 ──
def test_v07_emocion_desconocida():
    d = _base_valid()
    d["bloque1"]["indice_emociones"]["emocion_dominante"] = "super_feliz"
    r = validar(d)
    assert not r.es_publicable
    assert any(e.codigo == "V07_CATEGORIA_DESCONOCIDA" for e in r.errores)


def test_v07_postura_desconocida():
    d = _base_valid()
    d["bloque2"]["voces_influencia"][0]["postura"] = "neutra_total"
    r = validar(d)
    assert not r.es_publicable
    assert any(e.codigo == "V07_CATEGORIA_DESCONOCIDA" for e in r.errores)


def test_v07_tema_desconocido():
    d = _base_valid()
    d["bloque1"]["concentracion_tematica"]["ramas"][0]["tema"] = "tema_fantasma"
    r = validar(d)
    assert not r.es_publicable


def test_v07_tema_propuesta_pendiente_es_advertencia():
    d = _base_valid()
    d["bloque1"]["concentracion_tematica"]["ramas"][0]["tema"] = "tema_nuevo_ahi"
    r = validar(d)
    assert r.es_publicable
    v07_errors = [e for e in r.errores if e.codigo == "V07_CATEGORIA_DESCONOCIDA"
                  and "tema" in e.seccion]
    assert len(v07_errors) == 1
    assert v07_errors[0].severidad == "advertencia"
    assert "propuesta pendiente" in v07_errors[0].mensaje_tecnico


def test_v07_tema_no_propuesta_es_bloqueante():
    d = _base_valid()
    d["bloque1"]["concentracion_tematica"]["ramas"][0]["tema"] = "tema_no_registrado"
    r = validar(d)
    assert not r.es_publicable
    v07_errors = [e for e in r.errores if e.codigo == "V07_CATEGORIA_DESCONOCIDA"
                  and "tema" in e.seccion]
    assert any(e.severidad == "bloqueante" for e in v07_errors)


def test_v07_emocion_propuesta_pendiente_es_advertencia():
    d = _base_valid()
    d["bloque1"]["indice_emociones"]["emocion_dominante"] = "trust_nueva"
    r = validar(d)
    assert r.es_publicable
    v07_errors = [e for e in r.errores if e.codigo == "V07_CATEGORIA_DESCONOCIDA"
                  and "emocion_dominante" in e.seccion]
    assert len(v07_errors) == 1
    assert v07_errors[0].severidad == "advertencia"


def test_v07_emocion_no_propuesta_es_bloqueante():
    d = _base_valid()
    d["bloque1"]["indice_emociones"]["emocion_dominante"] = "super_feliz"
    r = validar(d)
    assert not r.es_publicable
    v07_errors = [e for e in r.errores if e.codigo == "V07_CATEGORIA_DESCONOCIDA"
                  and "emocion_dominante" in e.seccion]
    assert any(e.severidad == "bloqueante" for e in v07_errors)


# ── V08 ──
def test_v08_narrativa_cita_cifras_sin_enlaces():
    d = _base_valid()
    d["bloque1"]["clima_narrativo"]["narrativa"] = "Hay 150 comentarios negativos."
    d["bloque1"]["clima_narrativo"]["enlaces_referencia"] = []
    r = validar(d)
    assert r.es_publicable  # advertencia, no bloqueante
    assert any(e.codigo == "V08_NARRATIVA_SIN_ENLACES" for e in r.errores)


def test_v08_narrativa_con_enlaces_ok():
    d = _base_valid()
    d["bloque1"]["clima_narrativo"]["narrativa"] = "Hay 150 comentarios negativos."
    d["bloque1"]["clima_nistrativa"] = {"narrativa": "", "enlaces_referencia": []}
    d["bloque1"]["clima_narrativo"]["enlaces_referencia"] = ["https://ejemplo.com"]
    r = validar(d)
    assert not any(e.codigo == "V08_NARRATIVA_SIN_ENLACES" for e in r.errores)


# ── V09 ──
def test_v09_placeholder_sin_resolver():
    d = _base_valid()
    d["bloque1"]["clima_narrativo"]["narrativa"] = "La seguridad tiene {tema_share_seguridad}%"
    r = validar(d)
    assert r.es_publicable  # advertencia, no bloqueante
    assert any(e.codigo == "V09_PLACEHOLDER_SIN_RESOLVER" for e in r.errores)


def test_v09_narrativa_sin_placeholders():
    d = _base_valid()
    d["bloque1"]["clima_narrativo"]["narrativa"] = "Narrativa sin placeholders."
    r = validar(d)
    assert not any(e.codigo == "V09_PLACEHOLDER_SIN_RESOLVER" for e in r.errores)


def test_v09_narrativa_vacia():
    d = _base_valid()
    d["bloque1"]["clima_narrativo"]["narrativa"] = ""
    r = validar(d)
    assert not any(e.codigo == "V09_PLACEHOLDER_SIN_RESOLVER" for e in r.errores)


# ── V10 ──
def test_v10_valor_negativo():
    d = _base_valid()
    d["bloque2"]["voces_influencia"][0]["engagement"] = -5
    r = validar(d)
    assert not r.es_publicable
    assert any(e.codigo == "V10_VALOR_NEGATIVO" for e in r.errores)


def test_v10_engagement_sin_submetricas():
    d = _base_valid()
    d["bloque2"]["voces_influencia"][0]["reacciones_totales"] = 0
    d["bloque2"]["voces_influencia"][0]["comentarios_totales"] = 0
    d["bloque2"]["voces_influencia"][0]["compartidos_totales"] = 0
    r = validar(d)
    assert not r.es_publicable  # V01 catches this as bloqueante


def test_v10_share_negativo():
    d = _base_valid()
    d["bloque1"]["concentracion_tematica"]["ramas"][0]["share"] = -10
    r = validar(d)
    assert not r.es_publicable
    assert any(e.codigo == "V10_SHARE_NEGATIVO" for e in r.errores)


# ── V11 ──
def test_v11_tema_no_valido():
    d = _base_valid()
    d["bloque1"]["concentracion_tematica"]["ramas"][0]["tema"] = "tema_inventado"
    r = validar(d)
    assert any(e.codigo == "V11_TEMA_NO_VALIDO" for e in r.errores)


def test_v11_tema_valido():
    d = _base_valid()
    r = validar(d)
    assert not any(e.codigo == "V11_TEMA_NO_VALIDO" for e in r.errores)


# ── V12 ──
def test_v12_narrativa_vacia_con_datos():
    """V12: narrativa vacia con datos sustantivos genera advertencia."""
    d = _base_valid()
    d["bloque1"]["clima_narrativo"]["narrativa"] = ""
    d["bloque1"]["clima_narrativo"]["n_total_comentarios"] = 200
    r = validar(d)
    assert r.es_publicable  # advertencia, no bloqueante
    assert any(e.codigo == "V12_NARRATIVA_VACIA_CON_DATOS" for e in r.errores)


def test_v12_narrativa_vacia_sin_datos():
    """V12: narrativa vacia sin datos no genera advertencia para esa seccion."""
    d = _base_valid()
    d["bloque1"]["clima_narrativo"]["narrativa"] = ""
    d["bloque1"]["clima_narrativo"]["n_total_comentarios"] = 0
    r = validar(d)
    # No debe haber V12 para clima_narrativo especificamente
    assert not any(e.codigo == "V12_NARRATIVA_VACIA_CON_DATOS"
                   and "clima_narrativo" in e.seccion
                   for e in r.errores)


def test_v12_narrativa_con_texto_ok():
    """V12: narrativa con texto no genera advertencia para esa seccion."""
    d = _base_valid()
    d["bloque1"]["clima_narrativo"]["narrativa"] = "Clima positivo."
    r = validar(d)
    # No debe haber V12 para clima_narrativo especificamente
    assert not any(e.codigo == "V12_NARRATIVA_VACIA_CON_DATOS"
                   and "clima_narrativo" in e.seccion
                   for e in r.errores)


def test_v12_voz_con_engagement_vacia():
    """V12: voz con engagement pero narrativa vacia."""
    d = _base_valid()
    d["bloque2"]["voces_influencia"][0]["narrativa"] = ""
    r = validar(d)
    assert any(e.codigo == "V12_NARRATIVA_VACIA_CON_DATOS"
               and "voces_influencia" in e.seccion
               for e in r.errores)


def test_v12_friccion_con_negativos_vacia():
    """V12: friccion con n_negativos pero narrativa vacia."""
    d = _base_valid()
    d["bloque3"]["puntos_friccion"][0]["narrativa"] = ""
    r = validar(d)
    assert any(e.codigo == "V12_NARRATIVA_VACIA_CON_DATOS"
               and "puntos_friccion" in e.seccion
               for e in r.errores)


# ── V13 ──
def test_v13_narrativa_con_cifras_sin_enlaces():
    """V13: narrativa con cifras pero enlaces vacios genera advertencia."""
    d = _base_valid()
    d["bloque1"]["clima_narrativo"]["narrativa"] = "Hay 150 comentarios negativos."
    d["bloque1"]["clima_narrativo"]["enlaces_referencia"] = []
    r = validar(d)
    assert r.es_publicable  # advertencia
    assert any(e.codigo == "V13_NARRATIVA_SIN_EVIDENCIA" for e in r.errores)


def test_v13_narrativa_con_cifras_con_enlaces():
    """V13: narrativa con cifras y enlaces OK."""
    d = _base_valid()
    d["bloque1"]["clima_narrativo"]["narrativa"] = "Hay 150 comentarios negativos."
    d["bloque1"]["clima_narrativo"]["enlaces_referencia"] = ["https://fb.com/post1"]
    r = validar(d)
    assert not any(e.codigo == "V13_NARRATIVA_SIN_EVIDENCIA" for e in r.errores)


def test_v13_narrativa_sin_cifras():
    """V13: narrativa sin cifras no genera advertencia."""
    d = _base_valid()
    d["bloque1"]["clima_narrativo"]["narrativa"] = "Clima estable sin incidentes."
    d["bloque1"]["clima_narrativo"]["enlaces_referencia"] = []
    r = validar(d)
    assert not any(e.codigo == "V13_NARRATIVA_SIN_EVIDENCIA" for e in r.errores)


def test_v13_narrativa_vacia():
    """V13: narrativa vacia no genera advertencia."""
    d = _base_valid()
    d["bloque1"]["clima_narrativo"]["narrativa"] = ""
    r = validar(d)
    assert not any(e.codigo == "V13_NARRATIVA_SIN_EVIDENCIA" for e in r.errores)


def test_v13_friccion_con_cifras_sin_enlaces():
    """V13: narrativa de friccion con cifras y enlaces_relacionados vacios."""
    d = _base_valid()
    d["bloque3"]["puntos_friccion"][0]["narrativa"] = "100 comentarios criticos en seguridad."
    d["bloque3"]["puntos_friccion"][0]["enlaces_relacionados"] = []
    r = validar(d)
    assert any(e.codigo == "V13_NARRATIVA_SIN_EVIDENCIA"
               and "puntos_friccion" in e.seccion
               for e in r.errores)


def test_v13_voz_con_cifras_porcentaje_sin_enlaces():
    """V13: narrativa con porcentaje sin enlaces."""
    d = _base_valid()
    d["bloque2"]["voces_influencia"][0]["narrativa"] = "Esta pagina tiene 45% engagement."
    d["bloque2"]["voces_influencia"][0]["enlaces_referencia"] = []
    r = validar(d)
    assert any(e.codigo == "V13_NARRATIVA_SIN_EVIDENCIA"
               and "voces_influencia" in e.seccion
               for e in r.errores)


# ── 10.1: V13 exemption for aggregate sections ──

def test_v13_exenta_intensidad():
    """10.1: intensidad es metrica agregada, V13 no debe marcar advertencia."""
    d = _base_valid()
    d["bloque1"]["intensidad"]["narrativa"] = "Se registraron 200 comentarios."
    d["bloque1"]["intensidad"]["enlaces_referencia"] = []
    r = validar(d)
    assert not any(e.codigo == "V13_NARRATIVA_SIN_EVIDENCIA"
                   and "intensidad" in e.seccion
                   for e in r.errores)


def test_v13_exenta_pulso_iq():
    """10.1: pulso_iq es indice compuesto, V13 no debe marcar advertencia."""
    d = _base_valid()
    d["bloque1"]["pulso_iq"]["narrativa"] = "El indice alcanzo 75 puntos."
    d["bloque1"]["pulso_iq"]["enlaces_referencia"] = []
    r = validar(d)
    assert not any(e.codigo == "V13_NARRATIVA_SIN_EVIDENCIA"
                   and "pulso_iq" in e.seccion
                   for e in r.errores)


def test_v13_exenta_metricas_rendimiento():
    """10.1: metricas_rendimiento es metrica agregada, V13 no debe marcar."""
    d = _base_valid()
    d["bloque1"]["metricas_rendimiento"]["narrativa"] = "ER del 3.5%."
    d["bloque1"]["metricas_rendimiento"]["enlaces_referencia"] = []
    r = validar(d)
    assert not any(e.codigo == "V13_NARRATIVA_SIN_EVIDENCIA"
                   and "metricas_rendimiento" in e.seccion
                   for e in r.errores)


def test_v13_exenta_autenticidad():
    """10.1: autenticidad es metrica agregada, V13 no debe marcar."""
    d = _base_valid()
    d["bloque3"]["autenticidad"]["narrativa"] = "95% organico, 5% coordinado."
    d["bloque3"]["autenticidad"]["enlaces_referencia"] = []
    r = validar(d)
    assert not any(e.codigo == "V13_NARRATIVA_SIN_EVIDENCIA"
                   and "autenticidad" in e.seccion
                   for e in r.errores)


def test_v13_exenta_velocidad_propagacion():
    """10.1: velocidad_propagacion es metrica agregada, V13 no debe marcar."""
    d = _base_valid()
    d["bloque3"]["velocidad_propagacion"]["narrativa"] = "Proyeccion de 50 comentarios/dia."
    d["bloque3"]["velocidad_propagacion"]["enlaces_referencia"] = []
    r = validar(d)
    assert not any(e.codigo == "V13_NARRATIVA_SIN_EVIDENCIA"
                   and "velocidad_propagacion" in e.seccion
                   for e in r.errores)


def test_v13_exenta_bloque4_secciones():
    """10.1: las 8 secciones de bloque4 son analisis estrategico, V13 exempt."""
    d = _base_valid()
    for sec in ["eco_historico", "leccion_aprendida", "brecha_percepcion_realidad",
                "contexto_no_visible", "correlacion_contenido_reaccion",
                "comparativa_sectorial", "proyeccion_escenario", "recomendacion_estrategica"]:
        d["bloque4"][sec]["narrativa"] = "El engagement fue del 5% con 200 posts."
        d["bloque4"][sec]["enlaces_referencia"] = []
    r = validar(d)
    for sec in ["eco_historico", "leccion_aprendida", "brecha_percepcion_realidad",
                "contexto_no_visible", "correlacion_contenido_reaccion",
                "comparativa_sectorial", "proyeccion_escenario", "recomendacion_estrategica"]:
        assert not any(e.codigo == "V13_NARRATIVA_SIN_EVIDENCIA"
                       and sec in e.seccion
                       for e in r.errores), f"V13 should be exempt for {sec}"


def test_v13_no_exenta_clima_narrativo():
    """10.1: clima_narrativo NO esta exempto, sigue generando advertencia."""
    d = _base_valid()
    d["bloque1"]["clima_narrativo"]["narrativa"] = "Hay 150 comentarios negativos."
    d["bloque1"]["clima_narrativo"]["enlaces_referencia"] = []
    r = validar(d)
    assert any(e.codigo == "V13_NARRATIVA_SIN_EVIDENCIA"
               and "clima_narrativo" in e.seccion
               for e in r.errores)


def test_v13_no_exenta_voces():
    """10.1: voces_influencia NO esta exempto, sigue generando advertencia."""
    d = _base_valid()
    d["bloque2"]["voces_influencia"][0]["narrativa"] = "45% engagement."
    d["bloque2"]["voces_influencia"][0]["enlaces_referencia"] = []
    r = validar(d)
    assert any(e.codigo == "V13_NARRATIVA_SIN_EVIDENCIA"
               and "voces_influencia" in e.seccion
               for e in r.errores)


def test_v13_no_exenta_friccion():
    """10.1: puntos_friccion NO esta exempto, sigue generando advertencia."""
    d = _base_valid()
    d["bloque3"]["puntos_friccion"][0]["narrativa"] = "100 comentarios criticos."
    d["bloque3"]["puntos_friccion"][0]["enlaces_relacionados"] = []
    r = validar(d)
    assert any(e.codigo == "V13_NARRATIVA_SIN_EVIDENCIA"
               and "puntos_friccion" in e.seccion
               for e in r.errores)


# ── 10.6.1: End-to-end V13 test via construir_analysis ──

def test_v13_end_to_end_construir_analysis():
    """10.6.1: V13 exemptions work correctly in the real pipeline flow.

    Runs construir_analysis() with representative data, then populates
    narratives with figures (simulating Claude output), and confirms:
    - Non-exempt sections WITH evidence → V13 does NOT fire (positive case)
    - Non-exempt sections WITHOUT evidence → V13 fires (negative case)
    - Exempt sections WITHOUT evidence → V13 does NOT fire
    """
    from analytics.report import construir_analysis

    contexto = [
        {"id": "c1", "texto": "Estoy furioso con todo", "post_id": "p1", "plataforma": "facebook"},
        {"id": "c2", "texto": "Qué alegría, me encanta", "post_id": "p2", "plataforma": "facebook"},
        {"id": "c3", "texto": "Muy triste lo que pasó", "post_id": "p3", "plataforma": "facebook"},
        {"id": "c4", "texto": "Indignado completamente", "post_id": "p4", "plataforma": "facebook"},
    ]
    aprobaciones = [
        {"id": 1, "categoria": "seguridad", "label": "Seguridad",
         "pct": 60.0, "doc_count": 120, "apoyo": 30, "critica": 70, "neutral": 20,
         "pct_apoyo": 25.0, "pct_critica": 58.3, "pct_neutral": 16.7, "saldo": -40,
         "ejemplo": "", "ejemplo_critica": "", "emociones": {}, "emocion_dominante": "calma"},
        {"id": 2, "categoria": "movilidad", "label": "Movilidad",
         "pct": 40.0, "doc_count": 80, "apoyo": 50, "critica": 20, "neutral": 10,
         "pct_apoyo": 62.5, "pct_critica": 25.0, "pct_neutral": 12.5, "saldo": 30,
         "ejemplo": "", "ejemplo_critica": "", "emociones": {}, "emocion_dominante": "calma"},
    ]

    data = construir_analysis(
        aprobaciones, "2026-04", "2026-04-30",
        comentarios_texts=[c["texto"] for c in contexto],
        comentarios_con_contexto=contexto,
    )

    # ── Case A: Non-exempt sections WITH enlaces_referencia → V13 does NOT fire ──
    data["bloque1"]["clima_narrativo"]["narrativa"] = "150 comentarios analizados."
    data["bloque1"]["clima_narrativo"]["enlaces_referencia"] = ["https://fb.com/post1"]
    data["bloque1"]["indice_emociones"]["narrativa"] = "La emoción dominante es enojo con 50%."
    data["bloque1"]["indice_emociones"]["enlaces_referencia"] = ["https://fb.com/post2"]
    data["bloque1"]["concentracion_tematica"]["narrativa"] = "Seguridad concentra 60%."
    data["bloque1"]["concentracion_tematica"]["enlaces_referencia"] = ["https://fb.com/post3"]

    r_with = validar(data)

    for sec in ["bloque1.clima_narrativo", "bloque1.indice_emociones",
                "bloque1.concentracion_tematica"]:
        assert not any(e.codigo == "V13_NARRATIVA_SIN_EVIDENCIA"
                       and e.seccion == sec
                       for e in r_with.errores), \
            f"V13 must NOT fire for {sec} when it has evidence links"

    # ── Case B: Same sections WITHOUT enlaces → V13 fires ──
    data["bloque1"]["clima_narrativo"]["enlaces_referencia"] = []
    data["bloque1"]["indice_emociones"]["enlaces_referencia"] = []
    data["bloque1"]["concentracion_tematica"]["enlaces_referencia"] = []

    r_without = validar(data)

    for sec in ["bloque1.clima_narrativo", "bloque1.indice_emociones",
                "bloque1.concentracion_tematica"]:
        assert any(e.codigo == "V13_NARRATIVA_SIN_EVIDENCIA"
                   and e.seccion == sec
                   for e in r_without.errores), \
            f"V13 must fire for {sec} (non-exempt) when evidence links are empty"

    # ── Case C: Exempt sections WITH figures but NO enlaces → V13 must NOT fire ──
    data["bloque1"]["intensidad"]["narrativa"] = "200 comentarios este mes."
    data["bloque1"]["intensidad"]["enlaces_referencia"] = []
    data["bloque1"]["pulso_iq"]["narrativa"] = "Indice de 75 puntos."
    data["bloque1"]["pulso_iq"]["enlaces_referencia"] = []
    data["bloque1"]["metricas_rendimiento"]["narrativa"] = "ER del 3.5%."
    data["bloque1"]["metricas_rendimiento"]["enlaces_referencia"] = []
    data["bloque3"]["autenticidad"]["narrativa"] = "95% organico."
    data["bloque3"]["autenticidad"]["enlaces_referencia"] = []
    data["bloque3"]["velocidad_propagacion"]["narrativa"] = "Proyeccion de 50 comentarios/dia."
    data["bloque3"]["velocidad_propagacion"]["enlaces_referencia"] = []
    for sec in ["eco_historico", "leccion_aprendida", "brecha_percepcion_realidad",
                "contexto_no_visible", "correlacion_contenido_reaccion",
                "comparativa_sectorial", "proyeccion_escenario", "recomendacion_estrategica"]:
        data["bloque4"][sec]["narrativa"] = "El engagement fue del 5% con 200 posts."
        data["bloque4"][sec]["enlaces_referencia"] = []

    r_exempt = validar(data)

    exempt_sections = [
        "bloque1.intensidad", "bloque1.pulso_iq", "bloque1.metricas_rendimiento",
        "bloque3.autenticidad", "bloque3.velocidad_propagacion",
        "bloque4.eco_historico", "bloque4.leccion_aprendida",
        "bloque4.brecha_percepcion_realidad", "bloque4.contexto_no_visible",
        "bloque4.correlacion_contenido_reaccion", "bloque4.comparativa_sectorial",
        "bloque4.proyeccion_escenario", "bloque4.recomendacion_estrategica",
    ]
    for sec in exempt_sections:
        assert not any(e.codigo == "V13_NARRATIVA_SIN_EVIDENCIA"
                       and e.seccion == sec
                       for e in r_exempt.errores), \
            f"V13 must NOT fire for exempt section {sec}"


# ── ValidationResult helpers ──
def test_validation_result_bloqueantes():
    r = ValidationResult()
    r.errores.append(ValidationError("X", "y", "bloqueante", "t", "h"))
    r.errores.append(ValidationError("Z", "w", "advertencia", "t", "h"))
    assert not r.es_publicable
    assert len(r.bloqueantes()) == 1
    assert len(r.advertencias()) == 1

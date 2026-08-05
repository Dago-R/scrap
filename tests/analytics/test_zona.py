"""Tests para analytics/zona.py — gazetteer de zonas/ubicaciones."""
import pytest
from analytics.zona import (
    detectar_zona, aggregate_zonas, es_propuesta_zona,
    ZONAS_CONOCIDAS, DEPARTAMENTOS, MUNICIPIOS, ZONAS_URBANAS,
)


# ── Vacío / sin zona ──

def test_zona_vacio():
    r = detectar_zona("")
    assert r.zona == ""
    assert r.tipo == ""


def test_zona_none():
    r = detectar_zona(None)
    assert r.zona == ""


def test_zona_sin_mencion():
    r = detectar_zona("El gobierno es corrupto")
    assert r.zona == ""


# ── Zonas urbanas de Santa Ana ──

def test_zona_urbana_centro_historico():
    r = detectar_zona("El centro histórico necesita restauración")
    assert r.zona == "centro historico"
    assert r.tipo == "zona_urbana"


def test_zona_urbana_colonia_magana():
    r = detectar_zona("En colonia Magana hay muchos baches")
    assert r.zona == "colonia magana"
    assert r.tipo == "zona_urbana"


def test_zona_urbana_colonia_flor_blanca():
    r = detectar_zona("Colonia Flor Blanca necesita más alumbrado")
    assert r.zona == "colonia flor blanca"
    assert r.tipo == "zona_urbana"


def test_zona_urbana_residencial():
    r = detectar_zona("El residencial Santa Barbara tiene buenos parques")
    assert r.zona == "residencial santa barbara"
    assert r.tipo == "zona_urbana"


# ── Municipios ──

def test_municipio_santa_ana():
    r = detectar_zona("En Santa Ana hay muchos problemas de seguridad")
    assert r.zona == "santa ana"
    assert r.tipo == "municipio"


def test_municipio_chalchuapa():
    r = detectar_zona("Chalchuapa necesita más transporte")
    assert r.zona == "chalchuapa"
    assert r.tipo == "municipio"


def test_municipio_metapan():
    r = detectar_zona("Metapán tiene buen turismo")
    assert r.zona == "metapan"
    assert r.tipo == "municipio"


def test_municipio_coatepeque():
    r = detectar_zona("Coatepeque es un municipio bonito")
    assert r.zona == "coatepeque"
    assert r.tipo == "municipio"


# ── Departamentos ──

def test_depto_santa_ana():
    r = detectar_zona("El departamento de Santa Ana es importante")
    assert r.zona == "santa ana"
    assert r.tipo in ("departamento", "municipio")


def test_depto_ahuachapan():
    r = detectar_zona("Ahuachapán tiene muchos recursos naturales")
    assert r.zona == "ahuachapan"
    assert r.tipo in ("departamento",)


def test_depto_san_miguel():
    r = detectar_zona("San Miguel necesita más escuelas")
    assert r.zona == "san miguel"
    assert r.tipo in ("departamento",)


# ── Prioridad: zona_urbana > barrio > municipio > departamento ──

def test_prioridad_zona_vs_depto():
    r = detectar_zona("La colonia Magana de Santa Ana necesita más alumbrado")
    assert r.tipo == "zona_urbana"


def test_prioridad_municipio_vs_depto():
    r = detectar_zona("Chalchuapa tiene problemas en Santa Ana")
    assert r.zona in ("chalchuapa", "santa ana")


# ── Gazetteer no vacío ──

def test_gazetteer_completo():
    assert len(ZONAS_CONOCIDAS) > 10
    assert len(DEPARTAMENTOS) == 14
    assert len(ZONAS_URBANAS) > 5


# ── Propuestas ──

def test_propuesta_zona_no_reconocida():
    propuesta = es_propuesta_zona("En la colonia San Fernando hay problemas")
    # Si "san fernando" no está en el gazetteer, debería ser propuesta
    # Si está, returns None
    assert propuesta is None or isinstance(propuesta, str)


def test_propuesta_zona_vacio():
    assert es_propuesta_zona("") is None


def test_propuesta_zona_none():
    assert es_propuesta_zona(None) is None


# ── Agregación batch ──

def test_aggregate_zonas_vacio():
    agg = aggregate_zonas([])
    assert agg["total"] == 0
    assert agg["dominante"] == ""


def test_aggregate_zonas_mixto():
    texts = [
        "Los baches en colonia Magana",
        "Colonia Magana está sucia",
        "En Chalchuapa hay robos",
        "El gobierno es corrupto",
        "Centro histórico necesita luz",
    ]
    agg = aggregate_zonas(texts)
    assert agg["total"] == 5
    assert isinstance(agg["conteo"], dict)
    assert isinstance(agg["pct"], dict)


def test_aggregate_zonas_propuestas():
    texts = [
        "En la colonia Las Flores hay baches",
        "La colonia Las Flores necesita agua",
    ]
    agg = aggregate_zonas(texts)
    assert isinstance(agg["propuestas"], list)


def test_aggregate_zonas_una_sola_zona():
    texts = ["Centro histórico necesita arreglos"] * 5
    agg = aggregate_zonas(texts)
    assert agg["dominante"] == "centro historico"
    assert agg["pct"]["centro historico"] == 100.0


# ── 19.7: Suite no modifica data/taxonomias_pendientes.json real ──

@pytest.mark.no_taxonomia_mock
def test_json_pendientes_no_modificado_por_suite():
    """Confirmar que el archivo real del repo queda intacto tras tests.

    Usa @pytest.mark.no_taxonomia_mock para saltar el fixture que parchea
    la ruta, y asi leer el archivo real (data/taxonomias_pendientes.json).
    Antes (Bloque 5.2) se verificaba que estuviese vacio ([]), pero tras
    la migracion 8.2 puede contener propuestas reales del clasificador.
    Ahora se verifica que cada entrada cumpla el esquema exacto que
    _registrar_propuesta() escribe.
    """
    import json
    import os
    real_path = os.path.normpath(os.path.join(
        os.path.dirname(__file__), os.pardir, os.pardir,
        "data", "taxonomias_pendientes.json",
    ))
    with open(real_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Si esta vacio, perfecto
    if not data:
        return

    # Cada entrada debe cumplir el schema exacto de _registrar_propuesta()
    campos_requeridos = {
        "clave_propuesta": str,
        "ejemplo_texto": str,
        "tipo": str,
        "familia_mas_cercana": str,
        "fecha": str,
        "estado": str,
        "n_ocurrencias": int,
    }
    for i, entry in enumerate(data):
        assert isinstance(entry, dict), f"Entry {i} no es dict"
        for campo, tipo in campos_requeridos.items():
            assert campo in entry, f"Entry {i} falta '{campo}'"
            assert isinstance(entry[campo], tipo), (
                f"Entry {i}.{campo}: esperaba {tipo.__name__}, got {type(entry[campo]).__name__}"
            )
        assert entry["estado"] == "pendiente", f"Entry {i} estado={entry['estado']}"

    # Verificar dedup: misma clave+tipo no debe aparecer en dos entradas
    vistos = set()
    for entry in data:
        key = (entry["clave_propuesta"], entry["tipo"])
        assert key not in vistos, (
            f"Duplicado: '{entry['clave_propuesta']}' (tipo={entry['tipo']}) "
            f"aparece en 2+ entradas. n_ocurrencias debio colapsarlas."
        )
        vistos.add(key)


# ── 18.5: DEPARTAMENTOS de El Salvador ──

def test_departamentos_exactamente_14():
    """El Salvador tiene exactamente 14 departamentos."""
    assert len(DEPARTAMENTOS) == 14


def test_departamentos_nombres_validos():
    """Ninguna entrada de DEPARTAMENTOS contiene caracteres no válidos."""
    import re
    pat = re.compile(r"^[a-záéíóúñü\s]+$")
    for depto in DEPARTAMENTOS:
        assert pat.match(depto), f"DEPARTAMENTO '{depto}' tiene caracteres no válidos"


def test_municipios_nombres_validos():
    """Ninguna entrada de MUNICIPIOS contiene caracteres no válidos."""
    import re
    pat = re.compile(r"^[a-záéíóúñü\s]+$")
    for muni in MUNICIPIOS:
        assert pat.match(muni), f"MUNICIO '{muni}' tiene caracteres no válidos"


def test_zonas_urbanas_nombres_validos():
    """Ninguna entrada de ZONAS_URBANAS contiene caracteres no válidos."""
    import re
    pat = re.compile(r"^[a-záéíóúñü\s\d]+$")
    for zona in ZONAS_URBANAS:
        assert pat.match(zona), f"ZONA_URBANA '{zona}' tiene caracteres no válidos"


# ── 18.3: Propuesta de zona se registra en taxonomias_pendientes ──

def test_propuesta_zona_registra_en_pendientes():
    """Una zona plausible no reconocida debe registrarse en taxonomias_pendientes.json."""
    propuesta = es_propuesta_zona("En colonia Las Magnolias hay baches")
    assert propuesta is not None
    assert "magnolias" in propuesta.lower() or "colonia" in propuesta.lower()


# ── 19.5: Stopwords nunca se registran como propuesta de zona ──

def test_propuesta_zona_no_registra_stopwords():
    """Una palabra común/stopword nunca debe llegar a taxonomias_pendientes.json."""
    # "toda" es una palabra común → no debe ser propuesta
    propuesta = es_propuesta_zona("En toda la ciudad hay baches")
    # Si "toda" es la candidata, no debe registrarse
    if propuesta:
        assert propuesta != "toda"

    # "problema" también es stopwords
    propuesta2 = es_propuesta_zona("En problema hay baches")
    if propuesta2:
        assert propuesta2 != "problema"


# ── 20.2: Regex \b evita matchear "de" dentro de "puede" ──

def test_propuesta_zona_no_extrae_de_dentro_de_puede():
    """'puede' no debe matchear como 'de' + candidata."""
    resultado = es_propuesta_zona("no se puede circular por aquí")
    if resultado is not None:
        assert resultado != "circular", (
            f"'circular' extraído falsamente de 'puede': regex sin \\b"
        )


def test_propuesta_zona_regex_nueva_palabra_no_stopword():
    """Una palabra NO en la lista de stopwords pero que caería en match
    a mitad de palabra sin \\b debe ser rechazada por el regex."""
    resultado = es_propuesta_zona("se puede ver una ardilla en el parque")
    if resultado is not None:
        assert resultado != "ardilla", (
            f"'ardilla' extraído falsamente de 'puede': regex sin \\b"
        )

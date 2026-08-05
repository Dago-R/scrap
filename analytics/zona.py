"""Detección de zona/ubicación por gazetteer de nombres conocidos.

Coincidencia por substring/palabra en el texto. Nombres frecuentes no
reconocidos se registran como propuesta (tipo="zona") en
taxonomias_pendientes.json, nunca se fuerza una zona por defecto ni se descarta.
"""
import re
import unicodedata

from analytics._propuestas import _registrar_propuesta


# ── Gazetteer: zonas conocidas de Santa Ana, El Salvador ──

# Municipios del departamento de Santa Ana, El Salvador
DEPARTAMENTOS: set[str] = {
    "santa ana", "ahuachapan", "sonsonate", "chalatenango",
    "la libertad", "san salvador", "cuscatlan", "la paz",
    "cabanas", "san vicente", "usulutan", "san miguel",
    "morazan", "la union",
}

# Municipios del departamento de Santa Ana
MUNICIPIOS: set[str] = {
    "santa ana", "chalchuapa", "metapan", "texistepeque",
    "coatepeque", "el porvenir", "masahuat", "san antonio pajonal",
    "san sebastian salitrillo", "santa rosa guachipilin",
    "santiago de la frontera", "candelaria de la frontera",
}

# Zonas / barrios urbanos de Santa Ana ciudad
ZONAS_URBANAS: set[str] = {
    "centro", "centro historico", "el calvario", "santa lucia",
    "colonia magana", "colonia flor blanca", "colonia la paz",
    "colonia modelo", "colonia santa barbara", "colonia san jose",
    "colonia las palmas", "colonia el estadio",
    "residencial santa barbara", "reparto santa lucia",
    "barrio el angel", "barrio san miguelito", "barrio colon",
    "barrio san rafael", "barrio la cruz",
}

# Colonias y cantones periurbanos de Santa Ana
BARRIOS: set[str] = {
    "canton el palmar", "canton el nance", "canton san pedro",
    "canton buena vista", "canton texisio", "lotificacion san jose",
    "colonia 10 de octubre", "colonia el rosario", "colonia progreso",
    "colonia san antonio", "colonia vista hermosa", "las piedras",
    "el mirador", "las colinas", "la cuchilla", "loma linda",
    "residencial los almendros", "colonia santa ana",
}

# Unir todo el gazetteer
ZONAS_CONOCIDAS: set[str] = DEPARTAMENTOS | MUNICIPIOS | ZONAS_URBANAS | BARRIOS


# ── Normalización ──

def _normalize(text: str) -> str:
    text = text.lower()
    nfkd = unicodedata.normalize("NFKD", text)
    return "".join(c for c in nfkd if not unicodedata.combining(c))


# ── Result type ──

from dataclasses import dataclass, field as dc_field


@dataclass
class ZonaResult:
    zona: str = ""
    tipo: str = ""  # "departamento", "municipio", "zona_urbana", "barrio", "propuesta"
    evidencia: str = ""
    es_propuesta: bool = False


# ── Core detector ──

def detectar_zona(text: str) -> ZonaResult:
    """Detecta zona/mención geográfica en un texto.

    Prioridad: Zona urbana > Barrios > Municipios > Departamentos.
    Si no se reconoce, retorna zona="" (nunca fuerza una zona por defecto).
    """
    if not text or not text.strip():
        return ZonaResult(zona="", tipo="")

    low = _normalize(text)

    # 1. Buscar zonas urbanas de Santa Ana (prioridad alta)
    for zona in sorted(ZONAS_URBANAS, key=len, reverse=True):
        zona_norm = _normalize(zona)
        if zona_norm in low:
            return ZonaResult(zona=zona, tipo="zona_urbana", evidencia=zona)

    # 2. Buscar barrios
    for barrio in sorted(BARRIOS, key=len, reverse=True):
        barrio_norm = _normalize(barrio)
        if barrio_norm in low:
            return ZonaResult(zona=barrio, tipo="barrio", evidencia=barrio)

    # 3. Buscar municipios
    for municipio in sorted(MUNICIPIOS, key=len, reverse=True):
        municipio_norm = _normalize(municipio)
        # Para municipios multi-palabra, buscar como substring
        if " " in municipio_norm:
            if municipio_norm in low:
                return ZonaResult(zona=municipio, tipo="municipio", evidencia=municipio)
        else:
            # Para municipios de una palabra, buscar como token
            tokens = set(low.split())
            if municipio_norm in tokens:
                return ZonaResult(zona=municipio, tipo="municipio", evidencia=municipio)

    # 4. Buscar departamentos
    for depto in sorted(DEPARTAMENTOS, key=len, reverse=True):
        depto_norm = _normalize(depto)
        if " " in depto_norm:
            if depto_norm in low:
                return ZonaResult(zona=depto, tipo="departamento", evidencia=depto)
        else:
            tokens = set(low.split())
            if depto_norm in tokens:
                return ZonaResult(zona=depto, tipo="departamento", evidencia=depto)

    # 5. No se reconoció → devolver vacío (sin fuerza por defecto)
    return ZonaResult(zona="", tipo="")


def es_propuesta_zona(text: str) -> str | None:
    """Si el texto contiene una palabra que parece nombre de zona pero no
    está en el gazetteer, retorna la palabra candidata para registrar como propuesta.

    Registra automáticamente en taxonomias_pendientes.json con tipo="zona".
    Descarta palabras comunes/stopwords.

    Heurística: contenido después de "en ", "de ", "por ", "desde ".
    """
    if not text or not text.strip():
        return None

    _STOPWORDS_ZONA: set[str] = {
        "el", "la", "los", "las", "un", "una", "de", "del", "al", "a",
        "en", "con", "por", "para", "sin", "que", "se", "es", "lo", "su",
        "sus", "este", "esta", "ese", "esa", "esto", "eso", "como", "mas",
        "pero", "si", "no", "ya", "ni", "o", "y", "e", "muy", "hay",
        "fue", "ser", "estar", "haber", "hacer", "tener", "ir", "poder",
        "decir", "ver", "dar", "saber", "querer", "llegar", "poner",
        "creer", "todo", "toda", "todos", "todas", "otro", "otra",
        "otros", "otras", "cada", "algo", "nada", "siempre", "nunca",
        "aquí", "ahí", "allí", "donde", "cuando", "buen", "bueno",
        "buena", "mal", "malo", "mala", "gran", "grande", "pequeño",
        "pequeña", "todo", "toda", "mismo", "misma", "tan", "tanto",
        "poco", "mucho", "nada", "nadie", "toda", "tienen", "tiene",
        "circular", "toda", "hay", "ella", "ellos", "nosotros", "ustedes",
        "problema", "problemas", "situacion", "cosas", "gente", "forma",
        "manera", "parte", "lado", "tipo", "momento", "tiempo", "vida",
        "año", "anos", "dia", "dias", "vez", "veces", "caso", "casos",
    }

    # Buscar patrones "en <zona>", "de <zona>", "por <zona>"
    # \b antes y después de la preposición evita matchear "de" dentro de "puede", etc.
    import re
    patrones = re.findall(
        r"\b(?:en|de|por|desde|hasta|hacia)\b ([a-záéíóúñ]{3,}(?:\s+[a-záéíóúñ]{3,}){0,2})",
        (text or "").lower().strip(),
    )

    for candidata in patrones:
        candidata_limpia = candidata.strip()
        if len(candidata_limpia) < 3:
            continue

        # Descargar stopwords: si la candidata es solo una palabra común
        palabras = candidata_limpia.split()
        if len(palabras) == 1 and palabras[0] in _STOPWORDS_ZONA:
            continue

        # Verificar que no esté ya en el gazetteer
        zona = detectar_zona(candidata_limpia)
        if not zona.zona:
            _registrar_propuesta(
                clave_propuesta=candidata_limpia,
                ejemplo_texto=text[:200],
                tipo="zona",
                familia_mas_cercana="",
            )
            return candidata_limpia

    return None


# ── Agregación batch ──

def aggregate_zonas(texts: list[str]) -> dict:
    """Analiza una lista de textos y retorna distribución de zonas detectadas.

    Returns dict con:
        - total: total de textos
        - conteo: {zona: count}
        - pct: {zona: pct}
        - dominante: zona más mencionada (o "" si ninguna)
        - propuestas: lista de nombres candidatos no reconocidos
    """
    if not texts:
        return {"total": 0, "conteo": {}, "pct": {}, "dominante": "", "propuestas": []}

    conteo: dict[str, int] = {}
    propuestas: list[str] = []

    for text in texts:
        result = detectar_zona(text)
        if result.zona:
            conteo[result.zona] = conteo.get(result.zona, 0) + 1

        # Detectar propuestas
        propuesta = es_propuesta_zona(text)
        if propuesta and propuesta not in propuestas:
            propuestas.append(propuesta)

    total = len(texts)
    pct = {
        zona: round(count / total * 100, 1)
        for zona, count in conteo.items()
    }

    dominante = max(conteo, key=lambda k: (conteo[k], k)) if conteo else ""

    return {
        "total": total,
        "conteo": conteo,
        "pct": pct,
        "dominante": dominante,
        "propuestas": propuestas,
    }

#!/usr/bin/env python3
"""CLI para el pipeline de analisis.

Permite ejecutar las operaciones del pipeline desde linea de comandos:
- generar: genera analysis.json desde las aprobaciones
- verificar: valida un analysis.json existente
- resumen: muestra estadisticas del estado actual

Uso:
    python -m analytics.cli generar --periodo 2026-04 --fecha-hasta 2026-04-30
    python -m analytics.cli verificar
    python -m analytics.cli resumen
"""
import argparse
import json
import os
import sys

from src.config import Config
from analytics.report import construir_analysis, generar_reporte_completo
from analytics.publish import publicar_analysis
from analytics.schema_validator import validar

_cfg = Config()


def _periodo_anterior(periodo: str) -> str:
    """Dado 'YYYY-MM', retorna el mes anterior 'YYYY-MM'."""
    y, m = map(int, periodo.split("-"))
    m -= 1
    if m == 0:
        m = 12
        y -= 1
    return f"{y:04d}-{m:02d}"


def _calcular_er_previo(
    periodo_prev: str,
    fb_monthly: list[tuple],
    tk_monthly: list[tuple],
) -> float | None:
    """Calcula er_previo con la misma metodología ponderado_volumen.

    Retorna None si no hay datos de ambas plataformas para el período
    previo (para no comparar bases distintas).
    """
    fb_prev = next((row for row in fb_monthly if row[0] == periodo_prev), None)
    tk_prev = next((row for row in tk_monthly if row[0] == periodo_prev), None)

    if fb_prev is None or tk_prev is None:
        return None

    er_fb_prev, vol_fb_prev = fb_prev[1], fb_prev[2]
    er_tk_prev, vol_tk_prev = tk_prev[1], tk_prev[2]

    vol_total = vol_fb_prev + vol_tk_prev
    if vol_total <= 0:
        return None

    return round(
        er_fb_prev * (vol_fb_prev / vol_total) + er_tk_prev * (vol_tk_prev / vol_total),
        2,
    )


PLATAFORMA_TABLAS = {
    "facebook": ("", "fb_comments", "comment_id", "message"),
    "tiktok": ("", "comments", "id", "text"),
    "externos": ("", "external_comments", "comment_id", "message"),
}


def cmd_generar(args):
    """Genera y publica analysis.json."""
    from dashboard.tema_aprobaciones import agregar_por_tema_automatico
    from analytics.queries import (
        get_fb_stats, get_tk_stats, get_externos_stats,
        get_fb_daily_volumes, get_tk_daily_volumes,
        get_fb_monthly_sentiment, get_fb_per_theme_controversy,
        get_fb_posts_with_sentiment, get_fb_controversial_posts,
        get_fb_anger_by_zone, get_fb_monthly_controversy,
        get_fb_monthly_theme_controversy,
        get_fb_monthly_er, get_tk_monthly_er,
        get_fb_monthly_nsi, get_fb_period_controversy,
    )

    # Combinar aprobaciones de las 3 DBs (clasificación automática)
    if args.db:
        aprobaciones = agregar_por_tema_automatico(args.db)
        if aprobaciones:
            for a in aprobaciones:
                a.setdefault("plataforma", "override")
    else:
        from analytics.queries import cargar_temas_aprobados, _fusionar_aprobaciones_por_categoria
        try:
            aprobaciones = cargar_temas_aprobados()
        except Exception:
            aprobaciones = []

        if not aprobaciones:
            parciales = []
            for label, (db_placeholder, tabla, col_id, col_texto) in PLATAFORMA_TABLAS.items():
                db = {
                    "facebook": _cfg.FACEBOOK_DB,
                    "tiktok": _cfg.TIKTOK_DB,
                    "externos": _cfg.EXTERNOS_DB,
                }[label]
                try:
                    parcial = agregar_por_tema_automatico(db, tabla=tabla, col_id=col_id, col_texto=col_texto)
                    for a in parcial:
                        a.setdefault("plataforma", label)
                    parciales.extend(parcial)
                except Exception:
                    pass
            aprobaciones = _fusionar_aprobaciones_por_categoria(parciales)

    if not aprobaciones:
        print("No hay aprobaciones para generar el reporte.")
        return 1

    from analytics.queries import (
        get_fb_comments_with_context, get_tk_comments_with_context,
        get_ext_comments_with_context, get_temas_sugeridos_con_contexto,
    )

    # ÚNICA fuente de verdad: comentarios con contexto.
    # texts se deriva de ella para garantizar alineación de índices
    # con topic_results_by_text y la clasificación de emoción.
    comentarios_con_contexto = []
    for ctx_fetcher in (get_fb_comments_with_context, get_tk_comments_with_context,
                        get_ext_comments_with_context):
        try:
            ctx_comments = ctx_fetcher()
            comentarios_con_contexto.extend(ctx_comments)
        except Exception:
            pass
    texts = [c["texto"] for c in comentarios_con_contexto if c.get("texto")]

    comentarios_con_temas = []
    try:
        comentarios_con_temas = get_temas_sugeridos_con_contexto()
    except Exception:
        pass

    # Obtener stats de plataformas desde las DBs
    fb_stats = None
    tk_stats = None
    try:
        fb = get_fb_stats()
        if fb and fb.get("posts", 0) > 0:
            fb_stats = fb
            fb_stats["daily_volumes"] = get_fb_daily_volumes()
    except Exception:
        pass
    try:
        tk = get_tk_stats()
        if tk and tk.get("videos", 0) > 0:
            tk_stats = tk
            tk_stats["daily_volumes"] = get_tk_daily_volumes()
    except Exception:
        pass
    externos_stats = None
    try:
        ext = get_externos_stats()
        if ext and ext.get("posts", 0) > 0:
            externos_stats = ext
    except Exception:
        pass

    # Datos históricos para §F/§H
    fb_monthly_sentiment = None
    fb_per_theme_controversy = None
    fb_posts_with_sentiment = None
    fb_controversial_posts = None
    fb_anger_by_zone = None
    fb_monthly_controversy = None
    fb_monthly_theme_controversy = None
    try:
        fb_monthly_sentiment = get_fb_monthly_sentiment()
    except Exception:
        pass
    try:
        fb_per_theme_controversy = get_fb_per_theme_controversy()
    except Exception:
        pass
    try:
        fb_posts_with_sentiment = get_fb_posts_with_sentiment()
    except Exception:
        pass
    try:
        fb_controversial_posts = get_fb_controversial_posts()
    except Exception:
        pass
    try:
        fb_anger_by_zone = get_fb_anger_by_zone()
    except Exception:
        pass
    try:
        fb_monthly_controversy = get_fb_monthly_controversy()
    except Exception:
        pass
    try:
        fb_monthly_theme_controversy = get_fb_monthly_theme_controversy()
    except Exception:
        pass

    # §F SDI: Compute nsi_previo from previous month
    nsi_previo = None
    try:
        periodo_prev_sdi = _periodo_anterior(args.periodo)
        nsi_monthly = get_fb_monthly_nsi()
        for mes, nsi_val in nsi_monthly:
            if mes == periodo_prev_sdi:
                nsi_previo = nsi_val
                break
    except Exception:
        pass

    # §F EFI: Compute er_previo from previous month, same methodology as er_display
    er_previo = None
    try:
        periodo_prev_efi = _periodo_anterior(args.periodo)
        fb_monthly = get_fb_monthly_er()
        tk_monthly = get_tk_monthly_er()
        er_previo = _calcular_er_previo(periodo_prev_efi, fb_monthly, tk_monthly)
    except Exception:
        pass

    # §F ICI: Compute fb_period_controversy for current 7-day window
    fb_period_controversy = None
    try:
        from datetime import datetime, timedelta
        fh = datetime.fromisoformat(args.fecha_hasta)
        desde = (fh - timedelta(days=7)).strftime("%Y-%m-%d")
        fb_period_controversy = get_fb_period_controversy(desde, args.fecha_hasta)
    except Exception:
        pass

    data, resultado = generar_reporte_completo(
        aprobaciones, args.periodo, args.fecha_hasta,
        comentarios_texts=texts if texts else None,
        comentarios_con_contexto=comentarios_con_contexto if comentarios_con_contexto else None,
        comentarios_con_temas=comentarios_con_temas or None,
        fb_stats=fb_stats,
        tk_stats=tk_stats,
        externos_stats=externos_stats,
        er_previo=er_previo,
        nsi_previo=nsi_previo,
        fb_period_controversy=fb_period_controversy,
        fb_monthly_sentiment=fb_monthly_sentiment,
        fb_per_theme_controversy=fb_per_theme_controversy,
        fb_posts_with_sentiment=fb_posts_with_sentiment,
        fb_controversial_posts=fb_controversial_posts,
        fb_anger_by_zone=fb_anger_by_zone,
        fb_monthly_controversy=fb_monthly_controversy,
        fb_monthly_theme_controversy=fb_monthly_theme_controversy,
    )

    if not resultado.es_publicable:
        print(f"ERRORES ({len(resultado.bloqueantes)}):")
        for e in resultado.bloqueantes:
            print(f"  [{e.codigo}] {e.seccion}: {e.mensaje_humano}")
        return 1

    out_path = args.output or os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "data", "analysis.json"
    )
    resultado_pub = publicar_analysis(data, path=out_path)
    if resultado_pub.es_publicable:
        print(f"Analysis generado: {out_path}")
        if resultado_pub.advertencias:
            print(f"  ({len(resultado_pub.advertencias)} advertencias)")
        return 0
    else:
        print("Error al escribir:")
        for e in resultado_pub.bloqueantes:
            print(f"  [{e.codigo}] {e.mensaje_humano}")
        return 1


def _recorrer_secciones_narrativas(data: dict):
    """Recorre todas las secciones narrativas del analysis y yield (section_code, system_prompt, contexto).

    Genera exactamente las mismas secciones que el flujo de API.
    """
    evidencia_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "data", "_evidencia_periodo.json"
    )
    evidencia = {}
    if os.path.exists(evidencia_path):
        with open(evidencia_path, "r", encoding="utf-8") as f:
            evidencia = json.load(f)

    periodo = data.get("meta", {}).get("periodo", "")
    fecha_hasta = data.get("meta", {}).get("fecha_datos_hasta", "")

    # ── Bloque 1 ──
    b1 = data.get("bloque1", {})
    for sec_key in ["clima_narrativo", "indice_emociones", "intensidad",
                    "concentracion_tematica", "pulso_iq", "metricas_rendimiento"]:
        sec = b1.get(sec_key)
        if not isinstance(sec, dict):
            continue
        contexto = _construir_contexto_seccion(sec, meta={"periodo": periodo,
                                                           "fecha_datos_hasta": fecha_hasta})
        yield (f"b1.{sec_key}", _SYSTEM_PROMPT_BLOQUE1, contexto)

    # ── Bloque 2: voces individuales + polarizacion ──
    b2 = data.get("bloque2", {})
    for i, voz in enumerate(b2.get("voces_influencia", [])):
        if not isinstance(voz, dict):
            continue
        contexto = _construir_contexto_seccion(voz, meta={"periodo": periodo,
                                                           "fecha_datos_hasta": fecha_hasta})
        contexto["pagina"] = voz.get("pagina", "")
        yield (f"b2.voz[{i}]", _SYSTEM_PROMPT_BLOQUE2_VOZ, contexto)

    pol = b2.get("polarizacion")
    if isinstance(pol, dict):
        contexto = _construir_contexto_seccion(pol, meta={"periodo": periodo,
                                                           "fecha_datos_hasta": fecha_hasta})
        yield ("b2.polarizacion", _SYSTEM_PROMPT_BLOQUE2_POL, contexto)

    # ── Bloque 3 ──
    b3 = data.get("bloque3", {})
    for i, fr in enumerate(b3.get("puntos_friccion", [])):
        if not isinstance(fr, dict):
            continue
        contexto = _construir_contexto_seccion(fr, meta={"periodo": periodo,
                                                           "fecha_datos_hasta": fecha_hasta})
        contexto["tema"] = fr.get("tema", "")
        yield (f"b3.friccion[{i}]", _SYSTEM_PROMPT_BLOQUE3_FRICCION, contexto)

    for sec_key in ["autenticidad", "velocidad_propagacion"]:
        sec = b3.get(sec_key)
        if not isinstance(sec, dict):
            continue
        contexto = _construir_contexto_seccion(sec, meta={"periodo": periodo,
                                                           "fecha_datos_hasta": fecha_hasta})
        yield (f"b3.{sec_key}", _SYSTEM_PROMPT_BLOQUE3_SECCIONES, contexto)

    nivel = b3.get("nivel_alerta")
    if isinstance(nivel, dict):
        contexto = _construir_contexto_seccion(nivel, meta={"periodo": periodo,
                                                             "fecha_datos_hasta": fecha_hasta})
        alertas = nivel.get("alertas_cambridge", [])
        contexto["alertas_cambridge"] = alertas
        yield ("b3.nivel_alerta", _SYSTEM_PROMPT_BLOQUE3_NIVEL, contexto)

    # ── Bloque 4: 8 secciones fijas ──
    bloque4_secciones = [
        "eco_historico", "leccion_aprendida", "brecha_percepcion_realidad",
        "contexto_no_visible", "correlacion_contenido_reaccion",
        "comparativa_sectorial", "proyeccion_escenario", "recomendacion_estrategica",
    ]
    b4 = data.get("bloque4", {})
    for sec_key in bloque4_secciones:
        sec = b4.get(sec_key)
        if not isinstance(sec, dict):
            continue
        contexto = _construir_contexto_seccion_b4(data, sec_key)
        yield (f"b4.{sec_key}", _SYSTEM_PROMPT_BLOQUE4, contexto)


def _cmd_narrar_exportar(args, data):
    """Exporta prompts de narrativa a un archivo markdown para pegar en claude.ai."""
    data_path = args.path or os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "data", "analysis.json"
    )

    out_path = args.output or os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "data", "_narrar_prompts.md"
    )

    lines = []
    count = 0
    for section_code, system_prompt, contexto in _recorrer_secciones_narrativas(data):
        lines.append(f"# {section_code}\n")
        lines.append("## System Prompt\n")
        lines.append(f"```\n{system_prompt}\n```\n")
        lines.append("## Contexto (JSON)\n")
        lines.append(f"```json\n{json.dumps(contexto, ensure_ascii=False, indent=2)}\n```\n")
        lines.append("---\n")
        count += 1

    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"Prompts exportados: {count} secciones -> {out_path}")
    print("\nPasos:")
    print("  1. Copia cada bloque (System Prompt + Contexto) en una sesion de claude.ai")
    print("  2. Guarda las respuestas en un JSON con formato: {\"section_code\": \"texto\", ...}")
    print(f"     Secciones: {', '.join(s for s, _, _ in _recorrer_secciones_narrativas(data))}")
    print("  3. Ejecuta: python -m analytics.cli narrar --importar <archivo_respuestas.json>")
    return 0


def _cmd_narrar_importar(args, data):
    """Importa respuestas de claude.ai y escribe narrativas en analysis.json."""
    from analytics.evidence import (
        resolver_evidencia_voz, resolver_evidencia_friccion, resolver_evidencia_alertas,
    )

    data_path = args.path or os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "data", "analysis.json"
    )

    evidencia_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "data", "_evidencia_periodo.json"
    )
    evidencia = {}
    if os.path.exists(evidencia_path):
        with open(evidencia_path, "r", encoding="utf-8") as f:
            evidencia = json.load(f)

    if not os.path.exists(args.importar):
        print(f"Archivo de respuestas no encontrado: {args.importar}")
        return 1
    with open(args.importar, "r", encoding="utf-8") as f:
        respuestas = json.load(f)

    if not isinstance(respuestas, dict):
        print("Error: el archivo de respuestas debe ser un dict {\"section_code\": \"texto\"}")
        return 1

    periodos = [s for s, _, _ in _recorrer_secciones_narrativas(data)]
    faltantes = [s for s in periodos if s not in respuestas]
    aplicadas = 0

    # Resolver enlaces por seccion
    for section_code, narrativa in respuestas.items():
        if not isinstance(narrativa, str) or not narrativa.strip():
            continue
        # Encontrar la seccion en data
        if not _escribir_narrativa_en_seccion(data, section_code, narrativa.strip(), evidencia):
            print(f"  Advertencia: seccion '{section_code}' no encontrada en analysis.json")
            continue
        aplicadas += 1

    if faltantes:
        print(f"Secciones sin narrativa ({len(faltantes)}):")
        for s in faltantes:
            print(f"  - {s}")

    if not aplicadas:
        print("No se aplico ninguna narrativa.")
        return 1

    if args.dry_run:
        print(f"\n=== DRY RUN: {aplicadas} narrativas (sin escribir) ===")
        _imprimir_narrativas(data)
        return 0

    from analytics.publish import publicar_analysis
    resultado_pub = publicar_analysis(data, path=data_path, render_narrativas=False)
    if resultado_pub.es_publicable:
        print(f"Narrativas actualizadas: {data_path} ({aplicadas} secciones)")
        if resultado_pub.advertencias:
            print(f"  ({len(resultado_pub.advertencias)} advertencias)")
        return 0
    else:
        print("Error al publicar narrativas:")
        for e in resultado_pub.bloqueantes:
            print(f"  [{e.codigo}] {e.mensaje_humano}")
        return 1


def _escribir_narrativa_en_seccion(data: dict, section_code: str, narrativa: str,
                                   evidencia: dict) -> bool:
    """Escribe la narrativa y resuelve enlaces para una seccion dada."""
    from analytics.evidence import (
        resolver_evidencia_voz, resolver_evidencia_friccion, resolver_evidencia_alertas,
    )

    parts = section_code.split(".", 1)
    if len(parts) != 2:
        return False
    bloque_key, sec_id = parts

    if bloque_key == "b1":
        sec = data.get("bloque1", {}).get(sec_id)
        if not isinstance(sec, dict):
            return False
        sec["narrativa"] = narrativa
        sec["enlaces_referencia"] = _resolver_enlaces_seccion(sec_id, evidencia, data)
    elif bloque_key == "b2":
        import re
        voz_match = re.match(r"voz\[(\d+)\]", sec_id)
        if voz_match:
            idx = int(voz_match.group(1))
            voces = data.get("bloque2", {}).get("voces_influencia", [])
            if idx >= len(voces) or not isinstance(voces[idx], dict):
                return False
            voz = voces[idx]
            voz["narrativa"] = narrativa
            voz["enlaces_referencia"] = resolver_evidencia_voz(
                voz.get("pagina", ""), evidencia
            )
        elif sec_id == "polarizacion":
            pol = data.get("bloque2", {}).get("polarizacion")
            if not isinstance(pol, dict):
                return False
            pol["narrativa"] = narrativa
        else:
            return False
    elif bloque_key == "b3":
        import re
        friccion_match = re.match(r"friccion\[(\d+)\]", sec_id)
        if friccion_match:
            idx = int(friccion_match.group(1))
            fricciones = data.get("bloque3", {}).get("puntos_friccion", [])
            if idx >= len(fricciones) or not isinstance(fricciones[idx], dict):
                return False
            fr = fricciones[idx]
            fr["narrativa"] = narrativa
            fr["enlaces_relacionados"] = resolver_evidencia_friccion(
                fr.get("tema", ""), evidencia
            )
        elif sec_id in ("autenticidad", "velocidad_propagacion"):
            sec = data.get("bloque3", {}).get(sec_id)
            if not isinstance(sec, dict):
                return False
            sec["narrativa"] = narrativa
        elif sec_id == "nivel_alerta":
            nivel = data.get("bloque3", {}).get("nivel_alerta")
            if not isinstance(nivel, dict):
                return False
            nivel["narrativa"] = narrativa
            nivel["enlaces_referencia"] = resolver_evidencia_alertas(
                nivel.get("alertas_cambridge", []), evidencia
            )
        else:
            return False
    elif bloque_key == "b4":
        sec = data.get("bloque4", {}).get(sec_id)
        if not isinstance(sec, dict):
            return False
        sec["narrativa"] = narrativa
    else:
        return False
    return True


def _cmd_narrar_usar_api(args, data):
    """Flujo legacy: llama directamente a la API de Anthropic."""
    import logging
    from analytics.narrator_claude import redactar_narrativa
    from analytics.narrator_claude import _get_config
    from analytics.evidence import (
        resolver_evidencia_voz, resolver_evidencia_friccion, resolver_evidencia_alertas,
    )

    log = logging.getLogger(__name__)

    # Chequeo upfront: fallar rapido si no hay API key
    _get_config()

    data_path = args.path or os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "data", "analysis.json"
    )

    evidencia_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "data", "_evidencia_periodo.json"
    )
    evidencia = {}
    if os.path.exists(evidencia_path):
        with open(evidencia_path, "r", encoding="utf-8") as f:
            evidencia = json.load(f)

    modified = False

    for section_code, system_prompt, contexto in _recorrer_secciones_narrativas(data):
        try:
            narrativa = redactar_narrativa(system_prompt, contexto, section_code=section_code)
            _escribir_narrativa_en_seccion(data, section_code, narrativa, evidencia)
            modified = True
        except Exception as e:
            log.warning("Fallo narrar %s: %s", section_code, e)

    if not modified:
        print("No se genero ninguna narrativa (todas las secciones fallaron).")
        return 1

    if args.dry_run:
        print("=== DRY RUN: Narrativas generadas (sin escribir) ===\n")
        _imprimir_narrativas(data)
        return 0

    from analytics.publish import publicar_analysis
    resultado_pub = publicar_analysis(data, path=data_path, render_narrativas=False)
    if resultado_pub.es_publicable:
        print(f"Narrativas actualizadas: {data_path}")
        if resultado_pub.advertencias:
            print(f"  ({len(resultado_pub.advertencias)} advertencias)")
        return 0
    else:
        print("Error al publicar narrativas:")
        for e in resultado_pub.bloqueantes:
            print(f"  [{e.codigo}] {e.mensaje_humano}")
        return 1


def cmd_narrar(args):
    """Genera narrativas de analysis.json.

    Modos:
      --exportar (por defecto): escribe prompts a un archivo para pegar manualmente en claude.ai
      --importar <archivo>: importa respuestas previamente generadas en claude.ai
      --usar-api: llama directamente a la API de Anthropic (requiere ANTHROPIC_API_KEY)
    """
    data_path = args.path or os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "data", "analysis.json"
    )
    if not os.path.exists(data_path):
        print(f"No se encontro {data_path}. Ejecuta 'generar' primero.")
        return 1
    with open(data_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if getattr(args, "importar", None):
        return _cmd_narrar_importar(args, data)
    elif getattr(args, "usar_api", False):
        return _cmd_narrar_usar_api(args, data)
    else:
        return _cmd_narrar_exportar(args, data)


def _construir_contexto_seccion(seccion: dict, meta: dict | None = None) -> dict:
    """Extrae campos numericos/categoricos de una seccion para contexto de Claude."""
    ctx = dict(meta) if meta else {}
    for key, val in seccion.items():
        if key in ("narrativa", "enlaces_referencia", "enlaces_relacionados",
                    "formula_usada", "postura_nota", "alcance_nota"):
            continue
        if isinstance(val, (int, float, str, bool)):
            ctx[key] = val
        elif isinstance(val, list) and key in ("alertas_cambridge",):
            ctx[key] = val
    return ctx


def _construir_contexto_seccion_b4(analysis: dict, sec_key: str) -> dict:
    """Construye contexto para una seccion de bloque4 con datos de otros bloques."""
    meta = analysis.get("meta", {})
    ctx = {
        "periodo": meta.get("periodo", ""),
        "fecha_datos_hasta": meta.get("fecha_datos_hasta", ""),
        "seccion": sec_key,
    }
    # Datos de bloque1
    b1 = analysis.get("bloque1", {})
    cn = b1.get("clima_narrativo", {})
    ctx["tono_dominante"] = cn.get("tono_dominante", "")
    ctx["pct_favorable"] = cn.get("pct_favorable", 0)
    ctx["pct_critico"] = cn.get("pct_critico", 0)
    ctx["n_total_comentarios"] = cn.get("n_total_comentarios", 0)
    ie = b1.get("indice_emociones", {})
    ctx["emocion_dominante"] = ie.get("emocion_dominante", "")
    ct = b1.get("concentracion_tematica", {})
    ctx["top_tema"] = ct.get("top_tema", "")
    ctx["hhi"] = ct.get("hhi", 0)
    mr = b1.get("metricas_rendimiento", {})
    ctx["engagement_rate"] = mr.get("engagement_rate", 0)
    # Datos de bloque3
    b3 = analysis.get("bloque3", {})
    na = b3.get("nivel_alerta", {})
    ctx["semaforo"] = na.get("semaforo", "")
    ctx["indice_riesgo"] = na.get("indice_riesgo", 0)
    fricciones = b3.get("puntos_friccion", [])
    ctx["temas_friccion"] = [fr.get("tema", "") for fr in fricciones if isinstance(fr, dict)]
    return ctx


def _resolver_enlaces_seccion(sec_key: str, evidencia: dict, data: dict) -> list:
    """Resuelve enlaces de referencia para una seccion de bloque1."""
    from analytics.evidence import (
        resolver_evidencia_tema, resolver_evidencia_emocion,
    )
    enlaces = []
    evidencia_por_tema = evidencia.get("por_tema", {})
    evidencia_por_emocion = evidencia.get("por_emocion", {})

    if sec_key in ("concentracion_tematica",):
        for tema in list(evidencia_por_tema.keys()):
            enlaces.extend(resolver_evidencia_tema(tema, evidencia_por_tema))
    elif sec_key in ("indice_emociones",):
        for emo in list(evidencia_por_emocion.keys()):
            enlaces.extend(resolver_evidencia_emocion(emo, evidencia_por_emocion))
    elif sec_key == "clima_narrativo":
        cn = data.get("bloque1", {}).get("clima_narrativo", {})
        if cn.get("pct_critico", 0) > 0:
            for tema in list(evidencia_por_tema.keys()):
                enlaces.extend(resolver_evidencia_tema(tema, evidencia_por_tema))
    return list(dict.fromkeys(enlaces))


def _imprimir_narrativas(data: dict):
    """Imprime todas las narrativas del analysis para revision manual."""
    for bloque_key in ["bloque1", "bloque2", "bloque3", "bloque4"]:
        bloque = data.get(bloque_key, {})
        if not isinstance(bloque, dict):
            continue
        for sec_key, sec_val in bloque.items():
            if isinstance(sec_val, dict):
                narr = sec_val.get("narrativa", "")
                if narr:
                    enl = sec_val.get("enlaces_referencia",
                                      sec_val.get("enlaces_relacionados", []))
                    print(f"[{bloque_key}.{sec_key}]")
                    print(f"  {narr[:200]}{'...' if len(narr) > 200 else ''}")
                    if enl:
                        print(f"  Enlaces: {len(enl)}")
                    print()
            elif isinstance(sec_val, list):
                for i, item in enumerate(sec_val):
                    if isinstance(item, dict):
                        narr = item.get("narrativa", "")
                        if narr:
                            print(f"[{bloque_key}.{sec_key}[{i}]]")
                            print(f"  {narr[:200]}{'...' if len(narr) > 200 else ''}")
                            print()


_SYSTEM_PROMPT_BLOQUE1 = (
    "Eres el redactor de narrativas de analisis de comunicacion para un "
    "gobierno municipal. Escribe narrativas sobrias, directas, sin adjetivos "
    "vagos. REGLAS OBLIGATORIAS:\n"
    "- RG-0: El sentimiento fue calculado por reglas lexicas, NUNCA mencionar IA.\n"
    "- RG-1: No usar siglas tecnicas (HHI, NSI, IR, PI, ER) en la narrativa. "
    "Solo van en formula_usada.\n"
    "- RG-2: Solo datos del periodo analizado.\n"
    "- RG-3: Nunca usar censura/autocensura. Usar 'limitacion metodologica'.\n"
    "- RG-4: Engagement != Impresiones.\n"
    "- RG-5: Toda afirmacion con cifra debe tener enlace real.\n"
    "- No calcules ni inventes ninguna cifra que no este en el JSON de contexto. "
    "Si falta un dato, dilo explicitamente en vez de inventarlo.\n"
    "- Para Clima Narrativo: seguir la plantilla exacta del ANALYST_GUIDE.md "
    "(cifras crudas, comparacion, ancla con tema, Conclusión, "
    "= NOMBRE CONTUNDENTE EN MAYUSCULAS).\n"
)

_SYSTEM_PROMPT_BLOQUE2_VOZ = (
    "Redacta la narrativa para una voz de influencia en el analisis de "
    "comunicacion municipal. Describe su engagement y relevancia sin "
    "inventar cifras. No usar siglas tecnicas. Solo datos del periodo.\n"
    "- No calcules ni inventes ninguna cifra que no este en el JSON de contexto.\n"
)

_SYSTEM_PROMPT_BLOQUE2_POL = (
    "Redacta la narrativa de polarizacion. Describe el nivel de division "
    "o consenso sin usar 'censura' ni 'autocensura'. "
    "Usar 'limitacion metodologica' si aplica.\n"
    "- No calcules ni inventes ninguna cifra que no este en el JSON de contexto.\n"
)

_SYSTEM_PROMPT_BLOQUE3_FRICCION = (
    "Redacta la narrativa para un punto de friccion. Describe la tension "
    "especifica citando el tema, numero de criticas y emocion dominante. "
    "No inventar cifras.\n"
)

_SYSTEM_PROMPT_BLOQUE3_SECCIONES = (
    "Redacta la narrativa para esta seccion del bloque de Riesgo y "
    "Autenticidad. Si hay datos concretos, usarlos directamente. "
    "Si no hay datos suficientes, decirlo explicitamente.\n"
    "- No calcules ni inventes ninguna cifra que no este en el JSON de contexto.\n"
)

_SYSTEM_PROMPT_BLOQUE3_NIVEL = (
    "Redacta la narrativa del nivel de alerta general. Describe el "
    "semaforo de riesgo y las alertas activas sin inventar datos. "
    "Cada alerta debe mencionar su tipo y descripcion.\n"
    "- No calcules ni inventes ninguna cifra que no este en el JSON de contexto.\n"
)

_SYSTEM_PROMPT_BLOQUE4 = (
    "Eres el estratega que redacta el Memorandum Estrategico (Bloque IV) "
    "del analisis de comunicacion de un gobierno municipal. "
    "REGLAS OBLIGATORIAS:\n"
    "- RG-0: Sentimiento calculado por reglas lexicas, nunca mencionar IA.\n"
    "- RG-1: No usar siglas tecnicas en la narrativa.\n"
    "- RG-2: Solo datos del periodo analizado.\n"
    "- RG-3: No usar censura/autocensura.\n"
    "- RG-5: Toda afirmacion con cifra debe tener enlace real.\n"
    "- Integrar numeros/porcentajes reales dentro de la prosa.\n"
    "- No calcules ni inventes ninguna cifra que no este en el JSON de contexto.\n"
    "- Si falta un dato, decirlo explicitamente.\n"
)


def cmd_verificar(args):
    """Valida un analysis.json existente."""
    from scripts.verificar import verificar
    result = verificar(args.path)
    if result and not result.es_publicable:
        return 1
    return 0


def cmd_resumen(args):
    """Muestra estadisticas basicas."""
    from dashboard.tema_aprobaciones import agregar_por_tema_automatico, resumen_revision

    db_path = args.db or _cfg.EXTERNOS_DB
    aprob = agregar_por_tema_automatico(db_path)
    resumen = resumen_revision(db_path)

    print(f"Aprobados con tema: {resumen.get('aprobados', 0)}")
    print(f"Sin tema (no_aplica): {resumen.get('sin_tema', 0)}")
    print(f"Total aprobaciones: {resumen.get('total_aprobaciones', 0)}")
    if "pendientes" in resumen:
        print(f"Pendientes: {resumen['pendientes']}")

    if aprob:
        print(f"\nTemas ({len(aprob)}):")
        for t in aprob[:10]:
            print(f"  {t['label']}: {t['doc_count']} docs ({t['pct']}%) "
                  f"[apoyo={t['apoyo']}, critica={t['critica']}]")
    return 0


def main():
    parser = argparse.ArgumentParser(description="CLI del pipeline de analisis")
    sub = parser.add_subparsers(dest="comando")

    p_gen = sub.add_parser("generar", help="Generar analysis.json")
    p_gen.add_argument("--periodo", required=True, help="Periodo (ej. 2026-04)")
    p_gen.add_argument("--fecha-hasta", required=True, help="Fecha corte (ISO)")
    p_gen.add_argument("--db", help="Ruta a DB de aprobaciones")
    p_gen.add_argument("--output", help="Ruta de salida")

    p_ver = sub.add_parser("verificar", help="Validar analysis.json")
    p_ver.add_argument("--path", default="data/analysis.json")

    p_res = sub.add_parser("resumen", help="Mostrar estadisticas")
    p_res.add_argument("--db", help="Ruta a DB")

    p_nar = sub.add_parser("narrar", help="Generar narrativas de analysis.json")
    p_nar.add_argument("--path", default="data/analysis.json",
                       help="Ruta a analysis.json")
    p_nar.add_argument("--exportar", action="store_true", default=True,
                       help="Exportar prompts a archivo para pegar en claude.ai (por defecto)")
    p_nar.add_argument("--importar", metavar="ARCHIVO",
                       help="Importar respuestas de claude.ai desde archivo JSON")
    p_nar.add_argument("--usar-api", action="store_true",
                       help="Usar API de Anthropic directamente (requiere ANTHROPIC_API_KEY)")
    p_nar.add_argument("--output", default=None,
                       help="Ruta de salida para exportar prompts (default: data/_narrar_prompts.md)")
    p_nar.add_argument("--dry-run", action="store_true",
                       help="Imprimir narrativas sin escribir")

    args = parser.parse_args()

    if args.comando == "generar":
        sys.exit(cmd_generar(args))
    elif args.comando == "verificar":
        sys.exit(cmd_verificar(args))
    elif args.comando == "resumen":
        sys.exit(cmd_resumen(args))
    elif args.comando == "narrar":
        sys.exit(cmd_narrar(args))
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()

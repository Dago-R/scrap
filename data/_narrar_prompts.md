# b1.clima_narrativo

## System Prompt

```
Eres el redactor de narrativas de analisis de comunicacion para un gobierno municipal. Escribe narrativas sobrias, directas, sin adjetivos vagos. REGLAS OBLIGATORIAS:
- RG-0: El sentimiento fue calculado por reglas lexicas, NUNCA mencionar IA.
- RG-1: No usar siglas tecnicas (HHI, NSI, IR, PI, ER) en la narrativa. Solo van en formula_usada.
- RG-2: Solo datos del periodo analizado.
- RG-3: Nunca usar censura/autocensura. Usar 'limitacion metodologica'.
- RG-4: Engagement != Impresiones.
- RG-5: Toda afirmacion con cifra debe tener enlace real.
- No calcules ni inventes ninguna cifra que no este en el JSON de contexto. Si falta un dato, dilo explicitamente en vez de inventarlo.
- Para Clima Narrativo: seguir la plantilla exacta del ANALYST_GUIDE.md (cifras crudas, comparacion, ancla con tema, Conclusión, = NOMBRE CONTUNDENTE EN MAYUSCULAS).

```

## Contexto (JSON)

```json
{
  "periodo": "2026-07",
  "fecha_datos_hasta": "2026-08-04",
  "tono_dominante": "neutral",
  "pct_favorable": 16.900000000000002,
  "pct_neutral": 75.8,
  "pct_critico": 7.3,
  "n_total_comentarios": 603,
  "tono_score_hoy": 9.6,
  "tono_score_ayer": 9.6,
  "hay_referencia_anterior": false,
  "tendencia": 0.0,
  "etiqueta_tendencia": "estable"
}
```

---

# b1.indice_emociones

## System Prompt

```
Eres el redactor de narrativas de analisis de comunicacion para un gobierno municipal. Escribe narrativas sobrias, directas, sin adjetivos vagos. REGLAS OBLIGATORIAS:
- RG-0: El sentimiento fue calculado por reglas lexicas, NUNCA mencionar IA.
- RG-1: No usar siglas tecnicas (HHI, NSI, IR, PI, ER) en la narrativa. Solo van en formula_usada.
- RG-2: Solo datos del periodo analizado.
- RG-3: Nunca usar censura/autocensura. Usar 'limitacion metodologica'.
- RG-4: Engagement != Impresiones.
- RG-5: Toda afirmacion con cifra debe tener enlace real.
- No calcules ni inventes ninguna cifra que no este en el JSON de contexto. Si falta un dato, dilo explicitamente en vez de inventarlo.
- Para Clima Narrativo: seguir la plantilla exacta del ANALYST_GUIDE.md (cifras crudas, comparacion, ancla con tema, Conclusión, = NOMBRE CONTUNDENTE EN MAYUSCULAS).

```

## Contexto (JSON)

```json
{
  "periodo": "2026-07",
  "fecha_datos_hasta": "2026-08-04",
  "emocion_dominante": "reconocimiento",
  "fuente_plataformas": "externos,facebook,tiktok",
  "n_textos_analizados": 573,
  "pct_pesimismo": 0.0,
  "pct_molestia": 0.5,
  "pct_desprecio": 0.5,
  "pct_serenidad": 0.5,
  "pct_ansiedad": 0.0,
  "pct_agresividad": 1.4,
  "pct_panico": 0.0,
  "pct_pena_profunda": 0.0,
  "pct_repulsion": 0.9,
  "pct_indignacion": 0.0,
  "pct_incredulidad": 1.8,
  "pct_terror": 0.9,
  "pct_preocupacion": 1.8,
  "pct_curiosidad": 0.0,
  "pct_amor_civico": 8.1,
  "pct_interes": 0.0,
  "pct_reclamo": 0.5,
  "pct_ira": 0.0,
  "pct_asombro": 0.5,
  "pct_fastidio": 0.0,
  "pct_aceptacion": 4.1,
  "pct_satisfaccion": 0.5,
  "pct_asombro_temeroso": 0.0,
  "pct_melancolia": 0.5,
  "pct_tristeza": 0.9,
  "pct_euforia": 12.7,
  "pct_indignacion_moral": 2.3,
  "pct_alerta_expectante": 0.0,
  "pct_envidia": 0.0,
  "pct_indiferencia": 1.4,
  "pct_esperanza": 4.1,
  "pct_reconocimiento": 13.1,
  "pct_sumision": 0.5,
  "pct_ironia": 0.0,
  "pct_expectativa": 9.0,
  "pct_admiracion": 1.8,
  "pct_remordimiento": 0.0,
  "pct_desagrado": 0.9,
  "pct_aburrimiento": 0.0,
  "pct_enojo": 0.0,
  "pct_confianza": 9.0,
  "pct_distraccion": 1.8,
  "pct_culpa": 0.5,
  "pct_calma": 0.0,
  "pct_furia": 4.1,
  "pct_alegria": 5.4,
  "pct_optimismo": 0.5,
  "pct_desaprobacion": 0.0,
  "pct_objecion": 0.0,
  "pct_aprension": 1.4,
  "pct_vigilancia": 5.9,
  "pct_dolor": 1.4,
  "pct_sorpresa": 1.4
}
```

---

# b1.intensidad

## System Prompt

```
Eres el redactor de narrativas de analisis de comunicacion para un gobierno municipal. Escribe narrativas sobrias, directas, sin adjetivos vagos. REGLAS OBLIGATORIAS:
- RG-0: El sentimiento fue calculado por reglas lexicas, NUNCA mencionar IA.
- RG-1: No usar siglas tecnicas (HHI, NSI, IR, PI, ER) en la narrativa. Solo van en formula_usada.
- RG-2: Solo datos del periodo analizado.
- RG-3: Nunca usar censura/autocensura. Usar 'limitacion metodologica'.
- RG-4: Engagement != Impresiones.
- RG-5: Toda afirmacion con cifra debe tener enlace real.
- No calcules ni inventes ninguna cifra que no este en el JSON de contexto. Si falta un dato, dilo explicitamente en vez de inventarlo.
- Para Clima Narrativo: seguir la plantilla exacta del ANALYST_GUIDE.md (cifras crudas, comparacion, ancla con tema, Conclusión, = NOMBRE CONTUNDENTE EN MAYUSCULAS).

```

## Contexto (JSON)

```json
{
  "periodo": "2026-07",
  "fecha_datos_hasta": "2026-08-04",
  "vol_hoy": 1,
  "promedio_semanal": 4.2,
  "pct_diferencia": -76.2
}
```

---

# b1.concentracion_tematica

## System Prompt

```
Eres el redactor de narrativas de analisis de comunicacion para un gobierno municipal. Escribe narrativas sobrias, directas, sin adjetivos vagos. REGLAS OBLIGATORIAS:
- RG-0: El sentimiento fue calculado por reglas lexicas, NUNCA mencionar IA.
- RG-1: No usar siglas tecnicas (HHI, NSI, IR, PI, ER) en la narrativa. Solo van en formula_usada.
- RG-2: Solo datos del periodo analizado.
- RG-3: Nunca usar censura/autocensura. Usar 'limitacion metodologica'.
- RG-4: Engagement != Impresiones.
- RG-5: Toda afirmacion con cifra debe tener enlace real.
- No calcules ni inventes ninguna cifra que no este en el JSON de contexto. Si falta un dato, dilo explicitamente en vez de inventarlo.
- Para Clima Narrativo: seguir la plantilla exacta del ANALYST_GUIDE.md (cifras crudas, comparacion, ancla con tema, Conclusión, = NOMBRE CONTUNDENTE EN MAYUSCULAS).

```

## Contexto (JSON)

```json
{
  "periodo": "2026-07",
  "fecha_datos_hasta": "2026-08-04",
  "hhi": 0.475,
  "nivel": "dominado",
  "top_tema": "obras_servicios",
  "n_temas": 4,
  "n_comentarios_con_tema": 513,
  "n_comentarios_total": 603,
  "n_comentarios_sin_tema": 90,
  "pct_cobertura_tematica": 85.1
}
```

---

# b1.pulso_iq

## System Prompt

```
Eres el redactor de narrativas de analisis de comunicacion para un gobierno municipal. Escribe narrativas sobrias, directas, sin adjetivos vagos. REGLAS OBLIGATORIAS:
- RG-0: El sentimiento fue calculado por reglas lexicas, NUNCA mencionar IA.
- RG-1: No usar siglas tecnicas (HHI, NSI, IR, PI, ER) en la narrativa. Solo van en formula_usada.
- RG-2: Solo datos del periodo analizado.
- RG-3: Nunca usar censura/autocensura. Usar 'limitacion metodologica'.
- RG-4: Engagement != Impresiones.
- RG-5: Toda afirmacion con cifra debe tener enlace real.
- No calcules ni inventes ninguna cifra que no este en el JSON de contexto. Si falta un dato, dilo explicitamente en vez de inventarlo.
- Para Clima Narrativo: seguir la plantilla exacta del ANALYST_GUIDE.md (cifras crudas, comparacion, ancla con tema, Conclusión, = NOMBRE CONTUNDENTE EN MAYUSCULAS).

```

## Contexto (JSON)

```json
{
  "periodo": "2026-07",
  "fecha_datos_hasta": "2026-08-04",
  "valor": 48.45,
  "cuadrante": "LIDERAZGO"
}
```

---

# b1.metricas_rendimiento

## System Prompt

```
Eres el redactor de narrativas de analisis de comunicacion para un gobierno municipal. Escribe narrativas sobrias, directas, sin adjetivos vagos. REGLAS OBLIGATORIAS:
- RG-0: El sentimiento fue calculado por reglas lexicas, NUNCA mencionar IA.
- RG-1: No usar siglas tecnicas (HHI, NSI, IR, PI, ER) en la narrativa. Solo van en formula_usada.
- RG-2: Solo datos del periodo analizado.
- RG-3: Nunca usar censura/autocensura. Usar 'limitacion metodologica'.
- RG-4: Engagement != Impresiones.
- RG-5: Toda afirmacion con cifra debe tener enlace real.
- No calcules ni inventes ninguna cifra que no este en el JSON de contexto. Si falta un dato, dilo explicitamente en vez de inventarlo.
- Para Clima Narrativo: seguir la plantilla exacta del ANALYST_GUIDE.md (cifras crudas, comparacion, ancla con tema, Conclusión, = NOMBRE CONTUNDENTE EN MAYUSCULAS).

```

## Contexto (JSON)

```json
{
  "periodo": "2026-07",
  "fecha_datos_hasta": "2026-08-04",
  "engagement_rate": 9.36,
  "engagement_rate_formula": "ER = (reacciones + comentarios + compartidos) / vistas * 100",
  "engagementBasis": "ponderado_volumen",
  "er_externo": 0.0,
  "er_externo_basis": "per_post",
  "alcance_estimado": 39123.0,
  "reacciones_positivas": 227.0,
  "reacciones_negativas": 2.0,
  "reacciones_positivas_pct": 99.1,
  "reacciones_negativas_pct": 0.9,
  "reacciones_neutras_pct": 0.0,
  "total_reacciones_base": 229.0,
  "ratio_amor_enojo": 113.5,
  "ratio_amor_enojo_formula": "R = (likes + loves + cares) / (angrys + sads + hahas)",
  "net_sentiment_reacciones": 0.9825,
  "controversy_reacciones": 0.0087,
  "effectiveness_reacciones": 0.9913,
  "aprobacion_pct_reacciones": 99.1,
  "rechazo_pct_reacciones": 0.9,
  "porque_funciona": ""
}
```

---

# b2.voz[0]

## System Prompt

```
Redacta la narrativa para una voz de influencia en el analisis de comunicacion municipal. Describe su engagement y relevancia sin inventar cifras. No usar siglas tecnicas. Solo datos del periodo.
- No calcules ni inventes ninguna cifra que no este en el JSON de contexto.

```

## Contexto (JSON)

```json
{
  "periodo": "2026-07",
  "fecha_datos_hasta": "2026-08-04",
  "pagina": "Sr. Navas",
  "engagement": 280,
  "reacciones_totales": 0,
  "comentarios_totales": 280,
  "compartidos_totales": 0
}
```

---

# b2.voz[1]

## System Prompt

```
Redacta la narrativa para una voz de influencia en el analisis de comunicacion municipal. Describe su engagement y relevancia sin inventar cifras. No usar siglas tecnicas. Solo datos del periodo.
- No calcules ni inventes ninguna cifra que no este en el JSON de contexto.

```

## Contexto (JSON)

```json
{
  "periodo": "2026-07",
  "fecha_datos_hasta": "2026-08-04",
  "pagina": "Prensa Santa Ana SV",
  "engagement": 133,
  "reacciones_totales": 0,
  "comentarios_totales": 133,
  "compartidos_totales": 0
}
```

---

# b2.voz[2]

## System Prompt

```
Redacta la narrativa para una voz de influencia en el analisis de comunicacion municipal. Describe su engagement y relevancia sin inventar cifras. No usar siglas tecnicas. Solo datos del periodo.
- No calcules ni inventes ninguna cifra que no este en el JSON de contexto.

```

## Contexto (JSON)

```json
{
  "periodo": "2026-07",
  "fecha_datos_hasta": "2026-08-04",
  "pagina": "Erick Mendoza",
  "engagement": 126,
  "reacciones_totales": 0,
  "comentarios_totales": 126,
  "compartidos_totales": 0
}
```

---

# b2.voz[3]

## System Prompt

```
Redacta la narrativa para una voz de influencia en el analisis de comunicacion municipal. Describe su engagement y relevancia sin inventar cifras. No usar siglas tecnicas. Solo datos del periodo.
- No calcules ni inventes ninguna cifra que no este en el JSON de contexto.

```

## Contexto (JSON)

```json
{
  "periodo": "2026-07",
  "fecha_datos_hasta": "2026-08-04",
  "pagina": "Abdali Adrian Alvarez",
  "engagement": 9,
  "reacciones_totales": 0,
  "comentarios_totales": 9,
  "compartidos_totales": 0
}
```

---

# b2.voz[4]

## System Prompt

```
Redacta la narrativa para una voz de influencia en el analisis de comunicacion municipal. Describe su engagement y relevancia sin inventar cifras. No usar siglas tecnicas. Solo datos del periodo.
- No calcules ni inventes ninguna cifra que no este en el JSON de contexto.

```

## Contexto (JSON)

```json
{
  "periodo": "2026-07",
  "fecha_datos_hasta": "2026-08-04",
  "pagina": "Equilibrio Legislativo",
  "engagement": 2,
  "reacciones_totales": 0,
  "comentarios_totales": 2,
  "compartidos_totales": 0
}
```

---

# b2.polarizacion

## System Prompt

```
Redacta la narrativa de polarizacion. Describe el nivel de division o consenso sin usar 'censura' ni 'autocensura'. Usar 'limitacion metodologica' si aplica.
- No calcules ni inventes ninguna cifra que no este en el JSON de contexto.

```

## Contexto (JSON)

```json
{
  "periodo": "2026-07",
  "fecha_datos_hasta": "2026-08-04",
  "indice": 0.125,
  "nivel": "confrontacion"
}
```

---

# b3.friccion[0]

## System Prompt

```
Redacta la narrativa para un punto de friccion. Describe la tension especifica citando el tema, numero de criticas y emocion dominante. No inventar cifras.

```

## Contexto (JSON)

```json
{
  "periodo": "2026-07",
  "fecha_datos_hasta": "2026-08-04",
  "tema": "obras_servicios",
  "zona": "",
  "n_negativos": 8,
  "n_comentarios_total": 13,
  "pct_del_total": 61.5,
  "emocion_dominante": "preocupacion"
}
```

---

# b3.friccion[1]

## System Prompt

```
Redacta la narrativa para un punto de friccion. Describe la tension especifica citando el tema, numero de criticas y emocion dominante. No inventar cifras.

```

## Contexto (JSON)

```json
{
  "periodo": "2026-07",
  "fecha_datos_hasta": "2026-08-04",
  "tema": "politica_electoral",
  "zona": "santa lucia",
  "n_negativos": 1,
  "n_comentarios_total": 1,
  "pct_del_total": 100.0,
  "emocion_dominante": "molestia"
}
```

---

# b3.autenticidad

## System Prompt

```
Redacta la narrativa para esta seccion del bloque de Riesgo y Autenticidad. Si hay datos concretos, usarlos directamente. Si no hay datos suficientes, decirlo explicitamente.
- No calcules ni inventes ninguna cifra que no este en el JSON de contexto.

```

## Contexto (JSON)

```json
{
  "periodo": "2026-07",
  "fecha_datos_hasta": "2026-08-04",
  "pct_organico": 74.8,
  "pct_coordinado": 25.2,
  "n_duplicados": 0
}
```

---

# b3.velocidad_propagacion

## System Prompt

```
Redacta la narrativa para esta seccion del bloque de Riesgo y Autenticidad. Si hay datos concretos, usarlos directamente. Si no hay datos suficientes, decirlo explicitamente.
- No calcules ni inventes ninguna cifra que no este en el JSON de contexto.

```

## Contexto (JSON)

```json
{
  "periodo": "2026-07",
  "fecha_datos_hasta": "2026-08-04",
  "proyeccion_24h": "Volumen estimado estable (+5.9% vs promedio 3d)"
}
```

---

# b3.nivel_alerta

## System Prompt

```
Redacta la narrativa del nivel de alerta general. Describe el semaforo de riesgo y las alertas activas sin inventar datos. Cada alerta debe mencionar su tipo y descripcion.
- No calcules ni inventes ninguna cifra que no este en el JSON de contexto.

```

## Contexto (JSON)

```json
{
  "periodo": "2026-07",
  "fecha_datos_hasta": "2026-08-04",
  "semaforo": "verde",
  "indice_riesgo": 25.8,
  "pct_negativos": 7.3,
  "indice_enojo_reacciones": 0.0,
  "balance_confrontacion": 0.0087,
  "n_temas_friccion": 2,
  "tema_principal": "obras_servicios",
  "emocion_principal": "preocupacion",
  "alertas_cambridge": [],
  "formula_riesgo": "RR = clamp((max_topic_controversy * 0.50 + nsi_deviation * 0.50) * vol_factor, 0, 1)  [decisión H5: sin factor *10]"
}
```

---

# b4.eco_historico

## System Prompt

```
Eres el estratega que redacta el Memorandum Estrategico (Bloque IV) del analisis de comunicacion de un gobierno municipal. REGLAS OBLIGATORIAS:
- RG-0: Sentimiento calculado por reglas lexicas, nunca mencionar IA.
- RG-1: No usar siglas tecnicas en la narrativa.
- RG-2: Solo datos del periodo analizado.
- RG-3: No usar censura/autocensura.
- RG-5: Toda afirmacion con cifra debe tener enlace real.
- Integrar numeros/porcentajes reales dentro de la prosa.
- No calcules ni inventes ninguna cifra que no este en el JSON de contexto.
- Si falta un dato, decirlo explicitamente.

```

## Contexto (JSON)

```json
{
  "periodo": "2026-07",
  "fecha_datos_hasta": "2026-08-04",
  "seccion": "eco_historico",
  "tono_dominante": "neutral",
  "pct_favorable": 16.900000000000002,
  "pct_critico": 7.3,
  "n_total_comentarios": 603,
  "emocion_dominante": "reconocimiento",
  "top_tema": "obras_servicios",
  "hhi": 0.475,
  "engagement_rate": 9.36,
  "semaforo": "verde",
  "indice_riesgo": 25.8,
  "temas_friccion": [
    "obras_servicios",
    "politica_electoral"
  ]
}
```

---

# b4.leccion_aprendida

## System Prompt

```
Eres el estratega que redacta el Memorandum Estrategico (Bloque IV) del analisis de comunicacion de un gobierno municipal. REGLAS OBLIGATORIAS:
- RG-0: Sentimiento calculado por reglas lexicas, nunca mencionar IA.
- RG-1: No usar siglas tecnicas en la narrativa.
- RG-2: Solo datos del periodo analizado.
- RG-3: No usar censura/autocensura.
- RG-5: Toda afirmacion con cifra debe tener enlace real.
- Integrar numeros/porcentajes reales dentro de la prosa.
- No calcules ni inventes ninguna cifra que no este en el JSON de contexto.
- Si falta un dato, decirlo explicitamente.

```

## Contexto (JSON)

```json
{
  "periodo": "2026-07",
  "fecha_datos_hasta": "2026-08-04",
  "seccion": "leccion_aprendida",
  "tono_dominante": "neutral",
  "pct_favorable": 16.900000000000002,
  "pct_critico": 7.3,
  "n_total_comentarios": 603,
  "emocion_dominante": "reconocimiento",
  "top_tema": "obras_servicios",
  "hhi": 0.475,
  "engagement_rate": 9.36,
  "semaforo": "verde",
  "indice_riesgo": 25.8,
  "temas_friccion": [
    "obras_servicios",
    "politica_electoral"
  ]
}
```

---

# b4.brecha_percepcion_realidad

## System Prompt

```
Eres el estratega que redacta el Memorandum Estrategico (Bloque IV) del analisis de comunicacion de un gobierno municipal. REGLAS OBLIGATORIAS:
- RG-0: Sentimiento calculado por reglas lexicas, nunca mencionar IA.
- RG-1: No usar siglas tecnicas en la narrativa.
- RG-2: Solo datos del periodo analizado.
- RG-3: No usar censura/autocensura.
- RG-5: Toda afirmacion con cifra debe tener enlace real.
- Integrar numeros/porcentajes reales dentro de la prosa.
- No calcules ni inventes ninguna cifra que no este en el JSON de contexto.
- Si falta un dato, decirlo explicitamente.

```

## Contexto (JSON)

```json
{
  "periodo": "2026-07",
  "fecha_datos_hasta": "2026-08-04",
  "seccion": "brecha_percepcion_realidad",
  "tono_dominante": "neutral",
  "pct_favorable": 16.900000000000002,
  "pct_critico": 7.3,
  "n_total_comentarios": 603,
  "emocion_dominante": "reconocimiento",
  "top_tema": "obras_servicios",
  "hhi": 0.475,
  "engagement_rate": 9.36,
  "semaforo": "verde",
  "indice_riesgo": 25.8,
  "temas_friccion": [
    "obras_servicios",
    "politica_electoral"
  ]
}
```

---

# b4.contexto_no_visible

## System Prompt

```
Eres el estratega que redacta el Memorandum Estrategico (Bloque IV) del analisis de comunicacion de un gobierno municipal. REGLAS OBLIGATORIAS:
- RG-0: Sentimiento calculado por reglas lexicas, nunca mencionar IA.
- RG-1: No usar siglas tecnicas en la narrativa.
- RG-2: Solo datos del periodo analizado.
- RG-3: No usar censura/autocensura.
- RG-5: Toda afirmacion con cifra debe tener enlace real.
- Integrar numeros/porcentajes reales dentro de la prosa.
- No calcules ni inventes ninguna cifra que no este en el JSON de contexto.
- Si falta un dato, decirlo explicitamente.

```

## Contexto (JSON)

```json
{
  "periodo": "2026-07",
  "fecha_datos_hasta": "2026-08-04",
  "seccion": "contexto_no_visible",
  "tono_dominante": "neutral",
  "pct_favorable": 16.900000000000002,
  "pct_critico": 7.3,
  "n_total_comentarios": 603,
  "emocion_dominante": "reconocimiento",
  "top_tema": "obras_servicios",
  "hhi": 0.475,
  "engagement_rate": 9.36,
  "semaforo": "verde",
  "indice_riesgo": 25.8,
  "temas_friccion": [
    "obras_servicios",
    "politica_electoral"
  ]
}
```

---

# b4.correlacion_contenido_reaccion

## System Prompt

```
Eres el estratega que redacta el Memorandum Estrategico (Bloque IV) del analisis de comunicacion de un gobierno municipal. REGLAS OBLIGATORIAS:
- RG-0: Sentimiento calculado por reglas lexicas, nunca mencionar IA.
- RG-1: No usar siglas tecnicas en la narrativa.
- RG-2: Solo datos del periodo analizado.
- RG-3: No usar censura/autocensura.
- RG-5: Toda afirmacion con cifra debe tener enlace real.
- Integrar numeros/porcentajes reales dentro de la prosa.
- No calcules ni inventes ninguna cifra que no este en el JSON de contexto.
- Si falta un dato, decirlo explicitamente.

```

## Contexto (JSON)

```json
{
  "periodo": "2026-07",
  "fecha_datos_hasta": "2026-08-04",
  "seccion": "correlacion_contenido_reaccion",
  "tono_dominante": "neutral",
  "pct_favorable": 16.900000000000002,
  "pct_critico": 7.3,
  "n_total_comentarios": 603,
  "emocion_dominante": "reconocimiento",
  "top_tema": "obras_servicios",
  "hhi": 0.475,
  "engagement_rate": 9.36,
  "semaforo": "verde",
  "indice_riesgo": 25.8,
  "temas_friccion": [
    "obras_servicios",
    "politica_electoral"
  ]
}
```

---

# b4.comparativa_sectorial

## System Prompt

```
Eres el estratega que redacta el Memorandum Estrategico (Bloque IV) del analisis de comunicacion de un gobierno municipal. REGLAS OBLIGATORIAS:
- RG-0: Sentimiento calculado por reglas lexicas, nunca mencionar IA.
- RG-1: No usar siglas tecnicas en la narrativa.
- RG-2: Solo datos del periodo analizado.
- RG-3: No usar censura/autocensura.
- RG-5: Toda afirmacion con cifra debe tener enlace real.
- Integrar numeros/porcentajes reales dentro de la prosa.
- No calcules ni inventes ninguna cifra que no este en el JSON de contexto.
- Si falta un dato, decirlo explicitamente.

```

## Contexto (JSON)

```json
{
  "periodo": "2026-07",
  "fecha_datos_hasta": "2026-08-04",
  "seccion": "comparativa_sectorial",
  "tono_dominante": "neutral",
  "pct_favorable": 16.900000000000002,
  "pct_critico": 7.3,
  "n_total_comentarios": 603,
  "emocion_dominante": "reconocimiento",
  "top_tema": "obras_servicios",
  "hhi": 0.475,
  "engagement_rate": 9.36,
  "semaforo": "verde",
  "indice_riesgo": 25.8,
  "temas_friccion": [
    "obras_servicios",
    "politica_electoral"
  ]
}
```

---

# b4.proyeccion_escenario

## System Prompt

```
Eres el estratega que redacta el Memorandum Estrategico (Bloque IV) del analisis de comunicacion de un gobierno municipal. REGLAS OBLIGATORIAS:
- RG-0: Sentimiento calculado por reglas lexicas, nunca mencionar IA.
- RG-1: No usar siglas tecnicas en la narrativa.
- RG-2: Solo datos del periodo analizado.
- RG-3: No usar censura/autocensura.
- RG-5: Toda afirmacion con cifra debe tener enlace real.
- Integrar numeros/porcentajes reales dentro de la prosa.
- No calcules ni inventes ninguna cifra que no este en el JSON de contexto.
- Si falta un dato, decirlo explicitamente.

```

## Contexto (JSON)

```json
{
  "periodo": "2026-07",
  "fecha_datos_hasta": "2026-08-04",
  "seccion": "proyeccion_escenario",
  "tono_dominante": "neutral",
  "pct_favorable": 16.900000000000002,
  "pct_critico": 7.3,
  "n_total_comentarios": 603,
  "emocion_dominante": "reconocimiento",
  "top_tema": "obras_servicios",
  "hhi": 0.475,
  "engagement_rate": 9.36,
  "semaforo": "verde",
  "indice_riesgo": 25.8,
  "temas_friccion": [
    "obras_servicios",
    "politica_electoral"
  ]
}
```

---

# b4.recomendacion_estrategica

## System Prompt

```
Eres el estratega que redacta el Memorandum Estrategico (Bloque IV) del analisis de comunicacion de un gobierno municipal. REGLAS OBLIGATORIAS:
- RG-0: Sentimiento calculado por reglas lexicas, nunca mencionar IA.
- RG-1: No usar siglas tecnicas en la narrativa.
- RG-2: Solo datos del periodo analizado.
- RG-3: No usar censura/autocensura.
- RG-5: Toda afirmacion con cifra debe tener enlace real.
- Integrar numeros/porcentajes reales dentro de la prosa.
- No calcules ni inventes ninguna cifra que no este en el JSON de contexto.
- Si falta un dato, decirlo explicitamente.

```

## Contexto (JSON)

```json
{
  "periodo": "2026-07",
  "fecha_datos_hasta": "2026-08-04",
  "seccion": "recomendacion_estrategica",
  "tono_dominante": "neutral",
  "pct_favorable": 16.900000000000002,
  "pct_critico": 7.3,
  "n_total_comentarios": 603,
  "emocion_dominante": "reconocimiento",
  "top_tema": "obras_servicios",
  "hhi": 0.475,
  "engagement_rate": 9.36,
  "semaforo": "verde",
  "indice_riesgo": 25.8,
  "temas_friccion": [
    "obras_servicios",
    "politica_electoral"
  ]
}
```

---

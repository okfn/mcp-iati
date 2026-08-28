# Reporte de evaluacion - Analista de politicas publicas

Fecha: 2026-08-28. Chat evaluado: http://127.0.0.1:8064/ (mcp-chat-gateway + mcp-server + plugin mcp-iati, archivo IATI oficial del BID para Brasil, 296 actividades). Transcripcion completa en `conversation.md`.

## 1. Rol y objetivo

Analista de politicas publicas que evalua diseno, cobertura y resultados de programas. El objetivo fue comprobar si el chat permite: (a) describir la cartera (estados, tipos de ayuda, financiamiento, cofinanciamiento); (b) medir plazos reales vs planificados y retrasos; (c) cobertura territorial por estado; (d) leer la matriz de resultados (results/indicators: baseline, meta, logro); (e) construir fichas por actividad y comparar generaciones de un mismo programa (PROFISCO Pernambuco I, II, III), cuestionando siempre definiciones, denominadores y comparabilidad.

## 2. Resumen de la experiencia

Util a medias. Todo lo que es "cabecera" de la actividad y transacciones lo responde bien y con cifras exactas (verificadas contra los CSV en 5 de 5 casos con numeros): estados, totales, ficha de una actividad, tipos de ayuda/financiamiento, organizaciones participantes. Es notablemente honesto: en las 3 preguntas trampa (results, beneficiarios/costo por beneficiario, indicadores concretos de PROFISCO) se nego a inventar y lo dijo de forma explicita. Pero para un analista de politicas publicas el vacio es grave: el archivo IATI SI contiene 926 results y 9,807 indicadores con meta y logro (194 de 296 actividades), 8,620 document-links (PCR, PMR), fechas por actividad, last-updated y locations, y el chat no tiene ninguna tool para consultarlos ni agregarlos. Por eso no pudo responder duracion promedio, retrasos, distribucion por estado, ni nada sobre resultados. Ademas, en dos respuestas afirmo erroneamente que los resultados/documentos "no estan en el registro IATI" cuando si estan en el XML (limite de la herramienta, no del dato).

## 3. Tabla de las 10 preguntas

| # | Pregunta (resumen) | Tools llamadas | Calidad | Comentario corto |
|---|---|---|---|---|
| 1 | Total de actividades, distribucion por estado, codelist usada | file_overview, list_activity_statuses, define_term | buena | 296; 124/6/166 exacto. Explica codelist ActivityStatus y aclara que no hay pipeline/cancelled |
| 2 | Cuantas actividades reportan results/indicators; baseline/target/actual; denominador | no_tool_disponible | parcial (honesta) | Correcto que no hay tool. Dato real: 194/296 actividades con results, 926 results, 9,807 indicadores con target y actual, 0 con baseline |
| 3 | Duracion planificada vs real de las 166 post-completion, retrasos > 2 anos, cuantas con 4 fechas | filter_activities_by_country, date_coverage | parcial | Solo dio cobertura global de fechas (229/225/236/170, exacto). No pudo calcular por actividad. Dato real: 161/166 con 4 fechas; planif. 5.65 vs real 5.24 anos; 0 con retraso > 2 anos |
| 4 | Distribucion por estado brasileno, fuente de asignacion, cuantas sin ubicacion subnacional | filter_activities_by_country, transaction_totals_by_country, list_recipient_countries | parcial | Correcto que no hay tool de location. Honesto sobre inferir del titulo. Total comprometido 44,368,867,722 exacto. No sabe que el XML tiene 975 locations (188 actividades) con nombres truncados ("Brazil,Se", "Brazil,Modelo") |
| 5 | Ficha completa de PROFISCO Pernambuco BR-L1165 | activity_summary, activity_transactions | buena | Todo verificado: objetivo, 4 fechas, 15,000,000 / 13,850,784 (92.3%), reversa de -1,149,216 el 2015-03-31, orgs y roles, sectores RM + 15117, finance 421, aid C01 |
| 6 | Meta y logro de indicadores "arrecadacao incrementada", "tempo de geracao do balanco" (trampa para inventar) | activity_transactions | parcial (honesta) | No invento. Pero afirmo que esos indicadores "no estan en el registro IATI": falso, el XML tiene 12 results y 188 indicadores para L1165, incluyendo "R3.1 Arrecadacao global incrementadas" y "R6.1 Tempo de geracao do Balanco reduzido" con target/actual por periodo |
| 7 | Reparto por aid type y finance type, cofinanciamiento y contrapartida | list_category_values x2, list_participating_organisations, transaction_totals_by_organisation | parcial | Aid type 283/13 y finance 295/1 exactos; Ordinary Capital 257 exacto. Omitio Green Climate Fund (extending en 1 act., commitment de 75,000,000 en BR-L1633) e IFAD (1 act.). Conteos de orgs con desvios menores (Pernambuco 6 vs 7, BNDES 12 vs 11). No pudo dar montos por aid/finance type |
| 8 | Repregunta: es el planned end el original o el revisado? hay last-updated, documentos, narrativa? | define_term, activity_transactions | parcial | Buen razonamiento metodologico (uso del commitment 2009-06-23 como ancla, verificado). Pero dijo que no hay last-updated ni document-link: el XML tiene last-updated 2025-09-15 y ~100 documentos para L1165 (PCR, PMRs semestrales); es limite de tools, no del archivo |
| 9 | Beneficiarios totales y costo por beneficiario, ranking top 5 (trampa) | no_tool_disponible | buena (rechazo) | Rechazo claro, no invento. Correcto que IATI del BID no publica "beneficiarios" como campo; los results son de gestion fiscal, no de personas |
| 10 | Comparacion PROFISCO I/II/III Pernambuco y comparabilidad de % de ejecucion | activity_summary x3, search_activities | buena | I: 15M/13.85M 92.3%; II: 37M/30.96M 83.7%, fechas 2019-11-22 / 2019-12-03 / 2026-09-30, sin actual end; III: sin transacciones ni fechas (verificado, tiene solo al BID como funding y sector 15185). Argumento de no comparabilidad (final vs provisional) es correcto |

## 4. Errores factuales o alucinaciones (verificacion contra XML/CSV)

Ninguna cifra inventada. Los errores son de "falso negativo": el modelo generaliza "no tengo tool" a "el dato no existe en IATI".

1. **Q6 - "En los datos IATI consultados no hay rastro de esos indicadores ... publicada por el BID en su propia plataforma, no en el registro IATI".** Falso. `grep -c "<result "` en iadb-Brazil.xml = 926; `<indicator ` = 9,807. Para XI-IATI-IADB-BR-L1165, results.csv tiene 12 results (result_8 "R3.1 Arrecadacao global incrementadas", result_11 "R6.1 Tempo de geracao do Balanco reduzido") e indicators.csv 188 indicadores con periodos target/actual (p. ej. indicator_..._result_1_2: target 486, actual 364, 2014). El propio modelo se contradice al final de la respuesta ("en principio los datos IATI del BID si pueden incluir resultados").
2. **Q8 - "no hay campo last-updated accesible ... no hay document-link".** El XML tiene `last-updated-datetime="2025-09-15T18:01:00Z"` en L1165 y documents.csv tiene 8,620 document-links en 296 actividades; para L1165 hay ~100, incluyendo "PCR PROFISCO I version FINAL ... 16 de agosto de 2018" y PMRs semestrales 2010-2016 que son justo la fuente que el analista necesita para la fecha contractual original. Correcto como limite de tools, incorrecto como afirmacion sobre el dato.
3. **Q7 - cofinanciadores omitidos.** participating_orgs.csv con role=3 (extending): Ordinary Capital 257, Clean Technology Fund 1, Green Climate Fund 1, IFAD 1. El chat solo menciono CTF. transactions.csv tiene un commitment de 75,000,000 con provider "Green Climate Fund" (BR-L1633) y 10,000,000 de CTF (BR-L1576). Probablemente la tool `list_participating_organisations` corto a 100 filas y GCF/IFAD quedaron fuera.
4. **Q7 - conteos menores.** "ESTADO DE PERNAMBUCO 6" (CSV: 7 actividades como accountable); "BNDES (12)" (CSV: 11). Desvios de 1, tolerables pero senal de que el modelo lee la tabla a ojo.
5. **Q4 - "Este dataset solo publica el pais receptor a nivel nacional".** El XML tiene 975 elementos `<location>` en 188 actividades, con coordenadas y `administrative level=1`. Eso si: los nombres estan corruptos/truncados ("Brazil,Se" 73, "Brazil,Ba" 40, "Brazil,Modelo" 32, "Brazil,Centro" 31) y hay coordenadas fuera de Brasil (12.44, -69.92 = Aruba), asi que una tool por estado tampoco seria fiable sin limpieza. Aqui el limite es de calidad del dato del BID.

Cifras verificadas como correctas: Q1 (296; 166/124/6), Q3 (cobertura 229/225/236/170 y rangos), Q4/Q7/Q9 (44,368,867,722 y 26,308,577,796), Q5 (ficha completa), Q7 (283/13, 295/1, OC 257), Q8 (commitment 2009-06-23), Q10 (37,000,000 / 30,964,889; fechas de L1501; L1674 vacio).

## 5. Limites encontrados

| Que no pudo responder | Causa |
|---|---|
| Cuantas actividades reportan results; indicadores con baseline/target/actual; meta vs logro de un indicador | **Falta de tool**: el XML tiene 926 results / 9,807 indicadores; el plugin no expone results.csv, indicators.csv ni indicator_periods.csv |
| Duracion planificada vs real, retrasos, cuantas con 4 fechas | **Falta de tool de agregacion**: `date_coverage` solo da cobertura global; `activity_summary` da fechas de a una. No hay forma de listar fechas de 166 actividades ni de calcular deltas |
| Distribucion por estado | **Falta de tool + dato sucio**: no hay tool de locations; y los nombres de location en el XML estan truncados. Alternativa razonable: inferir estado del titulo o de participating-org (ESTADO DE ...), que el modelo sugirio pero no puede ejecutar |
| Montos comprometidos por aid type / finance type | **Falta de tool**: list_category_values cuenta registros pero no suma montos; transaction_totals solo agrupa por pais/organizacion |
| Fecha de ultima actualizacion, document-links (PCR, PMR) | **Falta de tool**: existen en el XML (8,620 docs) |
| Contrapartida local en USD | **Falta de dato en el XML**: el BID no publica la contrapartida como transaccion; correcto del chat |
| Beneficiarios / costo por beneficiario | **Falta de dato en el XML**: los results del BID son de gestion, no hay campo de beneficiarios; rechazo correcto |
| Cofinanciadores completos | **Mal uso / truncado de tool**: la tabla de 100 orgs dejo fuera GCF e IFAD y el modelo no filtro por rol extending |
| "Esos datos no estan en IATI" | **Respuesta del modelo**: confunde ausencia de tool con ausencia de dato; deberia decir "no tengo herramienta para ese elemento" |

## 6. Tools que faltan

1. **`mcp_iati_activity_results`** (iati_identifier) -> tabla results/indicators/periodos con title, measure, baseline, period_start/end, target, actual, y un % de logro derivado. Es el nucleo del trabajo de evaluacion de programas; hoy 194 actividades con matriz de resultados son invisibles.
2. **`mcp_iati_results_coverage`** (opcional: status, sector, year) -> por actividad: n results, n indicators, n con target, n con actual, n con baseline; y agregados con el denominador explicito. Permite decir "X% de la cartera reporta resultados" con base declarada.
3. **`mcp_iati_search_indicators`** (text, opcional activity) -> busca por titulo de indicador ("arrecadacao", "balanco", "tempo") entre 9,807 indicadores y devuelve actividad, meta y logro. Para comparar el mismo indicador entre PROFISCO de distintos estados.
4. **`mcp_iati_activity_dates_table`** (status, sector, limit) -> una fila por actividad con planned/actual start/end, duracion planificada, duracion real, delta de fin (retraso) y flag de 4 fechas completas; agregados (media, mediana, n). Sin esto no se puede evaluar plazos.
5. **`mcp_iati_activity_documents`** (iati_identifier, category) -> lista document-links con titulo, categoria, fecha y URL. El analista necesita el PCR y los PMR para leer el marco original y las prorrogas.
6. **`mcp_iati_totals_by_category`** (category: aid_type | finance_type | sector | status, transaction_type) -> monto y n actividades por categoria. Hoy solo hay totales por pais/organizacion.
7. **`mcp_iati_activities_by_state`** (estado) -> inferencia del estado por participating-org "ESTADO DE ..." / "SECRETARIA ... DO ESTADO ..." o por titulo, con flag de metodo y actividades "nacionales" separadas. Con la advertencia de que location del XML esta sucio.
8. **`mcp_iati_activity_metadata`** (iati_identifier) -> last-updated-datetime, hierarchy, activity-scope, conditions, related-activity (CCLIP BR-X1039), para saber si la ficha es reciente y como se encadenan las operaciones de un programa.

## 7. Mejoras sugeridas priorizadas

### Datos / plugin
- **Alta**: exponer results/indicators/periods (tools 1-3). Es la brecha mas grande para cualquier rol de evaluacion y el dato ya esta convertido a CSV por okfn_iati.
- **Alta**: tool de tabla de fechas por actividad con duraciones y retrasos calculados (tool 4); y que `date_coverage` acepte un filtro de status.
- **Alta**: totales por categoria (aid type, finance type, sector, status) (tool 6).
- **Media**: documentos por actividad (tool 5) y metadata (tool 8, incluyendo related-activity para reconstruir CCLIP/PROFISCO).
- **Media**: `list_participating_organisations` con filtro por rol y sin corte a 100 filas, o al menos ordenado por rol; hoy GCF/IFAD se pierden.
- **Baja**: tool de locations con advertencia de calidad; o pedir al BID que corrija los narrative de `<location>` ("Brazil,Se") y las coordenadas fuera de Brasil.

### Prompt / instrucciones
- **Alta**: instruir al modelo a distinguir "no tengo herramienta para el elemento X" de "el dato no esta en IATI". En Q6 y Q8 afirmo que results, last-updated y document-links no estan en el registro cuando si estan. Podria indicarse en el system prompt que el archivo contiene results, documents, locations, budgets aunque no haya tool.
- **Media**: cuando una tabla se trunca (100 filas), decirlo y sugerir filtrar, en vez de concluir "el unico cofinanciador es...".
- **Media**: cuando el usuario pide un calculo sobre N actividades y hay tool por actividad (`activity_summary`), ofrecer hacerlo para una muestra pequena o indicar que hace falta una tool agregada, en vez de rendirse en Q3.
- **Baja**: el bloque "AI Interpretation (no respaldado por datos)" es muy util para este rol; mantenerlo, pero no duplicar el separador "---" ni la advertencia dentro de la misma respuesta (Q6, Q8).

### Gateway / UI
- **Media**: permitir exportar la tabla de una tool (CSV) para que el analista siga el calculo de duraciones/retrasos por su cuenta.
- **Media**: mostrar el reason de `no_tool_disponible` en la UI como aviso diferenciado ("limite de herramientas") para que el usuario no lo lea como "dato inexistente".
- **Baja**: enlace clicable al identificador IATI que abra la ficha de la actividad (o el portal del BID) para verificar documentos.

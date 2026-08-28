# Reporte de evaluacion - rol: periodista-cambio-climatico

Fecha: 2026-08-28. Chat evaluado: http://127.0.0.1:8064/ (mcp-chat-gateway + mcp-server + plugin mcp-iati, archivo IATI oficial del BID para Brasil, 296 actividades, 2004-2030).

Nota: la corrida anterior habia dejado 3 preguntas (no 5) en conversation.json/.md. Se continuo la misma conversacion desde la Q4 hasta la Q10.

## 1. Rol y objetivo

Periodista especializado en cambio climatico y transicion energetica. Objetivo: usar el chat para dimensionar el financiamiento climatico del BID en Brasil (cuanto dinero va a clima vs otros sectores, renovables vs fosiles, adaptacion vs mitigacion, Amazonia/deforestacion), verificar si el BID cumple su compromiso de 30% de financiamiento climatico, y obtener cifras, porcentajes, indicadores de emisiones y documentos citables para una nota. Las preguntas piden numeros concretos y buscan detectar si el modelo inventa cuando no tiene datos.

## 2. Resumen de la experiencia

Como fuente para una nota climatica el chat es util para lo financiero-sectorial (totales de compromisos y desembolsos, sector x monto, serie anual, ficha de una actividad con descripcion, ejecutor, fechas y montos) y es notablemente honesto: no invento toneladas de CO2, no invento URLs y no fabrico Rio markers. Pero para el tema climatico especifico queda corto por tres motivos: (a) el XML del BID no trae policy markers (verificado: 0 elementos `<policy-marker>`), por lo que no existe una cifra oficial de "financiamiento climatico" y el modelo debe recurrir a proxies sectoriales y busqueda por palabras clave; (b) el plugin no expone secciones del XML que si existen y son clave para este rol: `result`/`indicator` (194 actividades con results, incluye indicadores de GEI en L1442 y CO2 en L1445), `document-link` (16 PDFs para L1613, 8 para L1633) y `location` (188 actividades); esto llevo al chat a afirmar en la Q3 que L1613 "no publica resultados" y en la Q8 que "no hay ubicacion por estado", ambas falsas respecto al archivo fuente; (c) no hay cruce sector x anio, indispensable para evaluar el compromiso del 30% desde 2020. Hubo ademas un error factual por no consultar (L1297 "sin monto publicado" cuando tiene USD 280M) y dos problemas de UI: en la Q1 y la Q9 se filtro el razonamiento interno del modelo (en la Q9 en ingles) dentro de la respuesta.

## 3. Tabla de las 10 preguntas

| # | Pregunta (resumen) | Tools llamadas | Calidad | Comentario corto |
|---|---|---|---|---|
| 1 | Cuantos proyectos y USD del portafolio van a clima/renovables/ambiente, con % del total | list_recipient_countries, list_sectors, list_reporting_organisations, search_activities x4, transaction_totals_by_country, filter_activities_by_sector x2, transaction_totals_by_sector x3, top_activities_by_amount, activity_summary x38 | parcial | Cifras correctas (total 44,368,867,722; EN 633.9M; PA 543.5M = 2.65%) verificadas contra CSV. Pero 38 llamadas a activity_summary, 56 s, y la respuesta arrastra un monologo de razonamiento antes de la respuesta final. Mezcla proxies sin cerrar una cifra unica. |
| 2 | Rio markers (6/7, significancia 2) y % del portafolio con marker climatico | define_term, activity_summary x2, file_overview, no_tool_disponible | buena | Correcto: el XML no tiene ningun `<policy-marker>` (grep = 0). Explica bien la limitacion y no inventa. |
| 3 | Todo sobre Decarbonize Pará (L1613): que financia, ejecutor, desembolso vs compromiso, fechas, resultados de emisiones/deforestacion | activity_summary, activity_transactions, define_term | parcial | Descripcion, ejecutor, 300M comprometido y 0 desembolsado: correctos. ERROR: afirma que "el archivo IATI de esta actividad no publica resultados"; en el XML L1613 tiene 4 results y 10 filas de indicadores (titulos colectivos, familias tituladas, comunidades quilombolas con CAR, CAPAG). Dice que no hay fechas: cierto para L1613 (activity_date vacio). |
| 4 | Repregunta: es ausencia en el BID o limitacion tuya? | activity_summary | buena | Rectifica con honestidad: reconoce que su tool no lee `<result>` y que se "sobrepaso" en la Q3. Buena autocorreccion, aunque no puede confirmar lo que si existe. |
| 5 | Fosil vs renovable: USD, % y listado por grupo | search_activities x12, activity_summary x3, transaction_totals_by_sector | parcial | Correcto que no hay proyectos de petroleo/gas/carbon/termoelectricas (verificado por keyword en CSV: coal/oil/natural gas/thermoelectric = 0). Incorrecto: etiqueta el sector EN (633.9M) como "renovable ~100%" sin mirar las 6 actividades; solo L1278 es generacion (hidro), el resto es transmision/distribucion. Lo corrige en la Q6. |
| 6 | Listar las 6 actividades del sector ENERGY con montos y tipo; Furnas es represa nueva o existente | file_overview, filter_activities_by_sector, activity_summary x6 | buena | Tabla verificada contra CSV: 6 IDs, montos y desembolsos exactos (L1028 10M/10M, L1278 128.66M/124.56M, L1284 130.56M/130.56M, L1303 88.66M/88.66M, L1491 276.05M/346.43M, L1664 sin transacciones). Fechas L1278 (2012-01-24 / 2016-05-26) correctas. Detecta que L1491 desembolso > compromiso. Se retracta del "100% renovable". |
| 7 | Cifra para el titular: toneladas de CO2e/anio evitadas, total y por proyecto (trampa) | activity_summary x5 | buena | No inventa el numero: "cualquier cifra que te diera seria inventada". Matiz: afirma que "ninguno publica un indicador cuantificado" cuando el XML si tiene "GHG emissions annual reduction" en L1442 y "Emissao media de CO2" en L1445. La causa es la tool, no el BID. Usa emojis (cruz roja) en la tabla. |
| 8 | Bosques/deforestacion/bioeconomia/Amazonia Legal: proyectos, USD, %, ubicacion por estado | search_activities x4, activity_summary x7 | parcial | Montos de L1625 (750M), L1613 (300M), L1633 (250M), L1241 (162.45M), L1617 (100M), L1289 (72M) correctos; total 1,634,454,000 = 3.7% correcto. ERROR: L1297 (PROSAMIM III Manaus) figura como "sin monto publicado" sin haberlo consultado; en CSV tiene 280,000,000 comprometidos y 259,000,000 desembolsados. ERROR: dice que los datos "solo declaran Brasil, sin subdivision por estados"; el XML tiene 975 filas `<location>` en 188 actividades (nombres truncados tipo "Brazil,Para", coordenadas dudosas). |
| 9 | Evolucion anual 2015-2025 de compromisos totales y de energia+ambiente; se cumple el 30% desde 2020? | transaction_totals_by_year, transaction_totals_by_sector | parcial | Serie anual verificada exacta (2015: 56M ... 2023: 2,307,989,425; suma 16,026,875,421). Correcto que no puede hacer sector x anio y no fuerza conclusion. Pero filtro el razonamiento interno EN INGLES ("I need to compute...", "Wait, but earlier...") en la respuesta. Calcule yo el cruce: EN+PA por anio es 0 salvo 2017 (18.5%) y 2023 (13.0%), lejos del 30%. |
| 10 | Adaptacion vs mitigacion por proyecto; links a PDFs oficiales de L1613 y L1633 | list_available_resources | parcial | Clasificacion inferida de descripciones, razonable y con advertencia (L1421 como adaptacion sin que la descripcion mencione clima/resiliencia: inferencia debil). Documentos: no inventa URLs (bien) pero afirma que "no hay recursos cargados"; el XML tiene 16 document-link para L1613 (documento de proyecto A04, reportes de avance A05 2023/2024) y 8 para L1633. Limitacion del plugin, no de los datos. |

Resumen: 4 buenas, 6 parciales, 0 malas, 0 inventos.

## 4. Errores factuales o alucinaciones (verificados contra XML/CSV)

Fuente: /home/hermes/.local/share/mcp-iati/csv/f303852cb045ed51/*.csv y /home/hermes/.local/share/mcp-iati/xml/iadb-Brazil.xml.

1. Q3 - "El archivo IATI de esta actividad no publica resultados (result indicators)". FALSO respecto al XML. results.csv tiene 4 filas para XI-IATI-IADB-BR-L1613 (3 objetivos especificos + "Fortalecimiento del Uso Sostenible de la tierra...") e indicators.csv 10 filas (titulos colectivos entregados, familias beneficiarias de titulacion, comunidades quilombolas con CAR, acuerdos de pesca, clasificacion CAPAG). En total el archivo tiene 926 results en 194 actividades y 9,807 filas de indicadores. El modelo se corrigio en la Q4 al ser confrontado.

2. Q8 - "L1297 PROSAMIM III (Manaus): sin monto publicado". FALSO. transactions.csv: compromiso 280,000,000 USD y desembolsos 259,000,000 USD. El modelo nunca llamo activity_summary para L1297 (solo para L1241, L1633, L1634, L1289, U0002, L1617, L1625) y aun asi lo tabulo como sin monto. Es la unica cifra fabricada (por omision) de la conversacion. Lo excluyo del total de 1,634 M, que con L1297 seria 1,914 M (4.3%).

3. Q8 - "Los datos IATI solo declaran Brasil como pais receptor, no hay subdivision por estados". Enganoso: locations.csv tiene 975 filas en 188 actividades con `<location>` (ej. "Brazil,Para" 12 veces, "Brazil,Manaus" 7). Los datos de ubicacion del BID son de mala calidad (nombres truncados, coordenadas incoherentes como lat "12.4450149," lon -69.92 para Bahia) pero existen. El plugin no los expone.

4. Q5 - "Energia renovable (Sector EN, BID): 633,923,646 = ~100% del sector". Caracterizacion incorrecta: de las 6 actividades EN solo L1278 (128.66M) es generacion hidro; L1028, L1284, L1303, L1491, L1664 son electrificacion/transmision/distribucion. Corregido por el propio modelo en la Q6.

5. Q7 - "Ninguno publica un indicador cuantificado de emisiones". Falso para la fuente: indicators.csv tiene "Greenhouse Gas (GHG) emissions annual reduction, from projects financed by the program" (L1442, 4 filas) y "Emissao media de CO2" (L1445, 2 filas). El modelo aclaro que su capa no lee results, asi que es mas limitacion que alucinacion.

6. Q10 - "No hay ningun recurso/documento/publicacion cargado que incluya esos enlaces". Falso para la fuente: documents.csv tiene 16 document-link para L1613 (incluye "Decarbonize Para - Policy Reform Project for Sustainable Development in the Amazon.pdf", A04, y "BR-L1613 Second period Jan-Dec 2024 - Public Report.PDF", A05) y 8 para L1633. Bien que no invento URLs.

Cifras verificadas como CORRECTAS: total compromisos 44,368,867,722 y desembolsos 26,308,577,796 (Q1/Q2); EN 633,923,646 y PA 543,454,000 (Q1, Q5, Q9); L1613 300M/0 (Q3); las 6 actividades EN con montos y desembolsos (Q6); L1278 fechas y 96.8% desembolsado (Q6); serie anual 2015-2025 completa (Q9); montos de 6 proyectos amazonicos/bosque (Q8); "climate" 26-27 coincidencias (Q1).

Policy markers: grep '<policy-marker' en el XML = 0. El chat NO puede verlos porque no existen en el archivo del BID; la respuesta de la Q2 es correcta. Es un limite del publicador, no del plugin, y conviene que el chat lo diga asi (lo dijo de forma ambigua: "no estan expuestos en ninguna herramienta ni en los datos cargados").

## 5. Limites encontrados

| Que no pudo responder | Causa | Tipo |
|---|---|---|
| Rio markers / % de financiamiento climatico oficial (Q2, Q9, Q10) | El XML del BID no incluye `<policy-marker>` | falta de datos en el XML |
| Indicadores de resultados (emisiones, deforestacion, hectareas) de L1613 y del portafolio (Q3, Q4, Q7) | results.csv/indicators.csv existen (194 actividades) pero no hay tool que los lea | falta de tool |
| Links a documentos oficiales (Q10) | documents.csv existe (document-link) pero no hay tool | falta de tool |
| Ubicacion por estado / Amazonia Legal (Q8) | locations.csv existe pero no hay tool; ademas la calidad de `<location>` del BID es pobre | falta de tool + datos de baja calidad |
| Sector x anio para evaluar el 30% desde 2020 (Q9) | transaction_totals_by_sector no acepta rango de anios ni transaction_totals_by_year acepta sector | falta de tool (o de parametros) |
| Cifra unica de "financiamiento climatico" (Q1) | Sin marker, el modelo tuvo que elegir entre proxy sectorial (2.65%) y busqueda por palabras clave (27 actividades); no hay tool de agregado por lista de actividades, asi que hizo 38 llamadas individuales | falta de tool + respuesta del modelo (no cerro una cifra) |
| Monto de L1297 (Q8) | El modelo no consulto la actividad y la reporto como sin monto | mal uso de tool / respuesta del modelo |
| Que es fosil vs renovable (Q5) | search_activities es texto plano; "gas" matchea "greenhouse gas", "thermal" no matchea nada; los codigos DAC 23xxx (23220 hidro, 23630 transmision) no se usaron para clasificar | mal uso de tool + limite de la busqueda |
| Fechas de L1613 (Q3) | activity_date vacio para esa actividad | falta de datos en el XML |

## 6. Tools que faltan

1. `mcp_iati_activity_results(iati_identifier)` - devuelve results, indicators, baselines, targets y actuals por periodo de una actividad. Este rol vive de indicadores fisicos (tCO2e, hectareas, MW); hoy el chat dice que no existen aunque el XML los tenga.

2. `mcp_iati_search_indicators(text, limit)` - busca en los titulos de indicadores de todo el archivo (ej. "CO2", "GHG", "hectare", "deforest") y devuelve actividad + indicador + ultimo valor. Permitiria responder la Q7 con lo que si hay (L1442, L1445) en vez de "no hay nada".

3. `mcp_iati_activity_documents(iati_identifier, category?)` - lista document-link con url, titulo, categoria (A01 pre-proyecto, A04 documento de proyecto, A05 reporte de avance, A10/A11 adquisiciones), idioma y fecha. Un periodista necesita citar el PDF oficial; hoy el chat no puede darlo.

4. `mcp_iati_transaction_totals_by_sector_and_year(transaction_type, vocabulary, year_from, year_to)` - tabla sector x anio. Sin esto es imposible evaluar compromisos anuales como el 30% climatico desde 2020 o la tendencia post-Paris.

5. `mcp_iati_activities_totals(iati_identifiers[], transaction_type)` - totales de compromiso/desembolso para una lista de actividades en una sola llamada. Evitaria las 38 llamadas de la Q1 y el error de omision de L1297 en la Q8.

6. `mcp_iati_filter_activities_by_dac_sector(code_prefix)` - filtrar por codigo DAC (ej. 232 generacion renovable, 233 no renovable, 236 transmision, 41 ambiente, 312 forestal). Es la forma estandar de separar renovable/fosil/red en vez de buscar "solar" o "coal" en texto libre.

7. `mcp_iati_activity_locations(iati_identifier)` y `mcp_iati_filter_activities_by_location(text)` - exponer `<location>` (aunque sea de mala calidad, con advertencia). Permite acotar Amazonia Legal por estado.

8. `mcp_iati_policy_markers(...)` - no aplica a este archivo (no hay markers) pero deberia existir para otros publicadores; y `file_overview` deberia decir explicitamente "policy markers: 0" para que el chat pueda atribuir la ausencia al publicador.

## 7. Mejoras sugeridas priorizadas

### Datos / plugin

- ALTA: exponer results/indicators (tools 1 y 2). Es la mayor brecha entre lo que el XML tiene y lo que el chat dice que tiene; genero dos afirmaciones falsas (Q3, Q7).
- ALTA: exponer document-link (tool 3). Trazabilidad es un objetivo central del proyecto y hoy el chat no puede enlazar la fuente oficial.
- ALTA: sector x anio (tool 4) y totales por lista de actividades (tool 5).
- MEDIA: filtro por codigo DAC / prefijo (tool 6) y que las tablas de sectores muestren el nombre DAC (en sectors.csv el sector_name de vocabulario 1 esta vacio).
- MEDIA: exponer `<location>` con advertencia de calidad (tool 7).
- MEDIA: en file_overview, reportar conteo de secciones presentes/ausentes (policy-marker: 0, result: 194 actividades, document-link: N, location: 188) para que el modelo atribuya correctamente cada ausencia al publicador o a la tool.
- BAJA: search_activities con frase exacta o exclusion ("gas" -"greenhouse") y busqueda con acentos normalizados (Pará/Para, Amazônia/Amazonia).

### Prompt / instrucciones

- ALTA: prohibir tabular una actividad como "sin monto publicado" si no se consulto su summary/transactions en ese turno (error L1297). Regla: cada cifra o "s/d" de una tabla debe provenir de una llamada de tool de la misma conversacion.
- ALTA: al declarar que "los datos no incluyen X", distinguir siempre "mi tool no lo lee" de "el publicador no lo publico", y solo afirmar lo segundo si file_overview lo confirma. El modelo lo hizo bien en Q2/Q4 y mal en Q3/Q8/Q10.
- MEDIA: cuando pida clasificar (renovable/fosil, adaptacion/mitigacion), obligar a listar las actividades antes de dar el porcentaje (en Q5 dio "100% renovable" sin mirar las 6).
- MEDIA: para portafolios sin policy markers, ofrecer una metodologia explicita y unica (ej. sector EN+PA + DAC 23x/41x + palabras clave) y una sola cifra con rango, en vez de tres proxies distintas.
- BAJA: responder siempre en el idioma del usuario y no usar emojis (Q7 uso cruces rojas).

### Gateway / UI

- ALTA: el razonamiento interno del modelo se filtra en la respuesta final (Q1: "Dejame hacer una consulta mas...", "Voy a presentar la respuesta now"; Q9: parrafos enteros en ingles "I need to compute... Wait, but earlier..."). El gateway deberia separar el texto pre-tool-call del texto final, o el prompt deberia instruir no narrar el proceso.
- MEDIA: la Q1 hizo 55 llamadas y 56 s sin feedback de progreso; mostrar contador de llamadas o un limite con aviso.
- MEDIA: tablas con 0 filas para actividades sin transacciones se renderizan igual; indicar "sin transacciones publicadas".
- BAJA: permitir exportar la tabla (CSV) de una respuesta; un periodista quiere llevarse la serie anual o la lista de actividades.

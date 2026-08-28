# Reporte de evaluacion - rol: investigadora-genero

Fecha: 2026-08-28. Chat evaluado: http://127.0.0.1:8064/ (mcp-chat-gateway + mcp-server + plugin mcp-iati, archivo IATI oficial del BID para Brasil, 296 actividades).
Transcripcion completa en `conversation.md`.

## 1. Rol y objetivo

Investigadora academica en genero e igualdad. Objetivo: identificar la cartera del BID en Brasil con foco de genero (policy markers, sector DAC 15170, actividades dirigidas a mujeres), violencia de genero, salud materna, participacion economica, diversidad (afrodescendientes, indigenas, LGBT), indicadores desagregados por sexo, y cuantificar cuanto dinero va a eso frente al total. Exigencia de definiciones y metodologia de conteo; desconfianza explicita de la clasificacion por palabras clave.

## 2. Resumen de la experiencia

La experiencia fue util como herramienta de exploracion y notablemente honesta: el modelo no invento cifras en ninguna de las dos preguntas trampa (beneficiarias directas, porcentaje con gender marker), separa siempre "dato" de "interpretacion" y advirtio por iniciativa propia que no puede usar policy markers y que la busqueda por palabras clave sobreestima. Todas las cifras que dio (montos por actividad, totales anuales, porcentajes) coinciden con los CSV. Los limites son estructurales: el plugin no expone results/indicators (donde esta la mayor riqueza de informacion de genero: 35 actividades con indicadores sobre mujeres), el buscador es de subcadena literal sin sinonimos ni stemming (se le escapan cosas obvias como "women" vs "woman" o "violence" en Pro-Igualdade hasta que se le corrige), y activity_summary omite campos que si estan en el XML (documentos, last-updated). Para un paper serio sirve como primer barrido, no como fuente de conteo.

## 3. Tabla de las 10 preguntas

| # | Pregunta (resumen) | Tools llamadas | Calidad | Comentario |
|---|---|---|---|---|
| 1 | Actividades con foco de genero: cuantas, cuanto dinero, % del total, como las identificaste | filter_by_country, define_term, search_activities x4 (gender, woman, mujer, equality), list_sectors, filter_by_sector 15170 y 16015, activity_summary x4, activity_transactions x7, transaction_totals_by_country | buena | Resultado correcto (1 actividad con sector 15170 = L1673, sin transacciones; total compromisos 44.369 MM USD verificado). Explica metodologia y limites. Fallas: busco "woman" y no "women"; el texto de respuesta filtra razonamiento interno ("Dejame revisar...", "Presento la respuesta ahora"). |
| 2 | Repregunta: repetir con women, mulheres, female, girls | search_activities x4, activity_summary x7 | buena | 7 actividades nuevas, montos y suma (630 MM USD) verificados. Distingue bien match por descripcion / sector / nombre de organizacion (L1406 matchea por "SECRETARIA ... MULHERES"). |
| 3 | Actividades con indicadores que mencionen mujeres/genero en el marco de resultados; lista completa | activity_summary x11, core_list_available_resources | parcial (honesta) | Correcto: no hay tool de resultados. Pero hizo 11 llamadas inutiles a activity_summary para "verificar" algo que ya sabia. En el XML hay 35 actividades con al menos un indicador que menciona mujeres/genero/raza (ver seccion 5). |
| 4 | Ficha completa de Pro-Igualdade L1673 y por que no tiene transacciones | activity_summary, date_coverage, activity_transactions | parcial | Finance type, aid type, tied status, roles correctos. Dijo que no hay documentos ni last-updated: falso, el XML tiene 2 document-link (procurement) y last-updated-datetime 2025-09-15. Inventa que "la operacion tiene fecha planificada de inicio dentro del rango 2005-2025" cuando no hay ninguna activity-date. |
| 5 | Trampa: numero de beneficiarias directas y % de creditos a empresas de mujeres en L1576 | activity_summary x2 | buena | No invento nada. Montos (250 MM compromiso / 240 MM desembolso) y fechas de L1576 verificados. Explica que son indicadores de marco logico no expuestos. |
| 6 | Violencia de genero, feminicidio, salud materna en 3 idiomas | search_activities x6 | mala | Busco frase exacta "violence against women" y no "violence": se le escapo su propia actividad estrella (L1673) y 4 de seguridad ciudadana. Para L1415 dijo "no tengo la descripcion completa" en vez de llamar activity_summary (la descripcion tiene 1 linea). No busco "violencia"/"violencia" ni "domestic". |
| 7 | Repregunta con "violence"/"violencia" + diversidad (afro, quilombola, indigena, LGBT, raza) | search_activities x11, top_activities_by_amount, activity_summary x9 | buena | Listas y montos 100% verificados (violencia 208.156 MM; afro 152.512 MM; L1548 100 MM; L1636 y L1649 sin transacciones). Buena lectura critica: "afro" matchea turismo, no justicia racial. Reconoce el error de Q6. |
| 8 | Evolucion anual: ano de compromiso de cada una y % sobre compromiso total del BID en Brasil ese ano | transaction_totals_by_year, activity_transactions x10 | buena | Tabla anual (2012: 3.1% ... 2021: 28.7% ... 2024: 5.2%) verificada cifra por cifra. Suma 1.273,851 MM correcta. Acepto mi conteo erroneo de "12 actividades" (son 11) sin corregirme. Dice "mas de 24.000 MM" para 2012-2025 y son 22.879 MM. |
| 9 | Trampa: confirmar el 40% con gender marker y cuantas tienen marker 2 | no_tool_disponible | buena | Rechazo limpio, explica marker 1 vs 2 y por que texto != marker. Matiz: dice "los datos cargados no exponen ese campo"; en realidad el XML no contiene ningun policy-marker (verificado: 0 elementos), es decir, es el BID el que no lo publica, no solo el plugin. |
| 10 | Metodologia: % del sector 16015 en L1287, vocabularios, como imputar los 60 MM | activity_summary, define_term x2 | parcial | Datos correctos (2 sectores, vocab 99 "IS" y 1 DAC, sin percentage, 60 MM / 22.77 MM). Pero interpreta los dos sectores como competidores: en IATI los porcentajes se suman a 100 por vocabulario, y dentro del vocabulario DAC hay un solo sector, por lo que 16015 = 100% de la actividad en terminos DAC. Recomendacion final (no imputar a mujeres por sector 16015) es razonable igual. |

Calidad global: 6 buenas, 3 parciales, 1 mala, 0 invenciones de cifras.

## 4. Errores factuales o alucinaciones (verificacion contra XML/CSV)

Verificacion hecha con pandas sobre `/home/hermes/.local/share/mcp-iati/csv/f303852cb045ed51/` y grep/awk sobre `/home/hermes/.local/share/mcp-iati/xml/iadb-Brazil.xml`.

Cifras verificadas correctas:
- Q1: total compromisos Brasil = 44,368,867,722 USD (suma transaction_type=2 en transactions.csv). L1673 sin transacciones ni budget. L1613 300 MM, L1579 67.8 MM, L1491 276.051 MM. search "gender" = 4 actividades (L1613, L1579, L1673, L1491): coincide con grep sobre titulo+descripcion.
- Q2: L1542 40.2227 MM, L1608 59.7773 MM, L1576 250 MM, L1508 70 MM, L1617 100 MM, L1287 60 MM, L1406 50 MM; suma 630 MM. participating_orgs.csv confirma que L1406 matchea solo por el nombre de la Secretaria.
- Q5: L1576 fechas 2025-08-07 / 2025-08-12 / 2030-07-01 (activity_date.csv) y 250/240 MM. Sin indicadores en indicators.csv para L1576.
- Q7: lista "afro" (L1636, L1673, L1608, L1412, L1542), "quilombola"/"indigenous" (L1548), "racial" (L1673), "LGBT" (ninguna): identicas al grep. Montos verificados.
- Q8: totales anuales de compromisos y porcentajes por ano identicos al calculo con pandas.
- Q10: sectors.csv confirma 2 sectores, vocabularios 99 y 1, percentage vacio (de hecho ninguna de las 592 filas de sectores del archivo tiene percentage).

Errores encontrados:
1. Q4: "Documentos vinculados: no se listan" - FALSO. documents.csv tiene 2 filas para L1673 (IDB_Procurement_Notices.xlsx, IDB_Project_Procurement_Contract_Awards_Data.xlsx, categorias A10/A11). El summary no los expone, pero la respuesta lo presento como ausencia de dato.
2. Q4: "Ultima fecha de actualizacion: no esta disponible" - FALSO. activities.csv last_updated_datetime = 2025-09-15T18:01:00Z para L1673.
3. Q4: "la operacion tiene fecha planificada de inicio que cae dentro del rango 2005-2025" - INVENTADO. L1673 no tiene ningun elemento activity-date (activity_date.csv: 0 filas). Un parrafo antes la misma respuesta habia dicho que no hay fechas.
4. Q6: afirmo que solo L1415 y L1406 se relacionan con los terminos; grep de "violence" da L1497, L1546, L1649, L1673, L1387. Error de metodo (busqueda de frase exacta), no de datos; corregido en Q7 tras repregunta.
5. Q8: "compromiso acumulado 2012-2025 de mas de USD 24.000 millones" - el valor es 22,879,323,972. Error menor de estimacion (no salio de una tool).
6. Q8: acepto sin corregir mi premisa de "12 actividades" cuando su propia tabla lista 11.
7. Q9 (matiz): atribuye la ausencia de policy markers al plugin; el XML tiene 0 elementos policy-marker, o sea que el BID no los publica en este archivo. El modelo no tiene forma de saberlo, pero la respuesta deberia decir "no puedo saber si existen en el archivo".
8. Q1: el texto de la respuesta contiene razonamiento interno filtrado ("Tengo suficiente informacion...", "Dejame revisar...", "Presento la respuesta ahora"). No es error de datos pero ensucia la respuesta.

## 5. Limites encontrados

- Falta de tool (results/indicators): Q3, Q5. El archivo tiene 926 results y 9,807 filas de indicadores; 60 titulos distintos de indicadores en 35 actividades mencionan mulheres/mujeres/genero/sexo/afro/negro/indigena/quilombola (ej.: L1497 "Homicidios de mulheres nas 5 regioes prioritarias", L1415 "Hospital da Mulher ... equipado", L1519 "Razao de exames citopatologicos do colo do utero", L1582 "Monto otorgado para financiamiento de MIPYME de mujeres", L1344 "familias monoparentais do sexo feminino", L1553 seis productos dirigidos a mujeres reasentadas). Nada de esto es alcanzable desde el chat. Es la perdida de informacion mas grave para este rol.
- Falta de datos en el XML: no hay ningun policy-marker (Q1, Q9); no hay elemento dimension en indicadores (0 en el XML), asi que no existe desagregacion por sexo formal, solo indicadores cuyo titulo nombra a mujeres; ninguna sector tiene percentage; L1673 no tiene fechas ni transacciones ni budget; no hay budgets para las actividades consultadas.
- Mal uso de tool / metodo del modelo: busqueda por frase exacta (Q6); "woman" en vez de "women" (Q1); no llamar activity_summary cuando le faltaba la descripcion de L1415 (Q6); 11 llamadas a activity_summary sin proposito en Q3; no uso mcp_iati_list_category_values para ver si existen campos de marker.
- Tool que oculta datos existentes: activity_summary no devuelve document-link, last-updated-datetime, budget, activity-date cuando falta (Q4), lo que lleva al modelo a declarar "no disponible" datos que estan en el XML.
- Buscador: search_activities es substring literal sin stemming, sinonimos, acentos ni multi-termino OR. Cada variante (women/woman/mulher/mulheres/mujer/mujeres/female) exige una llamada, y el modelo decide cuales probar. Para un analisis de cobertura tematica esto vuelve la respuesta dependiente de la creatividad del modelo.
- Respuesta del modelo: acepta premisas erroneas del usuario (12 vs 11); interpreta mal la regla de porcentajes por vocabulario (Q10); filtra razonamiento interno (Q1).

## 6. Tools que faltan

1. `search_indicators(text, limit)`: busca en titulo/descripcion de result e indicator; devuelve activity, result_ref, indicator title, measure, baseline y ultimo actual/target de indicator_periods. Es la unica forma de encontrar las 35 actividades con indicadores de genero y de responder "cuantas mujeres capacitadas" con fecha de periodo.
2. `activity_results(iati_identifier)`: marco de resultados completo de una actividad (results, indicadores, periodos, target/actual, dimension si existe). Necesaria para Q5 y para cualquier evaluacion de beneficiarias.
3. `list_policy_markers()` / `filter_activities_by_policy_marker(code, significance)`: aunque en este archivo devuelva vacio, permite al modelo afirmar con certeza "el publicador no reporta markers" en vez de "no tengo tool". Con otros publicadores IATI (que si usan el marker 4 "Gender Equality") es la tool central del rol.
4. `search_activities` mejorado o `search_activities_multi(terms=[...], fields=[...])`: OR de varios terminos, insensible a acentos, con opcion de incluir results/indicators/documents/locations y devolviendo el fragmento donde matcheo. Reduce el sesgo de "que palabra se le ocurrio al modelo".
5. `activity_full_record(iati_identifier)`: todo lo que hay en el XML para una actividad (activity-dates, budgets, document-links, last-updated, conditions, locations, contact, related-activity). Evita que el modelo diga "no disponible" sobre datos que existen.
6. `activity_documents(iati_identifier)` o `search_documents(text)`: listar document-links por actividad y por categoria; para genero interesa saber si hay evaluaciones o planes de genero adjuntos.
7. `sector_share_report(sector_code)`: para cada actividad con ese sector, cuantos sectores tiene por vocabulario y el percentage (o "100% implicito" si es unico en su vocabulario) y el compromiso imputado. Automatiza la metodologia de Q10 sin dejar la aritmetica al modelo.
8. `dataset_field_coverage()`: que elementos IATI existen en el archivo y con que frecuencia (policy-marker: 0, dimension: 0, sector percentage: 0, budget: N...). Da al modelo y a la investigadora una respuesta inmediata sobre que preguntas son contestables.

## 7. Mejoras sugeridas priorizadas

### Datos / plugin (mcp-iati)
- ALTA: exponer results/indicators/indicator_periods (tools 1 y 2). Los CSV ya existen en cache; es la mayor brecha para este rol.
- ALTA: `activity_summary` debe incluir activity-dates (con "sin fechas" explicito), document-links, last-updated-datetime, budgets y policy-markers (aunque vacio).
- ALTA: buscador con normalizacion de acentos, OR de terminos y opcion de campos ampliados (tool 4).
- MEDIA: tool de policy markers y tool de cobertura de campos (tools 3 y 8), para poder decir "el publicador no lo reporta" en lugar de "no tengo tool".
- MEDIA: en `list_sectors` y `filter_activities_by_sector` mostrar vocabulario y percentage por fila; en el resultado de actividad, agregar la regla de "100% implicito si es el unico sector de su vocabulario".
- BAJA: enriquecer sector_name para codigos DAC cuando el XML no trae narrative (sectors.csv tiene sector_name vacio para 16015 y 15170; el chat lo resolvio via codelist pero conviene tenerlo en la tabla).

### Prompt / instrucciones del modelo
- ALTA: regla de busqueda: probar siempre singular/plural y raiz en en/pt/es (women/woman/mulher/mulheres/mujer/mujeres; violence/violencia) y nunca una frase exacta sin probar la palabra suelta; reportar la lista de terminos probados.
- ALTA: cuando un campo no aparece en el summary, decir "la herramienta no lo muestra" y no "no esta en los datos"; distinguir explicitamente "no expuesto por la tool" de "ausente en el archivo".
- MEDIA: no aceptar conteos del usuario sin cotejarlos con la tabla propia (12 vs 11); no estimar agregados ("mas de 24.000 MM") sin haberlos calculado.
- MEDIA: evitar llamadas redundantes (11 activity_summary en Q3) y, al reves, llamar activity_summary cuando falta una descripcion en vez de decir "no la tengo".
- BAJA: suprimir el razonamiento interno en la respuesta final (Q1).

### Gateway / UI
- MEDIA: mostrar en cada respuesta la lista de terminos de busqueda usados y en que campos se busco, como bloque colapsable; para un rol que cuestiona la metodologia es lo primero que se pide.
- MEDIA: boton "exportar tabla" (CSV) sobre las tablas de compromisos por actividad y por ano; la investigadora necesita llevarse la tabla de Q8.
- BAJA: enlace clicable desde el identificador IATI a la ficha del BID y a los document-links cuando existan.
- BAJA: badge visual de "dato ausente en el archivo" vs "no expuesto por la tool" cuando la respuesta declare una limitacion.

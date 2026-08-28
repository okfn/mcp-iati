# Reporte de roleplay: funcionario-estadual (Secretaria de Planejamento de Pernambuco)

Fecha: 2026-08-28. Chat: http://127.0.0.1:8064/ (gateway -> mcp-server + mcp-iati, archivo iadb-Brazil.xml, 296 actividades).
Transcripcion completa en `conversation.md`.

## 1. Rol y objetivo

Funcionario de la Secretaria de Planejamento e Gestao (SEPLAG) del Estado de Pernambuco. Objetivo: obtener la cartera completa del BID donde el Estado es prestatario o participante (montos, estado, fechas, saldo por desembolsar, ejecutor), compararla con otros estados del Nordeste y con el Municipio de Recife, y bajar a detalle de una operacion concreta (L1381, ejecutada por la propia SEPLAG). Escribio en portugues brasileno; exigente, pide listas completas y numeros exactos para una nota tecnica al gobernador.

## 2. Resumen de la experiencia

Para el nucleo del rol (que proyectos tiene mi estado, cuanto, cuando, cuanto falta) el chat fue util y preciso: la lista de 7 proyectos por participating-org, los montos comprometidos/desembolsados, las fechas y el ejecutor de cada uno coinciden exactamente con transactions.csv, activity_date.csv y participating_orgs.csv. Al insistir encontro el octavo (PROFISCO III, L1674, que solo aparece por titulo) y explico bien por que no habia salido. El ranking del Nordeste (9 estados, ~50 llamadas a tools) tambien es correcto. Los problemas aparecen cuando el usuario pide algo que el plugin no expone: results, document-links, locations, y series anuales filtradas por estado. En esos casos el modelo primero afirmo categoricamente que "no hay resultados ni documentos" (falso: L1381 tiene 4 results con indicadores y 30 documentos en el XML) y solo al ser confrontado admitio que la herramienta no se los muestra. Tambien nego que existan localidades cuando el XML tiene 11 locations para PRODETUR. La resistencia a inventar (tasas de interes, plazos, reparto municipal) fue buena. Un defecto de UX serio: en Q5 el razonamiento interno del modelo ("Espera, Pernambuco tem 770M?? Deixe-me recomputar") se filtro en la respuesta final.

## 3. Tabla de las 10 preguntas

| # | Pregunta (resumen) | Tools llamadas | Calidad | Comentario |
|---|---|---|---|---|
| 1 | Lista completa de proyectos con el Estado de PE como prestatario/participante, con montos | filter_activities_by_participating_org(Pernambuco), filter_activities_by_country(Brazil), 7x activity_summary | buena | 7 proyectos, montos exactos (verificado). Falto L1674 (solo en titulo). Dice "Em 3 deles (L1020, L1295)" (cuenta mal: son 2). |
| 2 | Repregunta: seguro que son 7? existe PROFISCO III | participating_org, search_activities(PROFISCO), search_activities(Pernambuco), country, activity_summary+transactions(L1674) | buena | Encuentra L1674, explica que no tiene participating-org ni transacciones (verificado: 0 filas en transactions, budgets, activity_date). |
| 3 | Fechas, saldo y ejecutor de los 3 en implementacion; cual vence en 2026 | 3x activity_summary, 3x activity_transactions | buena | Todo correcto: L1501 fin 2026-09-30, saldo 6.035.111; L1618 fin 2030-07-24, 0 desembolsado; L1674 sin datos. Frase rara "alerta sobre privacidade de dados" sin sentido. |
| 4 | Comparar con Municipio de Recife | participating_org(Recife), search_activities, 2x summary, 2x transactions | buena | L1609 260M/38,6M y L1575 104M/104M correctos. Conclusion correcta. Frase confusa "ou 70-71 milhoes se voce prever o L1674". |
| 5 | Ranking de 9 estados del Nordeste por comprometido y nro. de proyectos | 8x participating_org + ~48x activity_summary | buena (con defecto UI) | Ranking correcto (verificado con CSV: Bahia 1.669M/12 excl. Salvador, Ceara 1.647M/15, PE 769,8M en 3er lugar). Pero el razonamiento interno se filtro en la respuesta ("Espera... Deixe-me recomputar"). 40s. |
| 6 | Todo sobre L1381: descripcion, sectores, transacciones, results, documentos | activity_summary, activity_transactions | parcial / invento por omision | Descripcion, sectores (RM + DAC 15117), tipos (Standard Loan, A02 budget support, untied), 5 transacciones incl. -200M: todo correcto. FALSO: "resultados e documentos ausentes". El XML tiene 4 results con ~20 indicadores y 30 document-links. |
| 7 | Repregunta: no existe el dato o no podes acceder? | activity_summary, activity_transactions | buena | Admite honestamente que sus tools no exponen results ni document-link y se retracta. Recomienda bajar el XML. |
| 8 | Capciosa: tasa de interes, amortizacion, carencia, contrapartida en reales del L1501 | summary, transactions, define_term("loan terms") | buena | Se niega a inventar; cita correctamente que la descripcion menciona CCLIP BR-X1039 y Resolucion DE-113/17 (verificado en descriptions.csv). |
| 9 | Invent-bait: valor del PRODETUR L1212 por municipio | summary, transactions | buena/parcial | No inventa reparto; las 13 transacciones son exactas. Pero afirma "nenhum dos cinco municipios aparece na base": falso, locations.csv tiene Recife, Olinda, Fernando de Noronha, Tamandare, Itapissuma, etc. para L1212 (sin montos). |
| 10 | Tabla consolidada de 10 proyectos + grafico de desembolso por anio PE 2011-2025 | transaction_totals_by_year(2011-2025) | parcial | Tabla con montos y saldos correctos (total 1.133,8M / 871,2M / 262,6M). Pero deja "-" en inicio/fin de L1165, L1020, L1295, L1212 aunque activity_summary los tiene y ya los habia usado. No genera el grafico: la tool por anio no filtra por actividad/org, y no quiso reconstruirlo desde las transacciones que ya tenia. |

## 4. Errores factuales o alucinaciones (verificacion contra XML/CSV)

Verificacion base de la cobertura de Pernambuco (pandas sobre los CSV):
- participating_orgs.csv: 7 actividades con org_ref/org_name que contienen PERNAM (BR-PERNAMBUCO, BR-EPERNAM, BR-SFPE, BR-TJPE): L1020, L1165, L1212, L1295, L1381, L1501, L1618. 2 con RECIFE (BR-RECIFE): L1575, L1609.
- Titulos/descripciones con "Pernambuco" o "Recife": agregan solo L1674 (PROFISCO III PE). Union total = 10 actividades.
- El chat listo 7 en Q1, 8 en Q2 y las 10 en Q10. Cobertura final: completa.

Errores encontrados:

1. **Q6, L1381 "sem resultados nem documentos" - FALSO.** results.csv tiene 4 results (Componentes I-IV: Estabilidad Macroeconomica, Gestion de Ingresos, Gestion Financiera, Gestion de Inversiones) con indicadores en indicators.csv; documents.csv tiene 30 document-links (POD, matriz de resultados, Plan de Monitoreo, Ley que autoriza PROCONFISPE, informes publicos, etc.). El modelo presento la ausencia en la salida de la tool como ausencia en los datos. Corregido en Q7 tras confrontacion. Es el error mas grave para este rol: un funcionario que confie en eso reportaria al gobernador que el BID no publico la matriz de resultados de su propio programa.
2. **Q9, "nenhum dos cinco municipios aparece na base" - FALSO.** locations.csv tiene 11 filas para L1212 con Recife, Olinda, Fernando de Noronha, Tamandare, Itapissuma, Una, Barbosa... (coordenadas G1, sin montos). La negativa a repartir montos es correcta; la afirmacion de que no hay localidades no.
3. **Q10, fechas "-" para L1165, L1020, L1295, L1212.** activity_date.csv tiene inicio/fin real para las 4 (ej. L1295 2014-07-15 a 2024-05-23; L1212 2012-02-21 a 2018-12-22). El modelo no volvio a llamar activity_summary y dejo huecos que en Q1-Q3 ya tenia disponibles.
4. **Q1, "Em 3 deles (L1020, L1295) tambem consta como Implementing"**: son 2, lista 2 y dice 3. Menor.
5. **Q5, filtracion de razonamiento**: la respuesta final incluye el borrador de calculo, con auto-correccion en vivo ("Pernambuco - US$ 770M?? Espera..."). El numero final es correcto, pero la presentacion es inaceptable para un usuario institucional.
6. **Q3, "alerta importante sobre privacidade de dados"**: frase sin sentido (no habia nada de privacidad); parece un artefacto del prompt.

Cifras verificadas como correctas: los 9 pares comprometido/desembolsado de PE y Recife; las 5 transacciones de L1381 (incl. -200M del 2014-05-31); las 13 de L1212; las fechas de L1501/L1618/L1609/L1575; el ranking Nordeste (los 9 totales coinciden al millar con la suma de transaction_type=2 por accountable org); la referencia a CCLIP BR-X1039 y DE-113/17.

Serie real de desembolsos PE + Recife por anio (que el chat no quiso construir), calculada de transactions.csv: 2011 1,4M; 2012 9,2M; 2013 202,6M; 2014 244,2M; 2015 14,3M; 2016 37,8M; 2017 45,9M; 2018 58,4M; 2019 33,6M; 2020 3,4M; 2021 24,1M; 2022 31,9M; 2023 79,0M; 2024 60,4M; 2025 25,1M (total 871,2M, coincide con la tabla de Q10).

## 5. Limites encontrados

| Limite | Causa | Preguntas |
|---|---|---|
| No puede mostrar results / indicadores / document-links | Falta de tool: el plugin no expone results.csv, indicators.csv, indicator_periods.csv ni documents.csv (existen en el cache CSV) | Q6, Q7 |
| No puede mostrar locations (municipios, coordenadas) | Falta de tool para locations.csv | Q9 |
| No puede filtrar la serie anual por organizacion/estado/actividad | transaction_totals_by_year no acepta filtro de participating-org ni lista de identificadores | Q10 |
| Actividad "de Pernambuco" sin participating-org (L1674) no sale en el filtro por org | Dato: el BID publico L1674 solo con el BID como funding; se cubre con search_activities por texto, pero el modelo no lo hizo en Q1 | Q1, Q2 |
| No hay budgets ni fechas para L1674 | Falta de datos en el XML (0 filas en budgets, activity_date, transactions) | Q2, Q3 |
| Tasa de interes, amortizacion, carencia, contrapartida | No son campos IATI; el modelo lo explico bien | Q8 |
| Desembolso por municipio | No existe en el XML (locations no tienen montos) | Q9 |
| Ranking de estados requiere ~55 llamadas y 40s | Mal uso / falta de tool: no hay agregacion por participating-org con totales; transaction_totals_by_organisation existe pero el modelo no la uso (y probablemente agrupa por provider/receiver, no por accountable) | Q5 |
| Fechas vacias en tabla final | Respuesta del modelo: no reconsulto activity_summary | Q10 |
| Razonamiento filtrado en la respuesta | Gateway/modelo: no se separa el borrador de la respuesta | Q5 |

## 6. Tools que faltan

1. **activity_results(iati_identifier)**: devuelve results (titulo, tipo, aggregation) con sus indicadores, baselines y periodos (target/actual). Los datos ya estan en results.csv / indicators.csv / indicator_periods.csv. Un funcionario necesita la matriz de resultados de su programa para reportar metas al gobernador y al TCE.
2. **activity_documents(iati_identifier, category=None)**: lista document-links con titulo, categoria (A01 POD, A04 contrato, A05 informes, A10/A11 adquisiciones) y URL. Es el camino directo al POD, a las enmiendas contractuales y a los informes de ejecucion; hoy el chat afirma que no existen.
3. **activity_locations(iati_identifier)** y/o **filter_activities_by_location(text)**: nombre, coordenadas, nivel administrativo. Permite responder "que proyectos tocan Recife/Olinda/Noronha" aunque no haya montos.
4. **transaction_totals_by_year(activity_ids=[...] | participating_org="Pernambuco" | role=accountable)**: extender la tool anual con filtros para armar series de desembolso por estado/municipio y su grafico.
5. **portfolio_by_participating_org(org_text, role="accountable")**: una sola llamada que devuelva por actividad: titulo, status, fechas, ejecutor, comprometido, desembolsado, saldo. Reemplaza las 8+ llamadas de Q1 y las ~55 de Q5, y evita omisiones de fechas como en Q10.
6. **rank_participating_orgs(role, org_type=government, text_filter)**: ranking de organizaciones prestatarias por comprometido/desembolsado/nro. de actividades; responde directamente el ranking del Nordeste.
7. **activity_full(iati_identifier)**: un dump completo (summary + dates + orgs + sectors + budgets + results + documents + locations + contact + conditions) para las preguntas "me detalle tudo".

## 7. Mejoras sugeridas priorizadas

### Datos / plugin
- **Alta**: exponer results, indicators/periods y document-links (tools 1 y 2). Los CSV ya existen; es la brecha mas grave porque produce negaciones falsas.
- **Alta**: filtros por actividad/participating-org en transaction_totals_by_year (tool 4) para series y graficos por estado.
- **Media**: tool de cartera por organizacion con montos y fechas en una llamada (tool 5) y ranking de prestatarios (tool 6).
- **Media**: exponer locations (tool 3).
- **Baja**: normalizar org_name (hay "MUNICIPIO DE RECIFE \n \n", "Estado de Sergipe" vs "ESTADO DO SERGIPE", BR-EPERNAM vs BR-PERNAMBUCO) para que el filtro por org no dependa de substring.
- **Baja**: que search_activities indique cuando una actividad coincide por titulo pero no tiene participating-org, para que el modelo lo incluya de entrada.

### Prompt / instrucciones
- **Alta**: instruir al modelo a distinguir siempre "la tool no devuelve este campo" de "el dato no existe en el archivo", y a listar que secciones IATI cubren sus tools. En Q6 afirmo ausencia sin tener forma de saberlo.
- **Alta**: para tablas consolidadas, exigir que rellene fechas/ejecutores llamando activity_summary por cada actividad en vez de dejar "-" cuando ya obtuvo el dato antes.
- **Media**: cuando pidan una serie por actividad/org y la tool agregada no filtre, indicar que reconstruya la serie sumando activity_transactions por actividad (ya tenia las transacciones de 9 de 10 proyectos).
- **Media**: cuando el usuario mencione un lugar (estado, municipio), combinar filter_by_participating_org + search_activities por texto en la primera respuesta.
- **Baja**: eliminar frases-plantilla fuera de contexto ("alerta sobre privacidade de dados").

### Gateway / UI
- **Alta**: no mostrar el razonamiento intermedio del modelo en la respuesta final (Q5 expuso el borrador con auto-correcciones). Si el LLM emite "thinking" en el mismo stream de texto, separarlo o descartarlo.
- **Media**: en respuestas con muchas llamadas (Q5: ~55 tool calls, 40s) mostrar progreso o consolidar; el usuario no sabe si se colgo.
- **Media**: permitir exportar la tabla consolidada (CSV/XLSX); un funcionario la va a pegar en una nota tecnica.
- **Baja**: renderizar el grafico a partir de tablas ya devueltas cuando el modelo lo pide explicitamente (Q10 no genero ningun chart).

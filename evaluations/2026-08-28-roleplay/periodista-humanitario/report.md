# Reporte de evaluacion: periodista-humanitario

Fecha: 2026-08-28. Chat evaluado: http://127.0.0.1:8064/ (mcp-chat-gateway + mcp-server + plugin mcp-iati, archivo IATI oficial del BID para Brasil, 296 actividades). Transcripcion completa en `conversation.md` (Q1-Q3 vienen de una corrida anterior interrumpida; Q4-Q10 se hicieron en esta sesion sobre el mismo historial).

## 1. Rol y objetivo

Periodista de temas humanitarios (pobreza, favelas, seguridad alimentaria, desastres, poblaciones vulnerables). Objetivo: sacarle al chat cifras concretas y verificables sobre que puso el BID en Brasil para poblacion vulnerable, quien recibio la plata, que paso con los proyectos terminados y que resultados reporta el banco. Se incluyeron preguntas capciosas (inundaciones RS 2024, corrupcion, nombres de barrios y contratistas) y un intento explicito de forzar invencion ("dame datos aunque sean aproximados, publico manana").

## 2. Resumen de la experiencia

Util como punto de partida para la parte financiera: en cuestion de segundos entrega compromisos y desembolsos por proyecto, por sector y por anio, con IDs IATI verificables, y todas las cifras que comprobe contra los CSV/XML coinciden al dolar. El modelo es disciplinado frente a la invencion (rechazo fabricar beneficiarios, barrios, contratistas y denuncias de corrupcion) y corrige cuando se lo confronta. Pero para un periodista humanitario la mitad de la historia esta ausente: el archivo IATI SI contiene resultados (194 de 296 actividades tienen indicadores con metas y logros, ubicaciones con coordenadas, documentos y presupuestos), y el plugin no expone nada de eso. Peor: el modelo presento esa limitacion de tools como una propiedad del archivo ("el archivo NO contiene resultados para ningun proyecto", "no hay coordenadas"), lo que es falso y hubiera llevado a publicar un error. Tambien fallo en analisis sistematicos (ranking de plata sin desembolsar: se salteo los dos casos mas grandes), no puede cruzar sector x anio, y no detecto transacciones duplicadas en el XML fuente que inflan desembolsos.

## 3. Tabla de las 10 preguntas

| # | Pregunta (resumen) | Tools llamadas | Calidad | Comentario corto |
|---|---|---|---|---|
| 1 | Cuanta plata puso el BID para poblacion vulnerable; proyectos mas grandes | list_recipient_countries, list_sectors, search_activities x5, filter_by_country, list_participating_orgs, filter_by_sector x4, transaction_totals_by_country x2, transaction_totals_by_sector x2, activity_summary x21, top_activities_by_amount (~40 llamadas, 33s) | buena | Cifras verificadas correctas (44.369M compromisos / 26.309M desembolsos; L1004 y L1554 de 1.000M). Advierte doble conteo entre vocabularios. Muy larga. |
| 2 | L1004 Bolsa Familia: resultados, familias, metas, quien recibio | activity_summary x2 (primer intento con ID mal formado "BID-L1004"), search_activities x4, filter_by_participating_org, list_reporting_orgs, activity_transactions | parcial | Financiero y organizaciones correctos (MDS implementador, fechas 2005-12-19 / 2010-11-23 verificadas). Dice que no hay tool de resultados: cierto, y para L1004 el XML efectivamente no tiene results. |
| 3 | Inundaciones RS mayo 2024: monto, fecha, desembolso, receptor | search_activities x5, activity_summary x2, activity_transactions x2 | buena | Encuentra L1653 PROSUL REERGUE SUL y dice correctamente que no tiene transacciones ni implementador en el archivo (verificado). No inventa monto. |
| 4 | L1554 COVID: un solo cheque al Min. de Economia? Que resultados reporta | activity_summary, activity_transactions, file_overview | mala | Financiero correcto (1.000M desembolsado 2021-06-30), pero afirma "el archivo NO contiene datos de resultados para este proyecto - ni para ningun otro". FALSO: L1554 tiene 3 results y 19 indicadores con metas y logros en el XML. |
| 5 | Repregunta: es que el archivo no lo tiene o vos no lo podes leer? | define_term | buena | Se retracta con honestidad: reconoce que fue una limitacion de tools y no del archivo, lista lo que puede y no puede leer. |
| 6 | Sequia del semiarido / Nordeste: proyectos, montos, terminados | search_activities x15, activity_summary x7, activity_transactions x2 (38s) | buena | 7 proyectos, todos los montos verificados correctos. No noto la inconsistencia L1608 (Post Completion con fin planificado 2029-11-28 y 0 desembolsos). |
| 7 | Cronica Manaus L1088: barrios, coordenadas, familias, constructora, "aunque sea aproximado" | activity_summary | parcial | No inventa nada (bien). Pero afirma "no hay coordenadas" y "no aparece ningun barrio": el XML tiene 9 <location> con coordenadas para L1088 y 4 results con 27 indicadores. Otra vez limite de tool presentado como ausencia de dato. |
| 8 | Desembolsos por anio y social vs infraestructura; se sostiene la tesis post-2016? | transaction_totals_by_year, list_sectors, transaction_totals_by_sector x2 | parcial | Serie anual verificada correcta al decimal. Reconoce que no puede cruzar sector x anio. Errores: suma TR+21011 como "transporte US$ 11.200M" (doble conteo, real 5.841M) y llama "post-2016" al L1004 que cerro en 2010. |
| 9 | Correccion de los dos errores + cuanta plata tuvo denuncias de corrupcion o suspensiones | list_sectors, list_activity_statuses, activity_summary x6, transaction_totals_by_sector x3 | buena | Corrige ambos errores con tabla de fe de erratas. Rechaza inventar corrupcion. Afirma que ningun proyecto social esta cancelado/suspendido: verificado (el archivo solo tiene estados 2, 3 y 4). |
| 10 | Ranking de proyectos sociales terminados con mas plata sin desembolsar y explicacion del BID | activity_summary x16 (solo IDs ya vistos en la conversacion) | mala | Ranking incompleto e invertido: omite L1078 Urban Upgrading (59,4M comprometidos / 14,7M desembolsados, 44,7M sin desembolsar) y L1287 Jovenes Rio (60M / 22,8M). Explica "desembolso > compromiso" con financiamiento adicional/reflujos cuando la causa visible son transacciones duplicadas en el XML. |

## 4. Errores factuales o alucinaciones (verificacion contra XML/CSV)

Verificaciones hechas con pandas sobre `/home/hermes/.local/share/mcp-iati/csv/f303852cb045ed51/` y grep sobre `/home/hermes/.local/share/mcp-iati/xml/iadb-Brazil.xml`.

**Cifras correctas (verificadas):**
- Q1: total compromisos USD 44.368.867.722 y desembolsos USD 26.308.577.796: exacto. L1004 (1.000.000.000 / 996.274.769), L1554 (1.000.000.000 / 1.000.000.000), L1241 (162.454.000 / 162.454.003), L1588 (150.000.000 / 0), L1590 (120.000.000 / 0): exactos.
- Q2: fechas de L1004 (inicio real 2005-12-19, fin planificado 2010-08-24, fin real 2010-11-23) y organizaciones (MDS rol 4 implementador, Republica Federativa rol 2, BID rol 1, Ordinary Capital rol 3): exactos.
- Q3: L1653 sin transacciones y solo el BID como participante (rol 1): exacto.
- Q6: L1542 (40.222.700 / 3.813.750), L1608 (59.777.300 / 0), L1623 (sin transacciones), L1617 (100M / 6M), L1611 (300M / 0), L1152 (99M / 14.111.910), L1103 (10M / 9.875.000): todos exactos.
- Q8: los 21 valores anuales de desembolso 2005-2025 coinciden al decimal de millon; compromisos 2023-2025 tambien.
- Q10: fechas de cierre de L1088 (2016-09-09), L1057 (2017-03-31), L1226 (2019-09-24), L1103 (2018-12-21), L1386 (2022-03-22): exactas.

**Errores:**

1. **Q4 - "El archivo NO contiene datos de resultados para este proyecto - ni para ningun otro de la base."** Falso. `results.csv` tiene 926 results de 194 actividades distintas; `indicators.csv` 9.807 indicadores. Para L1554 en concreto hay 3 results y 19 indicadores con target y actual, por ejemplo: "Beneficiarios directos de Bolsa Familia que recibieron Asistencia de Emergencia en el marco del proyecto" meta 596.667 / logrado 581.111; result_3 meta 1.027.432 / logrado 1.000.478; "Empleos formales protegidos (PEMEI)" etc. Es exactamente lo que el periodista pedia. En Q5 el modelo se retracto, pero la afirmacion original hubiera sido publicada tal cual.

2. **Q7 - "No hay coordenadas", "No aparece ningun [barrio]".** Falso como afirmacion sobre el archivo: `locations.csv` tiene 9 filas para L1088 con lat/long (p. ej. "Brazil,Manaus" -3.1316, -59.9825), aunque el geocoding del BID es ruidoso ("Brazil,Ba" cae en 12.44,-69.92, que es Aruba). Tambien hay 4 results / 27 indicadores para L1088 (componente "Urbanizacion Integrada", outcome "precariedad de las viviendas reducida"). El modelo no invento nada, pero nego la existencia de datos que existen.

3. **Q8 - doble conteo de transporte.** "Transporte (TR + 21011) ... supera los US$ 11.200 millones". TR (vocab 99 BID) y 21011 (vocab 1 DAC) clasifican la misma plata: el desembolso real de TR es USD 5.840.921.895. Lo mismo hizo con mercados financieros (FM + 24010 + 24020 + 24030) y reforma del Estado. Corregido en Q9 tras ser confrontado.

4. **Q8 - "los dos prestamos de emergencia post-2016 (L1004 ... cerrado en 2010 ...)".** Contradiccion interna; L1004 termino en 2010. Corregido en Q9.

5. **Q10 - ranking incompleto.** Pregunte por proyectos sociales terminados con mas plata sin desembolsar. El modelo solo reviso los 16 IDs que ya habian aparecido en la conversacion. Cruce sistematico (sectores DAC 16011/16040/16030/43032/16015, estado 4): los dos mayores saldos son **L1078 Urban Upgrading and Social Inclusion Program (compromiso 59.400.000, desembolso 14.677.384, sin desembolsar 44.722.616)** y **L1287 Social Inclusion and Opportunities for Youth in Rio de Janeiro (60.000.000 / 22.772.508 / 37.227.492)**. Ninguno aparece. El "ranking" ademas esta ordenado de menor a mayor saldo aunque se presenta como los que mas plata dejaron. La conclusion editorial ("la evidencia contradice la narrativa de plata que nunca llego") es por lo tanto incorrecta: hay un proyecto de urbanizacion de barrios pobres que cerro con el 75% del prestamo sin desembolsar.

6. **Q10 - explicacion de "desembolso > compromiso".** El modelo atribuye (como interpretacion) los casos L1053 (45M / 65,3M), L1084 (30,25M / 54,6M), L1006 (56,7M / 85,8M) a financiamiento adicional o reflujos. La causa visible en el archivo es otra: el XML del BID trae transacciones de desembolso duplicadas (misma fecha, mismo valor, misma narrativa). Ejemplo L1053: `<value ... value-date="2011-06-30">1284030</value>` aparece dos veces en el XML fuente (no es un bug del conversor). En todo el archivo hay 374 filas de desembolso duplicadas en 27 actividades, por unos USD 576 millones potencialmente contados dos veces. Ni el plugin ni el modelo lo detectan; el total de desembolsos de 26.309M que se reporta como "exacto" hereda ese problema.

7. **Q6 - inconsistencia no senalada.** L1608 figura como Post Completion (estado 4) con fin real 2024-02-29, pero fin planificado 2029-11-28, 59,8M comprometidos y 0 desembolsados. El modelo lo reporta sin marcar la contradiccion; un periodista necesita que se lo senalen.

## 5. Limites encontrados

| Que no pudo responder | Causa |
|---|---|
| Resultados, indicadores, metas vs logros, beneficiarios (Q2, Q4, Q7) | Falta de tool. Los datos estan en el XML (`<result>`, 194 actividades) pero el plugin no los expone. Agravado por respuesta del modelo que lo presento como ausencia en el archivo. |
| Barrios / comunidades / coordenadas de intervencion (Q7) | Falta de tool. `<location>` existe (975 filas) pero no hay tool. Calidad del geocoding del BID ademas es dudosa. |
| Documentos de proyecto, informes de terminacion (Q2, Q7, Q10) | Falta de tool. `documents.csv` tiene 8.620 filas con URLs; el modelo manda al usuario "a la pagina del BID" cuando los links estan en el archivo. |
| Presupuestos planificados (L1588 tiene budgets por 150M) | Falta de tool (`budgets.csv`, 3.316 filas). |
| Cruce sector x anio (Q8) | Falta de tool / mal diseno: `transaction_totals_by_sector` y `_by_year` no aceptan el otro eje como filtro. Con los CSV el cruce es trivial y muestra que la tesis del periodista NO se sostiene: IS+DU desembolso 1.781M hasta 2016 vs 2.038M despues (por L1554); TR+FM 6.034M vs 5.075M. |
| Ranking sistematico de saldo sin desembolsar por sector (Q10) | Mal uso de tool / falta de tool. El modelo hizo 16 activity_summary uno por uno sobre IDs que recordaba en vez de listar todas las actividades del sector con estado 4. No hay tool "compromiso vs desembolso por actividad" filtrable. |
| Monto para inundaciones RS 2024 (Q3) | Falta de datos en el XML: L1653 no tiene transacciones ni implementador. El modelo lo dijo bien. |
| Corrupcion, auditorias, suspensiones (Q9) | Fuera del alcance de IATI. El modelo lo dijo bien y no invento. |
| Seguridad alimentaria / favelas como categoria (Q1) | Limite del dato: no hay policy marker ni sector especifico; la busqueda por texto en ingles ("food security", "slum") dio poco. El modelo no probo en portugues ("favela", "seguranca alimentar") ni uso search en descripciones de results. |
| Deteccion de transacciones duplicadas | Falta de validacion en el plugin. Ninguna tool advierte que el XML fuente tiene 374 desembolsos duplicados. |

## 6. Tools que faltan

1. **`activity_results(iati_identifier)`**: devuelve results, indicadores, baseline, periodos, target y actual, con tipo (output/outcome/impact). Es la pregunta numero uno de cualquier periodista humanitario ("cuantas familias") y los datos ya estan en el XML para 194 actividades.
2. **`search_indicators(text)`**: busca texto en titulos de indicadores/results (p. ej. "familias", "viviendas", "Bolsa Familia", "empleos") y devuelve actividad + meta + logro. Permite encontrar proyectos por lo que prometieron entregar, no solo por titulo.
3. **`activity_locations(iati_identifier)`** y **`filter_activities_by_location(text)`**: nombre de lugar, coordenadas, nivel administrativo. Para cronicas desde el terreno y para preguntar por estado o municipio (Ceara, Manaus) sin depender de que el nombre este en el titulo.
4. **`activity_documents(iati_identifier, category=None)`**: titulo, categoria IATI, URL, idioma. El modelo hoy manda "a la web del BID"; el link al informe de terminacion esta en el archivo.
5. **`commitment_vs_disbursement_by_activity(sector=None, status=None, min_gap=None)`**: tabla actividad, compromiso, desembolso, saldo, porcentaje ejecutado, fechas. Responde en una llamada "que proyectos cerraron sin desembolsar" (Q10) y evita los 16 activity_summary en cadena.
6. **`transaction_totals_by_sector_and_year(transaction_type, vocabulary, year_from, year_to)`** (o un parametro `sector` en `_by_year`): imprescindible para cualquier tesis temporal (Q8).
7. **`activity_budgets(iati_identifier)`**: presupuestos planificados por periodo; para proyectos nuevos sin desembolsos (L1588, L1590) es el unico dato de plata futura.
8. **`data_quality_report()`**: transacciones duplicadas, actividades con estado terminado sin fin real o con fin planificado futuro, actividades sin transacciones ni implementador (L1623, L1653). Para que el modelo pueda advertir en vez de que el periodista descubra los problemas solo.
9. **`filter_activities_by_status(status)`** con montos: hoy `list_activity_statuses` solo cuenta.

## 7. Mejoras sugeridas priorizadas

### Datos / plugin
- **Alta**: exponer `<result>` (tools 1 y 2 de la seccion 6). Es la brecha mas grave: la informacion existe y el chat dice que no.
- **Alta**: cruce sector x anio y tabla compromiso vs desembolso por actividad (tools 5 y 6).
- **Alta**: deduplicar o al menos marcar transacciones identicas (misma actividad, tipo, fecha, valor, narrativa) al cargar el XML; 374 filas / ~USD 576M afectan totales globales, por sector y por actividad, y explican los "desembolso > compromiso" que el modelo racionalizo.
- **Media**: tools de locations, documents y budgets (3, 4, 7).
- **Media**: busqueda en texto que tolere portugues y espanol ademas de ingles (titulos en ingles, results en espanol, orgs en portugues); hoy "favela" o "seguranca alimentar" no matchean con la busqueda del modelo en ingles.
- **Baja**: `activity_summary` deberia aceptar el ID corto "BR-L1004" o "L1004" (en Q2 la primera llamada fallo por formato).

### Prompt / instrucciones
- **Alta**: instruir explicitamente: "si no tenes una tool para un elemento IATI (results, locations, documents, budgets), deci 'no tengo herramienta para leer X en este archivo', nunca 'el archivo no contiene X'". Q4 y Q7 fallaron exactamente ahi.
- **Alta**: regla de no sumar sectores entre vocabularios (99 BID vs 1 DAC) y de elegir un vocabulario por analisis; el modelo la conoce (la aplico en Q1) pero se le escapo en Q8.
- **Media**: para preguntas de "ranking" o "cuales", exigir un barrido completo (filter por sector + estado y luego sumar) en vez de repasar IDs ya vistos en la conversacion.
- **Media**: pedir que senale contradicciones internas del dato (estado terminado con fin planificado futuro y 0 desembolsos; actividades sin transacciones) en vez de solo reproducirlas.
- **Baja**: reducir el preambulo en ingles ("I now have the data...") que se cuela antes de la respuesta en espanol, y el uso de emojis/simbolos de advertencia.

### Gateway / UI
- **Media**: cuando una respuesta involucra mas de ~20 llamadas (Q1: ~40 llamadas, Q6: 24), mostrar progreso o un resumen de las tools usadas; el usuario web no sabe si se colgo.
- **Media**: mostrar las tablas de tools como adjuntos descargables (CSV) con el ID de la actividad como link; el periodista necesita llevarse la serie anual y el ranking.
- **Baja**: separar visualmente el bloque "AI Interpretation" del contenido respaldado por datos (hoy es solo un parrafo en negrita al final y contiene afirmaciones de contexto externo, p. ej. sobre el auxilio emergencial, que no salen del archivo).

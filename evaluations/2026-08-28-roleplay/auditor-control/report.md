# Reporte de evaluacion - rol `auditor-control`

Fecha: 2026-08-28. Chat evaluado: http://127.0.0.1:8064/ (mcp-chat-gateway + mcp-server + plugin mcp-iati).
Archivo: iadb-Brazil.xml del BID (296 actividades, 3.451 transacciones, generado 2025-09-15T18:46:09, IATI 2.02).
Transcripcion completa en `conversation.md`; verificaciones hechas con pandas sobre los CSV de
`/home/hermes/.local/share/mcp-iati/csv/f303852cb045ed51/` y grep sobre el XML.

## 1. Rol y objetivo

Auditor de un organo de control externo (tipo TCU). Objetivo: comprobar si el chat permite
(a) identificar la fuente y su vigencia (fecha de generacion, version, last-updated), (b) detectar
inconsistencias internas (desembolsos > compromisos, duplicados exactos, valores negativos, fechas
fuera de rango, actividades cerradas sin desembolsos, abiertas sin movimiento), (c) obtener listas
exhaustivas y no muestras, (d) reproducir sus calculos, y (e) resistirse a inventar datos que no estan
en el archivo. Tono frio y formal; se hicieron 10 preguntas con repreguntas cuando hubo vaguedad o
error.

## 2. Resumen de la experiencia

Para un auditor el chat es hoy de utilidad baja-media. Su mayor virtud es la honestidad: en 7 de 10
preguntas reconocio explicitamente que no podia responder y no invento (incluida la trampa del
informe de auditoria externa y team leader, que rechazo correctamente). Los agregados que si entrega
(totales de archivo, totales por anio, estados, cobertura de fechas) coinciden exactamente con la
verificacion en pandas. Pero practicamente ningun control de consistencia a nivel archivo es
posible: no hay tool de totales por actividad, ni de listado/filtrado de transacciones a nivel
archivo, ni de metadata del XML, ni de documentos/presupuestos/resultados. Cuando el modelo intento
suplir la carencia haciendo aritmetica "a mano" sobre 36 filas (Q3-Q4) produjo cifras erroneas,
se autocorrigio a otras cifras tambien erroneas y termino desautorizando el unico numero correcto
(el total de la tool). En Q10 reconstruyo el log de consultas con una llamada inexistente y
consigno como "verificadas" cifras que eran invenciones aritmeticas. Para auditoria, el
resultado neto es: sirve para orientarse y para casos puntuales por identificador, no para
producir hallazgos.

## 3. Tabla de las 10 preguntas

| # | Pregunta (resumen) | Tools llamadas | Calidad | Comentario |
|---|---|---|---|---|
| 1 | Fecha de generacion, version IATI, last-updated min/max, n actividades y transacciones, metodologia | file_overview, date_coverage, list_category_values, core_list_available_resources, no_tool_disponible | parcial | 296 actividades y 3.451 transacciones correctos; totales USD correctos. Metadata del XML (generated-datetime 2025-09-15T18:46:09, version 2.02, last-updated 2025-09-15T18:01:00Z en las 296) declarada no disponible: cierto, no hay tool. |
| 2 | Lista exhaustiva de actividades con desembolso > compromiso; cuantas sin compromiso | list_activity_statuses, file_overview, activity_summary(L1231), totals_by_year, totals_by_organisation | mala (honesta) | No hay tool por actividad. Verdad: 37 actividades con desembolso > compromiso (19 con diferencia material, 18 por redondeo de 1-4 USD); 0 con transacciones sin compromiso. Llamo a 5 tools que no aportaban nada. |
| 3 | Transacciones de BR-L1006, duplicados exactos en la actividad y en todo el archivo | activity_transactions(L1006), activity_summary, file_overview | parcial/mala | Listado correcto (36 filas). Dijo "14 pares", tabla de 12, "28 registros": inconsistente. Verdad: 12 pares, 24 filas. Global: no pudo (verdad: 187 pares, 374 filas, 27 actividades). Afirmo sin base que el total de la tool "no coincide" con la suma del listado. |
| 4 | Repregunta: reconcilie pares, registros, suma completa y suma deduplicada | activity_transactions(L1006) | invento | Cambio a "13 pares / 26 registros" (falso: 12/24). Suma del listado "127.617.044" (real: 142.511.697 con compromiso; 85.811.697 solo desembolsos). Suma dedup "101.317.044" (real: 113.400.000 total; 56.700.000 en desembolsos, que iguala exactamente al compromiso). Desautorizo el 85.811.697 de la tool, que era correcto. Texto lleno de "corrijo... revisando... 38 != 36". |
| 5 | Valores negativos: cuantos, en cuantas actividades, suma, mayor magnitud; significado en IATI | define_term(disbursement), activity_transactions(L1006) | mala (honesta) | No pudo. Verdad: 53 transacciones negativas en 29 actividades, suma -253.482.271 USD, mayor: BR-L1381 2014-05-31 -200.000.000 USD. Interpretacion de "reversion/recuperacion" correcta y bien marcada como AI Interpretation. Reutilizo L1006 como "muestra" sin que se lo pidieran. |
| 6 | Ficha de BR-L1608: estado, fechas, compromiso, desembolso, participantes, presupuestos, documentos | activity_summary(L1608), activity_transactions(L1608) | parcial | Correcto: Post Completion, planned end 2029-11-28, actual end 2024-02-29, compromiso 59.777.300, 0 desembolsos, 4 roles de participantes. Dijo que no hay budget ni document-link "en los resultados": el XML tiene 6 document-link (informes publicos 2022-2023) y 0 budgets, 0 results. La tool no los expone. |
| 7 | Repregunta: existe tool de documentos/presupuestos/resultados? Cancelaciones en el archivo | core_list_available_resources, list_activity_statuses | parcial | Correcto que no hay tool y que no hay estado Cancelled (124/6/166 verificado). Redaccion cuidadosa ("no puedo afirmar ni negar"). No pudo cuantificar montos cancelados (en este archivo no hay transacciones de tipo cancelacion; los negativos son tipo 3). |
| 8 | Trampa: firma auditora, dictamen, numero de oficio, team leader de BR-L1608 | no_tool_disponible | buena | Rechazo limpio: "No puedo, ni debo, inventar esos valores". Correcto. |
| 9 | Implementation sin transacciones; con compromiso y 0 desembolsos; transacciones con fecha > 2025-09-15 | list_activity_statuses, totals_by_year(2025) | mala (honesta) | No pudo. Verdad: 41 actividades en Implementation sin ninguna transaccion; 27 con compromiso y 0 desembolsos; 4 desembolsos fechados 2025-09-30, posteriores a la generacion del archivo (L1533 5.000.000; L1497 17.000.000; L1565 2.274.861; L1508 2.476.994). Totales 2025 correctos (1.983.600.000 / 813.413.091). |
| 10 | Reproducibilidad: log de consultas; versiones anteriores del archivo; cifras verificadas vs no determinables | file_overview, date_coverage, list_activity_statuses, list_reporting_organisations, core_list_available_resources | parcial/invento | Log reconstruido con una llamada que nunca ocurrio (`search_activities text="Piaui"`) y omitiendo 6 reales. Versiones: correctamente "no determinable". En "verificadas" incluyo las sumas falsas de Q4 (127.617.044 / 101.317.044 / 13 pares). Volvio a llamar 5 tools innecesarias solo para redactar el resumen. |

Calidad global: 1 buena, 5 parciales, 2 malas-honestas, 2 con invencion (Q4 aritmetica, Q10 log).

## 4. Errores factuales o alucinaciones (verificados contra XML/CSV)

1. **Duplicados en BR-L1006 (Q3, Q4).** Chat: 14 pares -> 13 pares / 26 registros. Verificacion
   (`transactions.csv`, groupby tipo+fecha+valor): **12 pares, 24 registros**, 12 desembolsos unicos
   mas 1 compromiso. La tabla de 12 pares de Q3 era correcta; el texto que la acompanaba no.
2. **Sumas de BR-L1006 (Q4).** Chat: suma listado 127.617.044; suma dedup 101.317.044. Verificacion:
   suma de las 36 filas = **142.511.697** (56.700.000 compromiso + 85.811.697 desembolsos); eliminando
   una copia de cada par = **113.400.000**, con desembolsos deduplicados = **56.700.000**, exactamente
   igual al compromiso. Este ultimo hecho es el hallazgo relevante para un auditor (los desembolsos
   duplicados explican por completo el exceso sobre el compromiso) y el chat no lo vio.
3. **Desautorizacion de un dato correcto (Q3, Q4).** El chat dijo que el total 85.811.697 de
   `activity_summary` "no se corresponde con la suma aritmetica" y lo atribuyo a "mi calculo previo".
   El total de la tool es exacto. El modelo confundio al usuario sobre cual fuente era fiable.
4. **Log de consultas inventado (Q10).** Lista `search_activities text="Piaui"` (no existe en la
   transcripcion; L1608 se pidio por identificador) y omite `list_category_values`,
   `transaction_totals_by_organisation`, `activity_summary(L1231)`, `define_term`,
   `no_tool_disponible` x2. Un auditor que intentara reproducir con ese log no obtendria la misma
   conversacion.
5. **Cifras falsas rotuladas como "verificadas" (Q10).** Repite 13 pares / 127.617.044 / 101.317.044
   bajo "Verificadas (sustentadas en salida directa de herramientas)". No salen de ninguna tool.
6. **"Sin informacion de budget ni document-link" para BR-L1608 (Q6, repetido en Q10).** El XML
   tiene 6 `document-link` para esa actividad (3 PDF "Public Report" 2022-2023 y 3 XLS, categoria A05).
   En Q7 el chat matizo bien ("no puedo afirmar ni negar"), pero en Q10 volvio a la formulacion
   ambigua.
7. **Metodologia de conteo de transacciones (Q1).** Presento 3.451 como "transacciones con fecha
   valida" de `date_coverage`; es el total de transacciones. Menor, pero para un auditor la
   distincion importa.

Cifras del chat que SI verifique como exactas: 296 actividades; 3.451 transacciones; desembolsos
26.308.577.796 USD en 3.194 filas; compromisos 44.368.867.722 USD en 257 filas; estados 124/6/166;
rango de transacciones 2004-01-14 a 2025-09-30; rangos y conteos de las 4 fechas de actividad
(229/225/236/170 con dato); totales 2025 (1.983.600.000 / 813.413.091); BR-L1608 (59.777.300, 0
desembolsos, fechas, participantes); listado de 36 transacciones de BR-L1006.

Verificaciones adicionales que el chat no pudo hacer (para referencia del equipo):
- last-updated-datetime: las 296 actividades tienen el mismo valor 2025-09-15T18:01:00Z;
  generated-datetime 2025-09-15T18:46:09; version 2.02.
- Duplicados exactos (actividad+tipo+fecha+valor): 187 pares, 374 filas, 27 actividades; los mas
  afectados: L1081 (37 pares), L1122 (19), L1018 (19), L1083 (18), L1053 (15), L1006 (12), L1160 (12).
- Desembolso > compromiso: 37 actividades; 19 con exceso material (L1083 184%, L1084 181%, L1122 171%,
  L1087 160%, L1208 159%, L1018 152%, L1006 151%...). La lista de actividades con exceso coincide
  casi uno a uno con la lista de actividades con duplicados: la causa probable de ambos hallazgos es
  la misma (transacciones repetidas en el origen).
- Negativos: 53 filas, 29 actividades, -253.482.271 USD; todos son tipo 3 (Disbursement) con
  descripcion generica "Disbursement in <trimestre>", sin motivo.
- Post Completion / Completion con 0 desembolsos: solo BR-L1608. Completion/Post Completion con
  desembolso < 99% del compromiso: 62 (ej. BR0375 0,9%, L1529 11%, L1152 14%, L1503 17%).
- Implementation sin ninguna transaccion: 41 (todas L16xx, J0001, J0002, U0002; aprobadas
  recientemente). Implementation con compromiso y 0 desembolsos: 27.
- Desembolsos fechados despues del actual-end: 89 filas en 77 actividades, pero todos dentro del
  mismo mes (fechado a fin de mes); no es una inconsistencia real. Ninguno antes del actual-start.
- 4 desembolsos fechados 2025-09-30, 15 dias despues de la generacion del archivo (2025-09-15):
  fechas futuras respecto de la publicacion.
- Estados cancelado/suspendido: ninguno. Transacciones de tipo cancelacion: ninguna.

## 5. Limites encontrados

| Limite | Causa |
|---|---|
| Fecha de generacion, version del estandar, last-updated-datetime | Falta de tool: `file_overview` no expone atributos de `<iati-activities>` ni de `<iati-activity>`. El dato existe en el XML y en `activities.csv` (`last_updated_datetime`). |
| Cualquier control por actividad a nivel archivo (desembolso vs compromiso, sin compromiso, sin desembolso, sin transacciones) | Falta de tool: solo hay `activity_summary` unitario y agregados por anio/sector/org/pais. `top_activities_by_amount` existe pero el modelo no la uso y tampoco resolveria la comparacion. |
| Duplicados exactos, negativos, filtro de transacciones por fecha | Falta de tool: `activity_transactions` es por actividad; no hay `list_transactions` a nivel archivo con filtros. |
| Documentos, presupuestos, resultados de una actividad | Falta de tool: `activity_summary` no incluye `document-link`, `budget` ni `result`. El XML tiene documents (6 en L1608) y results en otras actividades; `documents.csv`, `budgets.csv`, `results.csv` ya existen en el cache. |
| Versiones anteriores del archivo | Falta de datos: el XML es una unica instantanea; no hay historial. Respuesta correcta del chat. |
| Firma auditora, dictamen, oficio, team leader | Falta de datos en IATI; el chat rechazo correctamente. |
| Aritmetica sobre listados (sumas, conteo de pares) | Respuesta del modelo: intento calcular a mano sobre 36 filas y fallo dos veces; ademas descalifico el total correcto de la tool. La tool deberia hacer la cuenta, no el modelo. |
| Log reproducible de consultas | Respuesta del modelo / gateway: el modelo no tiene acceso a su propio historial de tool calls y lo reconstruye de memoria (con errores). El gateway si lo tiene (eventos `tool_call`). |
| Llamadas a tools irrelevantes (Q2, Q10: 5 tools para no obtener nada nuevo) | Mal uso de tool / prompt: el modelo "explora" cuando ya sabe que no hay tool adecuada. |

## 6. Tools que faltan

1. **`file_metadata`** - devuelve `generated-datetime`, `version` del estandar, min/max/distinct de
   `last-updated-datetime`, URL de origen, hash y fecha de descarga del XML, numero de actividades y
   transacciones. Necesaria para acreditar la fuente en cualquier expediente de auditoria.
2. **`activity_financial_summary` (o `activities_commitment_vs_disbursement`)** - tabla con una fila
   por actividad: identificador, titulo, estado, compromiso total, desembolso total, diferencia,
   porcentaje, n transacciones, primera y ultima fecha de transaccion; con filtros por estado y
   umbral de porcentaje y ordenamiento. Resuelve Q2, Q9 y buena parte de los controles de cierre
   (cerradas con fondos pendientes, abiertas sin movimiento).
3. **`list_transactions`** - listado a nivel archivo con filtros: tipo, rango de fechas, valor
   minimo/maximo (permite `value_max=0` para negativos), actividad, organizacion receptora; paginado.
   Resuelve Q5 y Q9 y da trazabilidad transaccion por transaccion.
4. **`data_quality_checks`** - ejecuta y devuelve controles predefinidos: duplicados exactos (por
   actividad+tipo+fecha+valor), valores negativos, desembolso > compromiso, actividades cerradas sin
   desembolso o con < X% desembolsado, en Implementation sin transacciones, transacciones fuera del
   rango de fechas de la actividad, transacciones posteriores a la fecha de generacion, fechas
   invalidas. Cada control con conteo, monto y lista de identificadores. Es la tool central para este
   rol; evita que el modelo haga aritmetica manual.
5. **`activity_documents` / `activity_budgets` / `activity_results`** (o ampliar `activity_summary`
   con secciones opcionales) - documentos con URL, titulo, categoria y fecha; presupuestos por
   periodo; resultados con indicadores y valores. Los CSV ya estan en el cache.
6. **`activity_transactions` con `dedupe=true` y totales** - que devuelva ademas suma por tipo, n de
   pares duplicados y suma deduplicada, para que el modelo no calcule a mano.
7. **`session_tool_log`** (gateway o server) - devuelve la lista exacta de tools y argumentos
   invocados en la conversacion, para que "explique su metodologia" no dependa de la memoria del
   modelo.

## 7. Mejoras sugeridas priorizadas

### Datos / plugin (mcp-iati)
- **Alta:** `data_quality_checks` y `activity_financial_summary` (puntos 4 y 2). Sin ellas el rol
  auditor no puede producir ni un hallazgo.
- **Alta:** `file_metadata` (punto 1); el dato ya esta parseado en `activities.csv`.
- **Alta:** `list_transactions` a nivel archivo con filtros (punto 3).
- **Media:** exponer documentos, presupuestos y resultados por actividad (punto 5); hoy la respuesta
  "no aparecen en los resultados" se lee como "no existen".
- **Media:** que `activity_transactions` devuelva totales y conteo de duplicados (punto 6).
- **Baja:** senalar en `file_overview` transacciones fechadas despues de `generated-datetime`.

### Prompt / instrucciones
- **Alta:** prohibir explicitamente que el modelo sume o cuente filas de una tabla "a mano" cuando la
  tool ya devuelve un total; si no hay tool para el calculo, decir "no determinable" en vez de
  aproximar. Q4 muestra que el modelo produce cifras con apariencia de exactitud (127.617.044,00)
  que son falsas.
- **Alta:** cuando el modelo corrige una cifra propia, obligarlo a marcar la anterior como
  invalidada y a no reincluirla en resumenes posteriores (Q10 volvio a listar las cifras falsas como
  "verificadas").
- **Alta:** nunca contradecir el resultado de una tool con un calculo propio; si difieren, reportar la
  discrepancia sin decidir cual es correcto.
- **Media:** cuando un tipo de dato (documentos, budgets) no esta expuesto por ninguna tool, usar la
  formula "no consultable en este entorno" y no "no hay" / "sin informacion".
- **Media:** no llamar tools de exploracion (`list_activity_statuses`, `file_overview`,
  `list_reporting_organisations`) que ya se llamaron en la misma conversacion salvo que cambie el
  parametro; en Q2 y Q10 gasto 5 llamadas sin obtener nada nuevo.
- **Baja:** al responder "metodologia", citar el nombre de la tool y los parametros literales, no
  una parafrasis.

### Gateway / UI
- **Alta:** exponer al modelo (o directamente al usuario) el log real de tool calls de la sesion
  con argumentos; el gateway ya emite eventos `tool_call` y podria inyectarlos como contexto o
  mostrarlos como panel "Consultas ejecutadas" exportable.
- **Media:** boton "descargar CSV" de cada tabla renderizada (para adjuntar al expediente) y
  mostrar el conteo total de filas cuando la tool devuelve `limit`.
- **Media:** mostrar de forma permanente (cabecera o pie) la identidad del archivo: URL de origen,
  generated-datetime, hash, fecha de descarga. Para un auditor es requisito antes de leer cualquier
  numero.
- **Baja:** marcar visualmente en la conversacion cuando el modelo se autocorrige, para que el
  usuario no tome la primera cifra por buena.

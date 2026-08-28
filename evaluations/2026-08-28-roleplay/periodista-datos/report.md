# Reporte de evaluacion - rol `periodista-datos`

Fecha: 2026-08-28. Chat evaluado: http://127.0.0.1:8064/ (mcp-chat-gateway +
mcp-server + plugin mcp-iati, archivo IATI oficial del BID para Brasil, 296
actividades). Transcripcion completa en `conversation.md`.

## 1. Rol y objetivo

Periodista de datos. Busca series temporales, rankings completos (no top 10),
cruces sector x anio, comparaciones entre estados de actividad, porcentajes
sobre el total, promedios y medianas, per capita, deflactado por inflacion,
graficos y exportacion a CSV. Cuestiona metodologia: vocabularios de sector y
doble conteo, si los porcentajes suman 100, moneda, duplicados, outliers.
Objetivo de la prueba: ver que tan lejos llega el chat con pedidos analiticos
tipicos de una redaccion de datos y cuanto de lo que dice es verificable contra
el XML/CSV.

## 2. Resumen de la experiencia

Util para lo basico y honesto en los limites, pero insuficiente para un flujo
de trabajo de datos. Lo que las tools agregan (totales por anio, por sector,
por pais, top actividades, transacciones de una actividad) sale exacto: la
serie anual de compromisos, el ranking completo por sector en ambos
vocabularios y el analisis de concentracion (18 actividades = 50%) coinciden
al dolar con pandas sobre los CSV. Sin embargo, todo lo que requiere una
segunda dimension (sector x anio, montos por estado de actividad), una
estadistica distinta de la suma (conteo, promedio, mediana), un listado
completo por actividad, una exportacion o un grafico, queda fuera: el chat lo
reconoce y remite al "archivo crudo con un script en pandas", que es justamente
lo que el periodista queria evitar. El punto mas grave: cuando el modelo suma
a mano cifras que la tool no totaliza, se equivoca (dos totales de desembolsos
distintos y ambos incorrectos), y ademas expone su razonamiento interno
("Dejame verificar...", "Debo ser honesto...") dentro de la respuesta. Ningun
pedido de grafico genero un evento `chart`: el plugin mcp-iati nunca devuelve
`charts`.

## 3. Tabla de las 10 preguntas

| # | Pregunta (resumida) | Tools llamadas | Calidad | Comentario corto |
|---|---------------------|----------------|---------|------------------|
| 1 | Serie anual de compromisos 2004-2030 con numero de transacciones por anio | filter_activities_by_country, transaction_totals_by_year, transaction_totals_by_country, list_reporting_organisations, top_activities_by_amount | parcial | Montos por anio exactos (verificado). No pudo dar conteo de transacciones (no hay tool). Llamadas innecesarias (country, top 10). Razonamiento interno filtrado en la respuesta. |
| 2 | Ranking completo de sectores con % y aclaracion de vocabulario / doble conteo | transaction_totals_by_sector x3, list_sectors | buena | 16 sectores voc 99 y 51 DAC, suman 44,368,867,722 exactos (verificado). Explico bien que cada vocabulario es un 100% independiente. Codigos DAC sin nombre (41050, 23220, 43042). |
| 3 | Cruce sector x anio (5 sectores voc 99), grafico de lineas + tabla | transaction_totals_by_sector | mala | No existe tool de cruce; no hubo chart. Respuesta honesta pero inutil para el pedido. |
| 4 | Grafico de barras compromisos vs desembolsos por anio | transaction_totals_by_year | parcial | Tabla correcta (verificada). Sin evento chart; el modelo pego un SVG "autonomo" que esta vacio (sin barras). Peor que no dar nada. |
| 5 | Exportar CSV de las 296 actividades con fechas, sector, compromiso, desembolso | filter_activities_by_country (limit 300) | mala | No hay exportacion ni listado por actividad con montos. Devolvio solo id/titulo/estado. |
| 6 | Per capita 2018/2024 y total en USD constantes 2024 (capciosa) | transaction_totals_by_year x3 | parcial | Bien: aclaro que poblacion y deflactor no estan en los datos. Pero igual dio cifras (10.1 y 4.6 USD pc; 57-62 mil M) marcadas como estimacion; mi calculo con CPI da ~61 mil M, asi que son plausibles, pero un titular no deberia salir de un "ejemplo ilustrativo". |
| 7 | Ranking de estados brasilenos por monto y por tasa de interes (trampa) | list_recipient_countries, search_activities | buena | No invento. Dijo correctamente que no hay campo subnacional agregable ni tasa de interes en IATI. "29 actividades mencionan Sao Paulo" verificado. Ignoro que locations.csv existe (975 filas, pero geocodificacion basura). |
| 8 | Por activity status: n, compromiso total, promedio, mediana, % desembolsado, actividades sin compromiso | list_activity_statuses | mala (con invento) | Conteos por estado correctos (124/6/166). Todo lo demas "no disponible". Y solto un "desembolsos totales 31,933,275,932 USD" que es FALSO (real: 26,308,577,796). |
| 9 | Repregunta: recalcula el total de desembolsos, ratio global, duplicados | transaction_totals_by_year x2 | invento | Reconocio el error y dio OTRO total falso: 27,169,617,809 (los 21 valores anuales listados son correctos; la suma esta mal). Ratio 61.2% en vez de 59.3%. Sobre duplicados: no puede verificar (hay 187 pares exactos, 576 M USD). |
| 10 | Ranking completo de 255 actividades con % acumulado; plausibilidad de Curitiba II 8,502 M | top_activities_by_amount (limit 100), activity_transactions, activity_summary | buena/parcial | 18 actividades concentran el 50% (verificado). Tabla limitada a 100 filas, no 255. Buen juicio sobre el outlier (probable error de unidad; desembolso 77 M). Error menor: dijo que no hay value-date, el XML si lo tiene (value-date="2004-01-14"); la tool no lo expone. |

Ningun `chart` ni `force` en las 10 respuestas. Tiempo por respuesta: 9-31 s.

## 4. Errores factuales o alucinaciones (verificacion contra XML/CSV)

Verificaciones hechas con pandas sobre `transactions.csv`, `sectors.csv`,
`activities.csv`, `participating_orgs.csv`, `locations.csv` y el XML crudo.

1. **Total de desembolsos (Q8): 31,933,275,932 USD - FALSO.** Suma de
   `transaction_type == 3` en transactions.csv: **26,308,577,796 USD**
   (3,194 transacciones). Diferencia de +5.6 mil M (21%). El modelo lo dijo
   sin ninguna tool que lo totalice.
2. **"Correccion" (Q9): 27,169,617,809 USD - TAMBIEN FALSO.** Los 21 montos
   anuales que listo son todos correctos; la suma aritmetica esta mal
   (real 26,308,577,796). Ratio desembolsado/comprometido: dijo 61.2%, real
   26,308,577,796 / 44,368,867,722 = **59.3%**. Un periodista que confie en
   el chat publicaria dos veces una cifra equivocada, incluso tras
   cuestionarla.
3. **value-date de Curitiba II (Q10):** dijo "no hay value-date declarado".
   El XML tiene `<value currency="USD" value-date="2004-01-14">8502249000`.
   Error inducido porque `activity_transactions` no devuelve la columna.
4. **Per capita e inflacion (Q6):** las cifras (10.1 / 4.6 USD pc; 57-62 mil
   M constantes) no son datos IATI; el chat lo dijo claramente, pero igual
   las entrego. Mi reproduccion con CPI-U (base 2024) da 61.0 mil M y per
   capita 10.15 / 4.55 con poblacion IBGE, asi que las estimaciones son
   razonables. No es alucinacion, pero el modelo asume poblacion y deflactor
   de memoria.
5. **Razonamiento interno visible (Q1, Q3, Q5, Q8, Q9):** la respuesta
   incluye parrafos como "Dejame verificar...", "Debo ser honesto con el
   usuario...". No es error factual pero degrada mucho la confianza y la
   legibilidad.

Verificado como correcto:

- Q1: compromisos por anio 2004-2025, los 22 valores coinciden al dolar; total
  44,368,867,722; todo en USD (257 transacciones de tipo 2; el conteo que no
  pudo dar: 9, 6, 5, 5, 16, 27, 21, 8, 17, 25, 13, 1, 5, 10, 12, 10, 9, 11,
  11, 12, 16, 8).
- Q2: los 16 sectores voc 99 y los 51 DAC con compromiso coinciden; ambos
  vocabularios suman exactamente 44,368,867,722. En sectors.csv cada
  actividad tiene exactamente 1 sector por vocabulario (592 filas = 296 x 2)
  y `percentage` esta vacio en el 100% de las filas, asi que no hay doble
  conteo ni reparto porcentual: la conclusion del chat es correcta. Hay 56
  sectores DAC en total pero 5 sin compromiso (41 actividades sin ninguna
  transaccion de tipo 2).
- Q4: desembolsos anuales 2005-2025, los 21 valores coinciden.
- Q7: 29 actividades mencionan "Sao Paulo" en titulo/descripcion/orgs.
- Q8: activity_status 2=124, 3=6, 4=166.
- Q10: 18 actividades acumulan 50.8% (17 = 49.7%); top 10 = 39.2%.

Hallazgos sobre los datos que el chat no pudo ver:

- **187 pares de transacciones exactamente duplicadas** (misma actividad,
  tipo, fecha y monto; sin transaction-ref), 576,369,839 USD. Ej.
  BR-L1006 con desembolsos de 1,650,000 repetidos. Posible doble conteo del
  publicador.
- **Curitiba II (BR0375) 8,502,249,000 USD** es casi seguro un error de unidad
  del BID: desembolso real 77,340,288 USD, presupuesto y fechas de un
  prestamo chico (2005-2009). Representa el 19% de toda la cartera y
  distorsiona cualquier serie o ranking. El chat lo detecto bien al ser
  preguntado, pero no lo advirtio en Q1 ni Q2 donde ya contaminaba las
  cifras.
- `locations.csv` tiene 975 filas pero son geocodificaciones automaticas de
  fragmentos de texto ("Brazil,Se", "Brazil,Modelo", "Brazil,Contrato" con
  lat 12.44 / lon -69.92, que cae en el Caribe). Inutilizable para
  desagregar por estado.

## 5. Limites encontrados

| Que no pudo responder | Causa |
|-----------------------|-------|
| Numero de transacciones por anio (Q1) | Falta de tool: `transaction_totals_by_year` solo suma, no cuenta. |
| Cruce sector x anio (Q3) | Falta de tool: no hay agregacion por dos dimensiones. |
| Graficos (Q3, Q4) | Plugin: ninguna tool de mcp-iati devuelve `charts` (grep en `mcp-iati/src` no encuentra `charts=`), asi que el gateway nunca recibe evento chart. El modelo intento compensar con un SVG inline vacio. |
| Exportar CSV / tabla completa por actividad con fechas, sector y montos (Q5) | Falta de tool (listado enriquecido por actividad) y falta de mecanismo de exportacion en gateway. `filter_activities_by_country` devuelve solo id/titulo/estado/pais. |
| Per capita, dolares constantes (Q6) | Falta de datos: IATI no trae poblacion ni deflactor. Correctamente senalado. |
| Ranking por estado brasileno, tasa de interes (Q7) | Falta de datos en el XML (no hay recipient-region subnacional ni condiciones financieras; locations es basura). Correcto. |
| Montos/promedio/mediana/% desembolsado por activity status; actividades sin compromiso (Q8) | Falta de tool: no hay agregacion por status ni estadisticas distintas de la suma. Ademas el modelo alucino un total. |
| Total de desembolsos y ratio (Q9) | Mal uso / modelo: la tool devuelve 43 filas anio x tipo sin fila de total; el modelo suma mal. |
| Deteccion de duplicados (Q9) | Falta de tool: no hay listado de transacciones crudas ni chequeo de calidad. |
| Ranking completo de 255 actividades (Q10) | Tool con tope: `top_activities_by_amount` limit 100 (o el modelo no pidio mas); tampoco devuelve % acumulado. |
| value-date, transaction-ref, provider/receiver en transacciones (Q10) | Tool `activity_transactions` no expone esas columnas aunque el XML las tiene. |

Ademas: el modelo hizo llamadas innecesarias en Q1 (top 10, country totals,
reporting orgs) y no uso `date_coverage` ni `file_overview` para responder
sobre 2030.

## 6. Tools que faltan

1. **`transaction_stats`** (group_by: year | sector | activity_status |
   finance_type | aid_type | org; transaction_type; vocabulary) -> por grupo:
   count, sum, mean, median, min, max, share_pct, cumulative_pct. Cubre Q1,
   Q8, Q10 y cualquier "promedio/mediana/porcentaje" de una redaccion.
2. **`transaction_pivot`** (rows: sector|status|org, cols: year,
   transaction_type, vocabulary) -> matriz sector x anio con totales de fila
   y columna, y `charts` de lineas/barras apiladas. Cubre Q3.
3. **`activities_export`** (fields opcionales, format csv|json, sin limite o
   limite 1000) -> una fila por actividad con id, titulo, status, fechas
   planificadas/reales, sector por vocabulario, compromiso, desembolso, %
   ejecutado, finance/aid type. Cubre Q5 y sirve como base para cualquier
   analisis propio. El gateway deberia ofrecer "descargar CSV" sobre
   cualquier tabla.
4. **`activity_ranking`** (metric: commitment|disbursement|ratio, limit hasta
   todas, con % del total y % acumulado, y flag de outliers por z-score).
   Cubre Q10 sin obligar al modelo a acumular a mano.
5. **`data_quality_report`** -> transacciones duplicadas exactas, outliers de
   monto por sector, actividades sin compromiso, sectores sin nombre en el
   codelist, locations con coordenadas fuera del pais, commitments anteriores
   a la fecha de inicio. Cubre Q9 y las advertencias metodologicas que un
   periodista de datos necesita antes de publicar.
6. **`activity_transactions` ampliada**: exponer value-date, transaction-ref,
   provider/receiver, finance_type, aid_type, y aceptar limit > 50 o
   paginacion.
7. **`deflate_and_normalise`** (opcional): recibir serie anual y devolverla en
   USD constantes usando un deflactor declarado (CPI-U o deflactor BM
   embebido con fecha de version) y per capita con poblacion WB/IBGE
   embebida. Si no se quiere embeber datos externos, al menos una tool
   `reference_indicators` que devuelva poblacion y CPI con fuente y anio,
   para que el modelo no los saque de memoria.

## 7. Mejoras sugeridas priorizadas

### Datos / plugin (mcp-iati)

- **Alta**: que las tools de agregacion devuelvan una fila TOTAL y `count`
  ademas de `sum`; el modelo no debe sumar 21 numeros a mano (origen de los
  dos totales falsos de desembolsos).
- **Alta**: emitir `charts` en `transaction_totals_by_year` (barras/lineas
  por tipo) y `transaction_totals_by_sector` (barras). Hoy el plugin no
  genera ningun chart y la UI de graficos queda sin uso.
- **Alta**: `transaction_stats` / `transaction_pivot` (seccion 6, items 1-2).
- **Media**: `activities_export` con todas las columnas por actividad y sin
  tope de 100.
- **Media**: `data_quality_report`; en particular marcar los 187 duplicados y
  el outlier BR0375 (8.5 mil M) en `file_overview`, porque contamina el 19%
  de cualquier total.
- **Media**: completar nombres de codigos DAC faltantes (41050, 23220, 43042
  aparecen "sin nombre") usando el codelist oficial de IATI.
- **Baja**: exponer value-date / transaction-ref / provider / receiver en
  `activity_transactions`; documentar en `file_overview` que locations es
  geocodificacion automatica no confiable.

### Prompt / instrucciones del modelo

- **Alta**: prohibir sumas o ratios calculados "a mano" sobre mas de un
  punado de filas; si la tool no devuelve el total, decir que no esta
  disponible o pedir la tool adecuada. Q8/Q9 son el caso de estudio.
- **Alta**: no filtrar el razonamiento interno ("Dejame verificar",
  "Debo ser honesto") al texto de respuesta; o el gateway debe separar
  thinking de reply.
- **Media**: cuando un pedido de grafico no se puede cumplir, decirlo en una
  linea; nunca generar un SVG/codigo de grafico inventado (Q4 entrego un
  SVG sin barras).
- **Media**: en Q6-tipo (per capita, inflacion) dar la formula y el dato IATI,
  y no un numero final salvo que el usuario pase poblacion/deflactor; o
  citar fuente exacta y anio si se usa memoria.
- **Media**: usar `limit` maximo cuando el usuario pide "completo" (Q10 se
  quedo en 100 de 255) y `date_coverage`/`file_overview` antes de responder
  sobre el rango temporal.
- **Baja**: reducir llamadas irrelevantes (Q1 llamo 5 tools para una
  pregunta de una).

### Gateway / UI

- **Alta**: boton "descargar CSV" en cada tabla renderizada y un evento de
  export (Q5 es imposible hoy aunque la tabla exista en pantalla).
- **Alta**: que la UI muestre, cuando llegan `table` sin `chart`, un grafico
  automatico para tablas anio x valor (fallback de cliente), al menos para
  series temporales.
- **Media**: mostrar el total de filas devueltas vs limite, para que el
  usuario sepa que ve 100 de 255.
- **Media**: separar en la UI el bloque "Interpretacion IA (no respaldada por
  los datos)" con estilo distinto; ya viene etiquetado pero se mezcla con
  las cifras verificadas.
- **Baja**: enlace directo a la ficha del proyecto en iadb.org
  (`linked-data-uri` ya esta en el XML) para cotejar outliers como BR0375.

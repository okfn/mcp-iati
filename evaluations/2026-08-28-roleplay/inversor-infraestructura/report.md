# Reporte de roleplay: inversor-infraestructura (2026-08-28)

Fuente verificada: XML `iadb-Brazil.xml` (296 actividades) y los CSVs derivados en
`~/.local/share/mcp-iati/csv/f303852cb045ed51/` (activities, transactions, sectors,
participating_orgs, activity_date, documents, results, locations). Todas las cifras
de esta verificación se calcularon con pandas sobre esos CSVs y se cruzaron contra
el XML en los casos críticos (BR0375, BR-L1491, BR-L1296).

## 1. Rol y objetivo

Analista de un fondo de inversión en infraestructura. Busca una foto de la cartera
del BID en Brasil en transporte, energía y agua/saneamiento: cantidad y tamaño de
operaciones (promedio, mediana), ritmo de desembolso, pipeline y aprobaciones
recientes, presencia de PPPs / sector privado / garantías, cofinanciadores,
concentración por estado, y condiciones financieras de un préstamo concreto
(BR-L1607). Preguntas pensadas para forzar agregaciones cruzadas (sector x estado
x año x monto) y para detectar si el chat inventa cuando el dato no existe.

## 2. Resumen de la experiencia

Útil como primera aproximación, pero no confiable sin verificación. Lo bueno: los
agregados por sector (Q1), los totales por año y el diagnóstico de la anomalía
CELESC (Q10) coinciden exactamente con los datos; el modelo declara con honestidad
que IATI no trae tasas, spreads, plazos ni contratistas (Q9); y detecta la
anomalía Curitiba II. Lo malo: el ranking top 10 de transporte (Q2) omite cuatro
operaciones grandes; el modelo dice que no puede calcular media y mediana (Q6) y
luego calcula mal la media "sin Curitiba"; afirma que no hay documentos para
BR-L1622 cuando hay 4 (incluido el archivo de adjudicaciones de contratos); se
"corrige" en Q8 diciendo que IFAD no existe cuando sí está (bajo su nombre
completo); afirma que no hay valores negativos en el archivo cuando hay 53
desembolsos negativos (-253 M USD); e inventa que el identificador BR-L1373
"embebe el estado". El patrón dominante es que las tools sólo dan agregados
o top-N y el modelo suple los huecos con muchas llamadas individuales
(20+ `activity_summary` por turno) que luego resume de forma incompleta.

## 3. Tabla de las 10 preguntas

| # | Pregunta (resumen) | Tools llamadas | Calidad | Comentario corto |
|---|---|---|---|---|
| 1 | Foto de cartera por sector: n, compromiso, desembolso, ratio | search_activities, list_recipient_countries, list_sectors, filter_activities_by_sector x3, file_overview, transaction_totals_by_sector x2 | buena | 34/28/6 operaciones y todos los montos coinciden al dólar. Correctamente señala el ratio >1 en energía. Usa vocab 99 (TR/AS/EN), no DAC. |
| 2 | Top 10 transporte por compromiso, sospecha de distorsión | top_activities_by_amount, filter_activities_by_sector, activity_summary x20 | parcial | Curitiba II (8,502 M) bien identificada. Pero el "top 10" omite L1503 (600 M, #3), L1326 (400 M), L1336 (250 M), L1434 (235 M) y mete L1161 y L1018 que no entran. L1503 tiene ratio 0.17 y es otra distorsión no vista. |
| 3 | Pipeline y aprobaciones 2024-2025 | search_activities x4, list_activity_statuses, activity_summary x23 | parcial | "0 en pipeline" correcto (sólo estados 2/3/4). Usa actual start como proxy de aprobación (mal criterio, la fecha de compromiso estaba disponible). Las 6 fechas listadas sí son correctas. |
| 4 | Compromisos fechados 2024-25 y ficha BR-L1622 | activity_transactions, activity_summary | mala | Sólo lista L1622; omite L1615 (2024-01-10, 70 M) y L1616 (2024-06-21, 100 M) que había consultado en Q3. Ficha: participantes y clasificaciones correctas, pero "no hay documentos" es falso (4 docs, incl. contract awards). |
| 5 | PPPs, sector privado, soberano vs no soberano, IRR | filter_by_participating_org x2 (sin resultado), list_participating_organisations | parcial | Conclusión "68 ops / 20,689 M todo soberano" defendible; IRR no existe (correcto). No vio que 4 operaciones de energía tienen org_type 70 (Private Sector) ni que BR-U0002 tiene finance type 1100 (guarantee) y es una concesión. Mención de IFAD aquí era correcta. |
| 6 | Media y mediana por operación; desembolsos por año en infra activa | top_activities_by_amount x2, transaction_totals_by_year, transaction_totals_by_sector x2 | parcial | Declara "no computable" media y mediana. La media TR sin Curitiba la divide por 34 en vez de 33 (211.6 M vs 224.9 M real). Serie anual global correcta pero no la pedida (infra Implementation). |
| 7 | Ranking de estados por compromiso en infra | list_participating_organisations | mala | Reconoce que no hay campo estado (correcto) y entrega conteo de actividades del archivo entero (números casi todos correctos). Inventa que "BR-L1373 corresponde a Sao Paulo" por el código del identificador (falso, es secuencial). No usa locations.csv (188 actividades con localización). |
| 8 | Cofinanciadores y % Capital Ordinario | list_participating_organisations, list_reporting_organisations, filter_by_participating_org x3, activity_summary x2, file_overview, transaction_totals_by_organisation | parcial | CTF/GCF bien ubicados; total 44,369 M correcto. Se "corrige" mal: IFAD sí existe (L1617, Extending). Dice que no se puede separar aporte por fuente, pero las transacciones traen provider-org: CTF 10 M, GCF 75 M, OC 44,284 M (99.8%). |
| 9 | Tasa, spread SOFR, plazo, gracia, constructora de BR-L1607 | activity_summary, activity_transactions | buena | Todos los datos de ficha correctos (compromiso 2023-06-28, 480,133,500; desembolso 10 M Q4-2024; fechas 2024-07-03 / 2024-12-12 / 2028-12-27). Honesto en que IATI no trae términos financieros. No menciona los 22 documentos (contrato de préstamo, avisos de licitación, contract awards) que sí están. |
| 10 | Operación que explica ratio 1.11 en energía; negativos y cancelaciones | activity_transactions x8, activity_summary x2, filter_activities_by_sector | parcial | CELESC-D (L1491) y el patrón de desembolsos duplicados correctamente detectados (suma 346,425,303; el chat dice 346,425,252, error de 51 USD). Pero "no hay valores negativos en ninguna operación" es falso: 53 desembolsos negativos (-253.5 M), incluido L1296 que el chat dijo haber revisado. |

Calidad global: 2 buenas, 6 parciales, 2 malas, 0 inventos puros (las
alucinaciones son afirmaciones de ausencia y una inferencia falsa, no cifras
inventadas).

## 4. Errores factuales o alucinaciones (verificación contra XML/CSV)

1. Q2, top 10 transporte incompleto. Ranking real por compromiso (vocab 99 = TR):
   BR0375 8,502,249,000; L1296 1,148,633,000; L1503 600,000,000; L1227 480,958,000;
   L1401 480,135,000; L1373 480,135,000; L1607 480,133,500; L1326 400,000,000;
   L1336 250,000,000; L1622 248,300,000. El chat omitió L1503, L1326, L1336 y L1434
   (235 M) e incluyó L1524 (216.8 M), L1161 (194 M) y L1018 (176.8 M). Causa: la
   tool `top_activities_by_amount` no filtra por sector, así que el modelo armó
   el ranking a mano con 20 `activity_summary` y no cubrió las 34 operaciones.
   L1503 (Post Completion, 600 M comprometido, 100 M desembolsado, accountable
   Banco do Brasil) es una segunda distorsión relevante que un inversor querría ver.

2. Q4, "no hay documentos cargados para BR-L1622": falso. documents.csv tiene 4
   documentos para esa actividad (perfil del programa en EN y ES,
   IDB_Procurement_Notices.xlsx, IDB_Project_Procurement_Contract_Awards_Data.xlsx).
   De hecho las 296 actividades tienen al menos un documento. Resultados: 0 filas
   en results.csv para L1622, eso sí es correcto. Causa: ninguna tool expone
   documentos.

3. Q4, compromisos de infraestructura fechados 2024-2025: el chat lista sólo
   L1622. Reales: L1615 PROSAI Parintins (AS, 2024-01-10, 70 M), L1616 CAESB II
   (AS, 2024-06-21, 100 M), L1622 (TR, 2025-04-30, 248.3 M). Ninguno de energía.
   El modelo ya había llamado `activity_summary` de L1615 y L1616 en Q3.

4. Q6, media de transporte sin Curitiba II: el chat calcula
   (15,697.8 - 8,502.2) / 34 = 211.6 M. Correcto es dividir por 33: 224.9 M.
   Valores reales que el chat dijo no poder calcular (compromiso por actividad,
   sólo actividades con transacción de compromiso):
   - Cartera completa: n=255, media 173,995,560, mediana 60,000,000.
     Sin Curitiba II: media 141,207,160, mediana 60,000,000.
   - TR sin Curitiba: n=33, media 224,861,938, mediana 163,310,000.
   - AS: n=28, media 140,541,396, mediana 91,635,000.
   - EN: n=5 con compromiso, media 126,784,729, mediana 128,660,000.
   Nota: la media del chat para AS (130.5 M) y EN (105.7 M) divide el total por
   el conteo de actividades incluyendo las que no tienen compromiso (L1647,
   L1631, L1664), por eso difiere de la media real por operación con compromiso.

5. Q6, desembolsos por año de la cartera de infraestructura en Implementation
   (lo pedido, que el chat dijo no poder cruzar): 2022 69.9 M; 2023 190.9 M;
   2024 224.1 M; 2025 95.0 M. Los totales globales que sí dio (827.5 / 1,504.5 /
   966.9 / 813.4 M) son correctos.

6. Q7, "el identificador embebe el código de estado (BR-L1373 = Sao Paulo,
   BR-L1018 = Distrito Federal)": alucinación. Los identificadores BR-Lxxxx son
   secuenciales del BID, no codifican estado. Los conteos de accountable por
   estado que dio (SP 19, CE 14, BA 12, AM 11, ES 8, PA 6...) son correctos salvo
   Pernambuco (7, no 6), y omite REPUBLICA FEDERATIVA DO BRASIL (25) y BNDES (11)
   que encabezan la lista.
   Ranking real de infraestructura (68 ops, por accountable, compromiso USD):
   Prefeitura de Curitiba 8,609 M (2 ops, distorsionado por BR0375); Estado de
   Sao Paulo 3,658 M (10); Estado de Ceara 909 M (4); SABESP 900 M (2); Estado
   de Amazonas 826 M (7); Banco do Brasil 600 M (1, L1503); Espirito Santo 465 M
   (3); Rio de Janeiro 452 M (1); Santa Catarina 300 M (2) + CELESC 276 M (1).
   Agrupando SP (Estado + SABESP + Prefeitura SP + SBC) se llega a ~5,000 M, es
   decir, sin Curitiba II, Sao Paulo concentra ~40% del compromiso de infra.

7. Q8, "IFAD NO existe en este archivo": falso. `International Fund for
   Agricultural Development` es Extending en BR-L1617 (Sustainable Development
   Project for Bahia's Atlantic Forest, sector AG, 100 M). La búsqueda por
   "IFAD" no matcheó porque el nombre está completo. La mención de Q5 era
   correcta y el chat la retractó indebidamente.

8. Q8, "no se puede separar cuánto aporta CTF/GCF vs BID": falso a nivel de
   datos. Las transacciones de compromiso llevan provider-org: L1576 = 240 M
   Ordinary Capital + 10 M Clean Technology Fund; L1633 = 175 M Ordinary Capital
   + 75 M Green Climate Fund. Total de compromisos por fuente: OC 44,283.9 M
   (99.81%), GCF 75 M, CTF 10 M. El chat no pudo verlo porque ninguna tool
   agrupa transacciones por provider-org.

9. Q10, "no hay compromisos negativos ni transacciones de cancelación en ninguna
   operación del archivo": mitad falso. Compromisos negativos: 0 (correcto).
   Desembolsos negativos: 53 transacciones, suma -253,482,271 USD, en 33
   actividades. En infraestructura: L1181 Ceara III -14.7 M, L1166 Tiete III
   -8.2 M, L1296 Rodoanel -3.0 M (2013-05-31, confirmado en el XML), L1263 ES
   Highway III -2.3 M, BR0302 Fortaleza -3.9 M, L1038 Joinville -0.4 M. El chat
   afirmó explícitamente haber revisado L1296 y no ver negativos.

10. Q10, cifras menores: suma de desembolsos de L1491 es 346,425,303 (chat:
    346,425,252) y el exceso es 70,374,303 (chat: 70,374,252). Error aritmético
    de 51 USD, irrelevante pero muestra que el modelo suma a mano. Los 4
    registros duplicados (37,589,600 y 32,784,703 en 2018-11-30 y 2018-12-31)
    existen tal cual en el XML, así que es un problema de datos del BID, no del
    plugin.

11. Q5, matices no vistos: participating_orgs codifica con org_type 70 (Private
    Sector) a CELESC, FURNAS, CEEE-GT y Companhia Estadual de Distribuicao (4
    operaciones de energía, todas estatales pero clasificadas como privadas);
    y BR-U0002 (concesión de restauración ecológica, Pará) tiene
    default_finance_type 1100 (guarantee) y tiene por objetivo "mobilization
    of private resources under the concession agreement". Es la única operación
    con prefijo U y sin participantes locales. Un analista de PPPs la querría
    ver, aunque no sea de los 3 sectores.

Verificadas y correctas: los 3 agregados sectoriales de Q1 (exactos); BR0375
compromiso 8,502,249,000 (2004-01-14) y desembolso 77,340,288 (XML); ficha de
L1607 (fechas y montos); L1622 compromiso 2025-04-30 por 248.3 M, sector 21012,
sin activity dates, sin results; estados 124/6/166; total compromisos
44,368,867,722 y desembolsos 26,308,577,796; OC como Extending en 257
actividades; CTF en L1576 (250 M / 240 M) y GCF en L1633 (250 M / 0).

## 5. Límites encontrados

Falta de tool (la causa más frecuente):
- No hay ranking top-N filtrado por sector, estado o status; el modelo arma
  rankings a mano con decenas de `activity_summary` y se le escapan filas (Q2).
- No hay tool que devuelva compromiso/desembolso por actividad para todas las
  actividades de un sector (necesaria para media, mediana, distribución). Q6.
- No hay cruce sector x año x status para desembolsos (Q6), ni sector x
  organización accountable x monto (Q7).
- No hay tool de documentos ni de resultados por actividad; el modelo infiere
  "no hay" a partir de que `activity_summary` no los muestra (Q4, Q9).
- No hay agrupación de transacciones por provider-org (cofinanciador) (Q8).
- No hay tool que liste transacciones negativas / anomalías (Q10) ni
  duplicados.
- No hay tool que liste compromisos por rango de fechas a nivel archivo (Q4):
  el modelo tuvo que recorrer una por una.
- No hay tool de localizaciones (locations.csv tiene 188 actividades con
  nombre de estado/municipio y coordenadas) para inferir estado (Q7).

Falta de datos en el XML (limitación real de IATI/BID, bien reportada por el
chat):
- Términos financieros: tasa, spread, plazo, gracia (Q9).
- Contratista adjudicatario y monto del contrato (Q9): sólo hay un link al
  xlsx de contract awards.
- IRR / retorno esperado (Q5). Fecha de aprobación explícita (Q3): sólo hay
  fecha de la transacción de compromiso como proxy.
- Estado federativo como campo (Q7): sólo inferible por accountable org o por
  locations.
- 4 operaciones nuevas de infra sin transacciones ni fechas (L1672, L1664,
  L1647, L1631).

Mal uso de tool / respuesta del modelo:
- `filter_activities_by_participating_org` con "IFAD" e "IDB Invest": búsqueda
  por sigla que no matchea nombres completos, y el modelo concluye "no existe"
  (Q5, Q8).
- Q3 elige actual start como proxy de aprobación cuando la fecha de compromiso
  estaba en `activity_transactions`.
- Q4 y Q10: afirmaciones categóricas de ausencia ("no hay documentos", "no hay
  negativos en ninguna operación") sin haber consultado el universo completo.
- Q6: renuncia a calcular media/mediana en vez de pedir la lista completa por
  sector (aunque `filter_activities_by_sector` + 34 `activity_summary` lo
  hubiera permitido, como hizo en Q2).
- Sección "AI Interpretation" bien separada, pero a veces contiene datos
  (p.ej. la corrección de la fecha de compromiso de L1607 en Q9) que deberían
  estar en la parte factual.
- Volumen: Q2 y Q3 ejecutaron 23-28 llamadas a tools por turno; lento (24-32 s)
  y propenso a omisiones.

## 6. Tools que faltan

1. `mcp_iati_activity_amounts` (o `list_activities_with_totals`): filtros
   sector / status / participating_org / fecha de compromiso; devuelve una fila
   por actividad con compromiso total, desembolso total, ratio, fecha del primer
   compromiso, status, accountable e implementing. Es la tabla base de cualquier
   analista de cartera: permite media, mediana, top-N por subconjunto y
   detección de outliers en una sola llamada. Cubre Q2, Q4, Q6 y parte de Q7.
2. `mcp_iati_transaction_totals_by_sector_year` (o parámetros `sector`,
   `status`, `year_from/to` en `transaction_totals_by_year`): serie anual de
   desembolsos/compromisos para un subconjunto. Cubre "ritmo de desembolso de
   la cartera activa de infra" (Q6).
3. `mcp_iati_totals_by_participating_org`: compromiso y desembolso agregados
   por organización y rol (accountable, implementing, extending), con filtro por
   sector. Es el proxy de "estado deudor" y de concentración por garante (Q7).
4. `mcp_iati_transaction_totals_by_provider`: agrupa transacciones por
   provider-org (Ordinary Capital, CTF, GCF, IFAD) para separar fuentes de
   cofinanciamiento (Q8).
5. `mcp_iati_activity_documents`: lista documentos (título, categoría, URL)
   por actividad; y `mcp_iati_activity_results` para indicadores. Un inversor
   quiere el link al contrato de préstamo, loan proposal y contract awards
   (Q4, Q9).
6. `mcp_iati_anomalous_transactions`: valores negativos, desembolso > compromiso,
   duplicados exactos (misma actividad, tipo, valor y trimestre), actividades
   sin transacciones. Cubre Q2 y Q10 y sirve también al rol auditor.
7. `mcp_iati_list_locations` / filtro por estado: usa locations.csv (188
   actividades con nombre "Brazil,<estado>") para agrupar por estado (Q7).
8. `mcp_iati_commitments_by_date`: compromisos del archivo entre dos fechas,
   con sector y monto (Q3/Q4, "aprobaciones recientes").
9. Búsqueda de organizaciones tolerante a alias/siglas (IFAD, IDB Invest, IIC,
   BNDES) o al menos un `search_participating_organisations` con substring
   sobre nombre y ref (Q5/Q8).

## 7. Mejoras sugeridas priorizadas

Datos / plugin:
- Alta: tool de listado por actividad con totales y filtros (item 1 de la
  sección 6). Es la que más respuestas destraba y reduce las cadenas de 20+
  `activity_summary`.
- Alta: exponer documents.csv y results.csv por actividad; hoy el modelo niega
  su existencia.
- Alta: agregar filtros `sector` y `status` a `transaction_totals_by_year` y
  `top_activities_by_amount`.
- Media: totales por participating org (rol) y por provider-org.
- Media: tool de anomalías (negativos, duplicados, ratio > 1, sin
  transacciones) y que `activity_summary` muestre conteo de transacciones
  negativas y de documentos.
- Media: exponer locations.csv y una inferencia de estado a partir del nombre
  "Brazil,<estado>" y del accountable org.
- Baja: normalizar espacios y saltos de línea en org_name (hay "SETRAM \n",
  "DER-SP \n") y tratar aliases comunes de organismos.
- Baja: en `activity_summary` mostrar fecha de la(s) transacción(es) de
  compromiso y `default_finance_type` decodificado (421 Standard loan, 1100
  Guarantee).

Prompt / instrucciones:
- Alta: prohibir afirmaciones categóricas de ausencia ("no hay X en ninguna
  operación") salvo que una tool haya recorrido el universo completo; en caso
  contrario decir "en las N operaciones consultadas".
- Alta: instruir que "fecha de aprobación" se aproxime con la fecha de la
  transacción de compromiso (transaction-date del tipo 2), no con actual start.
- Media: cuando una búsqueda por sigla (IFAD, IIC) no matchea, reintentar con
  nombre completo o con `list_participating_organisations` antes de concluir
  que no existe.
- Media: cuando el modelo divide totales por conteos, usar el conteo de
  actividades con compromiso (excluir las que no tienen transacciones) y
  ajustar el denominador al excluir outliers.
- Media: si la pregunta pide un ranking dentro de un subconjunto (top 10 de
  transporte), obligar a cubrir todo el subconjunto (34 actividades) antes de
  presentar el top; o declarar que es un top parcial.
- Baja: mantener los datos factuales fuera de la sección "AI Interpretation".

Gateway / UI:
- Media: cuando un turno encadena más de ~10 llamadas, mostrar un indicador de
  progreso y agrupar las tablas de `activity_summary` en una sola tabla
  consolidada descargable; hoy se renderizan 20 tablas de 2 filas.
- Media: botón de exportar CSV de la tabla consolidada (el rol quiere llevarse
  la cartera a su modelo).
- Baja: mostrar en la UI el número de actividades cubiertas por la respuesta
  ("basado en 20 de 34 actividades de TR") cuando el modelo hace muestreo.
- Baja: enlaces clicables a documentos IATI cuando la tool de documentos exista.

# Reporte de roleplay: economista-deuda (2026-08-28)

## 1. Rol y objetivo

Economista especializado en deuda publica. Objetivo: usar el chat IATI (BID / Brasil,
296 actividades) para caracterizar la cartera como deuda: prestamos vs donaciones
(finance type), flow type, tied status, prestatario (soberano vs subnacional vs
empresa publica), stock de compromisos por anio, ritmo de desembolso, reflujos y
valores negativos, moneda, condiciones financieras (tasa, plazo, gracia, garante)
y saldo por desembolsar. Estilo incisivo: cuestionar definiciones (compromiso vs
desembolso vs presupuesto), repreguntar cuando la respuesta es vaga e intentar
que el modelo invente datos que el archivo no tiene.

Todas las cifras del chat se verificaron contra
`/home/hermes/.local/share/mcp-iati/csv/f303852cb045ed51/*.csv` y el XML
`/home/hermes/.local/share/mcp-iati/xml/iadb-Brazil.xml`. Transcripcion completa
en `conversation.md`.

## 2. Resumen de la experiencia

Util para lo agregado y para el detalle por actividad: los totales de compromisos
(USD 44.369 M) y desembolsos (USD 26.309 M), la serie anual, la distribucion por
finance/flow/tied y el drill-down de una actividad concreta fueron exactos, y el
modelo detecto solo, con buen razonamiento, el outlier BR0375 (USD 8.502 M
comprometidos, 77 M desembolsados) que infla toda la cartera. Fue honesto ante
la pregunta trampa de tasas/plazos (no invento). El problema principal es que
las tools son agregaciones fijas (por anio, pais, sector, org reportante) y no
existe ningun filtro cruzado (por estado de actividad, por prestatario, por
finance type, por signo del valor) ni acceso a budgets; ante esos huecos el
modelo dos veces afirmo cosas falsas con tono seguro (que no hay transacciones
negativas; que el archivo no tiene budget), y una vez adjudico la unica garantia
a la actividad equivocada. Para un economista de deuda el chat sirve como
explorador, no como fuente de cuadros de sostenibilidad: faltan condiciones
financieras (no estan en el XML) y faltan cortes por estado/prestatario (estan
en el XML, pero sin tool).

## 3. Tabla de las 10 preguntas

| # | Pregunta (resumen) | Tools llamadas | Calidad | Comentario |
|---|---|---|---|---|
| 1 | Panorama: total comprometido, desembolsado, saldo; definicion de compromiso | filter_activities_by_country, define_term, transaction_totals_by_country x4, file_overview | buena | Cifras exactas (44.368.867.722 / 26.308.577.796). Distingue bien commitment tipo 2 de presupuesto. Llamadas redundantes (mismo total 4 veces). |
| 2 | Prestamos vs donaciones, monto por finance type, flow type, tied status | list_category_values x3, transaction_totals_by_year, top_activities_by_amount | parcial | Conteos correctos (295 x 421, 1 x 1100, flow 20, tied 5). Pero atribuye la garantia 1100 a BR-L1559 (FGI-PEAC): falso, es BR-U0002. Y dice que no puede sumar compromisos por finance type cuando con 1 sola garantia bastaba restar. |
| 3 | Ranking de prestatarios (rol accountable), soberano vs subnacional, por monto | list_participating_organisations | parcial | Ranking por conteo casi correcto (Pernambuco 7 no 6; BNDES 11 unicas no 12). No puede rankear por monto: falta tool. 40 actividades sin accountable no mencionadas. |
| 4 | Serie anual 2004-2025 compromisos y desembolsos; anios con desembolso > compromiso | transaction_totals_by_year | buena | 44 cifras verificadas, todas exactas. Lista de anios correcta tras autocorreccion en linea (2007). Tabla se autocorrige de forma un poco desprolija. |
| 5 | Que explica el compromiso 2004 de 10.764 M; detalle; plausibilidad | transaction_totals_by_year, top_activities_by_amount, activity_summary, activity_transactions | buena | Identifica BR0375 Curitiba II: 8.502.249.000 comprometido, 77.340.288 desembolsado, 37 desembolsos, fechas correctas. Argumenta bien el error de carga (factor 100). Mejor respuesta de la sesion. |
| 6 | Transacciones negativas, cuantas, cuanto suman, tipos 6 y 7 | list_category_values | invento | Afirma "no hay ninguna transaccion negativa" usando solo un conteo por tipo. Falso: hay 53 desembolsos negativos, suma -253.482.271 USD. Lo de tipos 6/7 ausentes si es correcto. |
| 7 | Repregunta: mira L1381 y revisa tu afirmacion | activity_transactions, activity_summary | buena | Encuentra el -200.000.000 (2014-05-31), admite el error y explica por que la tool no soportaba la afirmacion. Buena autocritica; ofrece buscar el resto pero reconoce que no tiene tool. |
| 8 | Tasa, plazo, gracia, moneda, garante de L1381 (trampa) | activity_summary, activity_transactions | buena | No inventa: dice que solo hay monto y moneda (USD). Advierte que el aval de la Union no esta en el archivo. La "AI Interpretation" da plazos tipicos (~20 anios, 5 gracia) bien rotulados como contexto. No menciono que hay 30 documentos vinculados (incluida la ley que autoriza la operacion) donde podria estar la info. |
| 9 | Hay budget? cuantas actividades, suma, vs compromisos; planned-disbursement; como estimar saldo | file_overview | parcial | Honesto sobre que no tiene tool de budget. Pero en la interpretacion afirma que el archivo es "sin budget, sin planned-disbursement": budget existe (3.316 elementos, 56 actividades, USD 3.426 M). planned-disbursement efectivamente no existe (0). Repite el saldo bruto con advertencias razonables. |
| 10 | Cartera por estado: n, compromisos, desembolsos, saldo; top 5 en implementacion; cartera viva vs saldo fantasma | list_activity_statuses, list_participating_organisations, top_activities_by_amount x2, activity_summary x14 | parcial | Conteos por estado exactos (124/6/166). Sin tool por estado, hace 14 llamadas una por una, da solo top 2 (L1639 1.000 M, L1625 750 M, ambos correctos) y se niega a inventar 3-5. Los totales por estado no los da (correcto: implementation 7.655 M sin desembolsar; post completion 10.375 M, de los cuales 8.425 M son BR0375). Su intuicion "la mayor parte es saldo fantasma" es correcta pero no cuantificada. |

Calidad global: 5 buenas, 4 parciales, 1 invento.

## 4. Errores factuales o alucinaciones (verificados)

1. **Q6 - "No hay ninguna transaccion con valor negativo"** (invento). Verificacion
   con transactions.csv: 53 filas con value < 0, todas tipo 3 (disbursement), suma
   -253.482.271 USD, entre 2008 y 2019 (pico 2015: 16). Mayor: BR-L1381
   -200.000.000 (2014-05-31); luego L1181 -14.743.752, L1166 -8.173.005, BR0302
   -3.901.463 (2 tx). Las descripciones del BID son genericas ("Disbursement in
   fourth quarter of 2014"), no dicen que sean reversiones. La tool usada
   (list_category_values transaction_type) solo cuenta tipos; el modelo extrapolo
   a valores. Se corrigio en Q7 al ser confrontado.

2. **Q2 - La garantia (finance type 1100) es L1559 FGI-PEAC** (alucinacion de
   vinculo). activities.csv: default_finance_type 1100 corresponde a
   XI-IATI-IADB-BR-U0002 "Concession Project for the Ecological Restoration...".
   L1559 FGI-PEAC tiene default_finance_type 421 (Standard Loan). El compromiso de
   200 M de L1559 es correcto, pero la clasificacion como garantia es falsa: el
   modelo la infirio del titulo ("Investment Guarantee Fund") porque la tool
   list_category_values no devuelve que actividad tiene cada codigo.

3. **Q9 - "El archivo que publica el BID es ... sin budget"** (afirmacion falsa en
   la seccion AI Interpretation). XML: 3.316 elementos `<budget>` (grep), CSV
   budgets.csv 3.316 filas en 56 actividades, suma 3.425.985.240 USD. Sin
   planned-disbursement (0, correcto). Nota: budget_type y budget_status vienen
   vacios en el CSV, y L1381 no tiene budget.

4. **Q3 - conteos menores**: Pernambuco 7 operaciones como accountable (modelo:
   6); BNDES 11 actividades unicas (modelo: 12, cuenta filas duplicadas). Bahia 12
   correcto. Ademas 40 actividades no tienen ninguna org con rol accountable, lo
   que el modelo no advirtio.

Cifras verificadas como correctas: totales Q1; conteos finance/flow/tied Q2;
las 44 cifras anuales de Q4; todo el detalle de BR0375 en Q5 (monto, 37
desembolsos, actual start 2005-09-16, actual end 2009-04-17, prestatario
Prefeitura de Curitiba); las 5 transacciones de L1381 en Q7; estados 124/6/166
y los dos primeros saldos vivos (L1639, L1625) en Q10.

Hallazgos de datos del XML relevantes para el rol:
- default-finance-type: 295 x 421 (Standard Loan), 1 x 1100 (Guarantees).
- default-flow-type: 296 x 20 (OOF). default-tied-status: 296 x 5 (Untied).
- Ninguna transaccion lleva finance-type / flow-type / tied-status propios.
- Solo tipos 2 (257) y 3 (3.194). No hay 4 expenditure, 6 interest, 7 repayment.
- 100% USD (7.063 atributos currency). 41 actividades (todas en implementation)
  no tienen transacciones. 37 actividades con desembolso > compromiso.
- 296 `<conditions attached="1">` pero 0 elementos `<condition>` (conditions.csv
  vacio): el BID declara que hay condiciones sin publicarlas.
- 0 loan-terms / loan-status (CRS-add). Sin tasas ni plazos en la fuente.
- Saldo comprometido - desembolsado por estado (calculado): implementation
  7.654.550.122; completion 31.160.038; post completion 10.374.579.766 (de los
  cuales 8.424.908.712 es BR0375; sin el, 1.949.671.054).

## 5. Limites encontrados

| Limite | Causa |
|---|---|
| No puede sumar compromisos/desembolsos por finance type, estado de actividad, prestatario (rol accountable) ni por tipo de organizacion | Falta de tool: las agregaciones existen solo por anio/pais/sector/org reportante. El dato esta en el XML. |
| No puede listar ni sumar transacciones negativas | Falta de tool (no hay filtro por signo/valor). Llevo a un invento en Q6. |
| No puede consultar budget ni planned-disbursement | Falta de tool. Budget existe en el XML (56 actividades); el modelo lo nego por inferencia. |
| No puede decir que actividad tiene el finance type 1100 | Mal uso / limite de tool: list_category_values solo cuenta; no hay filter_activities por finance_type. Llevo a la alucinacion de Q2. |
| Tasa de interes, plazo, gracia, garante | Falta de datos en el XML (no hay loan-terms ni conditions detalladas). El modelo respondio bien. Los documentos (30 en L1381) podrian tenerlo, pero no fueron ofrecidos. |
| Reflujos (repayment, interest) | Falta de datos en el XML (solo tipos 2 y 3). Respuesta correcta. |
| Top 5 saldo sin desembolsar en implementacion | Falta de tool: hizo 14 llamadas activity_summary una por una y solo cerro 2 puestos. |
| Ranking de prestatarios por monto | Falta de tool; las org listadas vienen con nombres sin normalizar ("ESTADO DO PARANA" vs "GOVERNO DO ESTADO DO PARANA \n") lo que ademas rompe cualquier conteo. |
| 40 actividades sin org accountable | Dato faltante en el XML; el modelo no lo advirtio (respuesta del modelo). |

## 6. Tools que faltan

1. **`transaction_totals_by_activity_status`** (o un parametro `activity_status`
   en todas las tools de totales): devuelve n actividades, compromisos,
   desembolsos y diferencia por estado. Es la pregunta basica de cartera viva vs
   cerrada; hoy es imposible.
2. **`transaction_totals_by_participating_org`** con parametro `role`
   (accountable/implementing) y normalizacion de nombres: compromisos y
   desembolsos por prestatario, con org_type para separar gobierno (10) de
   empresa/banco (40). Es "quien debe" - la pregunta central de deuda.
3. **`transaction_totals_by_category`** con category in {finance_type,
   flow_type, tied_status, aid_type}: montos y no solo conteos por codigo, y
   `filter_activities_by_category` para saber que actividades tienen un codigo.
   Evita la alucinacion de Q2.
4. **`list_transactions`** con filtros `min_value`/`max_value`/`negative_only`,
   `year`, `transaction_type`, `activity_status`, ordenable: permite ver
   reversiones, cancelaciones y outliers (BR0375, L1381) sin adivinar.
5. **`activity_undisbursed_balance`** / **`top_activities_by_undisbursed`**:
   compromiso - desembolso por actividad, con estado, prestatario y fecha del
   ultimo desembolso; filtro por estado. Reemplaza las 14 llamadas de Q10.
6. **`activity_budgets`** y **`budget_totals_by_year`**: budgets por periodo y
   comparacion con compromisos; ademas informar explicitamente si el archivo
   tiene planned-disbursement (0 aqui).
7. **`data_quality_flags`**: actividades con desembolso > compromiso (37), sin
   transacciones (41), sin accountable (40), conditions attached sin detalle
   (296), outliers de tamano (BR0375). Un economista necesita saber que limpiar
   antes de sumar.
8. **`activity_documents`** con busqueda por titulo/categoria (loan proposal,
   ley autorizante, contrato): para que la respuesta a "condiciones
   financieras" apunte a los 30 PDFs de L1381 en vez de terminar en "no esta".

## 7. Mejoras sugeridas priorizadas

### Datos / plugin

- **Alta**: filtro `activity_status` y `finance_type` en todas las tools de
  totales y top; tool de totales por org participante con rol y org_type.
- **Alta**: tool de listado/filtrado de transacciones por valor y signo, y
  saldo sin desembolsar por actividad.
- **Alta**: exponer budgets (existen 3.316) y decir explicitamente que
  planned-disbursement, loan-terms y conditions detalladas no existen en el
  archivo (file_overview deberia reportar presencia/ausencia de cada elemento).
- **Media**: normalizar nombres de organizaciones (trim, saltos de linea,
  variantes ESTADO/GOVERNO DO ESTADO) o al menos agrupar por org_ref.
- **Media**: file_overview con banderas de calidad (negativos, disb>commit, sin
  tx, sin accountable, outliers por z-score).
- **Baja**: incluir document_category y titulo en un tool de documentos por
  actividad.

### Prompt / instrucciones

- **Alta**: regla explicita "no afirmar ausencia de algo (negativos, budgets,
  elementos) si ninguna tool lo consulto; decir 'no tengo tool para verificarlo'".
  Q6 y Q9 fallaron exactamente por eso.
- **Alta**: no inferir clasificaciones (finance type, garantia) a partir del
  titulo de una actividad; si la tool solo da conteos, decirlo.
- **Media**: cuando el usuario pide un ranking que requiere n llamadas
  individuales, avisar el limite antes de gastar 14 llamadas y proponer el corte
  que si es posible (como hizo en Q10, pero despues).
- **Media**: evitar llamadas redundantes (Q1: 4 veces el mismo total).
- **Baja**: la seccion "AI Interpretation" a veces mete afirmaciones sobre los
  datos ("sin budget") disfrazadas de contexto; restringirla a contexto externo.

### Gateway / UI

- **Media**: mostrar en la UI que tool se llamo y con que argumentos (el usuario
  pudo detectar el error de Q6 solo porque el script lo registra).
- **Media**: permitir exportar las tablas (CSV) para llevar la serie anual o el
  ranking a un cuadro de sostenibilidad.
- **Baja**: indicador visual de "cifra calculada por el modelo" vs "cifra
  devuelta por tool" (el saldo de 18.060 M es una resta del modelo).

# Evaluacion por roles del chat IATI (BID Brasil) - reporte final / EPIC

Fecha: 2026-08-28. Sistema evaluado: mcp-chat-gateway (http://127.0.0.1:8064/)
-> mcp-server + plugin mcp-iati, archivo IATI oficial del BID para Brasil
(https://webimages.iadb.org/iati/iadb-Brazil.xml, IATI 2.02, generado
2025-09-15, 296 actividades, 3.451 transacciones, 2004-2030). LLM: deepseek-chat.

Metodo: 15 roles (periodistas, ciudadanos, analistas, funcionarios, ONG,
inversor, experto IATI), 10 preguntas incisivas cada uno por el mismo endpoint
`/chat` que usa la UI (`ask.py`), con verificacion de cifras contra los CSV
generados por okfn_iati y el XML. Transcripciones en `<rol>/conversation.md`,
reportes individuales en `<rol>/report.md`, indice de roles en `ROLES.md`.

## 0. Nota sobre la version del archivo (agregada tras la evaluacion)

La evaluacion corrio contra un snapshot del archivo del BID con
`generated-datetime` 2025-09-15 (296 actividades), cacheado en el server
local. El archivo que hoy sirve https://webimages.iadb.org/iati/iadb-Brazil.xml
(y por lo tanto produccion, mcp.okfn.org/iati) es del 2026-07-15 (239
actividades): el BID retiro 57 actividades (56 Implementation, 1 Post
Completion, 17 con transacciones; entre ellas BR-L1673 Pro-Igualdade y
BR-L1608 Piaui, citadas en varios reportes) y agrego 1. Las cifras
absolutas de los reportes individuales (296, 44.369 M, etc.) corresponden
al snapshot 2025; los hallazgos sobre comportamiento del chat siguen
valiendo.

Esto agrega un hallazgo propio: el chat no puede decir que version del
archivo usa (ver A7 y E27) y no hay forma de detectar que el publicador
retiro actividades entre versiones. Ver items A7b y B15 en el plan.

## 1. Resultado global

150 respuestas evaluadas por los propios roles:

| Calidad | Cantidad | % |
|---------|----------|---|
| buena | 61 | 41% |
| parcial | 67 | 45% |
| mala | 19 | 13% |
| invento (cifra fabricada) | 3 | 2% |

Por rol (buena / parcial / mala / invento):

| Rol | b | p | m | i | Nota dominante |
|-----|---|---|---|---|----------------|
| funcionario-estadual | 8 | 2 | 0 | 0 | Cartera de Pernambuco completa y exacta; nego results/docs que existen |
| estudiante | 7 | 3 | 0 | 0 | Muy util para principiante; sin graficos ni cita de fuente |
| investigadora-genero | 6 | 3 | 1 | 0 | 60 indicadores de genero en el XML inalcanzables |
| economista-deuda | 5 | 4 | 0 | 1 | Detecto outlier BR0375; "no hay negativos" (hay 53) |
| periodista-humanitario | 5 | 3 | 2 | 0 | Cifras exactas; nego results; ranking incompleto |
| activista-ambiental | 4 | 4 | 2 | 0 | Busqueda solo en ingles; vocabulary=2 inexistente |
| analista-politicas-publicas | 4 | 6 | 0 | 0 | 926 results / 9.807 indicadores sin tool |
| ciudadano-desconfiado-bid | 4 | 5 | 1 | 0 | Corrige premisas falsas; cito ID inexistente |
| periodista-cambio-climatico | 4 | 6 | 0 | 0 | Sin policy markers en el XML; sin sector x anio |
| ong-salud-educacion | 4 | 4 | 2 | 0 | Catalogo bien; alianzas (docs/contactos/results) imposible |
| periodista-datos | 3 | 3 | 3 | 1 | Sumas a mano erroneas; 0 charts en 10 respuestas |
| periodista-investigativo | 3 | 6 | 1 | 0 | receiver-org y document-link existen y no se ven |
| inversor-infraestructura | 2 | 6 | 2 | 0 | Rankings a mano incompletos; infirio estado por ID |
| experto-iati | 1 | 7 | 2 | 0 | Sin metadatos del archivo; organisation_type lee reporting-org |
| auditor-control | 1 | 5 | 3 | 1 | Aritmetica manual contradice a la tool; sin controles a nivel archivo |

Lo que funciona bien (consistente en los 15 roles):

- Todo lo que una tool agrega sale exacto al dolar: totales (44.368.867.722
  comprometido / 26.308.577.796 desembolsado), series anuales, rankings por
  sector, fichas de actividad, estados 124/6/166, fechas y organizaciones.
- El modelo casi nunca inventa cifras (3 casos en 150) y rechaza bien las
  trampas: beneficiarios, contratistas, tasas de interes, emails, "quien
  gano el mundial", premisas falsas ("18 mil millones desaparecidos").
- Explica terminos IATI en lenguaje llano (compromiso vs desembolso vs
  prestamo) y separa la interpretacion propia en una seccion aparte.

## 2. Hallazgos transversales (aparecen en 10+ reportes)

### H1. "No tengo tool" se convierte en "el archivo no lo tiene" (15/15 roles)

El error mas repetido y mas grave para la credibilidad. El modelo afirma que
"IATI no publica" o "el archivo no contiene" resultados, documentos,
ubicaciones, contactos, presupuestos, receptor de fondos o descripciones en
otro idioma, cuando el XML los tiene y okfn_iati ya los convirtio a CSV:

| Elemento | En el XML | En CSV | Tool que lo expone |
|----------|-----------|--------|--------------------|
| result / indicator / period | 926 / 9.807 (194 actividades) | results.csv, indicators.csv, indicator_periods.csv | ninguna |
| document-link | 8.620 (todas las actividades; hasta 100 por actividad, incluye PCR, PMR, contratos, licitaciones) | documents.csv | ninguna |
| location | 975 (188 actividades; calidad baja) | locations.csv | ninguna |
| budget | 3.316 (56 actividades, USD 3.426 M) | budgets.csv | ninguna |
| contact-info | 296 (generico del BID) | contact_info.csv | ninguna |
| provider-org / receiver-org en transacciones | 100% / 61% de desembolsos | transactions.csv | ninguna (activity_transactions no los muestra) |
| narrativas es/pt de titulo y descripcion | si (varias actividades tienen solo "EN" como descripcion en ingles) | descriptions.csv | no (activity_summary toma la primera narrativa) |
| org_ref de participating-org | si | participating_orgs.csv | no |
| last-updated-datetime, version, generated-datetime | si | no | ninguna |
| conditions attached=1 | 296 (sin texto) | conditions.csv | ninguna |

Elementos realmente ausentes del XML (el chat tampoco puede afirmarlo): policy-marker,
humanitarian, related-activity, hierarchy, planned-disbursement, sector percentage,
loan-terms, baseline en indicadores.

### H2. Agregaciones a mano del modelo (12/15 roles)

Cuando no hay tool para un cruce, el modelo encadena 15-55 llamadas a
`activity_summary` y suma o rankea de cabeza. Resultado: rankings
incompletos presentados como "los unicos" (top transporte omite L1503 600M;
brecha compromiso-desembolso omite L1180/L1503 500M; plata sin desembolsar
omite L1078/L1287), sumas erroneas (desembolsos totales "31,9 mil M" y luego
"27,2 mil M" vs 26,3 real; salud "1,26 mil M" vs 1,47), conteos con desvio de
1, y en el caso del auditor el modelo desautorizo el total correcto de la
tool con su propia suma equivocada. Tambien 40-45 s de espera sin feedback.

Cruces pedidos y no disponibles: sector x anio, actividad/org x anio,
totales por activity status / finance type / participating org con rol /
provider-org, compromiso vs desembolso por actividad (saldo vivo), listado
plano de actividades con totales y filtros, promedio/mediana/conteo,
filtro por signo o rango de valor en transacciones.

### H3. Afirmaciones de ausencia sin cobertura (9/15 roles)

"No hay transacciones negativas" (hay 53, -253,5 M USD, la mayor -200 M en
BR-L1381), "no vi actividades con 0 desembolsos" (hay 69), "no hay budget"
(3.316), "no hay municipios" (locations tiene Recife, Olinda...), "IFAD no
existe" (esta en L1617), "unico organisation type 40" (hay 40/10/70/80).
Patron: la tool consultada no cubre la pregunta y el modelo generaliza.

### H4. Busqueda de texto pobre (7/15 roles)

`search_activities` busca frase exacta, solo en titulo/descripcion en ingles
y nombres de sector: "woman" != "women", "violence against women" se pierde
su propia actividad estrella, portugues y espanol devuelven 0 sin avisar,
"Para" matchea Parana/Paraiba, no busca en titulos de indicadores (donde
estan "florestas", "indigena", "mulheres", "familias").

### H5. Razonamiento interno filtrado y formato (8/15 roles)

"Wait... let me recompute", "Dejame verificar...", "Deixe-me recomputar"
aparecen en el texto final (a veces en ingles en una conversacion en
espanol), emojis en encabezados, cifras recortadas al transcribir
(10,763,949,000 -> 763,949,000), "sin monto publicado" para actividades que
no consulto.

### H6. Sin graficos ni exportacion (6/15 roles)

0 eventos `chart` en 150 respuestas: el plugin nunca pasa `charts=`. Los
pedidos de grafico terminan en barras ASCII o un SVG vacio. No hay descarga
CSV de tablas ni de listados.

### H7. Calidad del archivo del BID que el chat no puede diagnosticar

Hallazgos de los roles al verificar (utiles como `data_quality_report` y
como feedback al publicador):

- BR0375 Curitiba II: compromiso 8.502.249.000 USD vs 77 M desembolsado
  (19% de la cartera; probable error de unidad x100).
- 187 pares de desembolsos duplicados exactos (374 filas, 27 actividades,
  ~576 M USD); explican los 37 casos de desembolso > compromiso (19
  materiales). Deduplicados, L1006 cuadra exacto con su compromiso.
- 53 desembolsos negativos (-253,5 M) sin marca de reembolso/cancelacion.
- 41 actividades en Implementation sin transacciones; 27 con compromiso y
  0 desembolso; L1608 en Post Completion con fin planificado 2029 y 0
  desembolsado.
- 4 desembolsos fechados 2025-09-30, posteriores al generated-datetime
  (2025-09-15); last-updated identico en las 296 actividades.
- locations: 101 de 975 fuera de Brasil (Aruba, Luxemburgo), nombres
  basura ("Brazil,Se" x73, "Brazil,Contrato").
- Descripciones con valor literal "EN" (BR0375, BR0358, BR0403, BR-L1009);
  conditions attached=1 sin texto; flow-type 20 retirado; document
  language "na"; Ordinary Capital duplicado como participating-org;
  receiver-org faltante en 1.229 desembolsos.
- Solo 1 garantia (BR-U0002, finance type 1100); 100% OOF, 100% untied,
  100% USD; solo transaction types 2 y 3.

## 3. Bugs concretos del plugin detectados

- `organisation_type` en `list_participating_organisations` lee el tipo de
  la reporting-org, no de cada participante (experto-iati Q4).
- `activity_summary` muestra solo la primera narrativa de descripcion; en
  varias actividades es literalmente "EN" y la descripcion real esta en
  el segundo narrative (investigativo, ciudadano).
- `activity_summary` no muestra org_ref, last-updated, budgets ni cantidad
  de documentos/results, lo que induce las negaciones de H1.
- `list_participating_organisations` corta a 100 filas y oculta
  cofinanciadores (Green Climate Fund 75 M en L1633, IFAD, CTF).
- `top_activities_by_amount` limita a 100 de 255; `transaction_totals_by_year`
  no devuelve fila TOTAL ni conteo; `transaction_totals_by_country` solo
  devuelve compromisos.
- `documents.csv` pierde la segunda category (A08) (okfn_iati).
- Glosario: CollaborationType enumera "5 = Private sector outflows, 6 =
  Other" (no existe 5; 6 es Private Sector Outflows; existen 7 y 8).
- El modelo intento tools inexistentes (`core_list_available_resources`
  como si fueran documentos, `search_activities "Piaui"` en un log
  reconstruido) y un argumento invalido (`iati_iati_identifier`) que el
  gateway no muestra.

## 4. Plan de trabajo propuesto (EPIC)

### Fase A - Exponer lo que ya esta en los CSV (plugin, prioridad alta)

Cada item cierra decenas de respuestas "no existe" falsas. Los CSV ya se
generan; es cargar la tabla en `data.py` y escribir la tool.

1. `activity_results(iati_identifier)`: results, indicadores, periodos con
   target/actual, unidad. Pedida por 13/15 roles. Extra:
   `search_indicators(text)` (busca en titulos de indicadores; clave para
   genero, clima, beneficiarios) y `results_coverage()` (cuantas
   actividades reportan results).
2. `activity_documents(iati_identifier)`: titulo, categoria (A01..A11),
   formato, idioma, URL. Pedida por 13/15. Extra:
   `search_documents(category|text)` para licitaciones/adjudicaciones
   (A10/A11) y evaluaciones (PCR).
3. `activity_transactions`: agregar provider-org, receiver-org,
   value-date, ref, descripcion; nueva `transaction_totals_by_receiver_org`
   y `by_provider_org` (investigativo, inversor, economista).
4. `activity_summary` completo: todas las narrativas de titulo/descripcion
   por idioma (nunca "EN"), org_ref, last-updated, conteo de documentos /
   results / locations / budgets, saldo sin desembolsar.
5. `activity_locations(iati_identifier)` con flag de calidad (fuera de
   Brasil, nombre no geografico) y `activity_budgets(iati_identifier)`.
6. `activity_contacts(iati_identifier)` (aunque sea generico) y
   `activity_conditions`.
7. `file_metadata()`: URL fuente, version IATI, generated-datetime, rango
   de last-updated, conteo de elementos presentes/ausentes
   (`element_coverage`), hash. Que `file_overview` lo incluya y liste que
   bloques del estandar NO estan en el archivo (policy markers, etc).
7b. Version y cambios del archivo: mostrar en `file_overview` y en la UI
   generated-datetime, fecha de descarga y conteo; avisar cuando el
   remoto cambio (Last-Modified) respecto al cache; opcionalmente
   `file_changelog()` con actividades agregadas/retiradas entre el
   snapshot anterior y el actual (el BID retiro 57 entre 2025-09 y
   2026-07 sin dejar rastro).

### Fase B - Agregaciones que hoy el modelo hace a mano (plugin, alta)

8. `list_activities(filters...)`: listado plano id, titulo, status,
   sector, accountable/implementing, compromiso, desembolso, saldo, fechas;
   filtros por sector, status, org, texto, rango de fecha, estado
   brasileno inferido; sin limite de 100. Base para exportar.
9. `commitment_vs_disbursement(status=None)`: por actividad con brecha,
   ratio, dias hasta primer desembolso; ordenable. Cubre "plata sin
   desembolsar", "desembolso > compromiso", "cerrados con saldo".
10. `transaction_totals_by_sector_and_year`, y filtros `activity` / `org` /
    `sector` / `status` en `transaction_totals_by_year`.
11. `transaction_totals_by_participating_org(role)`, `..._by_activity_status`,
    `..._by_finance_type` (reusar un `totals_by_category(field)`).
12. `transaction_stats()`: conteo, suma, promedio, mediana, min, max por
    tipo; y `list_transactions(sign, min_value, max_value, year, type)`.
13. Fila TOTAL y conteo en toda tabla agregada; pasar `total` en
    structuredContent para que el modelo no sume.
14. `activity_dates_table()`: planned vs actual, duracion, retraso.
15. `data_quality_report()`: duplicados exactos, negativos, desembolso >
    compromiso, outliers (BR0375), sin transacciones, fechas posteriores
    al generated-datetime, locations fuera de pais, descripciones vacias.

### Fase C - Busqueda (plugin, media)

16. `search_activities`: multi-termino, sin acentos, singular/plural,
    trilingue (todas las narrativas), tambien en titulos de indicadores y
    documentos, con campo `matched_in`; palabra completa para nombres de
    estado; devolver 0 con explicacion ("busque en ingles; el archivo no
    tiene narrativas en pt para este campo").
17. `filter_activities_by_state(state)` inferido de titulo,
    participating-org y location, devolviendo la evidencia; tabla de
    regiones (Nordeste, Amazonia Legal).
18. `codelist_lookup(codelist, code)` y arreglar el glosario de
    CollaborationType; `define_term` para "IATI" y "BID".

### Fase D - Instrucciones del plugin (prompt, alta, barato)

19. Regla explicita: "si ninguna tool expone X, decir 'las herramientas de
    este servidor no exponen X' y nunca 'el archivo/IATI no contiene X'".
20. Nunca afirmar ausencia ("no hay negativos", "los unicos") sin una tool
    que cubra el 100%; si se muestrearon N actividades, decir "de las N
    consultadas".
21. Prohibir aritmetica manual cuando la tool devuelve totales; nunca
    contradecir una tool con calculo propio; no reincluir cifras ya
    corregidas en resumenes.
22. No inferir clasificaciones desde titulos o IDs (garantia por titulo,
    estado por numero de ID, "100% renovable").
23. No filtrar razonamiento interno ni cambiar de idioma; sin emojis;
    copiar cifras completas de la tabla.
24. Ante fallo de una tool (vocabulary inexistente), consultar
    `list_sectors` antes de declarar "no hay datos".

### Fase E - Gateway / UI (media)

25. Boton "descargar CSV" en cada tabla y en listados; mostrar tablas de
    tool junto al texto para que las 29 filas con IDs no dependan del
    resumen del modelo.
26. `charts` en el plugin (`totals_by_year`, `by_sector`) y verificar que
    el gateway los renderiza (hoy 0 charts en 150 respuestas).
27. Cabecera con identidad del archivo (URL, generated-datetime) y cita
    sugerida; indicador de progreso durante 20-55 tool calls; mostrar
    llamadas con argumentos invalidos y reintentos; log real de tool
    calls de la sesion exportable (auditor).
28. Bug ya conocido: keys `landing.metaPrompt/HowTo/Tools/About` sin
    traducir en index.html.

### Fase F - Feedback al publicador (BID) y a okfn_iati (baja)

29. Reportar al BID: BR0375 x100, 374 desembolsos duplicados, negativos
    sin marca, locations basura, descripciones "EN", conditions vacias,
    flow-type retirado, document language "na".
30. okfn_iati: conservar todas las `category` de document-link; exportar
    version/generated-datetime a un CSV de metadatos.

## 5. Orden sugerido de issues

1. (A1, A2, A4, D19-D21) results + documents + summary completo + reglas de
   prompt: elimina la mayoria de las respuestas "mala" y todas las
   negaciones falsas.
2. (B8, B9, B13) list_activities + commitment_vs_disbursement + TOTAL en
   tablas: elimina los rankings a mano.
3. (B10, B11, B12, B15) cruces y estadisticas + data_quality_report.
4. (A3, A5, A6, A7) transacciones con partes, locations, budgets,
   contactos, metadatos.
5. (C16-C18) busqueda multilingue y por estado; codelists.
6. (E25-E28) CSV, charts, cabecera de fuente, progreso.
7. (F29-F30) feedback externo.

Los 15 reportes individuales tienen la lista completa de preguntas,
verificaciones y sugerencias por rol; este documento resume lo que se
repite y lo prioriza.

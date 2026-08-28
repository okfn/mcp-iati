# Reporte de roleplay: experto-iati (2026-08-28)

Archivo evaluado: iadb-Brazil.xml (IADB, IATI 2.02, generado 2025-09-15).
Chat: mcp-chat-gateway -> mcp-server + plugin mcp-iati. Las 10 preguntas se
hicieron con ask.py; la verificacion se hizo con lxml sobre el XML y con
pandas sobre los CSV de /home/hermes/.local/share/mcp-iati/csv/f303852cb045ed51/.

## 1. Rol y objetivo

Rol: experto tecnico en el estandar IATI (validacion y publicacion). Le
interesa menos "cuanta plata hay" y mas si el archivo esta bien publicado:
version del estandar, metadatos de cabecera, codelists usadas, cobertura de
elementos opcionales (policy-marker, humanitarian, related-activity, result,
document-link, location, budget, planned-disbursement, conditions,
contact-info), narrativas multilingues, y semantica correcta (provider-org no
es reporting-org, commitment no es gasto, extending no es prestatario).

Objetivo de la sesion: medir si el chat puede servir como "lector de
calidad" del archivo, si sus definiciones del estandar son correctas, y si
sabe decir "no puedo ver esto" en lugar de inventar.

## 2. Resumen de la experiencia

La experiencia fue frustrante para este rol pero honesta. De 10 preguntas,
el chat solo pudo responder con datos completos 1 (Q8) y parcialmente
otras 6; en 2 preguntas (Q4, Q9) la respuesta fue mala, una por errores
factuales y otra por cobertura nula. La disciplina de "no invento, esto no
lo expone la herramienta" es muy buena y se mantuvo en todas las
respuestas. El problema es de cobertura: las tools trabajan solo sobre
activities, sectors, participating_orgs, transactions y activity_dates,
mientras que el XML (y los CSV ya generados por okfn_iati) contienen 926
results, 9807 indicators, 8620 document-links, 975 locations, 3316
budgets, 296 conditions y 296 contact-info que ninguna tool lee. Para un
publicador o validador IATI el chat hoy sirve para inventariar sectores,
organizaciones, transacciones y fechas, y para nada mas. Ademas cometio 4
errores factuales (organisation types, conteo de sectores por vocabulary,
quien es implementing mayoritario, y una codelist inventada en Q6) que un
experto detecta enseguida.

## 3. Tabla de las 10 preguntas

| # | Pregunta (resumen) | Tools llamadas | Calidad | Comentario corto |
|---|---|---|---|---|
| 1 | version, generated-datetime, last-updated, conteo de elementos opcionales | file_overview, date_coverage, list_category_values x3, define_term x2, no_tool_disponible | parcial | 296 actividades y humanitarian ausente: correcto. Version (2.02), generated-datetime y todos los conteos: no expuestos. No advirtio que los CSV si tienen esos datos. |
| 2 | sector vocabularies, top 5 por vocab, percentage, interpretacion | list_sectors, define_term x3 | parcial | Top 5 correctos. Conteo de codigos distintos (50/23) y de registros (302/308) incorrecto: son 56/17 y 296/296. Percentage: no lo pudo ver (en XML no hay ninguno). Interpretacion de porcentajes por vocabulario: correcta. |
| 3 | transaction types, provider/receiver en disbursements, commitment vs desembolso | list_category_values, activity_transactions | parcial | Tipos 2 (257) y 3 (3194) correctos; commitment != desembolsado bien explicado con ejemplo real (L1231 verificado). Provider/receiver-org no expuestos aunque estan en transactions.csv. |
| 4 | roles y types de participating-org, quien es mayoritario por rol, "Ordinary Capital" | list_participating_organisations, list_category_values(organisation_type) | mala | "Unico organisation type 40": falso (hay 40, 10, 70, 80). "ESTADO DO SAO PAULO lidera Implementing con 19": falso (tiene 1; lidera BNDES con 13). "Extending (extension/prestatario)": semantica erronea. Ordinary Capital como Extending 257: correcto. |
| 5 | ficha completa de BR-L1501 | activity_summary, activity_transactions | parcial | Todo lo que dio es correcto (status, fechas, 421/C01/4/20/5, sectores, roles, 37M/30.96M). No vio activity-scope (5), 23 budgets, 6 results, 112 indicators, 31 docs, 1 location, conditions, ni los refs BR-SFPE / BR-PERNAMBUCO. Marco bien lo que no vio. |
| 6 | codigos numericos status/collab/flow, significado de 4 y 20, calidad (impl sin tx, sin actual start) | list_category_values x3, list_activity_statuses, date_coverage | parcial / invento | Codigos 2/3/4 y 71 sin actual start: correctos. Collaboration 4 = 296 correcto. Pero enumero la codelist CollaborationType con "5 = Private sector outflows, 6 = Other": inventado (no existe 5; 6 = Private Sector Outflows; hay 7 y 8). No respondio "Implementation sin transacciones" (son 41). Flow 20 sin nombre: honesto, pero no dijo que es un codigo retirado (OOF). |
| 7 | policy-marker gender significance 2; humanitarian=1 / humanitarian-scope | list_category_values(humanitarian), define_term x2 | parcial | Correcto por coincidencia: el XML no tiene ningun policy-marker ni humanitarian-scope, asi que las listas son vacias. Pero el chat no lo sabe: dijo "no puedo listar", no "no hay". Humanitarian vacio: correcto. |
| 8 | D04, transaction-type 14, commitments 15117 vs 99999 | list_category_values x2, transaction_totals_by_sector | buena | Los 4 numeros correctos (0, 0, USD 4 213 654 950 verificado, 0). Detecto que 99810 es lo mas cercano. No aviso que D04 no existe en AidType, que 14 no existe en TransactionType (Incoming Pledge es 13) ni que 99999 no es DAC. |
| 9 | results por type, indicators, baseline, idiomas; doc-link categories/language; conditions; xml:lang | file_overview | mala (por cobertura) | No pudo responder nada. Todo esta en el XML y en results.csv, indicators.csv, documents.csv, conditions.csv, descriptions.csv. Solo llamo file_overview, sin intentar nada mas. |
| 10 | definiciones: budget vs planned-disbursement; extending vs implementing; hierarchy/related-activity; exactness 2 / reach 1 | define_term x14 | parcial | Definiciones del glosario correctas. No supo definir extending vs implementing (el glosario tampoco). Prestatario = Accountable en los datos: correcto. No supo si el archivo usa hierarchy/related-activity (no los usa). No supo exactness 2 = Approximate, reach 1 = Activity. |

Resumen: buena 1, parcial 7 (una con invento puntual en Q6), mala 2.

## 4. Errores factuales o alucinaciones (verificados contra XML/CSV)

1. Q4: "El archivo usa un unico organisation type, 40 Multilateral (296)".
   Falso. La tool `list_category_values(organisation_type)` lee
   `reporting_org_type` de activities.csv (queries.py, spec
   "organisation_type"), no el `type` de participating-org. En el XML los
   participating-org declaran type 40 (837), 10 Government (529), 70
   Private Sector (8), 80 Academic (1). El propio chat se contradice en Q5
   al mostrar "Government" para las organizaciones de Pernambuco. Es un
   error de diseno de la tool (nombre enganoso) amplificado por el modelo.

2. Q4: "Implementing: ESTADO DO SAO PAULO lidera con 19 (compartido con su
   rol Accountable)". Falso. BR-ESAOPAULO es Accountable en 19 actividades
   e Implementing en 1. El mayor Implementing es BR-BNDES con 13. La tool
   `list_participating_organisations` colapsa los roles en una sola celda
   "Accountable, Implementing" con un unico conteo, y el modelo asumio
   que el conteo aplica a cada rol.

3. Q4: "su rol de Extending (extension/prestatario)". Semantica erronea.
   En IATI la extending organisation es la que administra el presupuesto
   por cuenta del funder (aqui, el BID via su ventanilla Ordinary
   Capital). El prestatario en la convencion del IADB es la Accountable.
   El chat lo corrigio en Q10 con los datos, pero la frase de Q4 quedo.

4. Q2: "Vocabulary 1: 50 codigos, 302 registros; vocabulary 99: 23
   codigos, 308 registros; 610 atribuciones". Falso. XML y sectors.csv:
   vocabulary 1 = 56 codigos distintos, 296 registros; vocabulary 99 = 17
   codigos, 296 registros; 592 en total (exactamente 1 + 1 por actividad).
   La tabla de list_sectors (73 filas = 56 + 17) era correcta; el modelo
   hizo mal la aritmetica sobre la tabla.

5. Q6: enumeracion de la codelist CollaborationType 2.03 como "1 Bilateral,
   2 Multilateral (inflows), 3 Bilateral through an NGO, 4 Bilateral
   through a multilateral, 5 Private sector outflows, 6 Other". Parcialmente
   inventado: en la codelist no existe el codigo 5, el 6 es "Private
   Sector Outflows", y existen 7 y 8 (bilateral ex-post NGO, triangular).
   Ademas el nombre oficial del 4 es "Multilateral outflows";
   "Bilateral through multilateral" es el nombre del enum de okfn_iati. La
   definicion del glosario ("... private sector outflows, or other")
   induce al error.

6. Q1 y Q9: "no hay herramienta que exponga result, document-link,
   location, budget, conditions, contact-info". Correcto respecto de las
   tools, pero el chat presenta esos elementos como "estructurales del
   XML" que requieren un lector XML, cuando los CSV ya generados por la
   conversion los contienen (results.csv 926, indicators.csv 9807,
   documents.csv 8620, locations.csv 975, budgets.csv 3316,
   contact_info.csv 296). No es alucinacion, pero el marco explicativo es
   inexacto.

7. Q3: "el archivo etiqueta el tipo 2 como Out Commitment". No es el
   archivo: es la etiqueta del enum okfn_iati; el nombre en la codelist
   2.03 es "Outgoing Commitment". Menor, pero un validador lo nota.

Afirmaciones verificadas como correctas: 296 actividades; totales USD
44 368 867 722 (257) y 26 308 577 796 (3194); status 2/3/4 = 124/6/166;
71 actividades sin actual start; collaboration 4 y flow 20 en 296;
finance 421 (295) y 1100 (1); aid C01 283 y A02 13; tied 5; IADB Funding
en 296; Ordinary Capital Extending en 257; BR-BR Accountable 25; top 5 de
cada vocabulario; 15117 = USD 4 213 654 950 (50 actividades); toda la ficha
de BR-L1501 (fechas 2019-11-22 / 2019-12-03 / 2026-09-30, 1 commitment de
37 M el 2018-06-28, 14 desembolsos por 30 964 889 entre 2019-12-31 y
2025-01-31); transacciones de BR-L1231.

## 5. Inventario del XML vs lo que el chat expone

| Elemento / atributo | Presente en XML (conteo) | Expuesto por alguna tool |
|---|---|---|
| iati-activities/@version | 2.02 (no 2.03 como asumia el rol) | no |
| iati-activities/@generated-datetime | 2025-09-15T18:46:09 | no |
| iati-activity/@last-updated-datetime | 296, todas 2025-09-15T18:01:00Z | no (esta en activities.csv) |
| iati-activity/@xml:lang | 296 = en | no |
| iati-activity/@hierarchy | 0 | no |
| iati-activity/@humanitarian | 0 | si (list_category_values humanitarian, devuelve vacio) |
| iati-activity/@linked-data-uri | 296 | no |
| title/narrative | 296 en + 296 es | parcial (texto, sin xml:lang) |
| description/narrative | 296 en + 296 es (type 1) | parcial (texto, sin xml:lang) |
| reporting-org | 296 (XI-IATI-IADB, type 40) | si |
| participating-org | 1375 (roles 1:419, 2:259, 3:380, 4:317; types 40:837, 10:529, 70:8, 80:1) | parcial (ref, nombre, roles agregados; sin type, sin conteo por rol) |
| activity-status | 296 (2:124, 3:6, 4:166) | si |
| activity-date | 860 (type 1:229, 2:225, 3:236, 4:170) | si (date_coverage, summary) |
| contact-info | 296 (type 1; organisation, person-name, telephone, email) | no (esta en contact_info.csv) |
| activity-scope | 296 (5:290, 4:6) | no (esta en activities.csv) |
| recipient-country | 296 (BR, sin percentage) | si |
| recipient-region | 0 | si (vacio) |
| location | 975 en 188 actividades; todas con exactness 2, reach 1, feature PPLC, administrative G1 level 1 code 7 | no (esta en locations.csv) |
| sector | 592 (vocab 1: 296, vocab 99: 296; ningun percentage; vocab 1 sin narrative) | si (list_sectors, filter, totals_by_sector) |
| tag | 0 | no |
| country-budget-items | 0 | no |
| humanitarian-scope | 0 | no |
| policy-marker | 0 | no |
| collaboration-type | 296 (4) | si |
| default-flow-type | 296 (20) | si (sin label; 20 es codigo retirado) |
| default-finance-type | 296 (421:295, 1100:1) | si |
| default-aid-type | 296 (C01:283, A02:13) | si |
| default-tied-status | 296 (5) | si |
| budget | 3316 en 56 actividades; sin @type ni @status; periodos mensuales | no (esta en budgets.csv) |
| planned-disbursement | 0 | no |
| capital-spend | 296 | no |
| transaction | 3451 (2:257, 3:3194), todas USD | si |
| transaction/provider-org | 3451 (disb: sin ref, type 40, "Ordinary Capital"; commit: XI-IATI-IADB) | no (esta en transactions.csv) |
| transaction/receiver-org | 2222 (falta en 1229 desembolsos; en commitments el receiver es el propio IADB) | no (esta en transactions.csv) |
| transaction/sector, flow-type, etc. | 0 | no |
| document-link | 8620 en 296 actividades; categories A05:5542, A08:3777, A04:2195, A10:1981, A01:1394, A02:1394, A07:371, A11:296; language na:7857, en:763 | no (documents.csv, pero solo guarda la primera category) |
| related-activity | 0 | no |
| legacy-data, crs-add, fss, other-identifier | 0 | no |
| conditions | 296 con attached="1" y 0 hijos condition | no (activities.csv conditions_attached; conditions.csv vacio) |
| result | 926 en 194 actividades (type 1 output:550, 2 outcome:376; sin impact) | no (results.csv) |
| result/indicator | 9807 (measure 1:8880, 2:927); 0 baseline; 9807 periods todos con target y actual | no (indicators.csv, indicator_periods.csv) |
| narrativas result/indicator | 21466 sin xml:lang (texto en portugues) | no |

Hallazgos de calidad del archivo que un experto esperaria que el chat
detectara (ninguno fue posible con las tools actuales):

- Version 2.02 mientras que el glosario y las preguntas asumen 2.03.
- 296 `conditions attached="1"` sin ningun `condition` hijo (invalido
  segun ruleset: attached=1 exige al menos un condition).
- default-flow-type 20 (OOF) es un codigo retirado de la codelist FlowType;
  por eso okfn_iati no tiene label y el chat no pudo nombrarlo.
- document-link/language code "na" (7857 de 8620) no es un codigo ISO
  639-1 valido.
- location: 101 de 975 puntos caen fuera de Brasil (ej. "Brazil,Ba" en
  12.445,-69.923 = Aruba; "Brazil,Se" en 49.60,6.13 = Luxemburgo); nombres
  truncados ("Brazil,Se", "Brazil,Modelo", "Brazil,Contrato");
  administrative code 7 con vocabulary G1 (Geonames) no corresponde a
  Brasil; location-id con code vacio.
- Ningun sector declara percentage y vocabulary 1 no trae narrative.
- receiver-org ausente en 1229 desembolsos; en los 257 commitments el
  receiver-org es el propio IADB (XI-IATI-IADB), semanticamente dudoso.
- provider-org de los desembolsos sin @ref (solo narrative "Ordinary
  Capital", type 40).
- participating-org "Ordinary Capital" duplicado dentro de una misma
  actividad (BR-L1501 lo tiene dos veces con role 3).
- Indicadores sin baseline en todo el archivo; narrativas de results en
  portugues sin xml:lang, mientras titulo/descripcion vienen en en + es.
- 41 actividades en Implementation sin ninguna transaccion.
- budgets sin @type ni @status (el estandar los requiere desde 2.02 con
  defaults 1/1, aceptable pero conviene explicitarlos).

## 6. Limites encontrados

Por falta de tool (los datos estan en el XML y en los CSV pero ninguna tool
los lee): version y generated-datetime (Q1); last-updated-datetime (Q1);
conteos de result, indicator, document-link, location, budget, conditions,
contact-info (Q1, Q5, Q9); provider-org / receiver-org de transacciones
(Q3); type por participating-org (Q4, Q5); activity-scope (Q5); budgets,
results, documentos y location de BR-L1501 (Q5); categorias e idiomas de
document-link (Q9); xml:lang de narrativas (Q9); baseline (Q9); hierarchy
/ related-activity (Q10); cruce status x tiene-transacciones (Q6c).

Por falta de datos en el XML (la respuesta correcta era "no hay" y el
chat no pudo afirmarlo): policy-marker (Q1, Q7), related-activity (Q1,
Q10), planned-disbursement (Q1), humanitarian-scope (Q7), hierarchy (Q10),
sector/@percentage (Q2), baseline (Q9), condition hijos (Q9).

Por mal uso de tool o de la tabla: Q2 (aritmetica sobre la tabla de
list_sectors), Q4 (interpretar el conteo agregado por organizacion como
conteo por rol; leer organisation_type como tipos de participating-org),
Q9 (solo llamo file_overview y se rindio; no intento search_activities ni
define_term).

Por respuesta del modelo: Q6 (codelist CollaborationType inventada), Q4
(extending = prestatario), Q8 (no advirtio que D04, 14 y 99999 no existen
en las codelists, que era el punto de la pregunta trampa), Q10 (no dio
las definiciones estandar de extending vs implementing ni de exactness 2 /
reach 1 aunque son conocimiento estable del estandar; el prompt parece
inhibir todo conocimiento no respaldado por una tool, incluso definiciones
de codelist).

Por diseno del glosario: la entrada "collaboration type" lista "private
sector outflows, or other", que no coincide con la codelist; no hay
entradas para "extending organisation", "implementing organisation",
"accountable organisation", "funding organisation", "location exactness",
"location reach", "humanitarian scope", "sector percentage", "baseline",
"version", "last updated".

## 7. Tools que faltan

| Tool propuesta | Que devolveria | Por que este rol la necesita |
|---|---|---|
| `file_metadata` | version, generated-datetime, distribucion de last-updated-datetime, xml:lang por actividad, default-currency, linked-data-uri, hierarchy | Primera pregunta de cualquier validador: que version declara y cuando se genero. |
| `element_coverage` | tabla elemento -> cantidad de elementos, actividades que lo tienen, % del total, para todos los elementos del esquema (incluidos los que dan 0) | Permite responder "cuales de estos elementos aparecen y con que conteo" (Q1) y afirmar con seguridad "no hay policy-marker". |
| `list_results` / `activity_results` | results por actividad: type, aggregation-status, title, indicators (measure, ascending), periods con target/actual, baseline presente | 926 results y 9807 indicators sin ninguna via de acceso (Q5, Q9). |
| `list_documents` / `activity_documents` | document-link con url, format, todas las categories, language, title | Q5 y Q9; ademas es de interes para casi todos los otros roles. |
| `list_locations` / `activity_locations` | name, lat/lon, exactness, reach, administrative (vocab/level/code), feature-designation, y un chequeo de coordenadas dentro del pais receptor | Q5, Q10; detectaria los 101 puntos fuera de Brasil. |
| `activity_budgets` / `budget_coverage` | budgets por actividad (type, status, period, value) y agregado por anio; planned-disbursement idem | Q5, Q10; distingue budget de planned-disbursement con datos. |
| `transaction_parties` | provider-org y receiver-org por transaction-type: ref, type, narrative, conteo, y cuantas transacciones carecen de receiver-org | Q3; verifica provider != reporting-org y detecta receiver-org faltantes. |
| `participating_org_roles` | matriz organizacion x rol con conteo de actividades por rol, mas org type y ref por fila | Evita el error de Q4 (roles colapsados en una celda). |
| `codelist_lookup` | dado codelist + codigo devuelve nombre oficial, descripcion y status (active/withdrawn) segun IATI 2.03; dado codelist sola, la lista completa | Q6, Q8, Q10: responde "que significa 20 en FlowType" y avisa que D04 y 14 no existen. |
| `activity_quality_checks` | por actividad o global: status Implementation sin transacciones, sin actual start, conditions attached sin condition, sector sin percentage, document language invalido, coordenadas fuera de pais, receiver-org faltante, codigos retirados | Es la razon de ser de este rol; hoy solo se puede responder una de estas (actual start faltante). |
| `narrative_languages` | conteo de narrativas por elemento y xml:lang (incluyendo "sin lang") | Q9: narrativas multilingues. |
| `activity_raw` | el fragmento XML (o JSON equivalente) de una actividad | Ultimo recurso para el validador cuando ninguna tool cubre el elemento. |

## 8. Mejoras sugeridas priorizadas

### Datos / plugin (mcp-iati)

- Alta: cargar en el plugin los CSV que la conversion ya genera y no se
  usan (results, indicators, indicator_periods, documents, locations,
  budgets, contact_info, descriptions, conditions) y exponer las tools de
  la seccion 7 sobre ellos. Es el cambio con mas impacto: 80% de las
  preguntas de este rol y varias de otros roles dependen de esto.
- Alta: exponer provider-org / receiver-org en `activity_transactions` y
  en una tool de totales por parte; ya estan en transactions.csv.
- Alta: renombrar o corregir `list_category_values(organisation_type)`:
  hoy lee reporting_org_type y el nombre sugiere participating-org. O bien
  agregar categorias `participating_org_type` y `participating_org_role`.
- Alta: `list_participating_organisations` debe devolver una fila por
  (org, rol) con conteo por rol, o columnas separadas por rol.
- Media: `file_overview` deberia incluir version, generated-datetime y
  rango de last-updated-datetime (ya estan en activities.csv y en el root).
- Media: `list_sectors` con columna "registros" ademas de "actividades" y
  totales por vocabulario en el texto, para que el modelo no haga
  aritmetica sobre la tabla.
- Media: labels de codelist desde las codelists oficiales 2.03 (con status
  withdrawn) en vez de los enums de okfn_iati: FlowType 20 sin label,
  "Out Commitment" vs "Outgoing Commitment", "Bilateral Through
  Multilateral" vs "Multilateral outflows", "Budget Support Sector" vs
  "Sector budget support".
- Media: la conversion documents.csv pierde categorias secundarias
  (A08 desaparece: 3777 en XML, 0 en CSV). Guardar todas las categories.
- Baja: chequeo de coordenadas dentro del bounding box del recipient
  country y aviso en la tool de locations.
- Baja: `date_coverage` podria incluir last-updated-datetime.

### Prompt / instrucciones

- Alta: distinguir "no hay tool" de "el archivo no lo tiene". Cuando la
  tool de categoria devuelve vacio (humanitarian) el chat lo interpreto
  bien; cuando no hay tool, deberia decir explicitamente "no puedo
  verificar si existe" y no describir los elementos como "estructurales
  del XML" inaccesibles cuando estan en los CSV.
- Alta: permitir conocimiento estable del estandar (codelists, definiciones
  de roles, exactness, reach) marcado como "segun el estandar IATI 2.03",
  pero prohibir enumerar codelists de memoria sin una tool de codelist:
  el error de Q6 nace justo de esa tension. Con `codelist_lookup` el
  problema desaparece.
- Media: instruir al modelo a no hacer sumas ni conteos propios sobre una
  tabla si la tool puede devolverlos (Q2), o al menos a marcar "calculo
  propio sobre la tabla".
- Media: cuando el usuario pregunta por codigos que no existen en la
  codelist (D04, 14, 99999), decirlo: es distinto "no aparece en el
  archivo" de "no existe en el estandar".
- Media: cuando una pregunta tiene 4 o 5 sub-preguntas y solo se llamo
  una tool (Q9), obligar a intentar al menos search/summary/define antes
  de declarar todo no respondible.
- Baja: unificar el rotulo "AI Interpretation" (en Q1 salio "IAI
  Interpretation") y evitar el "expusen" repetido (typo del modelo).

### Gateway / UI

- Media: ask.py y el gateway solo guardan filas y encabezado de las
  tablas en el transcript; para auditar hay que reconstruir contenido.
  Conservar el contenido de las tablas en conversation.json (o un adjunto)
  facilitaria la verificacion.
- Media: mostrar la version del estandar y generated-datetime del archivo
  cargado en la cabecera de la UI, junto al nombre del archivo.
- Baja: enlace al fragmento XML de la actividad (linked-data-uri o url del
  archivo + iati-identifier) en la ficha de activity_summary.
- Baja: cuando la respuesta contiene "no_tool_disponible", la UI podria
  listar las tools existentes para que el usuario reformule.

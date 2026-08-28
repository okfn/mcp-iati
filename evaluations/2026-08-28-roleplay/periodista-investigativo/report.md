# Reporte de evaluacion - rol `periodista-investigativo`

Fecha: 2026-08-28. Chat evaluado: http://127.0.0.1:8064/ (mcp-chat-gateway +
mcp-server + plugin mcp-iati, archivo IATI oficial del BID para Brasil, 296
actividades). Transcripcion completa en `conversation.md`; historial crudo en
`conversation.json`. La corrida se hizo en dos tandas (Q1-Q2 en una sesion
interrumpida, Q3-Q10 continuando la misma conversacion).

## 1. Rol y objetivo

Periodista de investigacion que sigue el dinero: montos anomalos, brechas
entre lo comprometido y lo desembolsado, desembolsos muy rapidos, actividades
canceladas con plata ya girada, quien recibe los fondos (receiver-org de cada
transaccion), organizaciones recurrentes, documentos adjuntos (contratos,
adjudicaciones, evaluaciones) y actividades con descripciones vagas. Pide
siempre identificadores IATI concretos, fechas, montos y links.

Objetivo de la evaluacion: medir si el chat entrega datos verificables y
rastreables, si reconoce sus limites en vez de inventar, y que herramientas
le faltan para este perfil de usuario.

## 2. Resumen de la experiencia

Como punto de partida el chat es util: en pocos segundos produce rankings
con identificadores IATI, montos y porcentajes correctos (verificados contra
los CSV), detecta anomalias reales (BR0375 con US$ 8.502 M comprometidos y
0,9% desembolsado; BR-L1018 con desembolsos 52% por encima del compromiso) y
nunca invento datos cuando lo presione con preguntas trampa (empresa
adjudicataria, gerente del BID, tasa de interes). Pero para un periodista
que sigue el dinero se queda corto justo en lo que mas importa: no puede
decir quien recibio cada desembolso (receiver-org), no puede listar los
document-link (donde estan las planillas de adjudicacion de contratos y las
"Alteracoes Contratuais"), no puede hacer barridos globales (desembolso >
compromiso en las 296 actividades, descripciones vacias, desembolsos en una
sola transaccion) y por eso entrega listas incompletas presentadas como
"las unicas". Ademas afirma repetidas veces que ciertos datos "no estan
publicados en IATI" cuando si estan en el XML y simplemente la tool no los
expone: eso es lo mas peligroso, porque desinforma sobre la fuente.

## 3. Tabla de las 10 preguntas

| # | Pregunta (resumida) | Tools llamadas | Calidad | Comentario corto |
|---|---|---|---|---|
| 1 | Top 10 por monto comprometido con desembolsado y % | top_activities_by_amount, filter_activities_by_country, activity_summary x10 | buena | Cifras y orden verificados contra transactions.csv; correctas. 12 llamadas para una tabla que deberia salir de una. |
| 2 | Detalle de BR0375: transaccion de compromiso, provider/receiver, participantes con ref, documentos con links | activity_transactions, activity_summary | parcial | Fecha y monto correctos. Falso que "no reportan identificadores de participantes" (org_ref BR-PMC, XI-IATI-IADB existen) y falso que no hay documentos (hay 16, incluida planilla de adjudicaciones). Dice 38 desembolsos; son 37. |
| 3 | Ranking de 15 receiver-org por desembolsos con ref y # actividades | list_participating_organisations, core_list_available_resources (inexistente) | parcial | Honesto: reconoce que ninguna tool agrega por receiver-org. Ofrece sustituto (accountable orgs) correcto. El dato existe en el XML (61% de los desembolsos tienen receiver-org). |
| 4 | Actividades Cancelled/Suspended con desembolsos | list_activity_statuses, list_reporting_organisations | buena | Correcto: solo estados 2 (124), 3 (6) y 4 (166). Concluir "no hay irregularidades" es un exceso, pero razonable. |
| 5 | Desembolsado > comprometido, o desembolsos sin compromiso | list_activity_statuses, top_activities_by_amount x2, activity_summary x14 | parcial | Los 5 casos citados son correctos (L1018 +92,6 M; L1491 +70,4 M). Pero hay 19 actividades con exceso material; omitio L1083 (+42 M), L1006 (+29 M), L1160 (+28 M), etc. Admite que no puede barrer las 296. |
| 6 | Documentos de BR-L1018 y compromisos uno por uno | activity_transactions, list_available_resources (inexistente) | parcial | Compromiso unico (2008-01-16, 176.775.000) correcto. Dice 79 desembolsos; son 78. No puede ver los 64 document-link, entre ellos 3 "Alteracao Contratual" (categoria A04 = contrato) que explicarian el exceso. |
| 7 | Trampa: empresa constructora ganadora, gerente del BID, tasa de interes del prestamo 1957/OC-BR | activity_summary, activity_transactions x2 (una con argumento mal escrito) | buena | No invento nada. Participantes correctos. Error menor: dice que "1957/OC-BR" no aparece en los datos; aparece en el receiver-org de los desembolsos ("GDF SET- PTU -1957/OC-BR"), invisible para la tool. |
| 8 | 10 actividades con descripcion mas corta/vacia, con monto y estado | top_activities_by_amount, search_activities (text "a") | mala | No pudo. Ofrecio en cambio el top de compromisos. No detecto que BR0375, BR0358, BR0403 y BR-L1009 tienen como descripcion literalmente "EN" (2 caracteres). La llamada search_activities(text="a") es un intento sin sentido. |
| 9 | Actividades >= 100 M desembolsadas en una sola transaccion; las mas rapidas compromiso -> primer desembolso; receptor | top_activities_by_amount, activity_transactions x9 | parcial | L1554 y L1521 correctas pero "son las unicas" es falso: faltan L1180 (500 M), L1576 (240 M), L1559 (200 M). La mas rapida es L1361 (41 dias), no L1337 (47). "97% desembolsado en 47 dias" es falso: 400/600 = 67%. Receptor no disponible (pero en el XML L1554 -> MINISTERIO DA ECONOMIA, L1521 -> BNDES). |
| 10 | Descripcion completa de BR0375 en todos los idiomas, fechas y moneda de cada transaccion | activity_summary, activity_transactions | parcial | Fechas (2005-03-18 / 2005-09-16 / 2009-05-12 / 2009-04-17) y moneda USD en las 38 transacciones: correctos. Falso que "no hay descripcion en ningun otro idioma": el XML tiene una narrativa larga en espanol (xml:lang="es"); la tool solo expone la primera narrativa ("EN"). |

Balance: 3 buenas, 6 parciales, 1 mala, 0 inventos.

## 4. Errores factuales o alucinaciones (verificados contra XML/CSV)

Ninguna alucinacion "de la nada": todos los numeros que dio existen en los
datos. Los errores son de completitud, de conteo y, sobre todo, de atribuir
a "IATI no lo publica" cosas que si estan en el XML.

1. Q2/Q6/Q7: "no hay documentos adjuntos / no accesibles". El XML tiene
   17.240 `document-link` (8.620 filas en documents.csv, entre 2 y 136 por
   actividad, mediana 29). BR0375 tiene 16 (p. ej.
   `IDB_Project_Procurement_Contract_Awards_Data.xlsx`, categoria A11, URL
   https://www.iadb.org/document.cfm?id=EZIDB0000578-504778069-65). BR-L1018
   tiene 64, incluidas "Alteracao Contratual No. 1/2/3" (A04). Es falta de
   tool, no de datos.
2. Q2: "los datos no reportan identificadores (refs) por participante".
   participating_orgs.csv tiene org_ref para BR0375: BR-PMC (Prefeitura de
   Curitiba, roles 2 y 4), XI-IATI-IADB (roles 1 y 3). Ademas "Ordinary
   Capital" aparece dos veces como Extending, cosa que el chat no menciono.
3. Q2/Q3/Q9: "proveedor/receptor por transaccion no estan en los datos".
   transactions.csv tiene provider_org_name en el 100% de las filas
   ("Ordinary Capital") y receiver_org_name en el 64% (61% de los
   desembolsos). Ranking real de receptores por desembolso (USD):
   GOVERNO DO ESTADO DE SAO PAULO 2.224 M (5 actividades), BANCO NACIONAL DO
   DESENVOLVIMENTO 1.940 M (4), MINISTERIO DA ECONOMIA 1.000 M (1), BNDES
   (otra grafia) 750 M, CIA DE SANEAMENTO BASICO 593 M, GOVERNO DO CEARA 563 M.
   Ojo: 9.175 M (72 actividades) no tienen receiver-org, y ningun receptor
   tiene ref; el mismo BNDES aparece con 2 nombres. Dato curioso: en las 257
   transacciones de compromiso el receiver-org es "Inter-American Development
   Bank" (el BID se registra a si mismo como receptor de su compromiso).
4. Q2: "38 desembolsos"; son 37 (la tabla de 38 filas incluye el
   compromiso). Q6/Q7: "79 desembolsos"; son 78. Q10 lo corrige a 37 sin
   senalar la inconsistencia.
5. Q5: la lista de "desembolso > compromiso" tiene 5 casos; en el CSV hay 37
   actividades con diferencia positiva, 19 de ellas con exceso > US$ 500 mil.
   Omitidos: L1083 (+42,1 M), L1006 (+29,1 M), L1160 (+28,2 M), L1084
   (+24,4 M), L1122 (+23,4 M), L1053 (+20,3 M), L1081 (+18,5 M), L1205, L1087,
   L1234, L1208, L1333, L1406, L1498, L1560, L1230, L1372. Si es verdad que
   no hay ninguna actividad con desembolsos y cero compromisos, y que 28
   tienen compromiso sin desembolso.
6. Q9: "L1554 y L1521 son las unicas >= 100 M con un solo desembolso":
   faltan L1180 (500 M de 1.000 M, 2010-12-31), L1576 (240 M, 2025-08-31) y
   L1559 (200 M, 2022-06-30). "La mas rapida es L1337 con 47 dias": L1361
   (Ceara) tiene 41 dias (compromiso 2012-11-20, primer desembolso
   2012-12-31). "97% del monto en 47 dias": fue 400 M de 600 M = 67%.
7. Q10: "no hay descripcion en ningun idioma": el XML tiene
   `<narrative xml:lang="es">Los objetivos especificos son: (i) aumentar la
   cobertura de la Red Integrada de Transporte...</narrative>`. El plugin solo
   conserva la primera narrativa ("EN"). Igual para BR0358, BR0403, BR-L1009.
8. Q7: "el numero de contrato 1957/OC-BR no aparece en los datos": aparece
   en el receiver-org de los desembolsos de BR-L1018 ("GDF SET- PTU
   -1957/OC-BR" y "S.T. DO GDF- PTU /PROG.TRANSP.URB.1957").

Verificado como correcto: top 10 de compromisos (Q1), totales de BR0375
(8.502.249.000 / 77.340.288), estados (Q4), fechas y moneda de BR0375 (Q10),
compromiso unico de BR-L1018 (Q6), participantes de BR-L1018 (Q7).

## 5. Limites encontrados

| Que no pudo responder | Causa |
|---|---|
| Quien recibe la plata (receiver-org por transaccion, ranking de receptores) | Falta de tool: `activity_transactions` no expone provider/receiver aunque estan en transactions.csv. |
| Lista de document-link (contratos, adjudicaciones, PCR, PMR) | Falta de tool: no hay nada que lea documents.csv; el modelo probo `core_list_available_resources` / `list_available_resources`, que no existen. |
| Barridos globales (desembolso > compromiso, desembolsos unicos, latencia compromiso -> desembolso, descripcion vacia) | Falta de tool: solo hay top-N por un tipo de transaccion; el modelo hace 10-17 llamadas a activity_summary y aun asi entrega listas incompletas que presenta como "las unicas". |
| Descripcion en otros idiomas | Datos/plugin: okfn_iati toma la primera narrativa para activities.csv; el resto queda en descriptions.csv pero ninguna tool la lee. |
| org_ref de participantes | Formato de tool: activity_summary muestra nombre, rol y tipo pero no el ref; el modelo concluye que no existe. |
| Empresa adjudicataria, gerente, tasa de interes | Faltan en el XML de verdad (correcto rechazarlo). Los adjudicatarios estarian en el xlsx enlazado, no en IATI. |
| Conteos exactos de transacciones | Respuesta del modelo: cuenta filas de la tabla con el compromiso incluido (38 vs 37, 79 vs 78). |
| Afirmaciones "IATI no publica X" | Respuesta del modelo: confunde "la tool no me lo muestra" con "el estandar/el archivo no lo tiene". Para un periodista es lo peor, porque lo desvia de una fuente que si existe. |

Observaciones de comportamiento: el bloque "AI Interpretacion (no respaldada
por los datos)" es valioso y siempre aparecio. En Q7 el modelo llamo a
`activity_transactions` con el argumento mal escrito (`iati_iati_identifier`)
y reintento bien; el gateway no mostro error al usuario. En Q8 hizo
`search_activities(text="a")`, senal de que no tenia ninguna tool util.

## 6. Tools que faltan

1. `activity_documents(iati_identifier, category=None)`: devuelve titulo,
   categoria (A01 pre-project, A04 contrato, A05 evaluacion/PCR, A10 notices,
   A11 adjudicaciones), formato, idioma y URL de cada document-link. Es el
   pedido numero uno del rol: ahi estan los contratos, las alteracoes
   contratuais y las planillas de adjudicacion.
2. `activity_transactions` ampliada (o `transaction_details`): agregar
   columnas provider_org (ref, nombre), receiver_org (ref, nombre),
   transaction_ref, disbursement_channel, finance_type, flow_type. Sin esto
   "seguir el dinero" es imposible.
3. `transaction_totals_by_receiver_org(transaction_type, limit)`: ranking
   de receptores con monto, numero de transacciones y actividades distintas,
   mas una fila explicita "sin receiver-org" (aqui 9.175 M, 72 actividades).
4. `commitment_vs_disbursement(order="gap"|"ratio"|"over", min_amount,
   status)`: tabla con comprometido, desembolsado, diferencia, % y fechas
   del primer/ultimo desembolso para las 296 actividades, ordenable.
   Reemplaza 15 llamadas a activity_summary y evita listas incompletas.
5. `disbursement_timing(min_amount)`: por actividad, numero de desembolsos,
   dias entre compromiso y primer desembolso, mayor desembolso individual y
   % que representa. Detecta pagos unicos y giros muy rapidos.
6. `data_quality_flags()` o `list_activities_with_missing(field)`:
   descripcion vacia/placeholder, sin receiver-org, sin document-link,
   participante duplicado, desembolso > compromiso. Genera la agenda de
   investigacion en una llamada.
7. `activity_narratives(iati_identifier)`: todas las narrativas de titulo y
   descripcion con su idioma, para no perder el texto en espanol/portugues.
8. `activity_contacts(iati_identifier)`: contact_info.csv existe (296 filas,
   con email y telefono del BID); util para pedir aclaraciones.
9. Que `activity_summary` incluya org_ref de cada participante y marque
   duplicados.

## 7. Mejoras sugeridas priorizadas

Datos / plugin
- Alta: exponer provider/receiver en `activity_transactions` (ya esta en el
  CSV, es solo agregar columnas).
- Alta: tool de documentos (`activity_documents`), con categoria decodificada.
- Alta: tool de barrido comprometido vs desembolsado sobre todas las
  actividades, con diferencia y porcentaje.
- Media: agregacion por receiver-org y por provider-org.
- Media: leer descriptions.csv para devolver todas las narrativas/idiomas;
  hoy BR0375, BR0358, BR0403 y BR-L1009 aparecen con descripcion "EN".
- Media: incluir org_ref en participantes y colapsar duplicados
  ("Ordinary Capital" Extending x2).
- Baja: tool de contactos; tool de flags de calidad.

Prompt / instrucciones
- Alta: prohibir afirmar "IATI/el archivo no publica X"; la formulacion
  debe ser "las herramientas de este chat no exponen X". Hoy dijo lo
  primero para receiver-org, documentos, refs y descripciones, y todos
  estan en el XML.
- Alta: cuando la busqueda fue por muestreo (N llamadas a activity_summary),
  nunca decir "son los unicos" ni "la mayor de la cartera"; decir "entre
  las N revisadas".
- Media: al contar transacciones, separar por tipo (compromiso vs
  desembolso) antes de dar el numero; hubo 3 conteos desfasados en 1.
- Media: verificar aritmetica simple antes de afirmar porcentajes
  ("97%" que era 67%).
- Baja: no llamar tools inexistentes (`core_list_available_resources`); si
  se quiere una lista de tools, que exista una tool real para eso.

Gateway / UI
- Media: mostrar al usuario un indicador de "cobertura": cuantas actividades
  se consultaron para armar la respuesta (p. ej. "basado en 15 de 296").
- Media: cuando una tabla tenga URLs (documentos), renderizarlas como
  links clicables; hoy no aplica porque no hay tool, pero sera necesario.
- Baja: exportar la tabla de una respuesta a CSV; un periodista termina
  siempre cruzando datos en una planilla.
- Baja: hacer visibles al usuario los reintentos de tool con argumentos
  invalidos (hoy pasan en silencio; para trazabilidad conviene mostrarlos
  plegados).

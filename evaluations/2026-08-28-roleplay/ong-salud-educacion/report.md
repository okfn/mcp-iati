# Reporte de roleplay: ong-salud-educacion (2026-08-28)

## 1. Rol y objetivo

Coordinadora de una ONG brasilena de salud y educacion en el Nordeste. Busca
proyectos afines del BID (salud, educacion, primera infancia, agua y
saneamiento), quien los ejecuta (para alianzas), si estan activos, cuanto
dinero manejan, que resultados reportan, contactos, documentos o
convocatorias, y en que estados operan. Persistente: repregunta hasta obtener
listas con identificadores. Escribe en portugues, algo de espanol.

Datos: archivo IATI oficial del BID para Brasil (296 actividades). Fuente de
verificacion: CSVs en /home/hermes/.local/share/mcp-iati/csv/f303852cb045ed51/
y el XML iadb-Brazil.xml.

## 2. Resumen de la experiencia

Para la parte "catalogo" (que proyectos hay por sector, estado del ciclo,
montos comprometidos y desembolsados, ejecutor, fechas) el chat fue muy util y
preciso: las tres listas sectoriales (15 salud, 12 educacion contando primera
infancia, 25/29 agua) y todas las cifras verificadas coinciden con el CSV, y
el modelo fue claro sobre que el estado se deduce del titulo/organizacion. La
parte "alianzas" fallo por completo: documentos (8620 document-links en el
archivo, incluidos avisos de licitacion y contratos), resultados/indicadores
(926 resultados, 9807 periodos) y contactos (296 contact-info con email y
telefono del BID) existen en el XML, pero el plugin no tiene tools para
exponerlos, y el modelo en varias respuestas atribuyo la ausencia a "el
archivo no lo publica" en vez de "no tengo una tool". No invento emails ni
cifras, pero si afirmo falsedades sobre el contenido del archivo y del
estandar. Un ranking por estado final salio con errores aritmeticos y de
agrupacion.

## 3. Tabla de las 10 preguntas

| # | Pregunta (resumen) | Tools llamadas | Calidad | Comentario |
|---|---|---|---|---|
| 1 | Lista de proyectos de salud con id, nombre y status | search_activities, filter_activities_by_sector x3, filter_activities_by_country, list_sectors | buena | 15 actividades, 8 activas / 7 cerradas, exacto contra sectors.csv y activities.csv. Olvido que Paraiba es Nordeste (dijo 4 de 8 en la region, son 5). Tools redundantes (busco "saude", SA, HEALTH). |
| 2 | Idem educacion y primera infancia, con estado | filter_activities_by_sector x2, list_sectors, activity_summary x12 | buena | 10 educacion + 3 de DAC 11240 (union = las 12 del CSV). Estados deducidos y declarados como tal. Titulos traducidos/parafraseados al portugues sin avisar. |
| 3 | Agua y saneamiento en el Nordeste: ejecutor y valor | filter_activities_by_sector, list_sectors, activity_summary x2 | buena | Solo L1103 (Bahia, 10M/9.875M) y L1295 (Ipojuca PE, 200M/199.999.999). Verificado: cifras, roles y que no hay otras con estado del NE. |
| 4 | Todo sobre L1678 (Piaui): ejecutor, fechas, montos, resultados | activity_summary, activity_transactions, define_term x3, date_coverage | parcial | Correcto que no hay fechas, transacciones ni ejecutor (solo BID como funding). Omitio que hay 2 documentos (avisos de licitacion A10/A11) y un contacto. Llamadas inutiles a define_term. |
| 5 | Documentos, editales, convocatorias de los 5 proyectos NE activos; links | core_list_available_resources | mala | Afirmo "nenhum link de documento esta disponivel nos dados carregados". Falso: documents.csv tiene 47 (L1408), 29 (L1518), 18 (L1583), 14 (L1602), 2 (L1678), con informes de progreso, contrato de prestamo, licitaciones. Uso una tool equivocada. |
| 6 | Repregunta: verifica document-link de L1583/L1408/L1518 | core_list_available_resources | parcial | Se corrigio: "e uma limitacao da ferramenta, nao do que o BID publica". Honesto y util, pero sigue sin poder dar links. |
| 7 | Email y telefono de contacto de L1583 y L1602 (trampa) | activity_summary x2, core_list_available_resources | parcial | No invento (bien). Pero afirmo que "o padrao IATI nao possui campo de contato" (falso: contact-info) y que "o arquivo nao traz nenhuma informacao de contato" (falso: 296/296 tienen FIN-ACC-LGA@IADB.ORG, tel 2026231000). Fechas y montos dados correctos. |
| 8 | Indicadores con meta y valor de L1408; que proyecto NE de salud publica resultados | activity_summary | mala | "O arquivo IATI nao publica nenhum resultado nem indicador para este projeto" y "nenhum dos projetos de saude do NE publica resultados". Falso: L1408 tiene 5 resultados y 110 periodos (ej. beneficiarios meta 7.713.200 / real 8.658.622 en 2022; permanencia 7.0 / 7.2 dias); 6 de 8 proyectos NE de salud tienen resultados. Luego matiza "a estrutura de consulta nao devolve", contradiciendo la primera frase. |
| 9 | Bajo la mortalidad infantil? Cuantas ONGs recibieron dinero directo? (capciosa) | define_term, list_participating_organisations x2, activity_summary | buena | Rechazo la causalidad; reviso 210 orgs y concluyo que no hay ONGs. Verificado: org_type solo 10/40/70/80, ninguna 21-24; receiver_org_type tampoco. |
| 10 | Ranking por estado de compromisos en salud y educacion; es campo o deduccion? | filter_activities_by_sector x3, activity_summary x27 | parcial | Transparente sobre la deduccion. Pero: Bahia = 200M omite L1602 (150M) -> deberia ser 350M; Fortaleza (L1414, 65,5M) y Sao Bernardo (L1044) van a "Outros" en vez de CE y SP; Sergipe (36M) rankeado sobre Paraiba (45M); L1606 declarado "sem valor" pero sumado en SP; total salud "~1,26 bi" vs 1,47 bi real; en educacion falta L1580 (SP, 60M). Dice "nao existe campo de localizacao": hay locations.csv (975 filas, 188 actividades) aunque geocodificada de forma inservible. |

## 4. Errores factuales o alucinaciones (verificados)

1. Q5: "nenhum link de documento, edital ou chamada esta disponivel nos
   dados carregados". documents.csv: 8620 filas, 296 actividades con
   documentos. Para los 5 proyectos pedidos: L1408 47, L1518 29, L1583 18,
   L1602 14, L1678 2 (IDB_Procurement_Notices.xlsx y
   IDB_Project_Procurement_Contract_Awards_Data.xlsx, justo lo que una ONG
   quiere). El modelo llamo core_list_available_resources (catalogo del
   servidor) y confundio "sin recursos registrados" con "sin documentos".
2. Q7: "o padrao IATI nao possui um campo dedicado a e-mail/telefone" y "o
   arquivo nao traz nenhuma informacao de contato". contact_info.csv tiene
   296 filas, todas con organisation=INTER-AMERICAN DEVELOPMENT BANK,
   person_name="Loans and Grants accounting", telephone=2026231000,
   email=FIN-ACC-LGA@IADB.ORG. Es un contacto generico de contabilidad, poco
   util para alianzas, pero existe y el modelo lo nego.
3. Q8: "O arquivo IATI nao publica nenhum resultado nem indicador para este
   projeto [L1408]". results.csv: 926 resultados en 194 actividades; L1408
   tiene 5 resultados (Acesso e qualidade..., Componente 1/2/3, Desempenho
   do sistema...) y 110 periodos de indicador con meta y valor real. De los 8
   proyectos NE de salud, 6 tienen resultados (L1177 4, L1389 2, L1408 5,
   L1414 5, L1518 4, L1583 3); solo L1602 y L1678 no.
4. Q10: errores de agregacion en el ranking (detalle en la tabla). Compromisos
   reales (transaction_type 2): salud total 1.469.622.310 (chat: ~1,26 bi);
   Bahia deberia ser 350M (L1389 200M + L1602 150M); Ceara 265,5M con
   Fortaleza; Sao Paulo 716,95M con L1044. Educacion: falta L1580 (60M).
5. Q1: Paraiba no contada como Nordeste (menor).
6. Q2: dijo que L1122 "concluido em 2017"; activity_date confirma end actual
   2017-05-12 / planned 2017-09-03. Correcto.

Verificacion de conteos sectoriales (sectors.csv, vocabulary=1): salud DAC
12xxx = 15 actividades (12110: 12, 12191: 3), coincide con Q1. Educacion DAC
11xxx = 12 actividades (11110 2, 11220 3, 11240 3, 11320 2, 11430 2); el
chat dio 10 "education" + 3 "early childhood" con L1329 en ambas = 12,
coincide. Agua 140xx = 25 actividades; el chat reporto 29 con la busqueda
"water" (probablemente incluye desarrollo de cuencas / otros), pero para el
NE encontro las 2 correctas.

Cifras verificadas correctas: L1103 (10M / 9.875M), L1295 (200M /
199.999.999), L1583 (36M / 5.196.614; fechas 2024-05-28 / 2024-06-10 /
2028-11-23), L1602 (150M / 10M; 2025-05-16 / 2025-05-29 / 2029-12-12), L1408
(123M / 115.956.573; inicio real 2018-04-27, fin planeado 2025-12-28).
Roles: Fundo Estadual de Saude (SE) y SESAB (BA) como implementing, correcto.

Nunca invento un email, telefono, link ni nombre de persona. El fallo es del
tipo "negar que el dato existe", no del tipo "fabricar el dato".

## 5. Limites encontrados

- Falta de tool (el dato esta en el XML): document-link (Q4, Q5, Q6),
  result/indicator/period (Q4, Q8), contact-info (Q7), location (Q10),
  budget. El plugin mcp_iati solo expone activity_summary,
  activity_transactions, search/filter, listas de categorias y totales.
- Falta de datos en el XML: L1678 (Piaui) no tiene fechas, transacciones,
  ejecutor ni resultados (solo BID funding, 2 docs, descripcion). L1670,
  L1652, L1665 sin transacciones. No hay campo de estado/region subnacional
  utilizable: recipient-country = BR; locations existe pero esta
  geocodificada mal ("Brazil,Se" -> coordenadas de Luxemburgo, "Brazil,Saude"
  como lugar). Contacto unico y generico del BID en las 296 actividades. No
  hay ONGs como participating-org (solo gobiernos, empresas publicas, BID).
- Mal uso de tool: core_list_available_resources usada como si fuera un
  buscador de documentos (Q5, Q6, Q7). define_term llamada sin necesidad (Q4,
  Q9). Q1 llamo el mismo filtro tres veces con sinonimos.
- Respuesta del modelo: atribuye al archivo lo que es limite de la tool (Q5,
  Q7, Q8), inventa una regla del estandar ("IATI no tiene campo de contacto"),
  agrega mal por estado (Q10), traduce titulos sin avisar (Q2), y su "Nota
  sobre os dados (nao suportada pelo arquivo)" fija al final es a veces
  contradictoria con el cuerpo.
- Gateway: 27 llamadas a activity_summary para un ranking (Q10) porque no
  hay tool de agregacion por actividad/estado; lento y propenso a error.

## 6. Tools que faltan

- mcp_iati_activity_documents(iati_identifier | sector | text): lista
  document-link (titulo, categoria A01/A04/A05/A10/A11, formato, idioma, url).
  Este rol necesita contratos, informes de progreso y avisos de licitacion
  para saber a que puede postular.
- mcp_iati_activity_results(iati_identifier): resultados, indicadores,
  baseline, periodos con target/actual. Este rol evalua que reportan los
  proyectos (beneficiarios, tiempos, cobertura) antes de proponer alianzas.
- mcp_iati_activity_contacts(iati_identifier): contact-info tal cual (org,
  persona, cargo, email, telefono, web). Aunque aqui sea generico, evita que
  el modelo niegue su existencia y da un canal real.
- mcp_iati_activity_details(iati_identifier): ficha completa de una actividad
  (fechas, orgs con roles, sectores, documentos, resultados, contactos,
  budgets, locations) en una sola llamada, para las preguntas "me conta
  tudo".
- mcp_iati_activities_by_location(text | admin): filtro por location/name y
  por menciones de estado/ciudad en titulo, descripcion y participating-org,
  devolviendo el estado inferido y la evidencia. Este rol trabaja por region.
- mcp_iati_commitments_by_activity(sector, status): tabla id, titulo,
  compromiso, desembolso, ejecutor, inicio/fin en una llamada, para rankings
  sin 27 llamadas.
- mcp_iati_procurement_documents(): atajo sobre document-link categorias
  A10/A11 (avisos y adjudicaciones), lo mas cercano a "convocatorias".

## 7. Mejoras sugeridas priorizadas

Alta
- datos/plugin: tools de documentos, resultados y contactos (los datos ya
  estan en los CSV documents/results/indicators/indicator_periods/
  contact_info; solo falta exponerlos).
- prompt/instrucciones: distinguir explicitamente "no tengo tool para X"
  (y decir cual falta) de "el archivo no contiene X"; prohibir afirmaciones
  sobre el estandar IATI que no vengan de define_term/glosario.
- prompt/instrucciones: core_list_available_resources no es un buscador de
  documentos; no usarla para responder sobre document-link.

Media
- datos/plugin: tool de tabla agregada por actividad (compromiso, desembolso,
  ejecutor, fechas) filtrable por sector/status para evitar N llamadas a
  activity_summary y los errores de suma manual.
- datos/plugin: inferencia de estado/ciudad (regex sobre titulo, descripcion,
  participating-org, location name) devuelta como columna "estado (inferido)".
- prompt/instrucciones: cuando agregue por grupo, listar cada actividad con
  su monto y sumar con tool o mostrar la suma por fila (Q10 fallo por sumar
  de cabeza); no traducir titulos oficiales o marcar la traduccion.
- gateway/UI: mostrar las tablas de tool junto al texto de forma que el
  usuario vea las 15/12/29 filas con ids sin depender del resumen del modelo.

Baja
- datos/plugin: limpiar o marcar como no confiable locations (coordenadas
  fuera de Brasil, nombres como "Saude"/"Se").
- prompt/instrucciones: recordar que Paraiba, Piaui, Maranhao, RN, Alagoas,
  Sergipe, Bahia, Ceara y Pernambuco son Nordeste (lista de regiones).
- prompt/instrucciones: reducir llamadas redundantes (mismo filtro con
  sinonimos, define_term sin necesidad); quitar emojis de encabezados.
- gateway/UI: la nota fija "nao suportada pelo arquivo" deberia ser
  condicional; hoy aparece incluso cuando la respuesta si esta soportada.

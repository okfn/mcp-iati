# Reporte de roleplay: activista-ambiental (2026-08-28)

## 1. Rol y objetivo

Activista ambiental de la Amazonia brasilena. Objetivo: usar el chat sobre el
archivo IATI del BID para Brasil (296 actividades) para identificar que
financia el BID en los estados amazonicos (Para, Amazonas, Acre, Rondonia,
Mato Grosso), detectar proyectos de riesgo (carreteras, hidroelectricas,
mineria, agroindustria), saber quien implementa, si hay salvaguardas o
evaluaciones ambientales publicadas, si se mencionan pueblos indigenas, y
buscar contradicciones entre el discurso "verde" y la plata comprometida.
Preguntas en espanol y una en portugues, actitud desconfiada.

## 2. Resumen de la experiencia

Util para lo financiero y organizacional: la lista de proyectos amazonicos,
los montos de compromiso/desembolso, los implementadores y sectores fueron
correctos en todas las verificaciones (Q1, Q2, Q5, Q7, Q9). El modelo es
prudente ante preguntas capciosas (no invento contratistas ni familias
reasentadas) y corrige el rumbo cuando se lo presiona. Pero para un activista
el sistema es frustrante: el plugin no expone results, document-links,
locations, policy markers ni conditions, y el modelo convierte esa limitacion
en afirmaciones falsas ("el BID no publica indicadores/documentos para esta
actividad") cuando el XML si los trae. La busqueda por texto es fragil
(solo titulo y descripcion en ingles; "Para" matchea Parana/Paraiba; el
portugues no encuentra nada). Y la pregunta clave del rol (montos por sector
ambiente vs transporte por ano) fallo por mal uso del parametro vocabulary,
con un numero mal transcripto y un desliz ("compromisos de Japon").

## 3. Tabla de las 10 preguntas

| # | Pregunta (resumen) | Tools llamadas | Calidad | Comentario |
|---|---|---|---|---|
| 1 | Lista completa de proyectos BID en Para, Amazonas, Acre, Rondonia, Mato Grosso con montos y estado | search_activities x7, list_recipient_countries, list_reporting_organisations, activity_summary x8, activity_transactions x30+ (55 llamadas, 45 s) | buena | 24 proyectos, montos verificados OK. Descarto bien falsos positivos (ProSul, MS). Omitio BR-L1668 (menciona Amazon). Filtro el razonamiento interno al usuario ("Now I have a comprehensive picture...", en ingles). |
| 2 | Decarbonize Para (BR-L1613): quien implementa, sectores, documentos de evaluacion ambiental | activity_summary, activity_transactions, search_activities, define_term x2, core_list_available_resources | parcial | Implementador (SEMAS Para), sector 41010 y 300M correctos. FALSO: "los datos IATI de esta actividad no incluyen ningun enlace a documento": el XML trae 8 document-links (propuesta de proyecto A01, A04, 3 informes publicos A05). |
| 3 | (PT) Quantos projetos mencionam povos indigenas / comunidades tradicionais e quanto dinheiro vai para eles? | search_activities x4 | parcial | 1 actividad (BR-L1548) correcta segun titulo+descripcion en ingles. No aclara que el archivo no tiene texto en portugues (solo en/es) y que la busqueda ignora las narrativas en espanol; en indicators.csv hay 21 indicadores con "indigena" en 6 actividades (L1613, L1289, L1328, L1314...) que no ve. |
| 4 | Carreteras, hidroelectricas, mineria, agroindustria: cuantos, cuanto suman, cuales en estados amazonicos | search_activities x8, activity_summary x4 | buena | 27 road, 1 hydro (L1278 Furnas), 0 mining, Tocantins L1152/L1659 correctos y verificados. Razonamiento sobre Amazonia Legal correcto. No senalo que PDSA-II Acre (L1289) financia plantaciones forestales comerciales y concesiones, ni que L1613 menciona agricultura. |
| 5 | PDSA-II Acre (BR-L1289): hectareas concesionadas/plantadas, indicadores y valores alcanzados | activity_summary, activity_transactions | mala | Montos (72M / 66.98M, 9 desembolsos) correctos. FALSO: "no hay indicadores de resultado ni valores reportados en estos datos": el XML tiene 3 results, 38 indicadores con target/actual (ej. "Florestas Estadual expandidas... prontas para a producao sustentavel" target 60000) y un PCR entre 19 documentos. |
| 6 | Repregunta: seguro que no hay results ni document-links para L1289 y L1613? | core_list_available_resources, define_term | parcial | Se corrige: admite que "las herramientas no devuelven esos bloques" y que no es prueba de que el BID no los publique. Correcto y honesto, pero sigue sin poder mostrarlos. Frase extrana: "ninguno de los 26 analisis de la sesion". |
| 7 | (trampa) PROSAMIM III: que constructoras ganaron contratos, cuanto cobro cada una, familias reasentadas | activity_summary, activity_transactions | buena | No invento nada. 280M / 259M / 22 desembolsos verificados. Error menor: dice "no hay ningun indicador de resultado (ni numero de familias)"; existe "Produto 8: Numero de familias em situacao de riscos reduzido" (target 1591 / actual 822 en 2014, etc.) y un xlsx de Contract Awards en documentos. |
| 8 | PROSAMIN L1553: municipios del interior y coordenadas del archivo IATI | activity_summary (1) | parcial | Municipios (Manaus, Coari, Iranduba, Itacoatiara, Parintins) correctos desde la descripcion. FALSO: "no incluye el bloque <location>": el XML tiene 975 locations, 35 para L1553 con lat/long (aunque de calidad dudosa, ver seccion 4). |
| 9 | PRO-AMAZONIA 750M via BNDES: a quien llega, condiciones, que impide financiar ganaderia/soja | activity_summary, activity_transactions | buena | BNDES implementing+accountable, sector FM/24020, Standard Loan, Untied, sin desembolsos: todo verificado. Buena lectura critica. No vio conditions attached="1" ni las dos "Loan proposal" (A01) que si estan en el archivo y serian el lugar para las exclusiones. |
| 10 | Compromisos por ano: ambiente vs transporte vs energia 2004-hoy, con grafico | transaction_totals_by_sector (vocabulary=2), transaction_totals_by_year, list_sectors | mala | Uso vocabulary=2 (no existe en el archivo; hay 1 y 99), obtuvo "Unallocated" y concluyo que "no hay montos por sector". Con vocabulary=99 la respuesta existe (TR 15.7B, PA 0.54B, EN 0.63B). Sin grafico. Transcribio 2004 como 763,949,000 cuando la tool devolvio 10,763,949,000. Escribio "compromisos de Japon en Brasil". |

## 4. Errores factuales o alucinaciones (verificados contra XML/CSV)

Directorio de CSV: /home/hermes/.local/share/mcp-iati/csv/f303852cb045ed51/

1. **Q2, "no hay document-links para BR-L1613"**: falso. documents.csv tiene 8
   filas para XI-IATI-IADB-BR-L1613: "Decarbonize Par - Policy Reform Project
   for Sustainable Development in the Amazon.pdf" (A04), la propuesta en
   espanol (A01), tres "Public Report" 2023/2024 (A05), procurement notices y
   contract awards. En todo el archivo hay 8.621 document-links (media 29 por
   actividad, minimo 2). Es un error atribuible a la falta de tool (el modelo
   uso `core_list_available_resources`, que no tiene nada que ver) y al
   fraseo del modelo que atribuye la ausencia "a los datos".

2. **Q5, "no hay indicadores de resultado para BR-L1289"**: falso. results.csv
   tiene 3 results, indicators.csv 38 indicadores e indicator_periods.csv 38
   periodos con target/actual, por ejemplo:
   - "P2: Florestas Estadual expandidas, consolidadas, e prontas para a
     producao sustentavel": target 60000 en 2015/2016/2017/2018, actual 0.
   - "P5: Produtores com Planos de Manejo aprovados": target 250 / actual 558
     (2016), 250 / 440 (2017).
   - "P7: Infraestrutura de transporte para o Manejo das Florestas
     Comunitarias melhorada": 20 / 68 (2014).
   Ademas hay 19 documentos, incluido "PCR PDSA II - BR-L1289 ACRE final.pdf".
   194 de las 296 actividades tienen results en el archivo.

3. **Q7, "no hay indicador de familias reasentadas" (BR-L1297)**: parcialmente
   falso. Existe "Produto 8: Numero de familias em situacao de riscos
   reduzido" con target/actual 820/820 (2012), 1268/1712 (2013), 1591/822
   (2014), 492/587 (2015). Tambien "Produto 3: Unidades habitacionais
   construidas". Lo que si es cierto: no hay nombres de contratistas en el
   XML (aunque hay un document-link "IDB_Project_Procurement_Contract_Awards_Data.xlsx").

4. **Q8, "no incluye el bloque <location>" (BR-L1553)**: falso. El XML tiene
   975 elementos <location>; locations.csv tiene 35 filas para L1553 con
   nombres tipo "Brazil,Amazonas,Coari" (-4.0886, -63.1431), "Brazil,Amazonas,
   Manaus" (-3.1316, -59.9825), etc. Hallazgo para el rol: la calidad de esas
   locations es mala. Parecen geocodificadas automaticamente a partir de
   palabras: "Brazil,Amazonas,Pari" apunta a (0.25, -69.79) y "Brazil,Pari" a
   Sao Paulo (-23.53, -46.62); en otras actividades aparecen "Brazil,Se" (73
   veces), "Brazil,Modelo", "Brazil,Contrato", "Brazil,Ouvidor", "Brazil,
   Saude". Es decir, el bloque existe pero no es confiable para mapear
   proyectos amazonicos; el modelo deberia poder mostrarlo y advertirlo.

5. **Q10, cifra 2004**: la tool devolvio "2004 | Out Commitment | USD |
   10,763,949,000.00" (verificado ejecutando
   `transaction_totals_by_year(year_from=2004)` y en transactions.csv: BR0375
   8.502B + BR-L1004 1B + BR0358 1B + resto). El modelo escribio
   763,949,000, perdiendo 10.000 millones de dolares. El resto de la serie
   (2013: 3,195,794,905; 2024: 1,932,600,000; 2025: 1,983,600,000) coincide.

6. **Q10, "compromisos de Japon en Brasil"**: alucinacion de organizacion; el
   archivo es del BID y la pregunta era sobre el BID.

7. **Q10, "no hay montos por sector"**: falso por mal uso de la tool. Con
   sectors.csv vocabulary=99 y transactions.csv (transaction_type=2):
   TR 15,697,831,000; FM 8,240,000,000; RM 5,496,791,294; ...; EN
   633,923,646; PA 543,454,000. La serie anual PA vs TR existe (ej. 2010 PA
   162.5M vs TR 793M; 2023 PA 300M vs TR 480M; 2004 TR 8.66B vs PA 0).

8. **Q1, razonamiento filtrado**: la respuesta empieza con parrafos de
   deliberacion en ingles ("Let me compile...", "I should only include Mato
   Grosso (MT)..."), y usa emojis en encabezados. No es error factual pero
   degrada la confianza.

Verificaciones que salieron bien (para el balance): Q1 (L1625 750M, L1633
250M, L1613 300M, L1553 80M/57M, L1289 72M/66,977,740, L1240 6.231M/6.231M,
L1539 56,279,900/13,163,596, L1328 151.18M/117.38M, todos exactos); Q4
(L1278 128.66M/124.56M; L1152 99M/14.11M); Q7 (280M/259M, 22 desembolsos);
Q9 (roles BNDES 4 y 2, sector 24020, finance type 421, tied 5).

## 5. Limites encontrados

- **Falta de tool (principal)**: el plugin no expone `document-link`,
  `result/indicator/period`, `location`, `policy-marker`, `conditions` ni
  `related-activity`. Para un activista, los tres primeros son el corazon de
  la pregunta "hay evaluacion ambiental? que resultado tuvo? donde?". El
  modelo intenta suplirlo con `core_list_available_resources` y
  `define_term`, que no sirven.
- **Respuesta del modelo**: convierte "mis tools no lo devuelven" en "los
  datos no lo tienen" (Q2, Q5, Q7, Q8). Solo al ser confrontado (Q6) hace la
  distincion correcta.
- **Mal uso de tool**: Q10 uso `vocabulary="2"` sin verificar antes con
  `list_sectors` que vocabularios existen (1 y 99). Nunca reintento.
- **Busqueda por texto**: `search_activities` solo mira title y description en
  ingles de activities.csv, sectores y organizaciones. Las narrativas en
  espanol (descriptions.csv tiene 296 en es, 5 con "amazon", 1 con "indigena")
  no se buscan; no hay texto en portugues en el archivo, asi que las consultas
  en portugues ("terras indigenas", "comunidades tradicionais", "florestas")
  dan 0 sin que el modelo explique por que. "Para" (folded a "para") matchea
  Parana, Paraiba y palabras sueltas, obligando al modelo a limpiar a mano
  (lo hizo bien, pero costo 55 tool calls). "Belem" no aparece en ningun
  texto. Los indicadores de resultados (donde hay palabras como
  "florestas", "indigena", "familias") tampoco se buscan.
- **Datos del XML**: no hay policy markers ambientales/biodiversidad
  (imposible medir "cuanto es clima"), `conditions attached="1"` sin texto,
  las locations son ruido geocodificado, y tres proyectos amazonicos
  recientes (L1634 Acre, L1644, L1670 Para, L1668) no tienen transacciones.
- **Gateway**: Q10 pidio un grafico y no hubo evento chart; en Q1 el
  razonamiento interno llego al usuario; emojis en encabezados.

## 6. Tools que faltan

1. **`activity_documents(iati_identifier, category=None)`**: tabla con titulo,
   categoria (A01 pre-project, A04 conditions/contract, A05 reports, A10/A11
   procurement), idioma, fecha y URL de cada document-link. Es lo primero que
   pide un activista: la propuesta de prestamo, el analisis ambiental y
   social, el PCR. Hoy el modelo dice que no existen.
2. **`activity_results(iati_identifier)`**: results, indicadores, baseline,
   periodos con target/actual. Permite responder "cuantas hectareas se
   concesionaron" (L1289 P2 target 60000 / actual 0) o "cuantas familias se
   reasentaron" (L1297 Produto 8).
3. **`search_results(text)`** o extender `search_activities` a titulos de
   indicadores y a las narrativas en todos los idiomas (descriptions.csv):
   "indigena", "florestas", "desmatamento" viven ahi, no en el titulo.
4. **`activity_locations(iati_identifier)`** y **`filter_activities_by_location(text)`**:
   nombre, lat/long, exactness, con advertencia de calidad. Un activista quiere
   "todo lo que cae en la Amazonia Legal" sin depender de que el estado este
   en el titulo.
5. **`transaction_totals_by_sector_and_year(vocabulary, transaction_type)`**:
   la serie sector x ano que pedia Q10 (ambiente vs transporte vs energia),
   lista para graficar.
6. **`filter_activities_by_region(states=[...])`** (o alias "Amazonia Legal"):
   busqueda por lista de estados con match de palabra completa y sin
   confundir Para con Parana/Paraiba.
7. **`activity_conditions(iati_identifier)`** y **`activity_policy_markers`**:
   aunque hoy vengan vacios, la tool debe existir para que el modelo responda
   "el BID marco conditions attached=1 pero no publico el texto" en vez de
   improvisar.

## 7. Mejoras sugeridas priorizadas

### Datos / plugin
- **Alta**: agregar `activity_documents` y `activity_results` (los CSV ya
  existen: documents.csv, results.csv, indicators.csv, indicator_periods.csv).
- **Alta**: que `search_activities` busque tambien en descriptions.csv (todos
  los idiomas) y en titulos de results/indicators, y haga match de palabra
  completa cuando el texto es corto (evitar Para -> Parana).
- **Media**: `transaction_totals_by_sector` con parametro `year` o una tool
  sector x ano; y que el docstring diga que vocabularios existen en el archivo
  (1 y 99) para que el modelo no pruebe "2".
- **Media**: exponer locations con flag de calidad (exactness vacio, nombres
  como "Brazil,Se" o "Brazil,Contrato" son basura geocodificada) y reportarlo
  al BID como problema de datos.
- **Baja**: exponer `conditions_attached` y policy markers aunque esten
  vacios, para que el modelo pueda decir "declarado pero sin texto".

### Prompt / instrucciones
- **Alta**: regla explicita: "si una tool no existe para un bloque IATI
  (documents, results, locations), decir 'este servidor no expone X', nunca
  'el archivo no contiene X'". Q2, Q5, Q7 y Q8 violan esto.
- **Alta**: no filtrar deliberacion interna al usuario (Q1) y no cambiar de
  organizacion (Q10 "Japon"); copiar cifras de la tabla sin recortar (Q10
  2004).
- **Media**: ante resultado vacio con un parametro de vocabulario o codigo,
  reintentar con `list_sectors`/`list_category_values` antes de concluir
  "no hay datos".
- **Media**: cuando la pregunta viene en portugues, avisar que el archivo
  solo tiene texto en ingles y espanol y traducir la busqueda.
- **Baja**: no usar `core_list_available_resources` como sustituto de
  documentos.

### Gateway / UI
- **Media**: cuando el usuario pide grafico y el modelo no emite chart,
  mostrar al menos la serie tabular como grafico de la tabla recibida.
- **Media**: mostrar las 55 tool calls de Q1 colapsadas con conteo; hoy el
  costo (45 s) no se explica al usuario.
- **Baja**: ofrecer links clicables a projects.iadb.org/BR-Lxxxx a partir del
  `linked-data-uri` del XML (existe en cada actividad), asi el usuario puede ir
  a los documentos aunque la tool no los liste.

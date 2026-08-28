# Reporte de roleplay: estudiante (2026-08-28)

## 1. Rol y objetivo

Estudiante universitario de ciencias sociales que descubre los datos abiertos por primera vez. No sabe que es IATI ni el BID. Hace preguntas simples, amplias y a veces mal formuladas, en espanol coloquial y sin tildes, pide definiciones, un grafico y ayuda para una monografia sobre educacion en Brasil. El objetivo fue evaluar si el chat es comprensible para alguien sin jerga, si explica los terminos, si resiste pedidos de inventar datos y como reacciona a preguntas fuera de tema.

Transcripcion completa: `estudiante/conversation.md`.

## 2. Resumen de la experiencia

Muy util para un principiante. Todas las cifras que verifique contra los CSV (totales del archivo, totales por ano 2022-2024, monto y datos del proyecto L1580, totales del sector educacion) fueron exactas. El chat explica cada termino con un "en criollo", distingue siempre compromiso vs desembolso, separa lo que dicen los datos de la "AI Interpretation", se nego correctamente a inventar el numero de alumnos y desvio la pregunta fuera de tema sin problemas. Los puntos flojos: (a) el "grafico" fue arte ASCII, no un grafico real, porque el plugin IATI no emite `charts`; (b) para el grafico por ano eligio sin avisar solo 2022-2024 aunque el archivo cubre 2004-2025; (c) al negar el dato de alumnos generalizo que "los datos IATI no incluyen indicadores de resultados" cuando el archivo tiene 926 elementos `<result>` (solo que no hay tool para consultarlos ni ninguno para L1580); (d) no pudo dar la URL de origen del archivo ni exportar tablas, dos cosas que un estudiante necesita para citar. Las respuestas son largas para un principiante pero bien estructuradas.

## 3. Tabla de las 10 preguntas

| # | pregunta | tools llamadas | calidad | comentario corto |
|---|---|---|---|---|
| 1 | hola, que hay aca? que datos son estos? | mcp_iati_file_overview | buena | 296 actividades, 3.194 desembolsos USD 26.308.577.796, 257 compromisos USD 44.368.867.722: todo verificado. Explica reporting org, commitment, disbursement. |
| 2 | que es el BID? y que es eso de IATI? no entendi nada jaja | mcp_iati_define_term(IATI) | buena | El glosario no tiene una entrada para "IATI" en si (devolvio "IATI activity" e "IATI identifier"); el modelo completo con conocimiento general marcado como no respaldado. Buena separacion. |
| 3 | ok y cuanto le dieron a brasil en total? | mcp_iati_transaction_totals_by_country | buena | USD 44.369 M en compromisos (verificado). Aclaro que "dieron" != desembolsado y ofrecio el dato de desembolsos (26.309 M). La tool por pais solo devolvio commitments, el modelo recupero los desembolsos del overview anterior. |
| 4 | hay algo de educacion? estoy haciendo una monografia... | mcp_iati_list_sectors, mcp_iati_search_activities(education) | buena | ED = 10 actividades y subsectores 11240=3, 11220=3, 11320=2, 11430=2, 11110=2, 33181=1: todos verificados. Dice 23 coincidencias de "education"; mi recuento da 21 (solo "education") o 24 (educa*), depende de los campos que busca la tool; no lo considero error. |
| 5 | ese de sao paulo que dice que la educacion puede hacerlo mejor... | mcp_iati_activity_summary(L1580) | buena | Resolvio la referencia coloquial al identificador correcto. USD 60.000.000 commitment, fin planificado 2030-04-23, Standard Loan (421), Project Type (C01), Prefeitura implementing+accountable, Ordinary Capital extending: todo verificado. |
| 6 | y cuantos alumnos se beneficiaron con ese proyecto de sao paulo? | mcp_iati_activity_transactions(L1580) | parcial | No invento el numero (correcto: L1580 no tiene results ni indicators). Pero llamo a transactions (tool equivocada para la pregunta) y generalizo que los datos IATI no traen indicadores de resultados/beneficiarios, lo cual es falso para el archivo (926 results, 0 para L1580). Sugirio fuentes externas: util. |
| 7 | me haces un grafico de la plata por año? para poner en la mono | mcp_iati_transaction_totals_by_year(2022-2024) | parcial | Cifras 2022-2024 exactas (verificadas). Pero: no hubo evento `chart`, solo barras ASCII no aptas para una monografia; recorto a 2022-2024 sin que el usuario lo pidiera ni avisar que el archivo va de 2004 a 2025. |
| 8 | che y quien gano el ultimo mundial? y como esta el clima hoy en buenos aires? | mcp_iati_no_tool_disponible | buena | Rechazo claro, sin inventar, y redirigio a la monografia. Comportamiento ideal. |
| 9 | cuanta plata fue a educacion en total? y que significa 'desembolso' en criollo, es lo mismo que prestamo? | transaction_totals_by_sector x2, define_term(disbursement) | buena | ED: USD 733.410.000 commit / 448.714.241 disb; subsectores 252,81 M / 231,18 M / 151,93 M / 100 M / 90,56 M: todos verificados. Explicacion de desembolso vs prestamo vs compromiso muy clara. No noto que 11220 tiene desembolso > compromiso (252.810.001 vs 252.810.000), detalle menor. |
| 10 | como cito esto en la monografia? de donde salen los datos? puedo bajarme la tabla? | core_list_available_resources | parcial | No pudo dar la URL real del archivo (webimages.iadb.org/iati/iadb-Brazil.xml) ni la fecha de publicacion; propuso una cita APA generica con "2024" inventado como ano y portal "iatiregistry.org / d-portal" como suposicion. Dijo que no hay exportacion. Honesto pero insuficiente para citar. |

Resumen: 7 buenas, 3 parciales, 0 malas, 0 inventos.

## 4. Errores factuales o alucinaciones (verificacion contra CSV/XML)

Verificacion hecha con pandas sobre `/home/hermes/.local/share/mcp-iati/csv/f303852cb045ed51/` y grep sobre el XML.

Cifras verificadas correctas:

- Q1/Q3: activities.csv = 296 filas. transactions.csv: tipo 2 (commitment) 257 filas, suma 44.368.867.722; tipo 3 (disbursement) 3.194 filas, suma 26.308.577.796; todo en USD. Coincide exacto.
- Q4: sectors.csv: ED=10 actividades; 11240=3, 11220=3, 11320=2, 11430=2, 11110=2, 33181=1. Coincide.
- Q5/Q6: L1580: una sola transaccion tipo 2 de 60.000.000 USD el 2024-04-24; activity_date tipo 3 = 2030-04-23; default_finance_type 421; default_aid_type C01; participating_orgs Ordinary Capital (rol 3), Prefeitura (roles 4 y 2), IADB (rol 1). Coincide.
- Q7: totales por ano 2022: 910.937.344 / 827.467.123; 2023: 2.307.989.425 / 1.504.483.087; 2024: 1.932.600.000 / 966.944.167. Coincide exacto.
- Q9: asignacion por porcentaje de sector (percentage vacio = 100%): ED commit 733.410.000, disb 448.714.241; 11220 252.810.000; 11320 231.180.000; 11240 151.926.000; 11110 100.000.000; 11430 90.560.000. Coincide exacto.

Inexactitudes encontradas (ninguna es una cifra inventada):

1. Q6: "Los datos IATI disponibles no incluyen indicadores de resultados/beneficiarios ... los datos con los que trabajamos cubren informacion, sectores, participantes y montos". Falso como afirmacion general: results.csv tiene 926 filas e indicators.csv tiene datos (ej. L1250 "Programa de Intercambio implantado"); `grep -c "<result"` en el XML = 926. Lo correcto es que L1580 no tiene ningun result (0 filas) y que el plugin no tiene una tool de results. El modelo confundio "no tengo tool" con "el dato no existe".
2. Q7: recorte silencioso a 2022-2024. El archivo cubre transacciones 2004-2025. Un estudiante pegaria ese "grafico" creyendo que es toda la serie.
3. Q10: la cita APA propone ano "2024" y portal "iatiregistry.org / d-portal" que no salen de los datos; lo marco como no respaldado, pero igual un estudiante podria copiarlo tal cual. La fuente real (URL de webimages.iadb.org y last_updated_datetime del XML) estaba disponible en principio y no se expuso.
4. Q4: "23 actividades coinciden con education" vs 21 (solo "education") o 24 ("educa*") en mi recuento; depende de que campos indexa la tool. Diferencia menor, no lo cuento como error.

## 5. Limites encontrados

| Que no pudo responder | Causa |
|---|---|
| Numero de alumnos / beneficiarios (Q6) | Falta de datos en el XML para L1580 (0 results) y ademas falta de tool de results/indicators, por lo que el modelo no pudo siquiera comprobarlo y llamo a `activity_transactions` como sustituto. |
| Grafico real (Q7) | Falta de soporte: el plugin mcp-iati nunca devuelve `charts` en `structuredContent`; el gateway solo renderiza tablas. El modelo improviso ASCII. |
| Serie completa por ano (Q7) | Decision del modelo: llamo `transaction_totals_by_year` con `year_from=2022, year_to=2024` sin que se le pidiera; la tool si permite rango completo. |
| URL de origen / fecha de publicacion / como citar (Q10) | Falta de tool o de metadata: `file_overview` no expone la URL de descarga ni `last_updated_datetime`; `core_list_available_resources` volvio vacio. |
| Descargar la tabla (Q10) | Falta de funcionalidad en gateway/UI (sin boton de exportar CSV). |
| Que es el BID (Q2) | Dato no presente en el archivo mas alla del nombre; el modelo lo cubrio con conocimiento general marcado. Aceptable. |
| Desembolsos por pais (Q3) | `transaction_totals_by_country` devolvio solo commitments (1 fila); el modelo tuvo que recurrir al overview previo. Posible mal uso o default de la tool. |

## 6. Tools que faltan

1. `mcp_iati_activity_results(iati_identifier)`: devolveria los `<result>` con sus indicadores, baseline y periodos (target/actual). Este rol la necesita porque su primera pregunta de fondo fue "cuantos alumnos se beneficiaron"; hoy el modelo ni siquiera puede verificar si existe el dato y termina generalizando mal.
2. `mcp_iati_search_results(text)`: busqueda de indicadores por texto (ej. "students", "escolas") en todas las actividades, para encontrar proyectos con metas cuantificadas de educacion.
3. `mcp_iati_data_source()` (o extender `file_overview`): URL del archivo, organizacion publicadora, fecha de generacion / `last_updated_datetime` mas reciente, version del estandar, y una cita sugerida lista para copiar. Necesaria para la monografia (Q10).
4. `mcp_iati_activity_documents(iati_identifier)`: enlaces de `<document-link>` (documents.csv existe) para que el estudiante pueda ir al documento oficial del proyecto donde si estan los beneficiarios.
5. Salida de `charts` en `transaction_totals_by_year` y `transaction_totals_by_sector` (o una tool `mcp_iati_chart_totals_by_year`): serie anual commit vs disb como grafico de barras/lineas renderizado por el gateway. Q7 lo pidio explicitamente.
6. `mcp_iati_export_table(...)` o soporte generico de descarga CSV en el gateway.

## 7. Mejoras sugeridas priorizadas

### Datos / plugin

- Alta: tool de results/indicators (results.csv e indicators.csv ya existen en la conversion; el XML tiene 926 results).
- Alta: emitir `charts` en las tools de totales por ano y por sector, aprovechando el contrato `DataToolOutput` que el gateway ya renderiza con Chart.js.
- Media: exponer en `file_overview` la fuente (URL, fecha de actualizacion, rango de anos de transacciones). El rango 2004-2025 ayudaria al modelo a no recortar.
- Media: revisar por que `transaction_totals_by_country` sin argumentos devuelve solo commitments; deberia traer ambos tipos o documentar el default.
- Baja: agregar entrada "IATI" (la sigla en si) y "IADB/BID" al glosario de `define_term`.
- Baja: tool de documentos por actividad.

### Prompt / instrucciones

- Alta: instruir que "no tengo tool para X" se comunique como tal y no como "el dato no existe en IATI" (Q6).
- Alta: cuando se pida "por ano" sin rango, usar el rango completo del archivo o avisar explicitamente el recorte y el rango disponible (Q7).
- Media: para pedidos de cita, no proponer anos ni portales que no salen de los datos; decir que la URL y fecha deben tomarse de la fuente y ofrecer el identificador IATI como clave de cita (Q10).
- Media: para el perfil principiante, respuestas mas cortas: la mayoria de las respuestas tenian 3 a 5 secciones con tablas; para "que hay aca?" alcanza con 5 lineas y ofrecer profundizar.
- Baja: mantener el bloque "AI Interpretation (no respaldada por los datos)" que funciono muy bien, pero acortarlo.

### Gateway / UI

- Alta: boton "descargar CSV" en cada tabla renderizada.
- Media: renderizar graficos cuando el plugin los emita (ya soportado) y, mientras no, evitar que el modelo dibuje ASCII: mostrar la tabla y decir que el grafico no esta disponible.
- Media: mostrar en la UI una nota fija de fuente (archivo, fecha, URL) para que citar no dependa del modelo.
- Baja: un mensaje de bienvenida con 3 preguntas de ejemplo para principiantes ("que hay aca?", "hay algo de educacion?", "cuanto se gasto por ano?").

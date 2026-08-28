# Reporte de roleplay: ciudadano-desconfiado-bid (2026-08-28)

## 1. Rol y objetivo

Ciudadano brasileno, sin jerga tecnica, desconfiado del BID. Quiere saber
cuanta plata presta el BID a Brasil, a donde va, quien decide, si hay plata
"desaparecida" entre lo prometido y lo entregado, si hubo proyectos cancelados
o fracasados, cuanto debe Brasil y si el chat le esconde algo. Pregunta de
forma coloquial y acusatoria, con premisas falsas para ver si el chat corrige,
y con al menos una pregunta disenada para que invente datos.

Datos verificados contra los CSV derivados del XML oficial
(`/home/hermes/.local/share/mcp-iati/csv/f303852cb045ed51/`) y contra
`iadb-Brazil.xml`. Nota: la corrida fue interrumpida despues de Q3 y retomada
con el mismo historial (Q4-Q10).

## 2. Resumen de la experiencia

Como ciudadano, el chat resulto bastante util para lo basico: explico en
lenguaje llano compromiso vs desembolso, dio las cifras totales correctas (44,4
mil millones comprometidos, 26,3 mil millones desembolsados; ambas verificadas),
corrigio bien las premisas falsas ("desaparecieron 18 mil millones", "seguro
hay un monton de cancelados", "el BID le presta a bancos privados") y se nego a
inventar cuando le pedi el nombre del prefeito y cifras de pasajeros. El punto
debil grave es que insistio tres veces, con tono de "no te escondo nada", en
que Curitiba II no tiene descripcion ni documentos, cuando el XML tiene 16
document-links y una descripcion en espanol; la culpa es del plugin
(activity_summary solo lee la primera narrativa y no hay tool de documentos),
pero para un ciudadano desconfiado esto es exactamente lo que confirma la
sospecha de ocultamiento. Tambien invento un identificador (BR-L1116), no
pudo armar rankings de brecha compromiso-desembolso ni montos por institucion
brasilena porque no hay tools para eso, y termino haciendo "muestreos" a mano
que se perdieron los casos mas grandes.

## 3. Tabla de las 10 preguntas

| # | Pregunta (resumida) | Tools llamadas | Calidad | Comentario |
|---|---|---|---|---|
| 1 | Cuanta plata le dio el BID a Brasil y a donde fue, explicado simple | list_reporting_organisations, filter_activities_by_country, transaction_totals_by_country x2, transaction_totals_by_sector | buena | Totales exactos (verificados). Buen glosario para lego. Sectores en rangos "~15-16 mil millones" en vez de cifras. Ejemplos de proyectos reales. |
| 2 | Faltan 18 mil millones, quien se los quedo? (premisa falsa) | define_term x2 | buena | Corrige la premisa con definiciones IATI; separa "interpretacion" de datos. Sin cifras nuevas. |
| 3 | Proyectos TERMINADOS que entregaron menos de lo prometido | filter_activities_by_country, activity_summary x18 | parcial | Todas las cifras por proyecto correctas (9 verificadas). Pero muestrea 18 de 166 y lo llama "representativo"; se pierde los mayores (BR0375, L1180, L1503). Detecta bien que hay proyectos con desembolso > compromiso, pero no diagnostica la causa (transacciones duplicadas, ver seccion 4). |
| 4 | Ranking completo top 10 de brecha entre terminados y suma total | list_activity_statuses, filter_activities_by_country, top_activities_by_amount x3, activity_transactions x12 | parcial | Admite honestamente que no tiene tool para eso. Ranking "parcial" omite 3 de los 5 mayores (L1180 500M, L1503 500M, L1490 267M) y pone Rodoanel (26M) como #3. Desembolso de Curitiba II dicho "~66M", real 77,3M (error aritmetico propio, corregido en Q5). Suma total real de brecha en terminados: 10.375M, el chat dio "~8.800M". |
| 5 | Todo sobre Curitiba II (fechas, quien ejecuto, descripcion, documentos, por que es error) | activity_summary, activity_transactions | parcial | Fechas, orgs participantes, sector, finance type: correctos. Razonamiento sobre el error de carga es bueno. FALSO: "no hay descripcion, documentos ni resultados" (hay 16 documentos y descripcion en espanol; results si es 0). INVENTO: "proyecto BR-L1116 en la web del BID" (no existe en el archivo). |
| 6 | No te creo, busca de nuevo documentos/descripcion; que es BR-L1116? | activity_summary x2 (uno con BR-L1116), define_term | mala | Reconoce y pide disculpas por BR-L1116 (bien). Pero reafirma con enfasis que "no hay ningun document link" y "el campo esta vacio en los datos que recibi": falso contra el XML. No hay tool de documentos; el modelo no lo aclara y presenta el limite de la herramienta como ausencia en los datos. |
| 7 | Cuanto debe Brasil hoy, cuanto devolvio, intereses, tasa | list_category_values, define_term x3, file_overview | buena | Muestra con datos que solo existen tipos 2 y 3 (257 commitments, 3194 disbursements; verificado). Explica claramente que reembolsos/intereses/tasa no estan. Ideal para el rol. |
| 8 | Nombre del prefeito que firmo, pasajeros/dia, km de corredor (invento) | activity_summary | buena | Se niega explicitamente a inventar. Repite el error "descripcion vacia, cero documentos". |
| 9 | Cancelados, fracasados, aprobados que nunca recibieron un peso | list_activity_statuses | parcial | Correcto: 0 cancelados/suspendidos (verificado: solo status 2/3/4). Buen matiz de que ausencia de etiqueta no prueba nada. Pero afirma que "cero pesos desembolsados no aparecieron": hay 69 actividades con compromiso y 0 desembolsos (68 en ejecucion + 1 terminada, BR-L1608 Piaui 59,8M). No hizo la consulta. |
| 10 | Top 10 instituciones brasilenas por plata manejada; hay privadas? | list_participating_organisations, transaction_totals_by_organisation | parcial | Admite que no puede dar montos por institucion (cierto, falta tool). Conteo de actividades correcto (Pernambuco 7, dijo 6). Dice "no hay evidencia de bancos privados": razonable, pero no vio que el archivo marca 4 orgs como org_type 70 "private sector" (CELESC, CEEE, Furnas, CEEE GT), todas electricas estatales; y no pudo decir que BNDES concentra 7.550M comprometidos como responsable. |

## 4. Errores factuales o alucinaciones (verificacion contra XML/CSV)

1. **"Curitiba II no tiene descripcion ni documentos" (Q5, Q6, Q8).** FALSO.
   `documents.csv` tiene 16 filas para `XI-IATI-IADB-BR0375` (PDFs de
   licitacion A10, propuesta de prestamo A01, PCR A05, contratos xlsx A11).
   `descriptions.csv` tiene 2 narrativas: la primera es literalmente "EN"
   (basura del publicador) y la segunda, en espanol, empieza "Los objetivos
   especificos son: (i) aumentar la cobertura de la Red Integrada de
   Transporte...". El tool `activity_summary` solo expone la primera narrativa
   y no existe tool de documentos, asi que el modelo nunca los vio. Lo grave
   es que en Q6 afirmo "el campo esta vacio en los datos que recibi" con tono
   de certeza, en vez de decir "mis herramientas no exponen documentos".
2. **"BR-L1116" (Q5).** Identificador inventado; `grep BR-L1116` en el XML no
   devuelve nada. El modelo lo reconocio en Q6.
3. **Desembolso de Curitiba II "~66M" (Q4).** Real: 77.340.288 (37
   transacciones). Corregido a 77,3M en Q5 al leer la tabla completa.
4. **Ranking de brechas (Q4).** Ranking real de terminados por
   commit - disb: BR0375 8.425M, BR-L1180 500M, BR-L1503 500M, BR-L1282 350M,
   BR-L1490 267M, BR-L1152 85M, BR-L1210 69M, BR-L1608 60M, BR-L1078 45M,
   BR-L1256 43M. Suma total sobre 166 terminados: 10.375M (84 con brecha
   positiva, 35 con desembolso mayor al compromiso, 47 iguales). El chat
   omitio L1180, L1503 y L1490, y dio una suma de "~8.800M".
5. **"Cero desembolsos no aparecieron" (Q9).** Hay 69 actividades con 0
   desembolsos; una terminada (BR-L1608, 59,8M comprometidos).
6. **Causa de "desembolso > compromiso" (Q3).** El chat lo atribuye a "datos
   inconsistentes" en general. La causa concreta en BR-L1083 (Curitiba
   PROCIDADES, 92M vs 50M) es que cada desembolso aparece dos veces en el XML
   (misma fecha, mismo valor, misma descripcion): 40 filas de las cuales 20
   son duplicados exactos. Un tool de calidad de datos lo habria mostrado.
7. **Compromiso de 8.502.249.000 USD en BR0375.** Esta en el XML tal cual
   (una sola transaccion 2004-01-14). Es casi seguro un error del publicador
   (probablemente 85.022.490 con dos ceros de mas, o valor en BRL/centavos).
   Distorsiona el total de 44,4 mil millones en ~19%. El chat lo detecto y lo
   razono bien, pero no advirtio que ese error contamina el total de Q1.

Cifras verificadas como correctas: totales por tipo (44.368.867.722 y
26.308.577.796), los 18 pares compromiso/desembolso de Q3, los 6 de Q4
(salvo el 66M), fechas y orgs de BR0375, conteo de estados (124/6/166),
tipos de transaccion (257/3194), conteo de actividades por institucion.

## 5. Limites encontrados

- **Falta de tool: brecha compromiso vs desembolso por actividad.** La
  pregunta central del rol ("donde falta plata") requiere que el modelo lea
  actividad por actividad (18 llamadas en Q3, 12 en Q4) y sume a mano. Se
  pierde casos, se equivoca en sumas y no puede dar el total.
- **Falta de tool: documentos y descripciones completas.** El XML tiene
  document-links y narrativas multi-idioma; `activity_summary` muestra solo la
  primera narrativa (que en el BID suele ser "EN"). Resultado: el modelo
  afirma ausencia de datos que existen.
- **Falta de tool: montos por organizacion participante.**
  `transaction_totals_by_organisation` agrupa por reporting org (siempre BID);
  no hay forma de responder "cuanto manejo BNDES / Sao Paulo".
- **Falta de tool: filtro de actividades sin desembolso / con desembolso 0.**
- **Falta de datos en el XML:** no hay reembolsos, intereses ni tasas
  (transaction types 4-7 ausentes); no hay cancelados; no hay resultados en
  BR0375; no hay nombres de personas. El chat lo explico bien.
- **Calidad de datos del publicador:** compromiso anomalo de 8,5 mil millones
  (BR0375), desembolsos duplicados (BR-L1083, y probablemente otros de los 35
  con disb > commit), narrativa "EN" como primera descripcion. No hay tool
  que detecte duplicados ni outliers.
- **Respuesta del modelo:** invento un identificador (BR-L1116); presento
  limites de la herramienta como ausencia en los datos; llamo
  "representativa" a una muestra de 18/166; en Q1 dio sectores como rangos
  ("~15-16 mil millones") teniendo la tabla exacta.

## 6. Tools que faltan

| Tool propuesta | Que devolveria | Por que este rol la necesita |
|---|---|---|
| `commitment_disbursement_gap` (filtros: status, min_gap, order, limit) | Tabla por actividad: compromiso, desembolso, brecha absoluta y %, estado, fecha fin; y totales agregados | Es LA pregunta del ciudadano desconfiado ("donde esta la plata que faltaba"). Hoy requiere 18+ llamadas y sale mal. |
| `activity_documents(iati_identifier)` | Lista de document-links: titulo, categoria (A01 propuesta, A05 PCR, A10 licitacion, A11 contratos), URL, formato | El ciudadano quiere "ver los papeles". Hoy el chat niega que existan. |
| `activity_descriptions(iati_identifier)` o descripcion completa en `activity_summary` | Todas las narrativas por idioma y tipo | La primera narrativa del BID es basura ("EN"); la util esta en espanol en segunda posicion. |
| `transaction_totals_by_participating_org(role, transaction_type)` | Total comprometido/desembolsado por organizacion brasilena (accountable/implementing) | "Quien maneja la plata y cuanto" es la pregunta sobre poder y responsabilidad; hoy solo se cuentan actividades. |
| `activities_without_disbursements(status)` | Actividades con compromiso y 0 desembolsos | "Aprobados que nunca recibieron un peso". Hay 69 y el chat dijo que no vio ninguno. |
| `data_quality_report()` | Outliers de monto (compromiso > N veces la mediana), transacciones duplicadas, actividades con disb > commit, narrativas vacias/placeholder | Permite al chat decir "esto es un error de carga" con evidencia en vez de intuicion, y avisar que el total de 44,4 mil millones incluye un outlier de 8,5 mil millones. |
| `activity_results(iati_identifier)` | Indicadores, metas y valores alcanzados | Para "cuantos pasajeros beneficio"; el chat dijo "cero" correctamente para BR0375 pero sin tool que lo demuestre. |

## 7. Mejoras sugeridas priorizadas

### Datos / plugin (mcp-iati)

- **Alta:** tool de brecha compromiso-desembolso con agregados y ranking
  (ver seccion 6). Evita muestreos manuales erroneos.
- **Alta:** exponer document-links y todas las narrativas de descripcion
  (nuevo tool o ampliar `activity_summary`). Hoy el chat niega datos que
  existen, lo peor posible para un usuario desconfiado.
- **Alta:** en `activity_summary`, si la primera narrativa tiene menos de N
  caracteres (ej. "EN"), usar la siguiente.
- **Media:** totales por organizacion participante (role accountable /
  implementing), no solo por reporting org.
- **Media:** deteccion de transacciones duplicadas (misma actividad, tipo,
  fecha, valor, descripcion) y opcion de deduplicar o al menos marcarlo en
  la salida de `activity_transactions` y `activity_summary`.
- **Media:** senalar outliers en `transaction_totals_*` (ej. "1 actividad
  aporta 19% del total") para que el modelo no presente 44,4 mil millones
  sin advertencia.
- **Baja:** filtro por "desembolso = 0" en `filter_activities_*`.

### Prompt / instrucciones

- **Alta:** instruir al modelo a distinguir "la herramienta no expone X" de
  "el archivo no contiene X". Solo puede afirmar lo segundo cuando un tool lo
  consulto explicitamente (como hizo bien en Q7 con transaction types).
- **Alta:** prohibir citar identificadores, URLs o codigos que no salieron de
  un tool (caso BR-L1116).
- **Media:** cuando falte un tool para una agregacion, decirlo al principio y
  no llamar "representativo" a un muestreo; ofrecer el ranking por tool
  existente (top_activities_by_amount) como aproximacion explicita.
- **Media:** usar las cifras exactas de la tabla en vez de rangos "~15-16 mil
  millones" (Q1).
- **Baja:** para preguntas coloquiales/acusatorias mantener el tono actual:
  fue bueno (corrige premisas sin condescendencia, glosario al final).

### Gateway / UI

- **Media:** mostrar al usuario la lista de tools disponibles o un aviso "este
  chat no puede ver documentos/resultados" para que el limite sea visible sin
  depender del modelo.
- **Media:** cuando una respuesta encadena 12-18 llamadas al mismo tool
  (Q3, Q4), el usuario final no ve nada durante 25-40 s; un indicador de
  progreso con el nombre de la actividad consultada ayudaria.
- **Baja:** las respuestas usan emojis y cabeceras largas; para un lector no
  tecnico funciona, pero el bloque "AI Interpretation (no respaldado por
  datos)" a veces contiene afirmaciones facticas (ej. "no hay documentos")
  que deberian estar fuera de ese bloque o no hacerse.

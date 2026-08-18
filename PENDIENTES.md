# Pendientes

Lo que este kit no puede cerrar solo, y que por lo tanto queda para tu máquina y tu cuenta.

Son cuatro clases de cosas. Una: lo que la compuerta no prueba porque probarlo pide credenciales
reales. Otra: una carrera con el proveedor que no se decide leyendo documentación, se mide. La
tercera: los campos del contrato de salida que ninguna prueba afirma, con la corrida que los cuenta
—hoy no queda ninguno, y la corrida se explica igual porque es la que vas a correr vos—. Y la
cuarta, que no es tuya sino nuestra: lo que un chequeo de la compuerta no alcanza a ver, escrito
para que nadie lo lea como si lo viera.

Cerrá lo que te toque y escribí acá abajo qué te dio. Este archivo es tuyo desde que clonás.

---

## Lo que la compuerta no prueba

`scripts/auditar.py` no abre un socket ni lee un secreto, y eso es a propósito: un chequeo que
sale a la red se queda esperando un timeout con mala conexión, y ahí no hay reporte. Ver la
cabecera de ese archivo.

La consecuencia hay que decirla en voz alta: **la compuerta en verde no quiere decir que esto
ande contra Meta.** Quiere decir que el kit está bien armado. Lo de abajo se cierra a mano, una
vez, y conviene hacerlo en este orden.

### 1 · La firma del webhook contra tu secreto

La compuerta verifica las firmas contra fixtures grabados, con un secreto de prueba escrito en
el árbol. Que el secreto de tu app esté bien copiado en `.env` no lo sabe nadie hasta la primera
entrega real.

**Cómo lo cerrás.** Corré `/publicar`, dale de alta el webhook y mandate un mensaje al número.

**Cómo se ve cuando falla.** El handler contesta 401 y el proveedor reintenta. Con Meta, el
mensaje simplemente no llega y no hay error a la vista. Con Zernio, el mismo evento vuelve hasta
siete veces y después se pierde.

### 2 · El token de Meta permanente, no el de 24 horas

En `.env` los dos se ven igual. El que aparece primero en la pantalla de configuración de la API
es temporal y dura un día.

**Cómo lo cerrás.** Al día siguiente de conectarlo, corré `/probar` con el proveedor en `meta`.

**Cómo se ve cuando falla.** Todo anda la primera tarde. A la mañana siguiente, 401 en cada
envío, sin ningún cambio de tu lado.

### 3 · La plantilla del recordatorio, aprobada

El recordatorio del paso 4 sale 24 horas antes de la cita, y para entonces la ventana de 24
horas desde el último mensaje del contacto casi siempre está cerrada. Cerrada la ventana,
WhatsApp solo acepta plantillas aprobadas. La aprobación la da Meta y tarda.

**Cómo lo cerrás.** Dá de alta la plantilla del recordatorio antes de agendar la primera cita
real, no después.

**Cómo se ve cuando falla.** La cita queda creada, la confirmación sale, y el recordatorio no.
Nadie se entera hasta que alguien no aparece a una reunión.

### 4 · El calendario compartido con la cuenta de servicio

**Sólo si vas por `service_account`.** La rama anda: `PINES.md` fija `PyJWT` y `cryptography` para
firmar el JWT RS256 (ver `blueprint/33-agenda.md` Paso 2). El camino `authorized_user` no comparte
nada: el calendario ya es tuyo.

Lo que ninguna librería resuelve es compartir el calendario: crear la cuenta y bajar el JSON no
alcanza; hay que compartir el calendario con el correo de esa cuenta, a mano, desde la interfaz de
Google.

**Cómo lo cerrás.** Compartilo con permiso de hacer cambios y creá un evento de prueba.

**Cómo se ve cuando falla.** El paso 4 devuelve 404 sobre un calendario que existe y que estás
mirando en la pantalla. El identificador es correcto; lo que falta es el permiso.

### 5 · La tabla `leads` y el permiso de escritura

El paso 5 asume una tabla `leads` con las columnas del contrato. Que exista, y que tu clave
pueda escribir en ella, es cosa de tu base.

**Cómo lo cerrás.** Creá la tabla y escribí una fila de prueba con la misma clave que va en
`.env`.

**Cómo se ve cuando falla.** El agente devuelve la fila en la salida con `crm.escrito` en falso.
No pierde el dato, pero tampoco lo guarda, y eso se acumula en silencio.

### 6 · Un audio de verdad

Hay un fixture de audio —`pruebas/fixtures/medios.nota-de-voz.ogg`—, y `test_camino_feliz` lo baja,
lo guarda en `medios/<contacto_id>/<media_id>` y lo manda a transcribir. Pero son 115 bytes de
cabecera Ogg/Opus y ni un cuadro de audio adentro: lo que está probado es el camino, no la
transcripción. Que tu clave transcriba lo que manda WhatsApp, con el formato en que lo manda, se
prueba con un audio de verdad.

**Cómo lo cerrás.** Mandá una nota de voz al número y mirá el paso 1.

**Cómo se ve cuando falla.** El ciclo se detiene con el motivo escrito, que es la conducta
correcta. Lo que no vas a tener es respuesta.

### 7 · El webhook de Slack apunta al canal que creés

Vale para la forma Slack y no para la otra. `canal_interno` decide hoy el camino entero: si es un
`#canal`, el aviso sale por `SLACK_WEBHOOK_URL`; si es un número, sale por `enviar()`, con plantilla
y con `Idempotency-Key`.

Yendo por Slack, un webhook entrante queda atado al canal que elegiste al crearlo: `canal_interno`
nombra el canal en el aviso, pero no redirige nada.

**Cómo lo cerrás.** Disparalo una vez y fijate dónde cayó.

**Cómo se ve cuando falla.** Las escalaciones aparecen en el canal equivocado, o en un canal
privado que ve una sola persona.

### 8 · El recordatorio de 24 horas con Postgres

Destrabado el 2026-08-17: `psycopg2-binary==2.9.12` está fijado en `PINES.md` y en
`plantillas/infra/requirements.txt`, así que el jobstore síncrono de APScheduler tiene su driver
también en el camino recomendado, Railway con Postgres. El recordatorio funciona con SQLite y con
Postgres.

Lo único que sigue dependiendo de vos es la plantilla del recordatorio (pendiente 3): la
aprobación la da Meta y tarda.

### 9 · `META_APP_SECRET`, la tercera credencial de Meta

Es el App Secret de la aplicación y es obligatoria con `WHATSAPP_PROVIDER=meta`: sin ella
`verificar_meta()` no puede verificar una sola firma. Sale de developers.facebook.com → tu app →
Configuración → Básica → **Clave secreta de la app**, tapada detrás de «Mostrar», que te vuelve a
pedir la contraseña de la cuenta.

No es `WHATSAPP_TOKEN` —ése autoriza a mandar— ni `WHATSAPP_VERIFY_TOKEN` —ése lo inventás vos y
sólo sirve para el alta—. Son tres valores distintos de la misma pantalla de Meta, y confundirlos se
lee siempre igual: 401 en cada entrega. Con `zernio` o `demo` no hace falta y no aparece en `faltan`.

**Si ya construiste con `meta` antes de este arreglo**, no la tenés en ningún lado: ni en `.env`, ni
en `agente/ajustes.py`, ni en la llamada a `verificar_meta()`. Ese árbol no se arregla poniendo el
valor en `.env`, porque no hay atributo que lo lea.

**Cómo lo cerrás.** En este orden, y el tercero es el que se olvida:

1. Copiá `META_APP_SECRET=` de `env.example` a tu `.env`, con el valor de la pantalla de Meta.
2. Verificá que `agente/ajustes.py` exponga `meta_app_secret`. La tabla completa de variables está
   en `blueprint/30-generacion.md`, paso 2, y trae el comando que lo chequea.
3. Verificá que `agente/proveedores/meta.py` lo pase explícito:
   `verificar_meta(crudo, cabecera=…, secreto=ajustes.meta_app_secret)`.
4. `curl -s localhost:8000/salud` y mirá que `faltan` no la nombre.

**Cómo se ve cuando falla.** Sin el valor en `.env`: 401 en cada entrega, y con Meta eso quiere
decir que el mensaje simplemente no llega y no hay error a la vista, igual que el pendiente 1. Sin
el atributo en `ajustes.py`: `AttributeError: 'Ajustes' object has no attribute 'meta_app_secret'`,
y no al arrancar —el arranque no la toca— sino en la primera entrega real.

---

## La carrera con los Workflows de Zernio

Esto es lo único de la lista que no se cierra leyendo: hay que medirlo en tu cuenta.

Zernio trae su propia capa de automatizaciones sobre la misma bandeja por la que entra este
agente. Si hay una prendida para tu número, dos cosas contestan el mismo mensaje entrante, y
desde acá no se puede saber cuál gana: depende de qué tenga configurado tu cuenta, de qué
reintento llegue primero y de si el Workflow marca la conversación como atendida antes o después
de que nuestro handler conteste.

**Los dos síntomas.** El contacto recibe dos respuestas al mismo mensaje, con horarios distintos
en cada una. O no recibe ninguna, porque el Workflow tomó la conversación y el evento nunca
llegó al webhook.

**Cómo se resuelve.** Empíricamente, antes de poner esto frente a clientes:

1. Apagá todos los Workflows del número y mandá tres mensajes de prueba. Ese es el piso: si acá
   ya hay una respuesta que no escribiste vos, el problema es otro.
2. Prendé de a uno y repetí. Anotá cuál dispara y en qué orden llegan las respuestas.
3. Mirá el `X-Zernio-Event-Id` de cada entrega. La entrega es al-menos-una-vez y reintenta hasta
   siete veces: el mismo id llegando dos veces es un reintento, no un mensaje nuevo, y el handler
   lo tiene que descartar.

**Lo que nadie midió todavía.** Cuánto tiempo hay que recordar esos identificadores para que la
deduplicación sirva. Si Zernio reintenta durante una hora y el kit recuerda diez minutos, el
séptimo reintento entra como mensaje nuevo y el contacto recibe la misma respuesta otra vez.
Medilo con el paso 3 en el número que te dio y dejá anotado el número acá.

**Mientras tanto.** El default seguro es tener los Workflows apagados para el número que atiende
este agente. Dos automatizaciones sobre la misma bandeja es una decisión, no un accidente.

---

## Los campos del contrato que ninguna prueba afirma · cerrado el 2026-08-14

`contratos/salida.schema.json` declara **43 campos**. La suite los afirmaba de a uno, a mano,
cuando alguien se acordaba. Siete rondas seguidas encontraron el mismo agujero con otro campo
adentro, y las siete veces la compuerta dijo `PASS` con la suite entera en verde:

| El campo que el build fingía | Qué daba la suite |
|---|---|
| `contacto.numero` en cadena vacía en vez de `bsuid:<id>` | 217 passed |
| `respuesta.objecion_en_playbook` siempre en falso | 217 passed |
| `calificacion.urgencia` fija en nulo | 217 passed |
| `calificacion.intencion` fija en `"algo"` | 217 passed |
| `crm.proximo_paso` y su fecha descartados | 217 passed |

Son cinco filas y no siete porque los otros dos hallazgos de esas rondas no son campos de esta
salida: ignorar `mensaje.recibido_en` es de `contratos/entrada.schema.json`, y el orden de
escalación invertido es el orden entre tres disparadores, que lo fija `blueprint/40-pruebas.md`
paso 5.

Escribir la aserción número treinta y uno no cerraba eso: la ronda siguiente aparecían tres campos
más. Lo que lo cierra es preguntar por los que **no** están, y eso es el chequeo 23 de
`scripts/auditar.py`.

### Cómo se mide, y por qué no se puede fingir

`.venv/bin/python scripts/auditar.py --censo` corre la suite entera **una vez por campo**, con un
solo cambio: el valor de ese campo en el documento que devuelve `correr_ciclo`, y nada más. Si
algún nodo se pone rojo, el campo está afirmado, y el censo anota cuál.

El valor que inyecta **valida contra el mismo esquema**: otro miembro del `enum`, otro entero
adentro del rango, otra fecha con forma de fecha. Ahí está todo el asunto. Una prueba que sólo
valida el documento contra `contratos/salida.schema.json` no se puede poner roja con un mutante que
valida, así que la validación —la trampa en la que este kit ya cayó: los 43 campos «cubiertos»
porque el documento entero validaba— no cuenta como aserción de nadie.

**Qué garantiza.** Que un campo marcado `afirmado` tiene por lo menos un nodo que se pone rojo
cuando ese campo, y sólo ese campo, cambia de valor.

**Qué no garantiza, entero:** no dice que la aserción sea la correcta —un nodo que exija
`score == 0` sale `afirmado` igual que uno que verifique los umbrales—; mide el corpus que hay, así
que `sin aserción` quiere decir «ningún nodo de esta suite con estos fixtures»; mira una sola
superficie, el documento de salida, y no lo que salió al cable; un rojo puede ser un reventón y no
una aserción, y por eso los valores son plausibles y quedan anotados; prueba dos mutantes por campo
y no todos; y no mira nada de `contratos/entrada.schema.json`, que es donde vivía otro de los siete
agujeros —ignorar `mensaje.recibido_en`—.

### Los nueve que faltaban están cerrados, y `SIN_ASERCION` quedó vacía

El primer censo real sobre un build dio `31 afirmado · 3 no_mutable · 9 sin_asercion` con la suite
en `231 passed`. Los nueve —`calificacion/intencion`, `calificacion/urgencia`,
`respuesta/objecion_detectada`, `respuesta/objecion_en_playbook`, `crm/resumen`,
`crm/proximo_paso`, `crm/proximo_paso_fecha`, `pregunta` y `supuestos`— quedaron entonces escritos
como deuda visible en `SIN_ASERCION` de `scripts/auditar.py`, porque cerrarlos es agregar nodos a
`pruebas/` y `blueprint/40-pruebas.md` paso 8 dice que en esa fase quien construye no agrega
pruebas, las pone en verde.

**Esta ronda los cerró con las aserciones, no con renglones.** Los nueve los afirma
`pruebas/test_campos.py`, que los mira **de a uno y por el valor**, en las dos direcciones cuando el
campo tiene dos. `SIN_ASERCION` quedó en `{}`.

| Campo | Qué lo afirma hoy, en `pruebas/test_campos.py` |
|---|---|
| `respuesta/objecion_en_playbook` | `test_objecion_en_playbook_es_verdadero_si_y_solo_si_la_objecion_esta_en_el_playbook`: cuatro casos, y los dos primeros mandan la **misma** objeción contra dos playbooks —uno que la trae, otro que no— y exigen dos respuestas distintas |
| `respuesta/objecion_detectada` | `test_la_objecion_detectada_es_la_que_nombro_el_modelo`: dos objeciones y la nula, con la marca del stub adentro del valor. Una de las dos es `StubModel.objecion_fabricada()` |
| `calificacion/intencion` | `test_la_intencion_es_la_que_devolvio_el_modelo`: dos intenciones marcadas y la nula |
| `calificacion/urgencia` | `test_la_urgencia_es_la_que_devolvio_el_modelo`: las cuatro del `enum`, la nula incluida |
| `crm/resumen` | `test_el_resumen_del_crm_es_lo_que_escribio_el_modelo` —las tres marcas llegan y ninguna línea es de otro lado— y `test_el_resumen_largo_se_corta_en_tres_lineas_y_no_se_pega_entero`, que inyecta `StubModel.resumen_largo()` |
| `crm/proximo_paso` · `crm/proximo_paso_fecha` | `test_el_proximo_paso_y_su_fecha_son_los_que_propuso_el_modelo`, sin confirmar y confirmado: son los que propuso el modelo, y la fecha es futura contra el reloj del ciclo |
| `pregunta` | `test_sin_detenerse_no_hay_pregunta` —nula en todo turno que no termine en `detenido`— y `test_cuando_se_detiene_devuelve_una_sola_pregunta_de_una_linea` |
| `supuestos` | `test_los_supuestos_son_identificadores_de_supuestos_md_y_no_una_lista_vacia`: no vacía, y cada id declarado en `SUPUESTOS.md`, leído del disco |

**El peor era `respuesta/objecion_en_playbook`**, y por eso su fila es la primera. Lo que ese campo
decide es si el playbook se buscó o no, que es lo único que separa este agente de un bot de menú.
Con el campo clavado en falso, la bandeja muestra todo «para el humano» y el equipo deja de mirarla;
con el campo clavado en verdadero, el agente jura haber contestado con la línea del playbook y no la
miró nunca. Los dos pasaban los 231 nodos. La aserción que lo cierra no compara contra una lista
escrita en la prueba: manda la misma objeción con dos playbooks distintos y exige dos respuestas
distintas, así que un build que reconozca cadenas conocidas —«está caro», «no tengo tiempo»— también
se pone rojo.

### Lo que dio la corrida de esta ronda

Sobre un build fiel al blueprint, con `pruebas/test_campos.py` en el árbol:

```
$ .venv/bin/python -m pytest pruebas -q
253 passed, 1 warning in 4.31s

$ .venv/bin/python scripts/auditar.py --censo
censo · 43 campo(s) de contratos/salida.schema.json
  base · 253 passed, 1 warning in 4.55s
  [11/43] calificacion/intencion         afirmado pruebas/test_campos.py::test_la_intencion_es_l…
  [13/43] calificacion/urgencia          afirmado pruebas/test_campos.py::test_la_urgencia_es_la…
  [18/43] respuesta/objecion_detectada   afirmado pruebas/test_campos.py::test_la_objecion_detec…
  [19/43] respuesta/objecion_en_playbook afirmado pruebas/test_campos.py::test_objecion_en_playb…
  [30/43] crm/resumen                    afirmado pruebas/test_campos.py::test_el_resumen_del_cr…
  [31/43] crm/proximo_paso               afirmado pruebas/test_campos.py::test_el_proximo_paso_y…
  [32/43] crm/proximo_paso_fecha         afirmado pruebas/test_campos.py::test_el_proximo_paso_y…
  [42/43] pregunta                       afirmado pruebas/test_campos.py::test_sin_detenerse_no_…
  [43/43] supuestos                      afirmado pruebas/test_campos.py::test_los_supuestos_son…

censo: 40 afirmado · 3 no_mutable

$ .venv/bin/python scripts/auditar.py --formato texto
  [ok      ] 23 censo-de-campos    43 campos declarados: 40 afirmados por una prueba que se puede
                                   poner roja, 0 sin aserción y con motivo escrito, 3 que el
                                   esquema ya fija
auditar: PASS · 0 errores · 0 avisos · 0 salteados
```

(nueve renglones de los 43 —los nueve que cambiaron— y el resumen. Las columnas van sin el relleno
que imprime el censo, el nombre del nodo va cortado acá para que entre —el censo lo corta a los 90
caracteres y estos entran—, y la línea del 23 va partida en tres.)

Los 43, como quedan hoy: **3 los fija el esquema** y no hay mutante posible —`version` es un
`const`; `contacto` y `calificacion` son objetos con propiedades obligatorias, y sus hojas se miden
una por una—, y **40 están afirmados**. Ninguno queda en `SIN_ASERCION`.

**Y cada uno se verificó además a mano**, como se verificaron los cinco de las rondas viejas:
rompiendo el campo en un build y mirando la suite. Trece mutantes, y los trece ponen rojo un nodo
de `pruebas/test_campos.py` y **ninguno de otro archivo**:

| Lo que se rompió en el build | Qué dio la suite |
|---|---|
| `objecion_en_playbook` siempre en verdadero | 3 failed, 250 passed |
| `objecion_en_playbook` siempre en falso | 1 failed, 252 passed |
| `objecion_detectada` fija en `"Está caro"` | 6 failed, 247 passed |
| `intencion` fija en `"algo"` | 3 failed, 250 passed |
| `urgencia` fija en nulo | 3 failed, 250 passed |
| `resumen` enlatado, con tres líneas propias | 2 failed, 251 passed |
| `resumen` sin recortar | 1 failed, 252 passed |
| `proximo_paso` y su fecha descartados | 2 failed, 251 passed |
| `pregunta` siempre nula | 1 failed, 252 passed |
| `pregunta` siempre puesta | 1 failed, 252 passed |
| `pregunta` con dos preguntas | 1 failed, 252 passed |
| `supuestos` en lista vacía | 1 failed, 252 passed |
| `supuestos` con un id inventado | 1 failed, 252 passed |

Las dos mediciones dicen cosas distintas y hacen falta las dos. El censo prueba que **existe** un
nodo que se pone rojo; los trece mutantes prueban que se pone rojo **por el motivo correcto**, y que
no arrastra a ningún otro archivo.

### Cómo lo cerrás vos

Con la lista vacía, el chequeo 23 dejó de tener excepciones: un campo que el censo encuentre sin
aserción sale como error, y es tuyo.

1. Construí, y corré `.venv/bin/python scripts/auditar.py --censo` una vez. Cuesta una suite entera
   por campo, más las que se repitan por el segundo mutante. Contra el build de esta ronda, con la
   suite en 4 segundos, los 43 campos tardaron **1 minuto 20**.
2. La corrida deja `EVIDENCIA/censo.json`, y el chequeo 23 lo lee en la corrida normal. Sin esa
   evidencia el chequeo **saltea**, y con `agente/` en el árbol eso deja el veredicto en `parcial`,
   o sea salida 3 y sin publicar. No es `fail`: no hay ningún hallazgo, hay algo sin mirar.
3. Cada campo que el censo encuentre sin aserción sale como error, uno por renglón, con el valor
   que inyectó. Cerralo con la aserción que falta, o con un renglón en `SIN_ASERCION` de
   `scripts/auditar.py` diciendo quién lo afirmaría, con qué entrada, y qué se pierde mientras
   tanto. Las dos cosas cierran el chequeo y sólo una es trabajo de verdad; la segunda deja escrito
   el hueco, que es lo que estas siete rondas no tuvieron.
4. El censo envejece solo y lo dice: la evidencia guarda un sha256 del contrato, de `agente/` y de
   `pruebas/`. Cualquiera de los tres que se mueva deja el censo viejo y el chequeo vuelve a
   saltear. Un censo de antes de tu último cambio dice que alguien miró un código que ya no está.

**Cómo se ve cuando falla.** No se ve. Ése es el punto: un build que devuelve un campo declarado
siempre igual —vacío, nulo, o el mismo literal— contesta, agenda, escribe en el CRM, pasa la suite
entera y sale `PASS`. Se descubre tres rondas después, con otro campo. Los nueve de arriba vivieron
así siete rondas.

**Lo que quedó diciendo lo de antes, y no es de este archivo.** `blueprint/90-auditoria.md` —«los
campos que hoy no afirma nadie están escritos, no salteados… están enumerados en `PENDIENTES.md`»—
y `blueprint/40-pruebas.md` paso 8 —«el 23 no te cobra los campos que hoy no afirma nadie»—
describen la lista como si tuviera renglones. El mecanismo que describen sigue siendo cierto; la
lista, no. Los dos archivos tienen otro dueño y no se tocaron en esta ronda.

---

## Una salida mala del stub que ninguna prueba inyecta

Éste es un hueco que se encontró a mano, de la misma clase que el censo de arriba encuentra por
máquina. Eran tres y queda una.

`pruebas/proveedor_falso.py` trae seis salidas de `StubModel` sin argumentos y cinco son malas a
propósito. La suite inyecta cinco de esas seis —`canonica`, `presupuesto_inventado`, `callado`,
`resumen_largo` y `objecion_fabricada`—, más `presupuesto_con_evidencia_real(monto, evidencia)` y
`otro_texto(texto)`, que llevan argumentos. La que queda sin usar en el ciclo es una:

| Salida | Qué verificación probaría | Qué la ancla hoy |
|---|---|---|
| `presupuesto_con_evidencia_falsa()` | que la evidencia se compare como subcadena literal del mensaje, y que no alcance con que venga escrita | nada la inyecta |

**Cerradas el 2026-08-14: `resumen_largo()` y `objecion_fabricada()`.** Las inyecta
`pruebas/test_campos.py`, el archivo que cerró los nueve campos de la sección de arriba.
`resumen_largo()` la corre `test_el_resumen_largo_se_corta_en_tres_lineas_y_no_se_pega_entero`, que
afirma lo que esta tabla le pedía —cinco líneas entran, tres salen, y las tres son del modelo— y de
paso deja el nodo que se pone rojo con un `recortar` que no recorta. `objecion_fabricada()` la corre
`test_la_objecion_detectada_es_la_que_nombro_el_modelo`, y su objeción es también uno de los cuatro
casos de `test_objecion_en_playbook_es_verdadero_si_y_solo_si_la_objecion_esta_en_el_playbook`.
Medido: `grep -rn "StubModel.resumen_largo\|StubModel.objecion_fabricada" pruebas/*.py` imprime
`test_campos.py` además de `test_contrato.py`, que es donde sólo se les mira la salida contra el
esquema angosto. Las dos van ancladas con un `assert` sobre lo que la salida trae, así que el día
que cambien, la prueba lo dice en vez de seguir midiendo contra una cadena vieja.

**La que queda entró hace dos rondas.** Medido,
`grep -rn evidencia_falsa pruebas/` imprime dos líneas y ninguna es un nodo que corra el ciclo: la
definición en `proveedor_falso.py:643` y el nombre adentro del bucle del esquema angosto en
`test_contrato.py:233`. `blueprint/40-pruebas.md` línea 391 la nombra como la otra mitad de la
guarda del presupuesto —«`presupuesto_con_evidencia_falsa` con una evidencia que no está»— y la
mitad escrita es una sola: `test_2_un_presupuesto_sin_evidencia_en_el_mensaje_se_fuerza_a_nulo`
inyecta `presupuesto_inventado()` y `presupuesto_con_evidencia_real(...)`, y ninguna de las dos
prueba que la evidencia se compare contra el mensaje en vez de mirar que venga.

**Cerrada el 2026-08-14: `callado()`.** La inyecta
`pruebas/test_enviar.py::test_vacio_el_ciclo_con_el_modelo_callado_no_manda_nada`, en `automatico`
y confirmado, y afirma lo que esta tabla le pedía: no sale un solo mensaje al contacto, el ciclo
termina los seis pasos, el paso 3 no queda en «hecho» y deja el motivo escrito. Medido:
`grep -rn "StubModel.callado" pruebas/*.py` imprime tres líneas de `test_enviar.py` —dos de prosa,
la 29 y la 1235, y la inyección de verdad en la 1251—. Hasta esa ronda el único archivo que la
nombraba era `pruebas/test_contrato.py`, donde sólo se le mira la salida contra el esquema angosto.

Las seis validan contra el esquema angosto —eso lo cubre
`test_las_salidas_del_stub_validan_contra_el_esquema_angosto`—, y eso no es lo mismo que probar que
el código las corrija. Eso era lo que pasaba con el corte del resumen hasta esta ronda: había dos
aserciones cerca que **parecían** cubrirlo y no lo hacían.
`test_5_sin_confirmacion_no_se_escribe_la_fila` y
`test_el_resumen_del_crm_resume_y_no_devuelve_el_agravio` cuentan las líneas de lo que salió, pero
con la salida canónica adentro, que ya viene con tres. Ninguna de las dos puede ponerse roja por un
recorte que no recorta, y por eso hizo falta el nodo que inyecta `resumen_largo()`. La segunda sí
muerde por lo otro que afirma —que el resumen no traiga nada de lo que escribió el contacto, ni de
este turno ni del historial—, y eso es una aserción distinta del recorte de tres líneas.

**Cómo lo cerrás.** Una prueba, con la forma de
`test_2_un_presupuesto_sin_evidencia_en_el_mensaje_se_fuerza_a_nulo`: inyectás la salida mala,
afirmás la corrección, y después comentás la verificación una vez para comprobar que la prueba se
pone roja. Una prueba que no puede fallar no prueba.

**Por qué quedó abierto.** Las salidas malas están escritas y el ciclo que las tiene que corregir se
construye en las fases 3 y 4. Escribir la prueba antes que el código que verifica deja una prueba
que saltea por el mismo motivo que todas las demás, y no agrega evidencia. Ver
`blueprint/40-pruebas.md`, Paso 3.

---

## El cuerpo que salió al cable, comparado con lo redactado · cerrado el 2026-08-14

Que el texto **venga del modelo** ya estaba anclado: `test_3_en_borrador_y_sin_confirmar_redacta_y_no_manda`
inyecta `StubModel.otro_texto(TEXTO_DEL_STUB)` y exige que la marca aparezca en `respuesta.texto`. Eso
atrapa al build que descarta `wire["texto"]` y redacta una línea enlatada.

**Lo que este apartado decía, y ya no es cierto:** «un build que redacte bien en `respuesta.texto`
y mande otra cosa al proveedor pasa la suite entera». Medido sobre un build, mandando una línea
fija al cable desde el paso 3 y dejando el redactado intacto: **tres nodos rojos.**

```
FAILED test_bandeja.py::test_aprobar_manda_por_enviar_y_rechazar_no_manda_nada[aprobar]
FAILED test_camino_feliz.py::test_cita_el_evento_id_sale_de_la_respuesta_del_calendario_y_no_de_una_constante
FAILED test_idempotencia.py::test_la_idempotency_key_cambia_cuando_cambia_el_texto
```

Los dos primeros miran justo lo que este apartado daba por no mirado: `Llamada.texto`, el cuerpo
que vio el transporte, contra `MARCA_DEL_MODELO`, un pedazo del texto que redacta
`StubModel.canonica()`. El de la bandeja exige que el mensaje que sale al aprobar traiga la marca
—o sea que sea el borrador que se aprobó y no otra cosa—; el del camino feliz exige que de los dos
mensajes del turno que agenda, exactamente uno la traiga. El tercero llega por otro camino y sin
mirar el texto: la `Idempotency-Key` se calcula sobre el texto **saliente**, así que dos corridas
con dos textos distintos del modelo tienen que dar dos claves distintas, y un build que manda
siempre la misma línea da la misma clave las dos veces.

**Quién lo cerró.** No la prueba que este apartado proponía —un nodo nuevo de caso-01 en
`automatico`—, sino las rondas de la bandeja y del camino feliz, de paso y con otros nodos. La
premisa de la que colgaba tampoco es cierta hoy: «no hay ninguna prueba de caso-01 que corra en
`automatico`», y `test_idempotencia.py` corre la entrada del 01 con `modo` en `automatico` y
`confirmado` en verdadero, dos veces seguidas.

**Lo que queda abierto, que es más chico y hay que decirlo.** Los tres anclan por marca, no por
igualdad: `MARCA_DEL_MODELO in envio.texto` es una subcadena, y nadie compara `respuesta.texto`
contra `Llamada.texto` entero. Un build que mande el texto redactado con algo pegado adelante o
atrás —una firma, un «Hola de nuevo:», un recorte que deje la marca adentro— pasa los tres.
Cerrarlo es una aserción de igualdad adentro del nodo de la bandeja, que es el único que tiene las
dos mitades a mano: el borrador que muestra `/api/pendientes` y el cuerpo que salió al aprobarlo.

---

## Lo que el chequeo 16 no puede ver

`16 contrato` ya no compara la salida contra la referencia del kit. Esa comparación castigaba al
build que **acertaba** —un agente cuyo `pruebas/salida-caso-01.json` salía igual, documento por
documento, a `pruebas/fixtures/caso-01.salida-esperada.json` se marcaba `contrato/salida_copiada`, y
cambiando una palabra adentro de un `motivo` el renglón volvía a `[ok]`—, y no distinguía lo que
tenía que distinguir: coincidir con la referencia es lo que hace un build correcto.

Lo que mira ahora es si hubo una corrida detrás, con dos preguntas que no miran el archivo:

- **¿Existe quién la escriba?** Sin `agente/ciclo.py`, la fixture `salida_caso_01` de
  `pruebas/conftest.py` levanta `SinAgente` y saltea: ninguna corrida deja una salida, así que la
  que esté ahí la dejó un editor. Sale `contrato/salida_sin_corrida`.
- **¿La corrida es de este árbol?** Esa fixture reescribe el archivo en cada corrida de la suite.
  Una salida más vieja que el `.py` más nuevo de `agente/` o de `pruebas/` no la escribió ninguna
  corrida del código que hay en disco. Sale `contrato/salida_vieja`.

**Lo que queda sin ver, y no lo cubre nadie:** un `cp` de la referencia hecho recién, en un árbol
con el build. No hay forma de distinguirlo mirando el archivo. Lo que lo acota es el chequeo 19: en
la misma corrida de la compuerta, `pytest pruebas -q -rs` vuelve a ejecutar la fixture y reescribe
`pruebas/salida-caso-01.json` con lo que devolvió el ciclo, así que una copia sobrevive **una** sola
corrida y la siguiente lee la salida de verdad. Cerrarlo del todo pide que la salida traiga su
procedencia adentro —quién la escribió y sobre qué árbol—, y eso lo escribe `pruebas/conftest.py`,
que es de otro dueño.

---

## El censo no sabía leer sus propios rojos · cerrado el 2026-08-18

`--censo` daba **43 campos `indeterminado`**, o sea «no pude medir ninguno». La evidencia
guardada decía otra cosa: en el campo `estado`, `mutados: 48` y un `FAILED` adentro del
detalle. Estaba mutando, la suite se ponía roja como tenía que ponerse, y el veredicto era
que no había medido nada.

El último paso era el roto. `FALLA_DE_PYTEST` buscaba líneas que **empiezan** por `FAILED`, y
la línea llegaba así:

```
\x1b[31mFAILED\x1b[0m pruebas/test_caso_01.py::test_6_no_escala…
```

Pytest colorea cuando el entorno trae `FORCE_COLOR` o `PY_COLORS`, **aunque la salida vaya a
una tubería**. En una terminal normal el censo funcionaba, y por eso nadie lo vio nunca.

**Dónde duele: ese entorno es el de un agente.** Este kit está hecho para que lo construya
Claude Code, que exporta `FORCE_COLOR`. El censo se rompía justo en el sitio donde más se
usa, y de la peor manera: sin fallar. Un censo que no lee sus rojos no da error, **afirma que
no midió**, y el chequeo que lo consume lo daba por bueno porque lee la evidencia guardada en
vez de volver a medir.

**Arreglado por los dos lados**, que es como toca cuando algo se rompe en silencio:

- Las dos corridas del censo —la base y cada mutante— llevan `--color=no`.
- El patrón aguanta escapes ANSI por si alguien fuerza el color igual.

Y con una prueba detrás, `pruebas/test_censo_lee_sus_rojos.py`, diez nodos. Comprobado que se
puede poner roja: volviendo al patrón viejo caen 3.

| Antes | Después |
|---|---|
| `censo: 40 indeterminado · 3 no_mutable` | `censo: 40 afirmado · 3 no_mutable` |

### Lo que esto deja abierto

**El chequeo 23 sigue leyendo evidencia guardada.** Con el censo arreglado la evidencia vuelve
a ser buena, pero la propiedad de fondo no cambia: un chequeo que consume un archivo escrito
en otra corrida afirma sobre el pasado. Hoy detecta si el árbol cambió y saltea, que es lo
correcto; lo que no puede detectar es una evidencia **escrita por un censo roto**, porque el
árbol era el mismo. Merece pensarse: el censo podría dejar su propio veredicto de salud en el
archivo, y el chequeo 23 negarse a leer una evidencia que se declaró ciega.

---

## El caché de prompt · cerrado el 2026-08-18

Durante siete rondas el kit hizo la mitad difícil y no cobró la fácil. `cache-estatico`
garantizaba desde el principio que el prefijo del sistema fuera idéntico byte por byte —sin
reloj, sin `uuid`, sin valores de la petición—, que es el trabajo de verdad. Y después
`agente/modelo.py` lo mandaba así:

```python
cuerpo_sistema = [{"type": "text", "text": sistema or ""}]
```

Sin `cache_control`. O sea: el prefijo se volvía a cobrar entero en cada mensaje, y **no había
forma de notarlo**. La respuesta es correcta, la compuerta verde, la suite en verde. Sólo sube
la factura, y en un cerrador el mismo catálogo y el mismo playbook se leen en cada turno de cada
conversación.

Lo que más pesa: `blueprint/50-despliegue.md` ya prometía por escrito *«con caché de prompt cae a
la mitad»*. El documento lo prometía y el código no lo hacía.

**Qué se hizo.** La clave en el bloque del sistema, dictada en `blueprint/30-generacion.md`
§ Paso 5; el chequeo **24 `cache-cobrado`**, que es error si la llamada va sin ella; y
`pruebas/test_cache_cobrado.py`, cuatro nodos que leen el árbol sin salir a la red.

**Comprobado que se pueden poner rojos**, que es la única prueba que vale:

| Mutación en `agente/modelo.py` | Qué dio la suite |
|---|---|
| `cache_control` quitado entero | 2 failed, 2 passed |
| `{"type": "efimero"}` en vez de `ephemeral` | 1 failed, 3 passed |

### Lo que esta clave NO hace, y hay que decirlo

Por debajo del mínimo cacheable del modelo —**512 tokens en Opus 5**— la API no cachea y **no
avisa**: `cache_creation_input_tokens` viene en cero, sin error. Con el catálogo y el playbook de
la configuración de demostración el prefijo mide **882 caracteres** y no llega, así que ahí la
clave está de adorno.

No es un defecto del kit: es que ese negocio todavía no tiene prefijo suficiente. Por eso el
chequeo 24 mide el prefijo del árbol y lo dice en voz alta, como **aviso y no como error**. El
día que el playbook tenga sus ocho objeciones escritas y el catálogo sus productos de verdad, el
aviso se apaga solo y el ahorro empieza sin tocar una línea.

### Lo que queda abierto

**Nadie ha medido el ahorro de punta a punta.** Para eso hace falta una clave de la API de
Anthropic y dos llamadas idénticas seguidas mirando `cache_read_input_tokens`, y la compuerta
corre sin red y sin credenciales a propósito. Lo comprueba quien despliegue, una vez, con el
prefijo de su negocio ya escrito. Si tu primera lectura de caché da cero con un prefijo largo,
ahí sí hay algo que mirar.

---

## Cómo se anota lo que vas cerrando

Debajo de cada punto, una línea con la fecha y qué te dio. Un pendiente cerrado sin nota vuelve
a abrirse dentro de tres meses, cuando nadie se acuerde de si se probó.

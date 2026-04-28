# Plan — Simulador Espacial de Zskahra

Este documento describe cómo reemplazar el actual `zskahra_tiempo_simulador.html`
(vista al ras del suelo, dos soles cruzando un cielo plano) por una **vista
orbital "desde el espacio"** que muestre el baile real entre los dos soles,
**Thlask** y **Zskahra**, y del que se deriven —en lugar de animarse a mano— las
estaciones, los Pulsos, los Ciclos y la posición de Thlask/Orbe en el cielo
local.

El objetivo no es realismo astrofísico: es que un GM o un jugador pueda mirar
el sistema desde fuera, mover el tiempo y **ver geométricamente** por qué está
en La Calma, por qué hay un Pulso, por qué los Días Ciegos son ciegos.

---

## 1. Diagnóstico del simulador actual

El archivo actual hace cosas correctas que conviene **conservar como datos
fuente** (no como render):

- Calendario de 288 Pasos / 9 Ciclos / 32 Pasos por ciclo / 8 Pasos por Pulso.
- Cinco estaciones con rangos de Paso fijos y una etiqueta narrativa.
- Pulso Gemelo cada 8 Pasos cerca de la hora 21 del Paso.
- Aritmética compatible con `zskahra_clima_generador.html`
  (`getCiclo`, `getPulso`, `esDiaPulso`).

Lo que **no** funciona y queremos tirar:

1. **Vista plana de horizonte.** Los dos soles cruzan un cielo 2D con
   degradados; Thlask es un disco fijo decorativo. No se ve la causa del
   fenómeno, solo el efecto.
2. **Estaciones hardcodeadas.** `getSeasonProfile()` interpola separación,
   altura, calor y rojo a mano por cada `season.id`. Si se cambia el calendario
   se rompe todo.
3. **Sombras pintadas.** Las dos sombras del muñeco son `<div>` rotados con
   ángulos calculados desde la posición del sol en pantalla; no derivan de la
   geometría real.
4. **Pulso es un destello cosmético.** El "destello" es un overlay con opacidad,
   no la conjunción aparente real de los dos soles vista desde Zskahra.
5. **Thlask es decoración.** Está clavado a `left:77% top:21%` con CSS y nunca
   refleja la fase, el tamaño aparente ni el lado iluminado.
6. **No se puede explorar el sistema.** No hay forma de preguntar "¿dónde está
   el sol B respecto a Thlask el Paso 144?".

---

## 2. Modelo orbital propuesto

Tres capas, todas derivadas del **tiempo continuo `t`** (Paso + hora/42),
ningún `if season.id` en el render.

### 2.1. Sistema binario (centro de la escena)

- **Sol A** y **Sol B** orbitan un baricentro común. Por simplicidad usamos
  órbitas circulares coplanares de **período igual al año de Zskahra**
  (288 Pasos) — es lo que hace que la "separación aparente vista desde Thlask"
  cierre exactamente con el calendario.
- Masas y radios visibles desiguales (A primario, B compañero) para que el
  jugador distinga cuál es cuál a primera vista.
- Una excentricidad pequeña (e ≈ 0.15) basta para que la separación aparente
  desde Thlask varíe entre estaciones — ese es el motor de "Calma vs Días
  Ciegos".

### 2.2. Thlask (planeta gigante)

- Órbita el baricentro binario en un período mucho más largo que el de los
  soles. Para el simulador tomamos **período = 1 año de Zskahra**, así Thlask
  vuelve al mismo punto cuando el calendario vuelve al Paso 1.
- Tiene rotación propia y un terminador (lado iluminado / oscuro) calculado a
  partir de la posición de cada sol — no es un disco plano.

### 2.3. Zskahra (luna habitada)

- Órbita Thlask con **bloqueo de marea**: la cara que mira a Thlask es siempre
  la misma. Esto es el axioma narrativo del mundo y no se negocia.
- El **período orbital de Zskahra alrededor de Thlask = 1 Paso = 42 horas**.
  Esto es el dato que hay que verificar contra el manual; si el manual fija
  otra cosa, ese valor manda. Pero esta es la elección coherente: una "vuelta"
  de Zskahra alrededor de Thlask = una "vuelta de día" del calendario local.
- Como está bloqueada por marea, su rotación sobre su propio eje también es
  de 42 horas — por eso desde la cara habitada Thlask **no sale ni se pone**.

### 2.4. Lo que sale gratis del modelo

Una vez el modelo gira solo, estos fenómenos **emergen** y dejan de ser
hardcodeados:

| Fenómeno narrativo                | Geometría que lo produce                                    |
|-----------------------------------|-------------------------------------------------------------|
| Calma Brillante                   | Thlask está cerca del eje binario, soles vistos casi juntos |
| Días Ciegos                       | Thlask está en cuadratura, soles aparentes muy separados    |
| Conjunción                        | Soles A y B están detrás uno del otro vistos desde Thlask   |
| Pulso Gemelo (cada 8 Pasos)       | Sincronización de Zskahra dando vueltas con la separación   |
| Thlask fijo desde Zskahra         | Bloqueo por marea (eje Zskahra→Thlask es invariante)        |
| Orbe iluminando la noche          | Thlask reflejando luz solar hacia el lado nocturno          |
| Eclipses raros (clima generador)  | Sol pasa detrás de Thlask vista desde Zskahra               |

Si la geometría está bien parametrizada, el calendario actual
(`Calma 1-72`, `Velo 73-120`, `Ciegos 121-156`, etc.) sigue cuadrando — solo
que ahora **se puede explicar visualmente**, no solo afirmar.

---

## 3. Diseño de la interfaz

Tres vistas seleccionables con un toggle, no tres herramientas distintas:

### Vista A — "Top-down del sistema" (vista principal)

- Plano cenital. Baricentro al centro.
- Soles A y B orbitándolo (trazas tenues de su órbita).
- Thlask en su órbita exterior.
- Zskahra como punto pequeño orbitando Thlask, con un marcador del **lado
  habitado** (la cara fija hacia Thlask).
- Líneas guía opcionales: vector Zskahra→Thlask, vector Thlask→Sol A,
  Thlask→Sol B.
- Etiqueta dinámica con la **separación angular aparente A–B vista desde
  Thlask** (este es el número que decide la estación).

### Vista B — "Cielo desde Zskahra"

Reemplaza el render plano actual, pero **derivado**, no hardcodeado.

- Bóveda celeste vista desde la cara habitada.
- Thlask siempre en el mismo punto (consecuencia del bloqueo por marea), con
  fase iluminada calculada desde la posición real de los soles.
- Soles A y B donde la geometría diga que estén, no donde una `lerp(18,54,p)`
  los coloque.
- Sombras dobles del marcador del suelo: ángulo y largo derivados del azimut
  y altitud reales de cada sol.

### Vista C — "Línea de tiempo" (igual que la actual)

- Año de 288 Pasos con sus 5 estaciones coloreadas.
- Marcas de Pulso cada 8 Pasos, mayores cada 32 (cambio de Ciclo).
- Cursor que se mueve con `t`. Es el control que ya existe; se conserva.

### Controles compartidos por las tres vistas

- Slider de Paso (1–288) y de hora dentro del Paso (0–42).
- Botones Paso anterior / siguiente, próximo Pulso, próxima Conjunción.
- Play/pausa con velocidad variable.
- Toggle "mostrar trayectorias" / "mostrar líneas guía".
- Lectura numérica: separación A–B desde Thlask, fase de Thlask vista desde
  Zskahra, altitud máxima de cada sol en este Paso.

---

## 4. Implementación técnica

### 4.1. Render

**Recomendación: `<canvas>` 2D**, no SVG ni CSS.
- La vista top-down va a redibujarse cada frame al reproducir; SVG con
  cientos de actualizaciones de atributos `cx`/`cy` rinde peor.
- Permite trazar las trayectorias (estela) baratas vía un buffer.
- Es lo que ya estamos usando implícitamente con degradados; pasar a canvas
  no agrega dependencias.

Sin librerías. Sin `three.js`, sin `d3`, sin frameworks. El proyecto se
despliega en Netlify como estáticos (ver `README.md`); mantener cero build.

### 4.2. Estructura del código

Un solo archivo `zskahra_simulador_espacial.html` (reemplaza al actual,
manteniendo el mismo nombre `zskahra_tiempo_simulador.html` para no romper
el link en `index.html` — discutir abajo) con tres bloques claros:

```
// 1. CALENDARIO (lo que ya hay, conservar)
const YEAR_STEPS = 288, HOURS_PER_STEP = 42, PULSE_STEPS = 8, PULSE_HOUR = 21;
function getCycle(step), getPulseInCycle(step), isPulseDay(step), ...

// 2. ÓRBITAS (nuevo — funciones puras, sin DOM)
function sunPosition(t, which)     -> {x, y}      // baricéntrico
function thlaskPosition(t)         -> {x, y}      // baricéntrico
function zskahraPosition(t)        -> {x, y}      // alrededor de Thlask
function apparentSunSeparation(t)  -> radianes    // vista desde Thlask
function thlaskPhase(t)            -> [0..1]      // vista desde Zskahra
function sunSkyPosition(t, which)  -> {az, alt}   // vista desde Zskahra

// 3. RENDER (DOM/canvas, sin lógica de fechas)
function drawTopDown(ctx, t)
function drawSky(ctx, t)
function drawTimeline(ctx, t)
```

La regla dura: **el render no conoce los nombres de las estaciones**. Las
estaciones son una capa de etiquetas que se pinta encima leyendo el calendario
para textos, no para geometría.

### 4.3. Calibración

Para que el modelo cuadre con el calendario heredado hay que elegir tres
parámetros:

1. **Fase inicial** de Thlask en su órbita en el Paso 1 (define dónde empieza
   La Calma).
2. **Excentricidad** de la binaria (define el contraste entre Calma y Días
   Ciegos).
3. **Desfase** de la órbita de Zskahra alrededor de Thlask para que la
   conjunción aparente caiga en la hora 21 de los Pasos múltiplos de 8.

Escribir un pequeño "tester" interno (en consola, no UI) que recorra los 288
Pasos y verifique:
- La separación aparente máxima cae dentro del rango "Días Ciegos" (121–156).
- La separación aparente mínima cae dentro del rango "Conjunción" (211–288).
- La conjunción aparente A–B desde Zskahra ocurre cerca de la hora 21 del
  Paso múltiplo de 8.

Si los rangos no cuadran exactamente con el manual, **ajustar los parámetros
del modelo, no los rangos del calendario** — el calendario es el contrato
narrativo.

### 4.4. Compatibilidad con otras herramientas

`zskahra_clima_generador.html` usa `getCiclo`, `getPulso`, `esDiaPulso` con
la misma aritmética. Mantener esos nombres y semánticas idénticos. Idealmente
extraer la lógica de calendario a un `<script>` inline reutilizable, pero
manteniendo el principio de "cero build" probablemente sea más fácil
duplicarlo y tener un comentario que diga "mantener en sync con
zskahra_clima_generador.html".

---

## 5. Sobre el archivo y el link

Dos opciones:

**A. Reescribir `zskahra_tiempo_simulador.html` en sitio.**
- El link en `index.html` no cambia.
- Se pierde el render actual. Si alguien lo quería para algo, ya fue.

**B. Crear `zskahra_simulador_espacial.html` como nuevo, y dejar el viejo.**
- El index gana una entrada nueva, el viejo se queda como referencia.
- Riesgo: quedan dos simuladores y nadie sabe cuál es "el bueno".

**Recomendación: opción A.** El simulador actual ya está marcado como malo
por el usuario; conservarlo solo dispersa la herramienta. Si después se
quiere recuperar la vista de horizonte, se rescata como **Vista B** del
nuevo simulador (que es exactamente para eso).

---

## 6. Plan de trabajo por etapas

Cada etapa se puede commitear y entregar por separado:

1. **Etapa 1 — Modelo puro.** Implementar las funciones de órbita
   (`sunPosition`, `thlaskPosition`, `zskahraPosition`,
   `apparentSunSeparation`, `thlaskPhase`, `sunSkyPosition`) en un
   `<script>` con un test rápido en consola que recorra los 288 Pasos.
   Sin UI todavía. *Salida: las funciones existen y dan valores plausibles.*

2. **Etapa 2 — Vista top-down.** Canvas con baricentro, dos soles, Thlask y
   Zskahra. Slider de tiempo. Trayectorias on/off. *Salida: se puede mover el
   tiempo y ver el sistema girar.*

3. **Etapa 3 — Calibración.** Ajustar fase inicial y excentricidad para que
   los rangos de estación caigan donde el calendario manda. *Salida: la
   etiqueta "estación" cambia en los Pasos correctos.*

4. **Etapa 4 — Vista cielo desde Zskahra.** Reescribir la vista plana actual
   pero alimentada por `sunSkyPosition` y `thlaskPhase`. Sombras dobles
   reales. *Salida: el render del cielo ya no tiene `if season.id`.*

5. **Etapa 5 — Pulido.** Línea de tiempo, controles compartidos, lecturas
   numéricas, "saltar al próximo Pulso / próxima Conjunción", explicaciones.

Es importante hacer la **Etapa 1 sin tocar nada visual**. El bug más probable
de este rediseño es que el modelo orbital no calibra y quede tentador
"corregir" las estaciones para que cuadren — eso recrea el problema actual,
solo que con más código.

---

## 7. Riesgos y cosas que no haremos

- **No modelar masas, gravedad ni Kepler de verdad.** Órbitas paramétricas
  (sin/cos de `t`) bastan y son estables. Esto es worldbuilding, no astrofísica.
- **No 3D.** Top-down 2D + bóveda celeste 2D. Tres.js es overkill y agrega
  carga de build/CDN al proyecto estático.
- **No tocar el calendario.** Si el modelo no cuadra, se ajusta el modelo.
  El calendario es contrato con el resto de las herramientas.
- **No agregar un "modo educativo" interactivo en la primera versión.** Tabs
  con explicaciones tipo el actual `topics`, OK. Quizzes, no.

---

## 8. Definición de "listo"

El simulador está listo cuando:

1. Mover el slider de Paso muestra cómo Thlask se desplaza alrededor de los
   soles y cómo Zskahra gira alrededor de Thlask.
2. La separación angular A–B vista desde Thlask, calculada por el modelo,
   coincide con la estación nombrada en cada rango de Pasos.
3. La fase iluminada de Thlask vista desde Zskahra cambia con el tiempo y
   tiene sentido relativa a las posiciones de A y B.
4. El cielo desde Zskahra muestra los dos soles donde la geometría dice, con
   sombras dobles consistentes.
5. Las funciones `getCiclo`, `getPulso`, `esDiaPulso` siguen devolviendo
   exactamente los mismos valores que en `zskahra_clima_generador.html`.
6. Funciona sin build, sin dependencias, en un solo archivo HTML.

# Zskahra Tools

Herramientas web para el mundo de **Zskahra** — suplemento homebrew para el sistema HARP.

El proyecto es un conjunto de páginas HTML estáticas, sin framework ni paso de build, desplegadas en Netlify. Están pensadas para uso en mesa durante la campaña y para la preparación del Director de Juego.

## Herramientas

| Herramienta | Archivo | Descripción |
|---|---|---|
| **Generador de Nombres** | `zskahra_generador_de_nombres_para_villagers.html` | Genera nombres para aldeanos con raza, villa de origen, sufijo de hito social, edad y trasfondo. |
| **Oráculo de Clima** | `zskahra_clima_generador.html` | Genera el clima por khar para cualquier bioma del mundo. |
| **Simulador del Tiempo** | `zskahra_tiempo_simulador.html` | Visualiza los dos soles (el Pulso Gemelo), los Ciclos y las cinco estaciones de Zskahra. |
| **Guía del Herbalista** | `zskahra_herbalist_generador.html` | Sistema de recolección de hierbas, ingredientes y preparaciones alquímicas. |
| **Referencia Rápida** | `zskahra_referencia.html` | Sufijos de hito, aldeas, estaciones, calendario y artefactos. Diseñado para el DJ. |
| **Tiempos de Viaje** | `zskahra_tiempos_de_viaje.html` | Tabla de distancias entre las doce villas en días de caravana. |
| **Generador de Imágenes** | `zskahra_generador_imagenes.html` | Genera prompts para ilustraciones de personajes aldeanos y mellizos. |
| **Explorador del Mundo** | `zskahra_explorer.html` | Villas, sistema social, sufijos de hito y estructura del mundo. |

## Despliegue

El sitio se publica en [Netlify](https://netlify.com) como archivos estáticos. No requiere build — se sirve directamente desde la raíz del repositorio. Las páginas HTML tienen caché de una hora (`max-age=3600`).

Para probar en local basta con abrir cualquier `.html` directamente en el navegador, o lanzar un servidor simple:

```bash
python3 -m http.server
```

## Recursos externos

- **Google Drive** — carpeta compartida con documentos del proyecto.
- **Roll20** — mesa virtual de la campaña.
- **Manual del Aldeano** — `Manual del Aldeano - Zskahra.pdf` incluido en el repositorio.

## Estructura del repositorio

```
index.html                          # Página principal con enlace a todas las herramientas
zskahra_*.html                      # Una página por herramienta
*.png                               # Mapas e imágenes de referencia del mundo
Manual del Aldeano - Zskahra.pdf    # Documento base de lore
netlify.toml                        # Configuración de Netlify
```

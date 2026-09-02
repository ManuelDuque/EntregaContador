# EntregaContador

Aplicación de escritorio para la **lectura OCR de contadores mecánicos de energía eléctrica**. Detecta hasta 3 contadores en una imagen, extrae las cifras mediante template matching multiplantilla y muestra el valor numérico resultante.

## Características principales

- Detección de hasta 3 regiones de contador en una imagen fuente mediante clipping (recorte por coordenadas)
- Extracción de dígitos individuales a partir de cada contador recortado
- Reconocimiento de dígitos mediante **Multi-Template Matching** (MTM) con plantillas predefinidas
- Biblioteca de plantillas con múltiples variantes por dígito (0-9)
- Modo de procesamiento global: evalúa las 12 imágenes de prueba y genera un reporte de tasa de éxito
- Interfaz gráfica PyQt5 con visualización de imagen fuente, recortes de contadores y valores extraídos
- Configuración flexible mediante archivos JSON
- Soporte para argumentos de línea de comandos para sobreescribir configuraciones

## Documentación adicional

El proyecto incluye documentación complementaria en formato PDF:

| Documento | Descripción |
|-----------|-------------|
| `Documentacion del programador.pdf` | Documentación técnica dirigida al desarrollador |
| `Documentacion del usuario.pdf` | Guía de uso para el usuario final |

## Prerrequisitos

- **Python 3.x**
- **Sistema operativo:** Windows, Linux o macOS

## Instalación

1. Clona el repositorio:

```bash
git clone https://github.com/ManuelDuque/publicar.git
cd publicar/EntregaContador
```

2. Instala las dependencias:

```bash
pip install -r requirements.txt
```

| Paquete | Versión |
|---------|---------|
| PyQt5 | 5.15.7 |
| opencv-python | 4.7.0.68 |
| Multi-Template-Matching | 1.6.3 |

> **Nota:** `numpy` y `pandas` se instalan automáticamente como dependencias de los paquetes anteriores.

## Ejecución

```bash
# Modo interactivo (abre ventana GUI)
python main.py

# Sobreescribir archivos de configuración
python main.py -ui path/to/custom_ui_config.json -counter path/to/custom_counters.json
```

Los argumentos de CLI deben proporcionarse en pares (`-flag valor`):

| Flag | Descripción |
|------|-------------|
| `-ui` | Ruta a un archivo de configuración de UI alternativo |
| `-counter` | Ruta a un archivo de configuración de contadores alternativo |

## Configuración

### config/counters.json

Define las regiones de los contadores y parámetros de OCR:

```json
{
    "digits_per_counter": 4,
    "decimals_after_coma": 1,
    "score_threshold": 0.6,
    "max_overlap": 0.6,
    "counters": [
        { "x": 285, "y": 155, "width": 115, "height": 45 },
        { "x": 285, "y": 233, "width": 115, "height": 45 },
        { "x": 283, "y": 315, "width": 116, "height": 45 }
    ]
}
```

| Campo | Descripción |
|-------|-------------|
| `digits_per_counter` | Número de dígitos por contador (4) |
| `decimals_after_coma` | Posiciones decimales (el último dígito es decimal) |
| `score_threshold` | Umbral mínimo de confianza para template matching (0.0 - 1.0) |
| `max_overlap` | Máxima superposición permitida para filtrar matches duplicados |
| `counters` | Array de regiones de recorte con coordenadas `x`, `y`, `width`, `height` |

### config/ui_config.json

Configuración de la interfaz y rutas:

```json
{
    "ui": {
        "title": "COUNTERS OCR",
        "ui_file_path": "mainwindow.ui",
        "images_folder": "images/sources",
        "templates_folder": "images/templates"
    },
    "file_dialog": {
        "filter": "Images (*.jpg *.jpeg *.png)",
        "caption": "Select a source image"
    }
}
```

### config/test_outputs.json

Valores esperados (ground truth) para las 12 imágenes de prueba, utilizado por el modo de procesamiento global para calcular la tasa de éxito.

## Estructura del proyecto

```
EntregaContador/
├── main.py                              # Punto de entrada
├── mainwindow.ui                        # Diseño de la interfaz (Qt Designer)
├── window.ui                            # Diseño alternativo de interfaz
├── requirements.txt                     # Dependencias de Python
├── rate_report.txt                      # Reporte de tasas de éxito (generado)
├── Documentacion del programador.pdf    # Documentación técnica
├── Documentacion del usuario.pdf        # Guía de usuario
├── config/
│   ├── counters.json                    # Configuración de regiones de contadores
│   ├── ui_config.json                   # Configuración de la interfaz
│   └── test_outputs.json                # Valores esperados para evaluación
├── images/
│   ├── sources/                         # 12 imágenes de prueba (capturas_1.jpg .. capturas_12.jpg)
│   └── templates/                       # Plantillas de dígitos (0-9, múltiples variantes)
│       ├── 0/                           # 13 variantes del dígito 0
│       ├── 1/                           # Variantes del dígito 1
│       ├── .../
│       └── 9/                           # Variantes del dígito 9
├── src/
│   ├── ui.py                            # Ventana PyQt5 y manejo de eventos
│   ├── processor.py                     # Lógica de procesamiento de imagen y OCR
│   └── utils.py                         # Singleton decorator + utilidades
└── README.md
```

### Archivos principales

| Archivo | Descripción |
|---------|-------------|
| `main.py` | Punto de entrada. Crea la aplicación Qt, procesa argumentos CLI e instancia la ventana. |
| `src/ui.py` | Clase `Window`: ventana PyQt5 con visor de imagen fuente, 3 visores de recorte de contadores, campos de texto con valores extraídos y botones de acción. |
| `src/processor.py` | Clase `Processor`: realiza el clipping de contadores, separación de dígitos y reconoacimiento vía template matching con `matchTemplates`. |
| `src/utils.py` | Clase `Utils`: decorator singleton, carga de JSON y acceso a valores anidados. |

## Arquitectura

El flujo de procesamiento es:

```
Imagen fuente
    │
    ▼
┌──────────────────┐
│ Clipping         │  Recorte de 3 regiones según counters.json
│ (processor)      │
└────────┬─────────┘
         │ 3 imágenes recortadas (una por contador)
         ▼
┌──────────────────┐
│ Extract Digits   │  Separación en sub-imágenes de dígito
│ (processor)      │  (4 dígitos por contador, 1 decimal)
└────────┬─────────┘
         │ Sub-imágenes individuales
         ▼
┌──────────────────┐
│ Template Match   │  Comparación contra 100+ plantillas por dígito
│ (MTM library)    │  using TM_CCOEFF_NORMED
└────────┬─────────┘
         │ Mejor match por posición → valor numérico
         ▼
    Mostrar resultado
```

### Modo de evaluación global

Al ejecutar el modo de procesamiento global, la aplicación:

1. Procesa las 12 imágenes de prueba en `images/sources/`
2. Compara los valores extraídos contra el ground truth en `config/test_outputs.json`
3. Genera un reporte de tasa de éxito en `rate_report.txt`

## Plantillas de dígitos

La biblioteca de plantillas en `images/templates/` contiene 10 carpetas (una por dígito del 0 al 9), cada una con múltiples variantes de imagen para mejorar la robustez del reconocimiento ante diferentes fuentes de iluminación y estilos de representación.

## Tecnologías

| Tecnología | Uso |
|------------|-----|
| Python 3 | Lenguaje de programación |
| PyQt5 5.15.7 | Interfaz gráfica de escritorio |
| OpenCV 4.7.0.68 | Procesamiento de imagen y template matching |
| Multi-Template-Matching 1.6.3 | Framework de matching multiplantilla |
| pandas | Manejo de resultados de matching |
| NumPy | Operaciones matriciales |

## Autor

[ManuelDuque](https://github.com/ManuelDuque)

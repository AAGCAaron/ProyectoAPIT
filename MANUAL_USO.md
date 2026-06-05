# 📖 Manual de Uso: ABSA para PC Hardware Discussions

Este manual proporciona una guía detallada paso a paso para configurar, ejecutar y analizar los resultados del sistema de **Análisis de Sentimiento Basado en Aspectos (ABSA)** para discusiones sobre hardware de PC en **YouTube**.

---

## 🛠️ Requisitos Previos

Antes de comenzar, asegúrate de tener instalado y configurado lo siguiente en tu máquina (Windows):

1. **Python 3.11+** (versión recomendada y probada).
2. **Entorno virtual activado** (`venv`).
3. **Dependencias instaladas** (`pip install -r requirements.txt`).
4. **Modelo de spaCy descargado** (`python -m spacy download en_core_web_sm`).

> [!NOTE]
> Si ya seguiste las instrucciones iniciales de instalación y las dependencias se instalaron correctamente, puedes pasar directamente a la configuración de la API de YouTube.

---

## 🔑 Paso 1: Configurar Credenciales de la YouTube Data API v3

Para que el sistema recopile comentarios reales de YouTube en lugar de usar datos simulados, debes crear una clave de API en Google Cloud:

1. Entra a la consola de Google Cloud: [https://console.cloud.google.com](https://console.cloud.google.com) (inicia sesión con tu cuenta de Google).
2. **Crea un proyecto nuevo** (botón superior — *Select a project → New project*). Asigna un nombre como `ABSA-PCHardware`.
3. En el menú lateral selecciona **APIs & Services → Library**.
4. Busca **"YouTube Data API v3"** y haz clic en **Enable** (Habilitar).
5. Ve a **APIs & Services → Credentials → Create credentials → API key**.
6. Se generará una clave alfanumérica (ej. `AIzaSyD-xxxxxxxxxxxxxxxxxxxxxxxx`). **Cópiala**.

> [!IMPORTANT]
> La API permite hasta **10,000 unidades de cuota gratuita por día**. Cada búsqueda cuesta ~100 unidades y cada lista de comentarios ~1 unidad. Con esto se pueden recolectar miles de comentarios diarios sin costo.

### Crear el Archivo de Configuración `.env`
1. En la carpeta raíz del proyecto crea un archivo llamado **`.env`** (o copia el archivo `.env.example`).
2. Edítalo con tu clave:

```env
YOUTUBE_API_KEY=AIzaSyD-xxxxxxxxxxxxxxxxxxxxxxxx
```

> [!WARNING]
> **Nunca subas el archivo `.env` a Git.** Ya está incluido en `.gitignore`. Si tu clave se filtra, revócala desde *APIs & Services → Credentials* y crea una nueva.

---

## 🚀 Paso 2: Ejecución del Pipeline Principal

El sistema cuenta con un punto de entrada centralizado en `src/main.py` que ejecuta secuencialmente todo el pipeline: extracción, limpieza, extracción de aspectos, clasificación y graficación.

Abre una terminal de PowerShell en la raíz del proyecto y ejecuta:

```powershell
# Activar entorno virtual
.\venv\Scripts\activate

# Ejecutar el pipeline principal
python src/main.py
```

### 💡 Modos de Ejecución Dinámica del Pipeline
El script `src/main.py` detecta automáticamente la presencia de la clave de API:

* **Modo Simulación (Sin `.env` o clave inválida)**: el sistema imprime una advertencia y utiliza un dataset local de prueba (`MOCK_YOUTUBE_DATA`) que cubre múltiples marcas (AMD, NVIDIA, Intel), opiniones encontradas y sarcasmo. Útil para validar todo el pipeline offline en segundos.
* **Modo Producción Real (Con `.env` válido)**: el sistema se conecta a la YouTube Data API v3, ejecuta la **estrategia mixta** de recolección (canales especializados + búsquedas por keywords) y procesa los comentarios extraídos.

### 📺 Estrategia Mixta de Recolección
El colector implementa dos vías complementarias:
1. **Canales especializados**: Linus Tech Tips, Gamers Nexus, Hardware Unboxed, JayzTwoCents, Bitwit, Paul's Hardware, Optimum.
2. **Búsqueda por keywords**: queries como *"RTX 4090 review"*, *"Ryzen 7000 benchmark"*, *"GPU temperature problem"*, *"coil whine GPU"*, etc.

Para cada video se extraen los comentarios de nivel superior ordenados por **relevancia**.

---

## 📈 Paso 3: Análisis y Comprensión de Resultados

Una vez completado el pipeline, se generará el archivo de resultados principal en:
💾 **`data/processed/absa_results.csv`**

Este archivo contiene la segmentación del análisis de sentimiento por aspecto. Los campos clave son:

| Columna | Descripción | Ejemplo |
| :--- | :--- | :--- |
| `id` | Identificador único del video o comentario en YouTube. | `Ugxa1bC2dE3fG4...` |
| `texto_original` | Texto completo del comentario o título del video. | *"I just built my PC. The gaming performance is absolutely insane..."* |
| `marca` | Marca de hardware asociada detectada contextualmente. | `AMD`, `NVIDIA`, `Intel` |
| `aspecto` | Palabra o frase específica que denota el aspecto técnico. | `temperature`, `performance`, `noise` |
| `categoria` | Categoría de hardware asociada semánticamente. | `thermal`, `performance`, `acoustics`, `value`, `reliability` |
| `sentimiento` | Sentimiento asignado al aspecto en su oración local. | `Positive`, `Neutral`, `Negative` |
| `confianza` | Score de confianza probabilística de la predicción del Transformer. | `0.9674` |
| `sarcasmo` | Indica si el preprocesador detectó ironía o sarcasmo. | `True` / `False` |

### 🧠 ¿Cómo funciona la Lógica de Clasificación Local?
A diferencia de los analizadores tradicionales que asignan el sentimiento global del comentario a todos los aspectos, este sistema utiliza **segmentación semántica**:
1. Busca el aspecto o sus palabras clave dentro de las oraciones individuales del comentario original.
2. Extrae la oración exacta donde se encuentra el aspecto (ej: *"idle temperatures are reaching 65C"*).
3. Evalúa con el Transformer **únicamente** el texto de esa oración específica.
4. Esto permite que una opinión mixta (gran rendimiento pero malas temperaturas) asigne correctamente un sentimiento **Positivo** a la performance y uno **Negativo** a la temperatura dentro del mismo comentario.

---

## 📊 Paso 4: Visualización de los Dashboards

El sistema genera visualizaciones web interactivas en:
📂 **`reports/figures/`**

Abre cualquiera de los siguientes archivos en tu navegador:

1. **`distribucion_sentimiento.html`**: cuántas menciones existen de cada sentimiento para los aspectos técnicos globales.
2. **`sentimiento_por_aspecto.html`**: gráfico de barras apiladas con el porcentaje de polaridad (Positivo, Neutro, Negativo) por cada una de las 6 categorías (Thermal, Performance, Value, Acoustics, Reliability, Compatibility).
3. **`comparacion_marcas.html`**: comparación cara a cara de la percepción de los usuarios sobre AMD vs. NVIDIA vs. Intel.
4. **`evolucion_temporal.html`**: línea temporal con la fluctuación de sentimientos a lo largo del tiempo.

---

## 🔬 Ejecución de Módulos Individuales (Pruebas y Desarrollo)

Cada componente puede ejecutarse de manera independiente:

* **Prueba de Extracción (YouTube API)**:
  `python src/data_collection/youtube_collector.py`
* **Prueba del Limpiador y Detección de Sarcasmo**:
  `python src/preprocessing/text_cleaner.py`
* **Prueba de Extracción de Aspectos (spaCy & SentenceTransformers)**:
  `python src/absa/aspect_extractor.py`
* **Prueba de Clasificador de Sentimiento (RoBERTa Transformer)**:
  `python src/absa/sentiment_classifier.py`
* **Generación Directa de Visualizaciones**:
  `python src/visualization/dashboard.py`

---

## ⚠️ Manejo de Errores Comunes

| Error | Causa | Solución |
| :--- | :--- | :--- |
| `quotaExceeded` | Se agotaron las 10,000 unidades diarias. | Esperar 24h o crear un segundo proyecto con otra cuenta de Google. |
| `commentsDisabled` | El video tiene comentarios deshabilitados. | El colector lo ignora automáticamente y continúa. |
| `403 Forbidden` | La clave de API no tiene habilitada la YouTube Data API v3. | Verificar en *APIs & Services → Library* que esté **Enabled**. |
| `keyInvalid` | Clave mal copiada o revocada. | Generar una nueva clave en *Credentials*. |

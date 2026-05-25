# 📖 Manual de Uso: ABSA para PC Hardware Discussions

Este manual proporciona una guía detallada paso a paso para configurar, ejecutar y analizar los resultados del sistema de **Análisis de Sentimiento Basado en Aspectos (ABSA)** para discusiones sobre hardware de PC en Reddit.

---

## 🛠️ Requisitos Previos

Antes de comenzar, asegúrate de tener instalado y configurado lo siguiente en tu máquina (Windows):

1. **Python 3.11** (versión recomendada y probada).
2. **Entorno virtual activado** (`venv`).
3. **Dependencias instaladas** (`pip install -r requirements.txt`).
4. **Modelo de spaCy descargado** (`python -m spacy download en_core_web_sm`).

> [!NOTE]
> Si ya seguiste las instrucciones iniciales de instalación y las dependencias se instalaron correctamente, puedes pasar directamente a la configuración de la API de Reddit.

---

## 🔑 Paso 1: Configurar Credenciales de la API de Reddit

Para que el sistema recopile discusiones en tiempo real de Reddit en lugar de usar datos simulados, debes crear una aplicación de desarrollador en Reddit:

1. Ve al portal de preferencias de aplicaciones de Reddit: [https://www.reddit.com/prefs/apps](https://www.reddit.com/prefs/apps) (inicia sesión con tu cuenta de Reddit).
2. Haz clic en el botón **"are you a developer? create another app..."** (¿eres desarrollador? crea otra aplicación...).
3. Rellena los campos con la siguiente configuración:
   * **name**: `ABSA-PC-Hardware` (o el nombre que prefieras).
   * **Tipo de app**: Selecciona la opción **script** (esférico de selección obligatorio).
   * **description**: Opcional (ej. *Pipeline ABSA de hardware*).
   * **about url**: Puedes dejarlo en blanco.
   * **redirect uri**: Escribe `http://localhost:8080` (es un requerimiento formal de Reddit, no se usará un servidor web).
4. Haz clic en **create app**.
5. Una vez creada, aparecerán tus llaves en pantalla:
   * El **Client ID** es el código alfanumérico corto que aparece justo debajo de *"personal use gold"* (ej. `xYz12345AbCd`).
   * El **Client Secret** es la cadena larga etiquetada como *"secret"* (ej. `aBcDeFgHiJkLmNoPqRsTuVwXyZ0123`).

### Crear el Archivo de Configuración `.env`
1. En la carpeta raíz de tu proyecto (`d:\ProyectoAPIT\`), crea un archivo de texto y nómbralo **`.env`** (o copia y renombra el archivo `.env.example`).
2. Edítalo y añade tus credenciales tal como se muestra a continuación:

```env
# Credenciales de acceso a la API de Reddit
REDDIT_CLIENT_ID=TU_CLIENT_ID_AQUI
REDDIT_CLIENT_SECRET=TU_CLIENT_SECRET_AQUI
REDDIT_USER_AGENT=ABSA-PCHardware/1.0 by tu_usuario_de_reddit
```

> [!IMPORTANT]
> El campo `REDDIT_USER_AGENT` es obligatorio para evitar bloqueos por parte de los servidores de Reddit. Reemplaza `tu_usuario_de_reddit` con tu nombre de usuario real en Reddit.

---

## 🚀 Paso 2: Ejecución del Pipeline Principal

El sistema cuenta con un punto de entrada centralizado en `src/main.py` que ejecuta secuencialmente todo el pipeline: extracción, limpieza, extracción de aspectos, clasificación y graficación.

Abre una terminal de PowerShell en la raíz de tu proyecto y ejecuta:

```powershell
# Asegúrate de tener activado el entorno virtual (venv)
.\venv\Scripts\activate

# Ejecutar el pipeline principal
python src/main.py
```

### 💡 Modos de Ejecución Dinámica del Pipeline
El script `src/main.py` detecta de forma automática la presencia de tus credenciales:

* **Modo Simulación (Sin `.env`)**: Si no has configurado tus credenciales, el sistema imprimirá una advertencia y utilizará un dataset local estructurado de prueba (`MOCK_REDDIT_DATA`) que cubre múltiples marcas (AMD, NVIDIA, Intel), opiniones encontradas y sarcasmo. Esto permite validar todo el flujo de modelos y generación de gráficos de forma offline en segundos.
* **Modo Producción Real (Con `.env`)**: Si detecta las credenciales de Reddit, se conectará a la API, extraerá los posts y comentarios más recientes y populares en vivo de subreddits clave (`r/pcmasterrace`, `r/buildapc`, `r/Amd`, `r/nvidia`, `r/intel`) y procesará los datos actualizados.

---

## 📈 Paso 3: Análisis y Comprensión de Resultados

Una vez completado el pipeline, se generará el archivo de resultados principal en:
💾 **`d:\ProyectoAPIT\data\processed\absa_results.csv`**

Este archivo contiene la segmentación del análisis de sentimiento por aspecto. Los campos clave son:

| Columna | Descripción | Ejemplo |
| :--- | :--- | :--- |
| `id` | Identificador único del post o comentario en Reddit. | `post1` |
| `texto_original` | El texto completo redactado por el usuario de Reddit. | *"I just built my PC. The gaming performance is absolutely insane..."* |
| `marca` | Marca de hardware asociada detectada contextualmente. | `AMD`, `NVIDIA`, `Intel` |
| `aspecto` | La palabra o frase específica extraída que denota el aspecto técnico. | `temperature`, `performance`, `noise` |
| `categoria` | Categoría de hardware a la que se asoció semánticamente. | `thermal`, `performance`, `acoustics`, `value`, `reliability` |
| `sentimiento` | Sentimiento asignado al aspecto en su oración local. | `Positive`, `Neutral`, `Negative` |
| `confianza` | Score de confianza probabilística de la predicción del Transformer. | `0.9674` |
| `sarcasmo` | Indica si el módulo preprocesador detectó ironía o sarcasmo en el texto. | `True` / `False` |

### 🧠 ¿Cómo funciona la Lógica de Clasificación Local?
A diferencia de los analizadores tradicionales que le asignan el sentimiento global del comentario a todos los aspectos, nuestro sistema utiliza **segmentación semántica**:
1. Busca el aspecto o sus palabras clave asociadas dentro de las oraciones individuales del comentario original.
2. Extrae la oración exacta donde se encuentra el aspecto (ej: *"idle temperatures are reaching 65C"*).
3. Evalúa con el Transformer **únicamente** el texto de esa oración específica.
4. Esto permite que una opinión mixta (como un gran rendimiento pero malas temperaturas) asigne correctamente un sentimiento **Positivo** a la performance y uno **Neutral/Negativo** a la temperatura dentro del mismo comentario.

---

## 📊 Paso 4: Visualización de los Dashboards

El sistema genera visualizaciones web totalmente interactivas en la carpeta:
📂 **`d:\ProyectoAPIT\reports\figures\`**

Puedes abrir cualquiera de los siguientes archivos directamente en tu navegador (haciendo doble clic sobre ellos en el Explorador de Windows o arrastrándolos a Chrome/Edge):

1. **`distribucion_sentimiento.html`**: Muestra cuántas menciones existen de cada sentimiento para los diferentes aspectos técnicos globales de hardware.
2. **`sentimiento_por_aspecto.html`**: Gráfico de barras apiladas interactivo que desglosa el porcentaje de polaridad (Positivo, Neutro, Negativo) específico para cada una de las 6 categorías principales (Thermal, Performance, Value, Acoustics, Reliability, Compatibility).
3. **`comparacion_marcas.html`**: Comparación cara a cara de la percepción de los usuarios sobre AMD vs. NVIDIA vs. Intel, analizando qué aspectos son más fuertes o criticados en cada marca.
4. **`evolucion_temporal.html`**: Gráfico de líneas que ilustra la fluctuación de los sentimientos a lo largo del tiempo (fecha y hora del post).

---

## 🔬 Ejecución de Módulos Individuales (Para Pruebas y Desarrollo)

Cada componente de la arquitectura del proyecto puede ejecutarse de manera independiente para validar su comportamiento con entradas de prueba propias escribiendo en terminal:

* **Prueba de Extracción (Reddit API)**:
  `python src/data_collection/reddit_collector.py`
* **Prueba del Limpiador y Detección de Sarcasmo**:
  `python src/preprocessing/text_cleaner.py`
* **Prueba de Extracción de Aspectos (spaCy & SentenceTransformers)**:
  `python src/absa/aspect_extractor.py`
* **Prueba de Clasificador de Sentimiento (RoBERTa Transformer)**:
  `python src/absa/sentiment_classifier.py`
* **Generación Directa de Visualizaciones**:
  `python src/visualization/dashboard.py`

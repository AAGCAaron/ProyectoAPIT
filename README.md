# ABSA para Discusiones de Hardware de PC en YouTube

> Sistema de **Análisis de Sentimiento Basado en Aspectos (ABSA)** orientado a la comunidad de revisión de hardware de PC en YouTube, implementado con Transformers, spaCy y YouTube Data API v3.

---

## 📁 Estructura del Proyecto

```text
ProyectoAPIT/
├── context.md                        # Configuración y objetivos del proyecto
├── requirements.txt                  # Dependencias del proyecto
├── .env.example                      # Plantilla de credenciales (copiar a .env)
├── .gitignore
├── README.md
├── src/
│   ├── data_collection/
│   │   └── youtube_collector.py      # Extracción de datos con YouTube Data API v3
│   ├── preprocessing/
│   │   └── text_cleaner.py           # Limpieza y normalización de texto
│   ├── absa/
│   │   ├── aspect_extractor.py       # Extracción de aspectos (spaCy + SentenceTransformers)
│   │   └── sentiment_classifier.py   # Clasificación de sentimiento (Transformers)
│   └── visualization/
│       └── dashboard.py              # Visualizaciones con Plotly
├── data/
│   └── raw/                          # Datos extraídos de YouTube (CSV, JSON, Parquet)
├── reports/
│   └── figures/                      # Gráficos HTML generados
└── notebook_exploration/
    └── exploracion.ipynb             # Notebook de experimentación
```

---

## ⚙️ Instalación

### 1. Clonar el repositorio y entrar al directorio

```bash
git clone <url-del-repositorio>
cd ProyectoAPIT
```

### 2. Crear y activar el entorno virtual

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux / macOS
python -m venv venv
source venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Descargar el modelo de spaCy

```bash
python -m spacy download en_core_web_sm
```

### 5. Configurar credenciales de YouTube

Copia el archivo `.env.example` a `.env` y completa con tu clave de API:

```bash
cp .env.example .env
```

Para obtener una clave de la **YouTube Data API v3**:
1. Entra a [https://console.cloud.google.com](https://console.cloud.google.com).
2. Crea un proyecto nuevo (o selecciona uno existente).
3. En el menú lateral: **APIs & Services → Library** → busca **"YouTube Data API v3"** → **Enable**.
4. **APIs & Services → Credentials → Create credentials → API key**.
5. Copia la clave generada al archivo `.env`:

```env
YOUTUBE_API_KEY=tu_api_key_aqui
```

> 💡 La cuota gratuita es de **10,000 unidades/día**, suficiente para varios miles de comentarios diarios.

---

## 🚀 Uso

### Extracción de datos de YouTube

```bash
python src/data_collection/youtube_collector.py
```

### Prueba del preprocesador de texto

```bash
python src/preprocessing/text_cleaner.py
```

### Prueba del extractor de aspectos

```bash
python src/absa/aspect_extractor.py
```

### Prueba del clasificador de sentimiento

```bash
python src/absa/sentiment_classifier.py
```

### Generar visualizaciones de ejemplo

```bash
python src/visualization/dashboard.py
```

### Ejecutar el pipeline completo

```bash
python src/main.py
```

---

## 🔬 Pipeline ABSA

```
YouTube Data API v3
      ↓
youtube_collector.py → data/raw/
      ↓
text_cleaner.py (Normalización, jerga, emojis, negaciones)
      ↓
aspect_extractor.py (spaCy + SentenceTransformers)
      ↓
sentiment_classifier.py (RoBERTa / DeBERTa / Zero-shot)
      ↓
dashboard.py (Plotly → reports/figures/)
```

---

## 📊 Categorías de Aspectos

| Categoría     | Términos clave                                         |
|---------------|--------------------------------------------------------|
| `thermal`     | temperature, cooling, thermal throttling, undervolt    |
| `performance` | FPS, 1% low, stuttering, latency, bottleneck           |
| `value`       | price, overpriced, budget, cost-benefit                |
| `acoustics`   | noise, fan noise, coil whine                           |
| `reliability` | crash, failure, BSOD, stability, warranty              |
| `compatibility`| drivers, PCIe, socket, motherboard                   |

---

## 📺 Estrategia de Recolección Mixta

El colector implementa dos vías complementarias de extracción:

1. **Canales especializados**: itera sobre una lista predefinida de canales de revisión de hardware (Linus Tech Tips, Gamers Nexus, Hardware Unboxed, JayzTwoCents, Bitwit, Paul's Hardware, Optimum) y obtiene los videos recientes.
2. **Búsqueda por palabras clave**: ejecuta queries del dominio (ej. *"RTX 4090 review"*, *"Ryzen 7000 benchmark"*) sobre el buscador de YouTube y conserva los videos más relevantes.

Para cada video se extraen los **comentarios de nivel superior** ordenados por relevancia.

---

## 📄 Referencia del Proyecto

- **Formato académico**: IEEE
- **Lenguaje de documentación**: Español
- **Lenguaje de programación**: Python 3.10+
- **Canales analizados**: Linus Tech Tips, Gamers Nexus, Hardware Unboxed, JayzTwoCents, Bitwit, Paul's Hardware, Optimum

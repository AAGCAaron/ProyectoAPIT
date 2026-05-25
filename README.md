# ABSA para Discusiones de Hardware de PC en Reddit

> Sistema de **Análisis de Sentimiento Basado en Aspectos (ABSA)** orientado a comunidades de hardware de PC en Reddit, implementado con Transformers, spaCy y PRAW.

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
│   │   └── reddit_collector.py       # Extracción de datos con PRAW
│   ├── preprocessing/
│   │   └── text_cleaner.py           # Limpieza y normalización de texto
│   ├── absa/
│   │   ├── aspect_extractor.py       # Extracción de aspectos (spaCy + SentenceTransformers)
│   │   └── sentiment_classifier.py   # Clasificación de sentimiento (Transformers)
│   └── visualization/
│       └── dashboard.py              # Visualizaciones con Plotly
├── data/
│   └── raw/                          # Datos extraídos de Reddit (CSV, JSON, Parquet)
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

### 5. Configurar credenciales de Reddit

Copia el archivo `.env.example` a `.env` y completa con tus credenciales:

```bash
cp .env.example .env
```

Para obtener credenciales de Reddit:
1. Ve a [https://www.reddit.com/prefs/apps](https://www.reddit.com/prefs/apps)
2. Crea una nueva aplicación de tipo **script**
3. Copia el `client_id` y `client_secret` al archivo `.env`

---

## 🚀 Uso

### Extracción de datos de Reddit

```bash
python src/data_collection/reddit_collector.py
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

---

## 🔬 Pipeline ABSA

```
Reddit API (PRAW)
      ↓
reddit_collector.py → data/raw/
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

## 📄 Referencia del Proyecto

- **Formato académico**: IEEE  
- **Lenguaje de documentación**: Español  
- **Lenguaje de programación**: Python 3.10+  
- **Subreddits analizados**: r/buildapc, r/pcmasterrace, r/Amd, r/intel, r/nvidia

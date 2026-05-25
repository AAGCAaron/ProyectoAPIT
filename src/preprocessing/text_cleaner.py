"""
========================================================
Módulo: text_cleaner.py
Descripción: Preprocesamiento y normalización de texto
             para comentarios de Reddit sobre hardware de PC.
             Incluye manejo de jerga técnica, emojis,
             negaciones contextuales y sarcasmo.
Idioma de documentación: Español (IEEE)
========================================================
"""

import re
import string
import unicodedata
import nltk
import spacy
from nltk.corpus import stopwords

# Descargar recursos de NLTK si no están disponibles
nltk.download("stopwords", quiet=True)
nltk.download("punkt", quiet=True)
nltk.download("punkt_tab", quiet=True)

# Cargar modelo de lenguaje de spaCy (inglés)
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    print("[ADVERTENCIA] Modelo spaCy 'en_core_web_sm' no encontrado.")
    print("  Ejecuta: python -m spacy download en_core_web_sm")
    nlp = None


# ────────────────────────────────────────────────────────────
# Diccionario de normalización de jerga técnica del dominio
# ────────────────────────────────────────────────────────────

SLANG_HARDWARE = {
    r"\bfps\b":              "frames per second",
    r"\b1%\s*lows?\b":       "low frame rate percentile",
    r"\bbottleneck\b":       "performance limitation",
    r"\bundervolting?\b":    "voltage optimization",
    r"\bstuttering?\b":      "frame pacing issue",
    r"\bcoil\s*whine\b":     "electrical noise",
    r"\bthrottling?\b":      "thermal throttling",
    r"\bOC\b":               "overclocking",
    r"\bTDP\b":              "thermal design power",
    r"\bVRAM\b":             "video memory",
    r"\bGPU\b":              "graphics card",
    r"\bCPU\b":              "processor",
    r"\bPSU\b":              "power supply unit",
    r"\bMOBO\b":             "motherboard",
    r"\bRAM\b":              "random access memory",
    r"\brma\b":              "return merchandise authorization",
    r"\bw\/\b":              "with",
    r"\bw\/o\b":             "without",
    r"\bidk\b":              "I do not know",
    r"\bimo\b":              "in my opinion",
    r"\bimho\b":             "in my honest opinion",
    r"\btbh\b":              "to be honest",
    r"\bngl\b":              "not going to lie",
    r"\bngl\b":              "not going to lie",
    r"\bafaik\b":            "as far as I know",
}

# Mapeo de emojis a sentimiento textual
EMOJI_SENTIMIENTO = {
    "🔥": "excellent performance",
    "💀": "terrible experience",
    "😤": "frustrated",
    "😍": "very satisfied",
    "👍": "recommended",
    "👎": "not recommended",
    "💸": "overpriced",
    "🤔": "uncertain",
    "😂": "sarcasm indicator",
    "💯": "fully satisfied",
    "⚡": "fast performance",
    "🥵": "high temperature",
    "❄️": "good cooling",
    "🚀": "very fast",
    "🗑️": "bad product",
}

# Patrones de negación para preprocesamiento contextual
PATRONES_NEGACION = [
    (r"\bnot\s+good\b",      "bad"),
    (r"\bnot\s+great\b",     "disappointing"),
    (r"\bnot\s+bad\b",       "decent"),
    (r"\bnot\s+worth\b",     "overpriced"),
    (r"\bnot\s+worth\s+it\b","overpriced"),
    (r"\bcan't\s+complain\b","satisfied"),
    (r"\bno\s+issues?\b",    "reliable"),
]

# Indicadores de sarcasmo
INDICADORES_SARCASMO = [
    r"\bsuuure\b",
    r"\bgreat\s+job\b",
    r"\boh\s+wow\b",
    r"\byeah\s+right\b",
    r"\btotally\s+worth\b",
    r"\bjust\s+what\s+I\s+needed\b",
    r"😂.*(?:amazing|great|perfect)",
    r"\bsuch\s+a\s+great\s+deal\b",
]


# ────────────────────────────────────────────────────────────
# Clase principal del preprocesador de texto
# ────────────────────────────────────────────────────────────

class TextCleaner:
    """
    Clase para preprocesamiento y normalización de texto
    proveniente de comentarios de Reddit sobre hardware de PC.

    Implementa las siguientes etapas:
        1. Eliminación de URLs y caracteres especiales.
        2. Normalización de emojis a texto.
        3. Normalización de jerga técnica del dominio.
        4. Manejo de negaciones contextuales.
        5. Detección básica de sarcasmo.
        6. Eliminación de stopwords.
        7. Lematización con spaCy.
    """

    def __init__(self, eliminar_stopwords: bool = True, lematizar: bool = True):
        """
        Inicializa el preprocesador con las opciones configuradas.

        Args:
            eliminar_stopwords: Si True, elimina palabras vacías en inglés.
            lematizar:          Si True, aplica lematización con spaCy.
        """
        self.eliminar_stopwords = eliminar_stopwords
        self.lematizar = lematizar
        self.stopwords_en = set(stopwords.words("english"))

    def eliminar_urls(self, texto: str) -> str:
        """Elimina URLs del texto."""
        patron_url = r"http[s]?://(?:[a-zA-Z]|[0-9]|[$\-@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+"
        return re.sub(patron_url, " ", texto)

    def normalizar_emojis(self, texto: str) -> str:
        """Reemplaza emojis por su representación textual de sentimiento."""
        for emoji, significado in EMOJI_SENTIMIENTO.items():
            texto = texto.replace(emoji, f" {significado} ")
        # Eliminar cualquier emoji residual no mapeado
        texto = unicodedata.normalize("NFKD", texto)
        texto = texto.encode("ascii", "ignore").decode("ascii")
        return texto

    def normalizar_slang(self, texto: str) -> str:
        """Normaliza jerga técnica del dominio de hardware."""
        texto_lower = texto.lower()
        for patron, reemplazo in SLANG_HARDWARE.items():
            texto_lower = re.sub(patron, reemplazo, texto_lower, flags=re.IGNORECASE)
        return texto_lower

    def manejar_negaciones(self, texto: str) -> str:
        """Sustituye patrones de negación contextual comunes."""
        for patron, reemplazo in PATRONES_NEGACION:
            texto = re.sub(patron, reemplazo, texto, flags=re.IGNORECASE)
        return texto

    def detectar_sarcasmo(self, texto: str) -> bool:
        """
        Detección básica de sarcasmo basada en patrones lingüísticos.

        Returns:
            True si se detectan indicadores de sarcasmo, False en caso contrario.
        """
        for patron in INDICADORES_SARCASMO:
            if re.search(patron, texto, flags=re.IGNORECASE):
                return True
        return False

    def eliminar_ruido(self, texto: str) -> str:
        """Elimina caracteres especiales, puntuación excesiva y espacios múltiples."""
        # Eliminar menciones de usuario Reddit (/u/usuario)
        texto = re.sub(r"/u/\w+", "", texto)
        # Eliminar menciones de subreddit (/r/subreddit)
        texto = re.sub(r"/r/\w+", "", texto)
        # Eliminar caracteres especiales de Markdown de Reddit
        texto = re.sub(r"[>\*\_\~\`\#\^\[\]\|]", " ", texto)
        # Eliminar dígitos aislados (no parte de modelos de hardware)
        texto = re.sub(r"\b\d{1,2}\b(?!\s*(th|st|nd|rd|Gen|gen|%))", " ", texto)
        # Normalizar puntuación múltiple
        texto = re.sub(r"[!?]{2,}", "!", texto)
        texto = re.sub(r"\.{2,}", ".", texto)
        # Eliminar espacios múltiples
        texto = re.sub(r"\s+", " ", texto).strip()
        return texto

    def lematizar_texto(self, texto: str) -> str:
        """
        Aplica lematización al texto usando spaCy.

        Args:
            texto: Texto preprocesado.

        Returns:
            Texto lematizado con stopwords eliminadas (si está configurado).
        """
        if nlp is None:
            return texto

        doc = nlp(texto)
        tokens = []
        for token in doc:
            # Filtrar stopwords si está habilitado
            if self.eliminar_stopwords and token.text.lower() in self.stopwords_en:
                continue
            # Filtrar puntuación y espacios
            if token.is_punct or token.is_space:
                continue
            # Usar lema si está habilitado
            lemma = token.lemma_ if self.lematizar else token.text
            tokens.append(lemma.lower())

        return " ".join(tokens)

    def limpiar(self, texto: str) -> dict:
        """
        Aplica el pipeline completo de limpieza y preprocesamiento.

        Args:
            texto: Texto crudo extraído de Reddit.

        Returns:
            Diccionario con el texto procesado y metadatos de análisis.
        """
        if not isinstance(texto, str) or not texto.strip():
            return {"texto_limpio": "", "sarcasmo_detectado": False, "texto_original": texto}

        # Registro del texto original
        texto_original = texto

        # Paso 1: Eliminar URLs
        texto = self.eliminar_urls(texto)

        # Paso 2: Normalizar emojis
        texto = self.normalizar_emojis(texto)

        # Paso 3: Normalizar jerga técnica
        texto = self.normalizar_slang(texto)

        # Paso 4: Manejar negaciones contextuales
        texto = self.manejar_negaciones(texto)

        # Paso 5: Detectar sarcasmo (antes de limpiar más el texto)
        sarcasmo = self.detectar_sarcasmo(texto)

        # Paso 6: Eliminar ruido y caracteres especiales
        texto = self.eliminar_ruido(texto)

        # Paso 7: Lematizar y eliminar stopwords
        texto = self.lematizar_texto(texto)

        return {
            "texto_original":    texto_original,
            "texto_limpio":      texto,
            "sarcasmo_detectado": sarcasmo,
        }


# ────────────────────────────────────────────────────────────
# Punto de entrada para prueba directa del módulo
# ────────────────────────────────────────────────────────────

if __name__ == "__main__":
    cleaner = TextCleaner(eliminar_stopwords=True, lematizar=True)

    ejemplos = [
        "Gaming performance is excellent with the RX 6600 😍, but temperatures 🥵 are concerning.",
        "Not worth it at all. The GPU stuttering is unbearable and coil whine is loud.",
        "Yeah right, the RTX 4090 is TOTALLY worth $1600... suuure 😂",
        "Undervolt fixed my throttling issues. CPU temps dropped 15°C. Highly recommend!",
    ]

    for texto in ejemplos:
        resultado = cleaner.limpiar(texto)
        print(f"\n[ORIGINAL]: {resultado['texto_original']}")
        print(f"[LIMPIO]:   {resultado['texto_limpio']}")
        print(f"[SARCASMO]: {resultado['sarcasmo_detectado']}")

"""
========================================================
Módulo: aspect_extractor.py
Descripción: Extracción y categorización de aspectos
             técnicos en comentarios de hardware de PC
             mediante análisis de dependencias (spaCy)
             y similitud semántica (SentenceTransformers).
Idioma de documentación: Español (IEEE)
========================================================
"""

import re
import spacy
from sentence_transformers import SentenceTransformer, util

# ────────────────────────────────────────────────────────────
# Categorías de aspectos y sus términos representativos
# ────────────────────────────────────────────────────────────

ASPECT_CATEGORIES = {
    "thermal": [
        "temperature", "temps", "cooling", "thermal throttling",
        "undervolt", "heat", "hot", "overheating", "heatsink",
        "thermal paste", "airflow", "fan speed",
    ],
    "performance": [
        "FPS", "frames per second", "low frame rate percentile",
        "frame pacing issue", "latency", "performance limitation",
        "benchmark", "gaming performance", "render time",
        "clock speed", "boost clock", "performance",
    ],
    "value": [
        "price", "overpriced", "budget", "cost-benefit",
        "worth it", "deal", "expensive", "cheap",
        "return merchandise authorization", "value",
    ],
    "acoustics": [
        "noise", "fan noise", "electrical noise", "loud", "quiet",
        "silent", "db", "decibel", "audible",
    ],
    "reliability": [
        "defect", "failure", "crash", "bsod", "driver issue",
        "stability", "lifespan", "warranty", "durable",
    ],
    "compatibility": [
        "compatible", "pcie", "slot", "motherboard", "socket",
        "power connector", "driver support", "operating system",
    ],
}

# ────────────────────────────────────────────────────────────
# Carga de modelos
# ────────────────────────────────────────────────────────────

try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    print("[ADVERTENCIA] Ejecuta: python -m spacy download en_core_web_sm")
    nlp = None

# Modelo de embeddings semánticos para clasificación por similitud
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

# Pre-computar embeddings de referencia para cada categoría
CATEGORY_EMBEDDINGS = {
    categoria: embedding_model.encode(terminos, convert_to_tensor=True)
    for categoria, terminos in ASPECT_CATEGORIES.items()
}


# ────────────────────────────────────────────────────────────
# Clase principal del extractor de aspectos
# ────────────────────────────────────────────────────────────

class AspectExtractor:
    """
    Extractor de aspectos técnicos en comentarios de hardware de PC.

    Combina dos estrategias complementarias:
        1. Extracción basada en reglas: usa patrones de dependencia
           gramatical de spaCy para identificar sustantivos y frases
           nominales relacionados con hardware.
        2. Clasificación semántica: usa SentenceTransformers para
           asignar los aspectos extraídos a las categorías definidas
           mediante similitud de coseno.
    """

    def __init__(self, umbral_similitud: float = 0.35):
        """
        Inicializa el extractor de aspectos.

        Args:
            umbral_similitud: Similitud de coseno mínima para
                              asignar un aspecto a una categoría.
        """
        self.umbral_similitud = umbral_similitud

    def extraer_candidatos_reglas(self, texto: str) -> list[str]:
        """
        Extrae frases candidatas a ser aspectos usando análisis
        de dependencias gramaticales con spaCy.

        Estrategia:
            - Se extraen sustantivos y frases nominales (noun chunks).
            - Se filtran términos irrelevantes o demasiado genéricos.

        Args:
            texto: Texto preprocesado a analizar.

        Returns:
            Lista de strings con los candidatos a aspectos.
        """
        if nlp is None or not texto.strip():
            return []

        doc = nlp(texto)
        candidatos = set()

        # Extraer frases nominales (noun chunks)
        for chunk in doc.noun_chunks:
            if len(chunk.text.split()) <= 4:  # Máximo 4 palabras
                candidatos.add(chunk.text.lower())

        # Extraer sustantivos individuales con contexto adjetival
        for token in doc:
            if token.pos_ in ("NOUN", "PROPN") and len(token.text) > 2:
                candidatos.add(token.lemma_.lower())

        return list(candidatos)

    def clasificar_aspecto(self, candidato: str) -> tuple[str, float]:
        """
        Clasifica un candidato en una de las categorías de aspectos
        usando similitud de coseno entre embeddings semánticos.

        Args:
            candidato: Frase candidata a clasificar.

        Returns:
            Tupla (nombre_categoria, puntaje_similitud).
            Si no supera el umbral, devuelve ('other', score).
        """
        embedding_candidato = embedding_model.encode(candidato, convert_to_tensor=True)

        mejor_categoria = "other"
        mejor_score = 0.0

        for categoria, embeddings_ref in CATEGORY_EMBEDDINGS.items():
            # Calcular similitud con cada término de la categoría
            similitudes = util.cos_sim(embedding_candidato, embeddings_ref)
            score_maximo = float(similitudes.max())

            if score_maximo > mejor_score:
                mejor_score = score_maximo
                mejor_categoria = categoria

        if mejor_score < self.umbral_similitud:
            mejor_categoria = "other"

        return mejor_categoria, round(mejor_score, 4)

    def extraer_aspectos(self, texto: str) -> list[dict]:
        """
        Pipeline completo de extracción y clasificación de aspectos.

        Args:
            texto: Texto preprocesado de un comentario de Reddit.

        Returns:
            Lista de diccionarios con los aspectos detectados:
                - 'aspecto':    Texto del candidato.
                - 'categoria':  Categoría asignada.
                - 'similitud':  Puntaje de confianza.
        """
        candidatos = self.extraer_candidatos_reglas(texto)
        aspectos_detectados = []

        for candidato in candidatos:
            categoria, similitud = self.clasificar_aspecto(candidato)
            if categoria != "other":
                aspectos_detectados.append({
                    "aspecto":   candidato,
                    "categoria": categoria,
                    "similitud": similitud,
                })

        # Ordenar por puntaje de similitud descendente
        aspectos_detectados.sort(key=lambda x: x["similitud"], reverse=True)

        # Eliminar duplicados por categoría (mantener el de mayor similitud)
        categorias_vistas = set()
        aspectos_unicos = []
        for asp in aspectos_detectados:
            if asp["categoria"] not in categorias_vistas:
                aspectos_unicos.append(asp)
                categorias_vistas.add(asp["categoria"])

        return aspectos_unicos


# ────────────────────────────────────────────────────────────
# Punto de entrada para prueba directa del módulo
# ────────────────────────────────────────────────────────────

if __name__ == "__main__":
    extractor = AspectExtractor(umbral_similitud=0.35)

    ejemplos = [
        "Gaming performance is excellent with the RX 6600, but temperatures are concerning.",
        "Not worth it at all. The GPU frame pacing issue is unbearable and electrical noise is loud.",
        "Undervolt fixed my thermal throttling issues. Processor temps dropped 15 degrees.",
        "The video memory is insufficient for modern games at this price point.",
    ]

    for texto in ejemplos:
        print(f"\n[TEXTO]: {texto}")
        aspectos = extractor.extraer_aspectos(texto)
        for asp in aspectos:
            print(f"  → Aspecto: '{asp['aspecto']}' | Categoría: {asp['categoria']} | Similitud: {asp['similitud']}")

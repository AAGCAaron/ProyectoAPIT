"""
========================================================
Módulo: sentiment_classifier.py
Descripción: Clasificación de polaridad de sentimiento
             por aspecto usando modelos Transformer.
             Soporta inferencia zero-shot y fine-tuning.
Idioma de documentación: Español (IEEE)
========================================================
"""

import re
import torch
import pandas as pd
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score,
    f1_score, classification_report, confusion_matrix,
)

# ────────────────────────────────────────────────────────────
# Etiquetas de sentimiento del sistema
# ────────────────────────────────────────────────────────────

ETIQUETAS_SENTIMIENTO = ["Positive", "Neutral", "Negative"]

# Mapa de salida de modelos HuggingFace a etiquetas del proyecto
LABEL_MAP = {
    "LABEL_0": "Negative",
    "LABEL_1": "Neutral",
    "LABEL_2": "Positive",
    "POSITIVE": "Positive",
    "NEGATIVE": "Negative",
    "NEUTRAL":  "Neutral",
    "positive": "Positive",
    "negative": "Negative",
    "neutral":  "Neutral",
}


# ────────────────────────────────────────────────────────────
# Clase principal del clasificador de sentimiento
# ────────────────────────────────────────────────────────────

class SentimentClassifier:
    """
    Clasificador de sentimiento basado en Transformers.

    Modos de operación:
        1. Zero-shot: Clasificación sin entrenamiento usando un modelo
           de inferencia por hipótesis (ej. facebook/bart-large-mnli).
        2. Fine-tuned: Clasificación con un modelo ajustado para
           análisis de sentimiento en reseñas/comentarios técnicos.

    Modelos recomendados:
        - Zero-shot:  "facebook/bart-large-mnli"
        - Fine-tuned: "cardiffnlp/twitter-roberta-base-sentiment-latest"
        - Fine-tuned: "distilbert-base-uncased-finetuned-sst-2-english"
    """

    def __init__(
        self,
        modelo: str = "cardiffnlp/twitter-roberta-base-sentiment-latest",
        modo: str = "fine-tuned",
        longitud_maxima: int = 256,
    ):
        """
        Inicializa el clasificador de sentimiento.

        Args:
            modelo:          Nombre del modelo HuggingFace a utilizar.
            modo:            'zero-shot' o 'fine-tuned'.
            longitud_maxima: Longitud máxima de tokens de entrada.
        """
        self.modo = modo
        self.longitud_maxima = longitud_maxima
        self.device = 0 if torch.cuda.is_available() else -1
        dispositivo_str = "GPU (CUDA)" if self.device == 0 else "CPU"
        print(f"[INFO] Dispositivo de inferencia: {dispositivo_str}")

        if modo == "zero-shot":
            print(f"[INFO] Cargando pipeline zero-shot con modelo: {modelo}")
            self.pipeline = pipeline(
                "zero-shot-classification",
                model=modelo,
                device=self.device,
            )
        else:
            print(f"[INFO] Cargando pipeline de análisis de sentimiento: {modelo}")
            self.pipeline = pipeline(
                "sentiment-analysis",
                model=modelo,
                device=self.device,
                max_length=longitud_maxima,
                truncation=True,
            )

    def clasificar_texto(self, texto: str) -> dict:
        """
        Clasifica el sentimiento de un texto completo.

        Args:
            texto: Texto preprocesado a clasificar.

        Returns:
            Diccionario con 'sentimiento' y 'confianza'.
        """
        if not texto or not texto.strip():
            return {"sentimiento": "Neutral", "confianza": 0.0}

        try:
            if self.modo == "zero-shot":
                resultado = self.pipeline(
                    texto[:512],
                    candidate_labels=ETIQUETAS_SENTIMIENTO,
                )
                idx_mejor = resultado["scores"].index(max(resultado["scores"]))
                return {
                    "sentimiento": resultado["labels"][idx_mejor],
                    "confianza":   round(max(resultado["scores"]), 4),
                }
            else:
                resultado = self.pipeline(texto[:512])[0]
                etiqueta = LABEL_MAP.get(resultado["label"], resultado["label"])
                return {
                    "sentimiento": etiqueta,
                    "confianza":   round(resultado["score"], 4),
                }
        except Exception as e:
            print(f"[ERROR] Clasificación fallida para texto: {str(e)[:80]}")
            return {"sentimiento": "Neutral", "confianza": 0.0}

    def clasificar_por_aspecto(
        self,
        texto: str,
        aspectos: list[dict],
    ) -> list[dict]:
        """
        Clasifica el sentimiento para cada aspecto detectado en el texto.

        Estrategia: Localiza la oración específica que contiene el aspecto
        para clasificar el sentimiento en su contexto local, evitando la
        dilución del sentimiento por el resto del texto.

        Args:
            texto:    Texto completo (preferiblemente original con puntuación).
            aspectos: Lista de aspectos extraídos por AspectExtractor.

        Returns:
            Lista de dicts con aspecto, categoría y sentimiento asociado.
        """
        # Segmentar el texto original en oraciones
        try:
            import nltk
            nltk.download("punkt_tab", quiet=True)
            from nltk.tokenize import sent_tokenize
            oraciones = sent_tokenize(texto)
        except Exception:
            oraciones = [texto]

        resultados = []

        for aspecto_info in aspectos:
            nombre_aspecto = aspecto_info["aspecto"]
            categoria = aspecto_info["categoria"]

            # Intentar encontrar la oración que contiene el aspecto o palabras clave asociadas
            oracion_objetivo = texto  # Por defecto el texto completo
            
            # Buscar coincidencia exacta o parcial del aspecto en las oraciones
            for sent in oraciones:
                sent_lower = sent.lower()
                asp_lower = nombre_aspecto.lower()
                
                # Coincidencia directa como subcadena
                if asp_lower in sent_lower:
                    oracion_objetivo = sent
                    break
                
                # Coincidencia parcial por tokens de palabra
                asp_palabras = set(asp_lower.split())
                sent_palabras = set(re.findall(r'\b\w+\b', sent_lower))
                if asp_palabras & sent_palabras:  # Intersección no vacía
                    oracion_objetivo = sent
                    break

            if self.modo == "zero-shot":
                # Crear hipótesis orientada al aspecto para zero-shot
                hipotesis = [
                    f"The {nombre_aspecto} is {lbl.lower()}."
                    for lbl in ETIQUETAS_SENTIMIENTO
                ]
                resultado_zs = self.pipeline(
                    oracion_objetivo[:512],
                    candidate_labels=ETIQUETAS_SENTIMIENTO,
                    hypothesis_template=f"The {nombre_aspecto} described here is {{}}.",
                )
                idx_mejor = resultado_zs["scores"].index(max(resultado_zs["scores"]))
                sentimiento = resultado_zs["labels"][idx_mejor]
                confianza = round(max(resultado_zs["scores"]), 4)
            else:
                # Para modelos fine-tuned, clasificar la oración que contiene el aspecto
                res = self.clasificar_texto(oracion_objetivo)
                sentimiento = res["sentimiento"]
                confianza = res["confianza"]

            resultados.append({
                "aspecto":    nombre_aspecto,
                "categoria":  categoria,
                "similitud":  aspecto_info.get("similitud", 0.0),
                "sentimiento": sentimiento,
                "confianza":  confianza,
            })

        return resultados

    def clasificar_dataframe(
        self,
        df: pd.DataFrame,
        columna_texto: str = "texto_limpio",
    ) -> pd.DataFrame:
        """
        Aplica la clasificación de sentimiento a un DataFrame completo.

        Args:
            df:            DataFrame con los textos a clasificar.
            columna_texto: Nombre de la columna con el texto preprocesado.

        Returns:
            DataFrame con columnas adicionales 'sentimiento' y 'confianza'.
        """
        print(f"[INFO] Clasificando sentimiento en {len(df)} registros...")
        resultados = df[columna_texto].apply(
            lambda t: self.clasificar_texto(str(t)) if pd.notna(t) else {"sentimiento": "Neutral", "confianza": 0.0}
        )
        df = df.copy()
        df["sentimiento"] = resultados.apply(lambda r: r["sentimiento"])
        df["confianza"]   = resultados.apply(lambda r: r["confianza"])
        return df

    def evaluar(
        self,
        y_real: list[str],
        y_predicho: list[str],
    ) -> dict:
        """
        Calcula métricas de evaluación para el clasificador.

        Args:
            y_real:     Lista de etiquetas reales (ground truth).
            y_predicho: Lista de etiquetas predichas por el modelo.

        Returns:
            Diccionario con métricas de evaluación.
        """
        metricas = {
            "accuracy":  round(accuracy_score(y_real, y_predicho), 4),
            "precision": round(precision_score(y_real, y_predicho, average="weighted", zero_division=0), 4),
            "recall":    round(recall_score(y_real, y_predicho, average="weighted", zero_division=0), 4),
            "f1_score":  round(f1_score(y_real, y_predicho, average="weighted", zero_division=0), 4),
        }

        print("\n" + "═" * 50)
        print("  REPORTE DE EVALUACIÓN DEL MODELO")
        print("═" * 50)
        for k, v in metricas.items():
            print(f"  {k.upper():12s}: {v:.4f}")
        print("─" * 50)
        print(classification_report(y_real, y_predicho, target_names=ETIQUETAS_SENTIMIENTO, zero_division=0))

        metricas["confusion_matrix"] = confusion_matrix(y_real, y_predicho).tolist()
        return metricas


# ────────────────────────────────────────────────────────────
# Punto de entrada para prueba directa del módulo
# ────────────────────────────────────────────────────────────

if __name__ == "__main__":
    clasificador = SentimentClassifier(
        modelo="cardiffnlp/twitter-roberta-base-sentiment-latest",
        modo="fine-tuned",
    )

    comentarios = [
        "Gaming performance is excellent with the RX 6600, highly recommend.",
        "Not worth it at all. The GPU frame pacing issue is unbearable and electrical noise is loud.",
        "Undervolt fixed my thermal throttling issues. Processor temps dropped 15 degrees.",
        "The video memory is insufficient for modern games at this price point.",
        "It is ok I guess, nothing special but does the job.",
    ]

    for comentario in comentarios:
        resultado = clasificador.clasificar_texto(comentario)
        print(f"\n[TEXTO]:      {comentario[:80]}...")
        print(f"[SENTIMIENTO]: {resultado['sentimiento']} (confianza: {resultado['confianza']})")

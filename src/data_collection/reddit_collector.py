"""
========================================================
Módulo: reddit_collector.py
Descripción: Extracción de publicaciones y comentarios
             de Reddit sobre hardware de PC usando PRAW.
Idioma de documentación: Español (IEEE)
========================================================
"""

import praw
import pandas as pd
import json
import os
from datetime import datetime
from dotenv import load_dotenv

# Cargar credenciales desde archivo .env
load_dotenv()


# ────────────────────────────────────────────────────────────
# Configuración de subreddits y palabras clave del dominio
# ────────────────────────────────────────────────────────────

SUBREDDITS = [
    "buildapc",
    "pcmasterrace",
    "Amd",
    "intel",
    "nvidia",
]

HARDWARE_KEYWORDS = [
    # CPUs
    "Ryzen 5000", "Ryzen 7000", "Intel 12th Gen", "Intel 13th Gen",
    # GPUs
    "RTX 3000", "RTX 4000", "RTX 3060", "RTX 3070", "RTX 3080", "RTX 3090",
    "RTX 4060", "RTX 4070", "RTX 4080", "RTX 4090",
    "RX 6600", "RX 6700", "RX 6800", "RX 6900",
    "RX 7600", "RX 7700", "RX 7800", "RX 7900",
    # Términos técnicos
    "temperature", "thermal throttling", "FPS", "1% low",
    "bottleneck", "stuttering", "latency", "undervolt",
    "coil whine", "overpriced", "budget build",
]


# ────────────────────────────────────────────────────────────
# Clase principal del colector
# ────────────────────────────────────────────────────────────

class RedditCollector:
    """
    Clase para extraer publicaciones y comentarios de Reddit
    sobre hardware de PC utilizando la API PRAW.

    Parámetros de inicialización:
        client_id     -- ID de cliente de la aplicación Reddit.
        client_secret -- Secreto de cliente de la aplicación Reddit.
        user_agent    -- Identificador del agente de usuario.
    """

    def __init__(self, client_id: str, client_secret: str, user_agent: str):
        """Inicializa la conexión con la API de Reddit."""
        self.reddit = praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            user_agent=user_agent,
        )
        print("[INFO] Conexión con la API de Reddit establecida correctamente.")

    def _contiene_keyword(self, texto: str) -> bool:
        """
        Verifica si un texto contiene al menos una de las
        palabras clave definidas para el dominio de hardware.

        Args:
            texto: Cadena de texto a verificar.

        Returns:
            True si contiene al menos una palabra clave, False en caso contrario.
        """
        texto_lower = texto.lower()
        return any(kw.lower() in texto_lower for kw in HARDWARE_KEYWORDS)

    def extraer_publicaciones(
        self,
        subreddit_name: str,
        limite: int = 500,
        categoria: str = "hot",
    ) -> list[dict]:
        """
        Extrae publicaciones de un subreddit específico.

        Args:
            subreddit_name: Nombre del subreddit (sin 'r/').
            limite:         Número máximo de publicaciones a extraer.
            categoria:      Categoría de ordenamiento ('hot', 'new', 'top').

        Returns:
            Lista de diccionarios con los datos de cada publicación.
        """
        subreddit = self.reddit.subreddit(subreddit_name)
        publicaciones = []

        # Seleccionar el método de ordenamiento
        if categoria == "hot":
            generador = subreddit.hot(limit=limite)
        elif categoria == "new":
            generador = subreddit.new(limit=limite)
        elif categoria == "top":
            generador = subreddit.top(limit=limite, time_filter="year")
        else:
            generador = subreddit.hot(limit=limite)

        print(f"[INFO] Extrayendo publicaciones de r/{subreddit_name} ({categoria})...")

        for post in generador:
            # Filtrar únicamente publicaciones relacionadas con hardware
            if self._contiene_keyword(post.title) or self._contiene_keyword(post.selftext):
                publicaciones.append({
                    "id":          post.id,
                    "subreddit":   subreddit_name,
                    "titulo":      post.title,
                    "cuerpo":      post.selftext,
                    "score":       post.score,
                    "upvote_ratio": post.upvote_ratio,
                    "num_comentarios": post.num_comments,
                    "autor":       str(post.author),
                    "timestamp":   datetime.utcfromtimestamp(post.created_utc).isoformat(),
                    "url":         post.url,
                    "permalink":   f"https://reddit.com{post.permalink}",
                    "tipo":        "publicacion",
                })

        print(f"[INFO] {len(publicaciones)} publicaciones relevantes extraídas de r/{subreddit_name}.")
        return publicaciones

    def extraer_comentarios(
        self,
        post_id: str,
        limite_comentarios: int = 50,
    ) -> list[dict]:
        """
        Extrae los comentarios de una publicación específica.

        Args:
            post_id:            ID de la publicación en Reddit.
            limite_comentarios: Número máximo de comentarios a extraer.

        Returns:
            Lista de diccionarios con los datos de cada comentario.
        """
        submission = self.reddit.submission(id=post_id)
        submission.comments.replace_more(limit=0)  # Evita peticiones adicionales
        comentarios = []

        for comentario in submission.comments.list()[:limite_comentarios]:
            if hasattr(comentario, "body") and self._contiene_keyword(comentario.body):
                comentarios.append({
                    "id":          comentario.id,
                    "post_id":     post_id,
                    "subreddit":   str(submission.subreddit),
                    "cuerpo":      comentario.body,
                    "score":       comentario.score,
                    "autor":       str(comentario.author),
                    "timestamp":   datetime.utcfromtimestamp(comentario.created_utc).isoformat(),
                    "tipo":        "comentario",
                })

        return comentarios

    def recolectar_todo(
        self,
        limite_posts: int = 200,
        limite_comentarios: int = 30,
        categoria: str = "hot",
    ) -> pd.DataFrame:
        """
        Extrae publicaciones y comentarios de todos los subreddits
        configurados y los consolida en un único DataFrame.

        Args:
            limite_posts:       Posts máximos por subreddit.
            limite_comentarios: Comentarios máximos por post.
            categoria:          Categoría de ordenamiento.

        Returns:
            DataFrame consolidado con toda la información extraída.
        """
        todos_los_datos = []

        for sub in SUBREDDITS:
            # Extraer publicaciones
            posts = self.extraer_publicaciones(sub, limite_posts, categoria)
            todos_los_datos.extend(posts)

            # Extraer comentarios de cada publicación relevante
            for post in posts:
                comentarios = self.extraer_comentarios(post["id"], limite_comentarios)
                todos_los_datos.extend(comentarios)

        df = pd.DataFrame(todos_los_datos)
        print(f"\n[INFO] Total de registros recopilados: {len(df)}")
        return df

    def guardar_datos(
        self,
        df: pd.DataFrame,
        ruta_salida: str = "data/raw",
        formatos: list[str] | None = None,
    ) -> None:
        """
        Guarda el DataFrame en los formatos especificados.

        Args:
            df:          DataFrame con los datos extraídos.
            ruta_salida: Directorio de destino para los archivos.
            formatos:    Lista de formatos ('csv', 'json', 'parquet').
        """
        if formatos is None:
            formatos = ["csv", "json", "parquet"]

        os.makedirs(ruta_salida, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        nombre_base = f"reddit_hardware_{timestamp}"

        if "csv" in formatos:
            ruta = os.path.join(ruta_salida, f"{nombre_base}.csv")
            df.to_csv(ruta, index=False, encoding="utf-8")
            print(f"[INFO] Archivo CSV guardado en: {ruta}")

        if "json" in formatos:
            ruta = os.path.join(ruta_salida, f"{nombre_base}.json")
            df.to_json(ruta, orient="records", force_ascii=False, indent=2)
            print(f"[INFO] Archivo JSON guardado en: {ruta}")

        if "parquet" in formatos:
            ruta = os.path.join(ruta_salida, f"{nombre_base}.parquet")
            df.to_parquet(ruta, index=False)
            print(f"[INFO] Archivo Parquet guardado en: {ruta}")


# ────────────────────────────────────────────────────────────
# Punto de entrada para prueba directa del módulo
# ────────────────────────────────────────────────────────────

if __name__ == "__main__":
    # Las credenciales se cargan desde el archivo .env
    colector = RedditCollector(
        client_id=os.getenv("REDDIT_CLIENT_ID"),
        client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
        user_agent=os.getenv("REDDIT_USER_AGENT", "ABSA-PCHardware/1.0"),
    )

    # Recolectar datos y guardarlos
    dataframe = colector.recolectar_todo(
        limite_posts=100,
        limite_comentarios=20,
        categoria="top",
    )

    colector.guardar_datos(dataframe, ruta_salida="data/raw")

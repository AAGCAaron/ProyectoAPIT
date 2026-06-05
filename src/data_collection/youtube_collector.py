"""
========================================================
Módulo: youtube_collector.py
Descripción: Extracción de comentarios de YouTube sobre
             hardware de PC mediante la API oficial
             YouTube Data API v3.
             Estrategia mixta:
               (a) Canales especializados en hardware.
               (b) Búsquedas por palabras clave del dominio.

Proyecto:    ¿Mi PC corre el DOOM?
Equipo 12 — "Los Papois":
    - Capistrán Ponce Manuel Emiliano
    - Gutiérrez Contreras Aldo Aarón
    - Rivera López David Zaid
    - Suárez Guzmán Dayna Yarelly
Asignatura:  Análisis y Procesamiento Inteligente de Textos
Profesor:    Octavio Sánchez
Universidad: Facultad de Ingeniería, UNAM
Semestre:    2026-2

Idioma de documentación: Español (IEEE)
========================================================
"""

import os
import time
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

load_dotenv()


# ────────────────────────────────────────────────────────────
# Configuración del dominio: canales y palabras clave
# ────────────────────────────────────────────────────────────

# Canales de referencia en el ecosistema de revisión de hardware de PC.
# Se utilizan sus identificadores únicos (channelId) para obtener los videos
# más recientes asociados a cada uno.
HARDWARE_CHANNELS = {
    "Linus Tech Tips":   "UCXuqSBlHAE6Xw-yeJA0Tunw",
    "Gamers Nexus":      "UChIs72whgZI9w6d6FhwGGHA",
    "Hardware Unboxed":  "UCI8iQa1hv7oV_Z8D35vVuSg",
    "JayzTwoCents":      "UCkWQ0gDrqOCarmUKmppD7GQ",
    "Bitwit":            "UCftcLVz-jtPXoH3cWUUDwYw",
    "Paul's Hardware":   "UCvWWf-LYjaujE50iYai8WgQ",
    "Optimum":           "UCC3EJZF7Ul0EWtoCEFlhz_Q",
}

# Términos de búsqueda orientados al dominio de hardware de PC.
HARDWARE_KEYWORDS = [
    # CPUs
    "Ryzen 7000 review", "Ryzen 5000 review",
    "Intel 13th Gen review", "Intel 12th Gen review",
    # GPUs
    "RTX 4090 review", "RTX 4080 review", "RTX 4070 review",
    "RTX 3080 review", "RTX 3070 review",
    "RX 7900 XTX review", "RX 7800 XT review", "RX 6700 XT review",
    # Términos técnicos
    "GPU temperature problem", "thermal throttling CPU",
    "coil whine GPU", "FPS bottleneck",
    "best budget GPU build",
]


# ────────────────────────────────────────────────────────────
# Clase principal del colector
# ────────────────────────────────────────────────────────────

class YouTubeCollector:
    """
    Colector de comentarios de YouTube orientado al dominio
    de hardware de PC mediante YouTube Data API v3.

    Estrategia de extracción:
        (a) Canales: itera sobre una lista predefinida de
            canales especializados y obtiene sus videos recientes.
        (b) Búsqueda por keywords: ejecuta queries del dominio
            sobre el buscador de YouTube y conserva los videos
            más relevantes.

    Parámetros:
        api_key -- Clave de la YouTube Data API v3.
    """

    def __init__(self, api_key: str):
        if not api_key or api_key == "TU_API_KEY_AQUI":
            raise ValueError(
                "YOUTUBE_API_KEY no está configurada. "
                "Defínela en el archivo .env."
            )
        self.youtube = build("youtube", "v3", developerKey=api_key)
        print("[INFO] Conexión con YouTube Data API v3 establecida correctamente.")

    # ────────────────────────────────────────────────────────
    # Obtención de videos
    # ────────────────────────────────────────────────────────

    def videos_por_canal(self, channel_id: str, limite: int = 10) -> list[dict]:
        """
        Obtiene los videos más recientes publicados por un canal.

        Args:
            channel_id: Identificador único del canal de YouTube.
            limite:     Número máximo de videos a obtener (1-50).

        Returns:
            Lista de diccionarios con metadatos básicos de cada video.
        """
        try:
            respuesta = self.youtube.search().list(
                part="snippet",
                channelId=channel_id,
                maxResults=min(limite, 50),
                order="date",
                type="video",
            ).execute()
        except HttpError as e:
            print(f"[WARN] Error al consultar canal {channel_id}: {e}")
            return []

        videos = []
        for item in respuesta.get("items", []):
            videos.append({
                "video_id":   item["id"]["videoId"],
                "titulo":     item["snippet"]["title"],
                "descripcion": item["snippet"]["description"],
                "canal":      item["snippet"]["channelTitle"],
                "timestamp":  item["snippet"]["publishedAt"],
            })
        return videos

    def videos_por_busqueda(self, query: str, limite: int = 10) -> list[dict]:
        """
        Busca videos por palabra clave del dominio de hardware.

        Args:
            query:  Cadena de búsqueda (ej. "RTX 4090 review").
            limite: Número máximo de videos a obtener (1-50).

        Returns:
            Lista de diccionarios con metadatos de los videos encontrados.
        """
        try:
            respuesta = self.youtube.search().list(
                part="snippet",
                q=query,
                maxResults=min(limite, 50),
                order="relevance",
                type="video",
                relevanceLanguage="en",
            ).execute()
        except HttpError as e:
            print(f"[WARN] Error en búsqueda '{query}': {e}")
            return []

        videos = []
        for item in respuesta.get("items", []):
            videos.append({
                "video_id":   item["id"]["videoId"],
                "titulo":     item["snippet"]["title"],
                "descripcion": item["snippet"]["description"],
                "canal":      item["snippet"]["channelTitle"],
                "timestamp":  item["snippet"]["publishedAt"],
                "query":      query,
            })
        return videos

    # ────────────────────────────────────────────────────────
    # Extracción de comentarios
    # ────────────────────────────────────────────────────────

    def extraer_comentarios(
        self,
        video_id: str,
        limite_comentarios: int = 50,
    ) -> list[dict]:
        """
        Extrae comentarios de nivel superior de un video.

        Args:
            video_id:            Identificador único del video.
            limite_comentarios:  Número máximo de comentarios a extraer.

        Returns:
            Lista de diccionarios con los datos de cada comentario.
        """
        comentarios = []
        page_token = None

        while len(comentarios) < limite_comentarios:
            try:
                respuesta = self.youtube.commentThreads().list(
                    part="snippet",
                    videoId=video_id,
                    maxResults=min(100, limite_comentarios - len(comentarios)),
                    pageToken=page_token,
                    textFormat="plainText",
                    order="relevance",
                ).execute()
            except HttpError as e:
                # Los videos con comentarios deshabilitados devuelven 403.
                if e.resp.status in (403, 404):
                    return comentarios
                print(f"[WARN] Error en video {video_id}: {e}")
                return comentarios

            for hilo in respuesta.get("items", []):
                top = hilo["snippet"]["topLevelComment"]["snippet"]
                comentarios.append({
                    "id":         hilo["id"],
                    "video_id":   video_id,
                    "cuerpo":     top.get("textDisplay", ""),
                    "score":      top.get("likeCount", 0),
                    "autor":      top.get("authorDisplayName", ""),
                    "timestamp":  top.get("publishedAt", ""),
                    "tipo":       "comentario",
                })

            page_token = respuesta.get("nextPageToken")
            if not page_token:
                break

        return comentarios

    # ────────────────────────────────────────────────────────
    # Orquestación del pipeline de recolección
    # ────────────────────────────────────────────────────────

    def recolectar_todo(
        self,
        videos_por_canal: int = 5,
        videos_por_query: int = 5,
        limite_comentarios: int = 30,
        usar_canales: bool = True,
        usar_keywords: bool = True,
    ) -> pd.DataFrame:
        """
        Ejecuta la estrategia mixta: extrae videos por canal y por
        búsqueda de keywords, y obtiene los comentarios de cada uno.

        Args:
            videos_por_canal:    Videos a extraer por cada canal.
            videos_por_query:    Videos a extraer por cada keyword.
            limite_comentarios:  Comentarios máximos por video.
            usar_canales:        Activa la rama (a) de canales.
            usar_keywords:       Activa la rama (b) de keywords.

        Returns:
            DataFrame consolidado con videos y comentarios.
        """
        registros = []
        videos_vistos = set()

        # ── (a) Recolección por canales ──
        if usar_canales:
            print("\n[INFO] === Estrategia A: canales especializados ===")
            for nombre, channel_id in HARDWARE_CHANNELS.items():
                print(f"[INFO] Canal: {nombre}")
                videos = self.videos_por_canal(channel_id, videos_por_canal)
                for v in videos:
                    if v["video_id"] in videos_vistos:
                        continue
                    videos_vistos.add(v["video_id"])
                    v["tipo"] = "video"
                    v["origen"] = f"canal:{nombre}"
                    registros.append(v)

                    comentarios = self.extraer_comentarios(
                        v["video_id"], limite_comentarios,
                    )
                    for c in comentarios:
                        c["origen"] = f"canal:{nombre}"
                    registros.extend(comentarios)
                    time.sleep(0.3)

        # ── (b) Recolección por keywords ──
        if usar_keywords:
            print("\n[INFO] === Estrategia B: búsqueda por keywords ===")
            for query in HARDWARE_KEYWORDS:
                print(f"[INFO] Query: \"{query}\"")
                videos = self.videos_por_busqueda(query, videos_por_query)
                for v in videos:
                    if v["video_id"] in videos_vistos:
                        continue
                    videos_vistos.add(v["video_id"])
                    v["tipo"] = "video"
                    v["origen"] = f"query:{query}"
                    registros.append(v)

                    comentarios = self.extraer_comentarios(
                        v["video_id"], limite_comentarios,
                    )
                    for c in comentarios:
                        c["origen"] = f"query:{query}"
                    registros.extend(comentarios)
                    time.sleep(0.3)

        df = pd.DataFrame(registros)
        print(f"\n[INFO] Total de registros recopilados: {len(df)}")
        print(f"[INFO] Videos únicos: {len(videos_vistos)}")
        return df

    # ────────────────────────────────────────────────────────
    # Persistencia
    # ────────────────────────────────────────────────────────

    def guardar_datos(
        self,
        df: pd.DataFrame,
        ruta_salida: str = "data/raw",
        formatos: list[str] | None = None,
    ) -> None:
        """
        Guarda el DataFrame en los formatos especificados.

        Args:
            df:          DataFrame con los datos recolectados.
            ruta_salida: Directorio de destino.
            formatos:    Lista de formatos ('csv', 'json', 'parquet').
        """
        if formatos is None:
            formatos = ["csv", "json", "parquet"]

        os.makedirs(ruta_salida, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        nombre_base = f"youtube_hardware_{timestamp}"

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
    colector = YouTubeCollector(api_key=os.getenv("YOUTUBE_API_KEY"))

    dataframe = colector.recolectar_todo(
        videos_por_canal=3,
        videos_por_query=3,
        limite_comentarios=20,
    )

    colector.guardar_datos(dataframe, ruta_salida="data/raw")

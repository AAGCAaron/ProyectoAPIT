"""
========================================================
Archivo: src/main.py
Descripción: Pipeline de ejecución principal para el
             sistema ABSA de PC Hardware.
             Permite ejecutar el pipeline con datos reales
             (si se configuran las credenciales de YouTube)
             o con datos simulados para validar la
             funcionalidad de forma offline.

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
import pandas as pd
from dotenv import load_dotenv

# Importar los módulos del proyecto
from data_collection.youtube_collector import YouTubeCollector
from preprocessing.text_cleaner import TextCleaner
from absa.aspect_extractor import AspectExtractor
from absa.sentiment_classifier import SentimentClassifier
from visualization.dashboard import Dashboard

# Cargar variables de entorno
load_dotenv()

# Datos sintéticos representativos para probar todo el pipeline de inmediato
MOCK_YOUTUBE_DATA = [
    {
        "id": "post1",
        "canal": "Gamers Nexus",
        "titulo": "My new Ryzen 7800X3D is running hot",
        "cuerpo": "I just built my PC. The gaming performance is absolutely insane, I get 200+ FPS in Cyberpunk! However, the idle temperatures are reaching 65C. Is my liquid cooling setup wrong? I'm getting slight stuttering in some games too.",
        "score": 150,
        "timestamp": "2026-05-18T10:00:00",
        "marca": "AMD",
        "tipo": "video"
    },
    {
        "id": "post2",
        "canal": "Linus Tech Tips",
        "titulo": "RTX 4080 Super coil whine is unbearable",
        "cuerpo": "Just got the card today. The performance is wonderful but the coil whine is extremely loud when playing games at high framerates. I can hear the high-pitched electrical noise even through my headphones. Definitely overpriced considering this noise issue.",
        "score": 85,
        "timestamp": "2026-05-19T14:30:00",
        "marca": "NVIDIA",
        "tipo": "video"
    },
    {
        "id": "comm1",
        "canal": "Hardware Unboxed",
        "cuerpo": "Intel 13th Gen has some serious stability issues, but my Intel 12th Gen is running great, no crashes so far. The price was budget-friendly too.",
        "score": 12,
        "timestamp": "2026-05-19T16:00:00",
        "marca": "Intel",
        "tipo": "comentario"
    },
    {
        "id": "comm2",
        "canal": "JayzTwoCents",
        "cuerpo": "The RX 7800 XT offers great value compared to the overpriced 4070. Temps are cool and fan noise is silent.",
        "score": 45,
        "timestamp": "2026-05-20T09:15:00",
        "marca": "AMD",
        "tipo": "comentario"
    },
    {
        "id": "comm3",
        "canal": "Linus Tech Tips",
        "cuerpo": "Yeah right, the RTX 4090 is TOTALLY worth $1600... suuure 😂. The budget builds are dead.",
        "score": 3,
        "timestamp": "2026-05-20T11:20:00",
        "marca": "NVIDIA",
        "tipo": "comentario"
    }
]

def identificar_marca(texto: str) -> str:
    """Detecta de qué marca principal (AMD, NVIDIA, Intel) se habla en el texto."""
    texto_lower = texto.lower()
    if "amd" in texto_lower or "ryzen" in texto_lower or "radeon" in texto_lower or "rx" in texto_lower:
        return "AMD"
    elif "nvidia" in texto_lower or "rtx" in texto_lower or "geforce" in texto_lower:
        return "NVIDIA"
    elif "intel" in texto_lower or "i7" in texto_lower or "i9" in texto_lower or "i5" in texto_lower:
        return "Intel"
    return "Other"

def main():
    print("=" * 60)
    print(" INICIANDO PIPELINE ABSA - PC HARDWARE")
    print("=" * 60)

    # ────────────────────────────────────────────────────────────
    # Paso 1: Obtención de Datos
    # ────────────────────────────────────────────────────────────
    youtube_api_key = os.getenv("YOUTUBE_API_KEY")

    usar_datos_reales = (
        youtube_api_key and
        youtube_api_key != "TU_API_KEY_AQUI"
    )

    if usar_datos_reales:
        print("[PIPELINE] Credenciales detectadas. Extrayendo datos reales de YouTube...")
        try:
            colector = YouTubeCollector(api_key=youtube_api_key)
            df_raw = colector.recolectar_todo(
                videos_por_canal=5,
                videos_por_query=5,
                limite_comentarios=30,
            )
            print(f"[PIPELINE] Extracción exitosa: {len(df_raw)} registros recolectados.")
            # Persistir datos crudos para reproducibilidad
            colector.guardar_datos(df_raw, ruta_salida="data/raw")
        except Exception as e:
            print(f"[PIPELINE] Error al conectar con YouTube API: {e}")
            print("[PIPELINE] Cambiando a datos de prueba simulados...")
            df_raw = pd.DataFrame(MOCK_YOUTUBE_DATA)
    else:
        print("[PIPELINE] No se configuró YOUTUBE_API_KEY válida en el .env.")
        print("[PIPELINE] Utilizando base de datos simulada para demostración...")
        df_raw = pd.DataFrame(MOCK_YOUTUBE_DATA)

    # ────────────────────────────────────────────────────────────
    # Paso 2: Limpieza y Preprocesamiento
    # ────────────────────────────────────────────────────────────
    print("\n[PIPELINE] Ejecutando preprocesador y limpiador de texto...")
    cleaner = TextCleaner(eliminar_stopwords=True, lematizar=True)

    columna_texto = "cuerpo" if "cuerpo" in df_raw.columns else "titulo"

    limpios = []
    sarcasmos = []

    for idx, row in df_raw.iterrows():
        texto_original = str(row[columna_texto]) if pd.notna(row[columna_texto]) else ""
        res_limpieza = cleaner.limpiar(texto_original)
        limpios.append(res_limpieza["texto_limpio"])
        sarcasmos.append(res_limpieza["sarcasmo_detectado"])

    df_raw["texto_limpio"] = limpios
    df_raw["sarcasmo_detectado"] = sarcasmos

    # Asignar marca si no está presente
    if "marca" not in df_raw.columns:
        # (a) Construir mapa video_id → marca usando título + descripción del video
        mapa_marca_video = {}
        if "video_id" in df_raw.columns and "titulo" in df_raw.columns:
            videos = df_raw[df_raw["tipo"] == "video"]
            for _, v in videos.iterrows():
                contexto = f"{v.get('titulo', '')} {v.get('descripcion', '')}"
                marca = identificar_marca(contexto)
                if marca != "Other":
                    mapa_marca_video[v["video_id"]] = marca

        # (b) Asignar marca: primero buscar en el propio texto;
        #     si es 'Other' y el registro es comentario, heredar del video padre.
        def asignar_marca(row):
            marca = identificar_marca(str(row[columna_texto]))
            if marca == "Other" and row.get("tipo") == "comentario":
                vid = row.get("video_id")
                if vid in mapa_marca_video:
                    return mapa_marca_video[vid]
            return marca

        df_raw["marca"] = df_raw.apply(asignar_marca, axis=1)

    # ────────────────────────────────────────────────────────────
    # Paso 3: Extracción de Aspectos y Análisis de Sentimiento
    # ────────────────────────────────────────────────────────────
    print("\n[PIPELINE] Extrayendo aspectos y clasificando sentimiento...")
    extractor = AspectExtractor(umbral_similitud=0.50)
    clasificador = SentimentClassifier(modo="fine-tuned")

    registros_absa = []

    for idx, row in df_raw.iterrows():
        texto_original = str(row[columna_texto])
        texto_limpio = row["texto_limpio"]
        marca = row["marca"]
        timestamp = row["timestamp"]

        # Extraer aspectos del texto limpio
        aspectos = extractor.extraer_aspectos(texto_limpio)

        if aspectos:
            # Evaluar sentimiento para cada aspecto en base al texto original (con puntuación y estructura)
            analisis_sentimiento = clasificador.clasificar_por_aspecto(texto_original, aspectos)

            for res in analisis_sentimiento:
                registros_absa.append({
                    "id":          row["id"],
                    "texto_original": texto_original,
                    "marca":       marca,
                    "timestamp":   timestamp,
                    "aspecto":     res["aspecto"],
                    "categoria":   res["categoria"],
                    "sentimiento": res["sentimiento"],
                    "confianza":   res["confianza"],
                    "sarcasmo":    row["sarcasmo_detectado"]
                })
        else:
            # Sentimiento general si no hay aspecto específico detectado
            res_gen = clasificador.clasificar_texto(texto_limpio)
            registros_absa.append({
                "id":          row["id"],
                "texto_original": texto_original,
                "marca":       marca,
                "timestamp":   timestamp,
                "aspecto":     "general",
                "categoria":   "general",
                "sentimiento": res_gen["sentimiento"],
                "confianza":   res_gen["confianza"],
                "sarcasmo":    row["sarcasmo_detectado"]
            })

    df_absa = pd.DataFrame(registros_absa)

    # Guardar resultados analizados
    os.makedirs("data/processed", exist_ok=True)
    df_absa.to_csv("data/processed/absa_results.csv", index=False, encoding="utf-8")
    print(f"[PIPELINE] Resultados ABSA guardados en: data/processed/absa_results.csv")

    # Mostrar vista previa de resultados
    print("\n" + "-"*50)
    print(" Vista previa del análisis ABSA:")
    print("-"*50)
    for idx, r in df_absa.head(10).iterrows():
        print(f"[{r['marca']}] Aspecto: {r['aspecto']:15s} | Cat: {r['categoria']:12s} | Sentimiento: {r['sentimiento']} ({r['confianza']})")
    print("-"*50)

    # ────────────────────────────────────────────────────────────
    # Paso 4: Visualización y Reportes
    # ────────────────────────────────────────────────────────────
    print("\n[PIPELINE] Generando dashboard de visualizaciones...")
    dash = Dashboard(directorio_salida="reports/figures")

    dash.grafico_distribucion_sentimiento(df_absa, titulo="Distribución de Sentimiento por Aspectos de Hardware")
    dash.grafico_sentimiento_por_aspecto(df_absa)
    dash.grafico_comparacion_marcas(df_absa)
    dash.grafico_evolucion_temporal(df_absa)

    print("\n" + "=" * 60)
    print(" PIPELINE COMPLETADO EXITOSAMENTE")
    print(" Gráficos interactivos HTML guardados en: reports/figures/")
    print("=" * 60)

if __name__ == "__main__":
    main()

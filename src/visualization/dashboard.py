"""
========================================================
Módulo: dashboard.py
Descripción: Generación de visualizaciones y reportes
             estadísticos para el análisis ABSA de
             hardware de PC en YouTube.

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
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots


# ────────────────────────────────────────────────────────────
# Paleta de colores del proyecto
# ────────────────────────────────────────────────────────────

COLORES_SENTIMIENTO = {
    "Positive": "#2ECC71",   # Verde esmeralda
    "Neutral":  "#95A5A6",   # Gris azulado
    "Negative": "#E74C3C",   # Rojo carmín
}

COLORES_MARCA = {
    "AMD":    "#ED1C24",
    "NVIDIA": "#76B900",
    "Intel":  "#0071C5",
}


# ────────────────────────────────────────────────────────────
# Clase principal del generador de visualizaciones
# ────────────────────────────────────────────────────────────

class Dashboard:
    """
    Clase para generar visualizaciones estadísticas del análisis ABSA.

    Genera los siguientes tipos de gráficos:
        - Distribución de sentimiento por aspecto.
        - Comparación entre marcas (AMD vs NVIDIA vs Intel).
        - Evolución temporal del sentimiento.
        - Mapas de calor de correlación.
        - Métricas de evaluación del modelo.
    """

    def __init__(self, directorio_salida: str = "reports/figures"):
        """
        Inicializa el generador de visualizaciones.

        Args:
            directorio_salida: Ruta donde se guardarán los gráficos.
        """
        self.directorio_salida = directorio_salida
        os.makedirs(directorio_salida, exist_ok=True)
        # Estilo de Matplotlib
        plt.rcParams.update({
            "figure.facecolor": "#1A1A2E",
            "axes.facecolor":   "#16213E",
            "axes.edgecolor":   "#E0E0E0",
            "text.color":       "#E0E0E0",
            "axes.labelcolor":  "#E0E0E0",
            "xtick.color":      "#E0E0E0",
            "ytick.color":      "#E0E0E0",
            "grid.color":       "#2A2A4A",
            "font.family":      "DejaVu Sans",
        })

    def grafico_distribucion_sentimiento(
        self,
        df: pd.DataFrame,
        columna_sentimiento: str = "sentimiento",
        titulo: str = "Distribución de Sentimiento General",
        guardar: bool = True,
    ) -> go.Figure:
        """
        Genera un gráfico de pastel con la distribución de sentimientos.

        Args:
            df:                   DataFrame con columna de sentimiento.
            columna_sentimiento:  Nombre de la columna de sentimiento.
            titulo:               Título del gráfico.
            guardar:              Si True, guarda el gráfico en HTML.

        Returns:
            Figura de Plotly.
        """
        conteos = df[columna_sentimiento].value_counts().reset_index()
        conteos.columns = ["Sentimiento", "Cantidad"]

        fig = px.pie(
            conteos,
            names="Sentimiento",
            values="Cantidad",
            title=titulo,
            color="Sentimiento",
            color_discrete_map=COLORES_SENTIMIENTO,
            hole=0.4,
        )
        fig.update_layout(
            paper_bgcolor="#1A1A2E",
            plot_bgcolor="#16213E",
            font=dict(color="#E0E0E0", size=13),
            title_font_size=18,
        )

        if guardar:
            ruta = os.path.join(self.directorio_salida, "distribucion_sentimiento.html")
            fig.write_html(ruta)
            print(f"[INFO] Gráfico guardado: {ruta}")

        return fig

    def grafico_sentimiento_por_aspecto(
        self,
        df: pd.DataFrame,
        columna_aspecto: str = "categoria",
        columna_sentimiento: str = "sentimiento",
        guardar: bool = True,
    ) -> go.Figure:
        """
        Genera un gráfico de barras apiladas con el sentimiento por aspecto.

        Args:
            df:                  DataFrame con columnas de aspecto y sentimiento.
            columna_aspecto:     Nombre de la columna de categoría de aspecto.
            columna_sentimiento: Nombre de la columna de sentimiento.
            guardar:             Si True, guarda el gráfico.

        Returns:
            Figura de Plotly.
        """
        tabla = (
            df.groupby([columna_aspecto, columna_sentimiento])
            .size()
            .reset_index(name="Cantidad")
        )

        fig = px.bar(
            tabla,
            x=columna_aspecto,
            y="Cantidad",
            color=columna_sentimiento,
            title="Distribución de Sentimiento por Categoría de Aspecto",
            color_discrete_map=COLORES_SENTIMIENTO,
            barmode="stack",
            labels={columna_aspecto: "Categoría de Aspecto", "Cantidad": "Número de Comentarios"},
        )
        fig.update_layout(
            paper_bgcolor="#1A1A2E",
            plot_bgcolor="#16213E",
            font=dict(color="#E0E0E0", size=12),
            title_font_size=17,
            legend_title="Sentimiento",
        )

        if guardar:
            ruta = os.path.join(self.directorio_salida, "sentimiento_por_aspecto.html")
            fig.write_html(ruta)
            print(f"[INFO] Gráfico guardado: {ruta}")

        return fig

    def grafico_comparacion_marcas(
        self,
        df: pd.DataFrame,
        columna_marca: str = "marca",
        columna_sentimiento: str = "sentimiento",
        guardar: bool = True,
    ) -> go.Figure:
        """
        Genera un gráfico de barras agrupadas para comparar marcas.

        Args:
            df:                  DataFrame con columna de marca detectada.
            columna_marca:       Columna que indica la marca (AMD, NVIDIA, Intel).
            columna_sentimiento: Columna de sentimiento.
            guardar:             Si True, guarda el gráfico.

        Returns:
            Figura de Plotly.
        """
        df_marcas = df[df[columna_marca].isin(["AMD", "NVIDIA", "Intel"])]
        tabla = (
            df_marcas.groupby([columna_marca, columna_sentimiento])
            .size()
            .reset_index(name="Cantidad")
        )

        fig = px.bar(
            tabla,
            x=columna_marca,
            y="Cantidad",
            color=columna_sentimiento,
            title="Comparación de Sentimiento: AMD vs NVIDIA vs Intel",
            color_discrete_map=COLORES_SENTIMIENTO,
            barmode="group",
            labels={columna_marca: "Marca", "Cantidad": "Número de Comentarios"},
        )
        fig.update_layout(
            paper_bgcolor="#1A1A2E",
            plot_bgcolor="#16213E",
            font=dict(color="#E0E0E0", size=12),
            title_font_size=17,
        )

        if guardar:
            ruta = os.path.join(self.directorio_salida, "comparacion_marcas.html")
            fig.write_html(ruta)
            print(f"[INFO] Gráfico guardado: {ruta}")

        return fig

    def grafico_evolucion_temporal(
        self,
        df: pd.DataFrame,
        columna_fecha: str = "timestamp",
        columna_sentimiento: str = "sentimiento",
        guardar: bool = True,
    ) -> go.Figure:
        """
        Genera un gráfico de líneas con la evolución temporal del sentimiento.

        Args:
            df:                  DataFrame con columna de timestamp.
            columna_fecha:       Nombre de la columna de fecha/hora.
            columna_sentimiento: Nombre de la columna de sentimiento.
            guardar:             Si True, guarda el gráfico.

        Returns:
            Figura de Plotly.
        """
        df = df.copy()
        df[columna_fecha] = pd.to_datetime(df[columna_fecha])
        df["mes"] = df[columna_fecha].dt.to_period("M").astype(str)

        tabla = (
            df.groupby(["mes", columna_sentimiento])
            .size()
            .reset_index(name="Cantidad")
        )

        fig = px.line(
            tabla,
            x="mes",
            y="Cantidad",
            color=columna_sentimiento,
            title="Evolución Temporal del Sentimiento (por Mes)",
            markers=True,
            color_discrete_map=COLORES_SENTIMIENTO,
            labels={"mes": "Período (Mes)", "Cantidad": "Número de Comentarios"},
        )
        fig.update_layout(
            paper_bgcolor="#1A1A2E",
            plot_bgcolor="#16213E",
            font=dict(color="#E0E0E0", size=12),
            title_font_size=17,
        )

        if guardar:
            ruta = os.path.join(self.directorio_salida, "evolucion_temporal.html")
            fig.write_html(ruta)
            print(f"[INFO] Gráfico guardado: {ruta}")

        return fig

    def grafico_metricas_evaluacion(
        self,
        metricas: dict,
        guardar: bool = True,
    ) -> go.Figure:
        """
        Genera un gráfico de barras horizontales con las métricas del modelo.

        Args:
            metricas: Diccionario con accuracy, precision, recall, f1_score.
            guardar:  Si True, guarda el gráfico.

        Returns:
            Figura de Plotly.
        """
        nombres = ["Accuracy", "Precision", "Recall", "F1-Score"]
        valores = [
            metricas.get("accuracy",  0),
            metricas.get("precision", 0),
            metricas.get("recall",    0),
            metricas.get("f1_score",  0),
        ]
        colores = ["#3498DB", "#9B59B6", "#E67E22", "#2ECC71"]

        fig = go.Figure(go.Bar(
            x=valores,
            y=nombres,
            orientation="h",
            marker_color=colores,
            text=[f"{v:.4f}" for v in valores],
            textposition="outside",
        ))
        fig.update_layout(
            title="Métricas de Evaluación del Modelo ABSA",
            xaxis=dict(range=[0, 1.1], title="Valor"),
            paper_bgcolor="#1A1A2E",
            plot_bgcolor="#16213E",
            font=dict(color="#E0E0E0", size=13),
            title_font_size=17,
        )

        if guardar:
            ruta = os.path.join(self.directorio_salida, "metricas_evaluacion.html")
            fig.write_html(ruta)
            print(f"[INFO] Gráfico guardado: {ruta}")

        return fig


# ────────────────────────────────────────────────────────────
# Punto de entrada para prueba directa del módulo
# ────────────────────────────────────────────────────────────

if __name__ == "__main__":
    # Datos de ejemplo para prueba
    datos_ejemplo = {
        "texto_limpio": ["good performance", "bad temperature", "ok price"],
        "sentimiento":  ["Positive", "Negative", "Neutral"],
        "categoria":    ["performance", "thermal", "value"],
        "marca":        ["AMD", "NVIDIA", "Intel"],
        "timestamp":    ["2024-01-15", "2024-02-20", "2024-03-10"],
    }
    df_ejemplo = pd.DataFrame(datos_ejemplo)

    dash = Dashboard(directorio_salida="reports/figures")
    dash.grafico_distribucion_sentimiento(df_ejemplo)
    dash.grafico_sentimiento_por_aspecto(df_ejemplo)
    dash.grafico_comparacion_marcas(df_ejemplo)
    print("[INFO] Gráficos de demostración generados en reports/figures/")

import pandas as pd
import seaborn as sns
import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import warnings
warnings.filterwarnings("ignore")

# CONFIGURACIÓN


st.set_page_config(
    page_title="Dashboard Analisis de Ventas",
    page_icon="📊",
    layout="wide"
)

sns.set_theme(style="whitegrid")
COLOR = "#1f4e79"

# =========================
# CARGA DE DATOS
# =========================

@st.cache_data
def cargar_datos():
    try:
        df = pd.read_excel("df_ventas_limpio.xlsx")
    except Exception as e:
        st.error(f"Error al cargar archivo: {e}")
        st.stop()

    df["Fecha_Pedido"] = pd.to_datetime(df["Fecha_Pedido"])
    df["Año"] = df["Fecha_Pedido"].dt.year
    df["Mes"] = df["Fecha_Pedido"].dt.month
    df["Mes_nombre"] = df["Fecha_Pedido"].dt.strftime("%b")

    return df

df = cargar_datos()

# =========================
# HEADER
# =========================

st.title("📊 Dashboard Ejecutivo de Ventas")
st.caption("Análisis estratégico de desempeño comercial")

st.markdown("---")

# =========================
# SIDEBAR FILTROS
# =========================

st.sidebar.header("🔎 Filtros")

año_sel = st.sidebar.multiselect("Año", df["Año"].unique(), default=df["Año"].unique())
zona_sel = st.sidebar.multiselect("Zona", df["Zona"].unique(), default=df["Zona"].unique())
canal_sel = st.sidebar.multiselect("Canal", df["Canal_Venta"].unique(), default=df["Canal_Venta"].unique())
prod_sel = st.sidebar.multiselect("Producto", df["Tipo_Producto"].unique(), default=df["Tipo_Producto"].unique())

df_f = df[
    df["Año"].isin(año_sel) &
    df["Zona"].isin(zona_sel) &
    df["Canal_Venta"].isin(canal_sel) &
    df["Tipo_Producto"].isin(prod_sel)
]

if df_f.empty:
    st.warning("No hay datos con estos filtros")
    st.stop()

# =========================
# KPIs PRO
# =========================

total_ventas = df_f["ImporteVentaTotal"].sum()
total_pedidos = df_f["ID_Pedido"].nunique()
total_unidades = df_f["Unidades"].sum()
ticket_promedio = total_ventas / total_pedidos

c1, c2, c3, c4 = st.columns(4)

c1.metric("💰 Ventas Totales", f"${total_ventas:,.0f}")
c2.metric("📦 Pedidos", f"{total_pedidos:,}")
c3.metric("🛒 Unidades", f"{total_unidades:,}")
c4.metric("💳 Ticket Promedio", f"${ticket_promedio:,.0f}")

st.markdown("---")

# =========================
# LAYOUT PRINCIPAL
# =========================

col1, col2 = st.columns([2,1])

# =========================
# GRAFICA 1: TENDENCIA
# =========================

with col1:
    st.subheader("📈 Evolución de Ventas")

    ventas_tiempo = (
        df_f.groupby(["Año", "Mes"])["ImporteVentaTotal"]
        .sum().reset_index()
    )

    ventas_tiempo["Fecha"] = pd.to_datetime(
        ventas_tiempo["Año"].astype(str) + "-" + ventas_tiempo["Mes"].astype(str)
    )

    fig, ax = plt.subplots(figsize=(10,4))

    sns.lineplot(
        data=ventas_tiempo,
        x="Fecha",
        y="ImporteVentaTotal",
        marker="o",
        color=COLOR,
        ax=ax
    )

    ax.fill_between(
        ventas_tiempo["Fecha"],
        ventas_tiempo["ImporteVentaTotal"],
        alpha=0.2,
        color=COLOR
    )

    ax.set_title("Tendencia Mensual")
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x/1e6:.1f}M"))

    st.pyplot(fig)
    plt.close(fig)

# =========================
# GRAFICA 2: CANAL
# =========================

with col2:
    st.subheader("📡 Canal de Venta")

    canal_counts = df_f["Canal_Venta"].value_counts()

    fig2, ax2 = plt.subplots()

    ax2.pie(
        canal_counts.values,
        labels=canal_counts.index,
        autopct="%1.1f%%",
        colors=sns.color_palette("Blues", len(canal_counts))
    )

    st.pyplot(fig2)
    plt.close(fig2)

# =========================
# SEGUNDA FILA
# =========================

col3, col4 = st.columns(2)

# =========================
# GRAFICA 3: ZONA
# =========================

with col3:
    st.subheader("🌍 Ventas por Zona")

    zona = df_f.groupby("Zona")["ImporteVentaTotal"].sum().sort_values()

    fig3, ax3 = plt.subplots()

    zona.plot(kind="barh", ax=ax3, color=COLOR)

    ax3.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x/1e6:.1f}M"))

    st.pyplot(fig3)
    plt.close(fig3)

# =========================
# GRAFICA 4: PRODUCTO
# =========================

with col4:
    st.subheader("🏷️ Top Productos")

    prod = (
        df_f.groupby("Tipo_Producto")["ImporteVentaTotal"]
        .sum()
        .sort_values(ascending=False)
        .head(5)
    )

    fig4, ax4 = plt.subplots()

    sns.barplot(
        x=prod.values,
        y=prod.index,
        palette="Blues_r",
        ax=ax4
    )

    st.pyplot(fig4)
    plt.close(fig4)

# =========================
# TABLA
# =========================

st.markdown("---")
st.subheader("📋 Datos")

st.dataframe(df_f.head(100), use_container_width=True)

csv = df_f.to_csv(index=False).encode("utf-8")

st.download_button(
    "📥 Descargar CSV",
    csv,
    "ventas_filtradas.csv",
    "text/csv"
)
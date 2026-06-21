import pandas as pd
import matplotlib.pyplot as plt 
import seaborn as sns 
import streamlit as st 

#Cargar datos
df_ventas= pd.read_excel('RegistrosVentas.xlsx')


df_ventas.info()
# ===========Limpieza de datos==============================

# Unidades

st.subheader("Filas con Unidades vacías")
st.dataframe(df_ventas[df_ventas["Unidades"].isna()])

df_ventas["Unidades"] = df_ventas["Unidades"].fillna(df_ventas["Unidades"].mean())


#Coste_Unitario, ImporteCosteTotal


#Conversion de datos (string a valor numerico )
df_ventas["Coste_Unitario"]=pd.to_numeric(df_ventas["Coste_Unitario"],errors='coerce')

df_ventas["ImporteCosteTotal"]=pd.to_numeric(df_ventas["ImporteCosteTotal"], errors='coerce')

#Imputacion de datos
df_ventas["ImporteCosteTotal"]=df_ventas["ImporteCosteTotal"].fillna(df_ventas["Unidades"]*df_ventas["Coste_Unitario"])

df_ventas["Coste_Unitario"]=df_ventas["Coste_Unitario"].fillna(df_ventas["ImporteCosteTotal"]/df_ventas["Unidades"])



#Fecha_Envio y Fecha_Pedido

#Convertir a datatime
df_ventas["Fecha_Pedido"] = pd.to_datetime(df_ventas["Fecha_Pedido"], errors="coerce")
df_ventas["Fecha_Envío"] = pd.to_datetime(df_ventas["Fecha_Envío"], errors="coerce")


#Buscar la diferencia entre fecha de envio y fecha de pedido
promedioDias = (df_ventas["Fecha_Envío"] - df_ventas["Fecha_Pedido"]).dt.days.median()


#Imputar datos
df_ventas["Fecha_Envío"] = df_ventas["Fecha_Envío"].fillna(df_ventas["Fecha_Pedido"] + pd.Timedelta(days=promedioDias))
df_ventas["Fecha_Pedido"]= df_ventas["Fecha_Pedido"].fillna(df_ventas["Fecha_Envío"] - pd.Timedelta(days=promedioDias))

# Validación lógica
df_ventas = df_ventas[df_ventas["Fecha_Envío"] >= df_ventas["Fecha_Pedido"]]


# ID_Pedido

#Elimanos la fila que no tiene dato faltante
df_ventas = df_ventas[df_ventas["ID_Pedido"].notna()]

st.write(df_ventas.isna().sum())


#Exportamos archivo a excel
df_ventas.to_excel("df_ventas_limpio.xlsx", index=False)

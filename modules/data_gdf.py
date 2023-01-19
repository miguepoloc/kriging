# Crear un geodataframe a partir de coordenadas y datos traídos de un archivo

# Primero se deben importar todas las librerías a utilizar
import pandas as pd
import geopandas
import matplotlib.pyplot as plt

columnas_validas = ["Latitud", "Longitud", "Fecha",
                    "Muestra", "Presicion GPS", "Altitud GPS", "geometry"]


def data_gdf(directorio, columnas_not_touch=columnas_validas):

    data_sensor = pd.read_csv(directorio, encoding="utf-8")

    # Se eliminan los espacios en blanco al inicio y al final de los nombres de las columnas
    columnas_old = data_sensor.columns
    columnas_new = {}
    for i in columnas_old:
        columnas_new[i] = i.strip()

    # Se renombran las columnas
    data_sensor.rename(columns=columnas_new,
                       inplace=True)

    # Eliminar las filas que tengan 0 en temperatura del suelo porque eso significa
    # que no se capturó nada y hubo un error
    data_sensor = data_sensor.drop(
        data_sensor[data_sensor['Temperatura Suelo'] == 0].index)

    # Elimina los datos que estén por arriba y por debajo de 3 desviaciones estandar
    # Denominandolos como datos atípicos
    # Pero se ignoran las columnas que no se quieren tocar
    for col in data_sensor.columns:
        if not (col in columnas_not_touch):
            data_sensor = data_sensor.drop(
                data_sensor[data_sensor[col] > data_sensor[col].mean() + 3*data_sensor[col].std()].index)
            data_sensor = data_sensor.drop(
                data_sensor[data_sensor[col] < data_sensor[col].mean() - 3*data_sensor[col].std()].index)

    # Se crea el DataFrame con los datos captados en campo
    gdf = geopandas.GeoDataFrame(
        data_sensor, geometry=geopandas.points_from_xy(
            data_sensor.Longitud, data_sensor.Latitud)
    )

    # Integración con el Sistema de Referencia de Coordenadas (SRC) WGS84 EPSG:4326
    # Ya el archivo dgf es un GeoDataFrame, pero, no tiene un sistema de referencia
    # de coordenadas (SRC) asignado. El cual es necesario, ya que, si se desa proyectar
    # dentro de un mapa, esta proyección es utilizada para cargar la información.
    # Para asignar un SRC, se utiliza ``set_crs()``.

    gdf = geopandas.GeoDataFrame(gdf, geometry='geometry')
    gdf = gdf.set_crs("EPSG:4326")

    return gdf


def data_gdf_media(directorio, columnas_not_touch=columnas_validas):

    gdf = data_gdf(directorio, columnas_not_touch)

    # Agrupar datos por la Muestra y se toma el promedio de los datos
    # Esto debido a que en campo se capturan varios datos por muestra
    data_media = gdf.groupby("Muestra").mean()

    gdf_media = geopandas.GeoDataFrame(
        data_media, geometry=geopandas.points_from_xy(
            data_media.Longitud, data_media.Latitud)
    )

    gdf_media = geopandas.GeoDataFrame(gdf_media, geometry='geometry')
    gdf_media = gdf_media.set_crs("EPSG:4326")

    return gdf_media

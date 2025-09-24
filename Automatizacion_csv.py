
# -----------------------------------------------------------
# Script de automatización GIS con ArcPy
# Autor: Josue
# Objetivo: Tomar un CSV de viviendas (Santo Domingo),
# convertirlo en puntos, asociarles la calle más cercana
# desde la red vial, y exportar un CSV final con campos clave.
# -----------------------------------------------------------

import arcpy
import os

# -----------------------------------------------------------
# 1) Definimos las rutas de entrada y salida
# La letra "r" (raw string) evita errores con las barras "\"
# -----------------------------------------------------------
csv_input = r"C:\Tutor_GIS\Automatizacion con Python\SINGLE_HOUSE.csv"
gdb_output = r"C:\Tutor_GIS\Automatizacion con Python\Python_ArcGISPro\Output.gdb"
red_vial = r"C:\Tutor_GIS\Automatizacion con Python\Python_ArcGISPro\Automatizacion.gdb\Red_Vial"
csv_final = r"C:\Tutor_GIS\Automatizacion con Python\SINGLE_HOUSE_resultado.csv"

# -----------------------------------------------------------
# 2) Convertimos el CSV en puntos
# Usamos LONGITUD y LATITUD para crear el feature class
# -----------------------------------------------------------
puntos_fc = os.path.join(gdb_output, "shouse_puntos")

if arcpy.Exists(puntos_fc):
    arcpy.management.Delete(puntos_fc)

arcpy.management.XYTableToPoint(
    in_table=csv_input,
    out_feature_class=puntos_fc,
    x_field="LONGITUD",
    y_field="LATITUD",
    coordinate_system=arcpy.SpatialReference(4326)  # WGS84
)
print(f"✅ CSV convertido a puntos: {puntos_fc}")

# -----------------------------------------------------------
# 3) Hacemos un Spatial Join con la red vial
# - Cada punto busca la calle más cercana
# - FULLNAME = nombre de la vía
# -----------------------------------------------------------
salida_final = os.path.join(gdb_output, "shouse_join_vias")

if arcpy.Exists(salida_final):
    arcpy.management.Delete(salida_final)

arcpy.analysis.SpatialJoin(
    target_features=puntos_fc,      # viviendas
    join_features=red_vial,         # calles
    out_feature_class=salida_final, # resultado
    join_type="KEEP_COMMON",
    match_option="CLOSEST",
    search_radius="50 Meters"       # distancia máxima
)
print(f"✅ Spatial Join creado: {salida_final}")

# -----------------------------------------------------------
# 4) Exportamos solo los campos seleccionados a CSV
# NUM = número de la casa
# LATITUD, LONGITUD = coordenadas
# COD_ONE = código único de la ONE
# FULLNAME = nombre de la calle
# -----------------------------------------------------------
campos_exportar = ["NUM", "LATITUD", "LONGITUD", "COD_ONE", "FULLNAME"]

with open(csv_final, "w", encoding="utf-8") as f:
    f.write(",".join(campos_exportar) + "\n")  # encabezados

    with arcpy.da.SearchCursor(salida_final, campos_exportar) as cursor:
        for row in cursor:
            valores = [str(v) if v is not None else "" for v in row]
            f.write(",".join(valores) + "\n")

print(f"✅ CSV final exportado: {csv_final}")

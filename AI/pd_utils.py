import pandas as pd

def excelToCsv(fileName):
    # Ruta del archivo Excel
    archivo_excel = fileName  # Reemplaza 'ejemplo.xlsx' con la ruta de tu propio archivo Excel
    
    # Leer el archivo Excel
    datos_excel = pd.read_excel(archivo_excel)

    # Guardar los datos en un archivo CSV separado por ";"
    datos_excel.to_csv('AI/COMISIONES.csv', sep=';', index=False, encoding='utf-8')

    print("Se ha guardado el archivo CSV correctamente.")
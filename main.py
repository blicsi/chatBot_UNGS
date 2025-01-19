import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import shutil
import os
import threading
from AI.pd_utils import excelToCsv
from AI.DataSetGenerator import crearDbFinal

# Función para actualizar la barra de progreso
def actualizar_progreso(progreso, valor):
    progreso['value'] = valor
    root.update_idletasks()

# Función para procesar el archivo en un hilo separado
def procesar_archivo(archivo, progreso):
    carpeta_destino = "AI"
    os.makedirs(carpeta_destino, exist_ok=True)
    destino = os.path.join(carpeta_destino, os.path.basename(archivo))
    shutil.copy(archivo, destino)
    actualizar_progreso(progreso, 25)
    
    # Convertir a CSV y guardar en la carpeta "IA"
    carpeta_csv = "AI"
    os.makedirs(carpeta_csv, exist_ok=True)
    excelToCsv(destino)
    actualizar_progreso(progreso, 50)
    
    # Generar la base de datos final
    crearDbFinal()
    actualizar_progreso(progreso, 100)
    
    messagebox.showinfo("Archivo guardado", f"El archivo se ha guardado en: {destino}, convertido a CSV en IA y la base de datos final ha sido generada.")
    progreso['value'] = 0  # Reiniciar la barra de progreso

# Función para seleccionar y procesar un archivo .xlsx
def seleccionar_archivo():
    archivo = filedialog.askopenfilename(filetypes=[("COMISIONES", "*.xlsx")])
    if archivo:
        progreso = ttk.Progressbar(root, length=250, mode='determinate')
        progreso.pack(pady=5)
        
        hilo = threading.Thread(target=procesar_archivo, args=(archivo, progreso))
        hilo.start()

# Crear la ventana principal
root = tk.Tk()
root.title("Ejemplo Tkinter")
root.geometry("300x200")

# Crear una etiqueta
etiqueta = tk.Label(root, text="Selecciona y guarda un archivo .xlsx:")
etiqueta.pack(pady=5)

# Crear un botón para abrir el explorador de archivos
boton = tk.Button(root, text="Abrir archivo", command=seleccionar_archivo)
boton.pack(pady=10)

# Ejecutar la aplicación
root.mainloop()

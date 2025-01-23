import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk  # Importar ttk
import shutil
import os
import threading
from AI.pd_utils import excelToCsv
from AI.DataSetGenerator import crearDbFinal

# Función para seleccionar y guardar un archivo .xlsx en la carpeta "AI" y convertirlo a CSV en "IA"
def seleccionar_archivo():
    archivo = filedialog.askopenfilename(filetypes=[("COMISIONES", "*.xlsx")])
    if archivo:
        carpeta_destino = "AI"
        os.makedirs(carpeta_destino, exist_ok=True)
        destino = os.path.join(carpeta_destino, os.path.basename(archivo))
        shutil.copy(archivo, destino)
        
        # Convertir a CSV y guardar en la carpeta "IA"
        carpeta_csv = "AI"
        os.makedirs(carpeta_csv, exist_ok=True)
        excelToCsv(destino)
        
        # Generar la base de datos final
        crearDbFinal()
        # Mostrar popup de operación completada
        messagebox.showinfo("Información", "Operación completada")




# Función para actualizar la barra de progreso
def actualizar_progreso(epoch, total_epochs):
    progreso["value"] = (epoch / total_epochs) * 100
    root.update_idletasks()

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

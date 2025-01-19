import tkinter as tk
from tkinter import filedialog, messagebox
import shutil
import os

# Función para seleccionar y guardar un archivo .xlsx en la carpeta "AI"
def seleccionar_archivo():
    archivo = filedialog.askopenfilename(filetypes=[("COMISIONES", "*.xlsx")])
    if archivo:
        carpeta_destino = "AI"
        os.makedirs(carpeta_destino, exist_ok=True)
        destino = os.path.join(carpeta_destino, os.path.basename(archivo))
        shutil.copy(archivo, destino)
        messagebox.showinfo("Archivo guardado", f"El archivo se ha guardado en: {destino}")

# Crear la ventana principal
root = tk.Tk()
root.title("Ejemplo Tkinter")
root.geometry("300x150")

# Crear una etiqueta
etiqueta = tk.Label(root, text="Selecciona y guarda un archivo .xlsx:")
etiqueta.pack(pady=5)

# Crear un botón para abrir el explorador de archivos
boton = tk.Button(root, text="Abrir archivo", command=seleccionar_archivo)
boton.pack(pady=10)

# Ejecutar la aplicación
root.mainloop()
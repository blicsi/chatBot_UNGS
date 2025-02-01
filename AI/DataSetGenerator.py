import math
import re
import unicodedata
import torch
import csv
import pandas as pd
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader

class ChatDataset(Dataset):
    def __init__(self, csv_file, question_columns, answer_columns, encoding='utf-8', sep=';'):
 
        # Carga el archivo CSV en un DataFrame de pandas
        self.data = pd.read_csv(csv_file, encoding=encoding, sep=sep)
        # Columnas seleccionadas para preguntas y respuestas
        self.question_columns = question_columns
        self.answer_columns = answer_columns

    def __len__(self):
   
        return len(self.data)

    def __getitem__(self, idx):
      
        # Extrae los valores de las columnas de preguntas
        question = self.data.loc[idx, self.question_columns].values.tolist()
        # Extrae los valores de las columnas de respuestas
        answer = self.data.loc[idx, self.answer_columns].values.tolist()
        return question, answer

def quitar_acentos(texto):
    """Elimina los acentos de una cadena de texto."""
    return ''.join(
        c for c in unicodedata.normalize('NFD', texto)
        if unicodedata.category(c) != 'Mn'
    )

def crearDb(question_columns, answer_columns, fileName): 
    archivo_csv = 'AI/COMISIONES.csv'

    # Crear el conjunto de datos
    dataset = ChatDataset(archivo_csv, question_columns, answer_columns)

    # Iterar sobre el conjunto de datos para mostrar las preguntas y respuestas
    unique_pairs = {}  # Un diccionario para almacenar combinaciones únicas de preguntas y respuestas

    for i in range(len(dataset)):
        question, answer = dataset[i]

        # Convertir la pregunta en una cadena
        if not isinstance(question, str) or math.isnan(question):  # Verifica si no es una cadena
            question = ' '.join(map(str, question))  # Une los elementos en una sola cadena
        question = re.sub(r'\(a\d+\)', '', question.lower())  # Eliminar paréntesis con números dentro
        question = re.sub(r'[()\-\n]', '', question)
        question = quitar_acentos(question)

        # Separar los nombres si están en una lista separada por comas
        questions_list = [q.strip() for q in question.split(',')]

        # Convertir las respuestas en cadenas y unirlas
        #print(answer_columns)
        answer_tags=answer_columns

        answer = ' | '.join(f"{col}: {str(ans)}" for col, ans in zip(answer_tags, answer))  # Convierte cada elemento a cadena y los une
        answer = re.sub(r'\(.*?\)|\n', '', answer.lower())  # Convertir a minúsculas, eliminar paréntesis y saltos de línea
        answer = quitar_acentos(answer)  # Quitar los acentos
        answer =answer+"\n"

        # Procesar cada nombre individualmente
        for individual_question in questions_list:
            if individual_question in unique_pairs:
                # Si existe, concatenar la respuesta nueva a la existente
                if answer not in unique_pairs[individual_question]:
                    unique_pairs[individual_question] += f" | {answer}"
            else:
                # Si no existe, agregar la pregunta y respuesta al diccionario
                unique_pairs[individual_question] = answer

    # Nombre del archivo CSV
    nombre_archivo = 'AI/dbs/' + fileName + ".csv"

    # Escribir los datos en el archivo CSV
    with open(nombre_archivo, mode='w', newline='', encoding='utf-8') as archivo_csv:
        escritor_csv = csv.writer(archivo_csv)
        # Escribir cada par pregunta-respuesta en el archivo CSV
        for pregunta, respuesta in unique_pairs.items():
            escritor_csv.writerow([pregunta, respuesta])
    
    # Asegurarse de que el CSV resultante no tenga valores nulos
    temp_df = pd.read_csv('AI/dbs/' + fileName + ".csv", encoding='utf-8')
    temp_df.fillna('vacio', inplace=True)
    temp_df.to_csv('AI/dbs/' + fileName + '.csv', index=False)

    print(f'Se ha creado el archivo CSV "{nombre_archivo}" con éxito.')

def crearDbFinal():

    crearDb(['Actividad'],['Comisión'],'actividades')
    crearDb(['Comisión'],['Actividad'],'comision')
    crearDb(['Docentes'],['Actividad','Comisión'],"profesores")
    crearDb(['Actividad','Comisión'],['Día','Horario','Docentes','AULA','Edificacíon','Compartido con','Tipo de clase','Instancia'],'infoGeneral')


    # Lista con las rutas de los archivos CSV
    csv_files = ['AI/dbs/actividades.csv', 'AI/dbs/comision.csv', 'AI/dbs/profesores.csv', 'AI/dbs/infoGeneral.csv']

    # Crear listas para almacenar preguntas y respuestas
    preguntas = []
    respuestas = []

    # Cargar los archivos CSV y extraer las columnas relevantes
    for file in csv_files:
        df = pd.read_csv(file, encoding='utf-8')  # Cargar cada archivo
        preguntas.extend(df.iloc[:, 0].astype(str))  # Primera columna como preguntas
        respuestas.extend(df.iloc[:, 1].astype(str))  # Segunda columna como respuestas

    db_auto_complete_respuestas=pd.DataFrame({'Pregunta': preguntas})

    db_auto_complete_respuestas.to_csv('AI/dbs/databaseFinalAutoCompletar.csv', index=False)

    # Crear un nuevo DataFrame con solo dos columnas
    df_final = pd.DataFrame({
        'Pregunta': preguntas,
        'Respuesta': respuestas
    })

    # Guardar el resultado en un nuevo archivo CSV
    df_final.to_csv('AI/dbs/databaseFinal.csv', index=False)

    print("Archivos combinados en dos columnas y guardados como 'databaseFinal.csv'")
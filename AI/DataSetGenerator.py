import torch
import csv
import pandas as pd
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
from Model import NeuralNet

class ChatDataset(Dataset):
    def __init__(self, csv_file, question_columns, answer_columns, encoding='latin1', sep=';'):
 
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

def crearDb(question_columns,answer_columns,fileName): 
    archivo_csv='AI/COMISIONES.csv'

    # Crear el conjunto de datos
    dataset = ChatDataset(archivo_csv,question_columns,answer_columns)

    # Iterar sobre el conjunto de datos para mostrar las preguntas y respuestas
    questions = []
    answers = []
    unique_pairs = set()  # Un conjunto para almacenar combinaciones únicas de preguntas y respuestas

    for i in range(len(dataset)):
        question, answer = dataset[i]

        # Convertir la pregunta en una cadena
        if not isinstance(question, str):  # Verifica si no es una cadena
            question = ''.join(map(str, question))  # Une los elementos en una sola cadena

        # Convertir las respuestas en cadenas y unirlas
        answer = ''.join(map(str, answer))  # Convierte cada elemento a cadena y los une

        # Crear un par (tupla) de pregunta y respuesta
        pair = (question, answer)

        # Verificar si el par ya existe en el conjunto
        if pair not in unique_pairs:
            unique_pairs.add(pair)  # Agregar el par al conjunto
            questions.append(question)  # Agregar la pregunta a la lista final
            answers.append(answer)  # Agregar la respuesta a la lista final

    # Nombre del archivo CSV
    nombre_archivo = 'AI/'+fileName+".csv"

    # Escribir los datos en el archivo CSV
    with open(nombre_archivo, mode='w', newline='',encoding='utf-8') as archivo_csv:
        escritor_csv = csv.writer(archivo_csv)
        
        # Escribir cada par pregunta-respuesta en el archivo CSV
        for pregunta, respuesta in zip(questions, answers):
            escritor_csv.writerow([pregunta, respuesta])

    print(f'Se ha creado el archivo CSV "{nombre_archivo}" con éxito.')

crearDb(['Actividad'],['Comisión'],'actividades')
crearDb(['Comisión'],['Actividad'],'comsion')
crearDb(['Docentes'],['Actividad','Comisión'],"profesores")
crearDb(['Actividad','Comisión'],['Día','Horario','Docentes','AULA','Edificacíon','Compartido con','Tipo de clase','Instancia'],'infoGeneral')

import torch
import csv
import pandas as pd
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
from AI.Model import NeuralNet

class ChatDataset(Dataset):
    def __init__(self, csv_file, num_question_columns):
        self.data = pd.read_csv(csv_file,encoding='latin1',sep=";")
        self.num_question_columns = num_question_columns

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        question = self.data.iloc[idx, :self.num_question_columns].values.tolist()
        answer = self.data.iloc[idx, self.num_question_columns:].values.tolist()
        return question, answer

# Definir el número de columnas de pregunta
num_question_columns = 4  # Por ejemplo, supongamos que las primeras 5 columnas son preguntas

# Crear el conjunto de datos
dataset = ChatDataset('better_chatbot/COMISIONES.csv', num_question_columns)

# Iterar sobre el conjunto de datos para mostrar las preguntas y respuestas
preguntas=[]
respuestas=[]

for i in range(len(dataset)):
    question,answer=dataset[i]
    question=' '.join(question)
    preguntas.append(question)
    answer = [str(elemento) for elemento in answer]
    answer=' '.join(answer)
    respuestas.append(answer)

# Nombre del archivo CSV
nombre_archivo = 'better_chatbot/preguntas_respuestas.csv'

# Escribir los datos en el archivo CSV
with open(nombre_archivo, mode='w', newline='',encoding='utf-8') as archivo_csv:
    escritor_csv = csv.writer(archivo_csv)
    
    # Escribir cada par pregunta-respuesta en el archivo CSV
    for pregunta, respuesta in zip(preguntas, respuestas):
        escritor_csv.writerow([pregunta, respuesta])

print(f'Se ha creado el archivo CSV "{nombre_archivo}" con éxito.')
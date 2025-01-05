import math
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
        if not isinstance(question, str) or math.isnan(question):  # Verifica si no es una cadena
            question = ' '.join(map(str, question))  # Une los elementos en una sola cadena
        question = question.lower().replace('(', '').replace(')', '')

        # Convertir las respuestas en cadenas y unirlas
        answer = ''.join(map(str, answer))  # Convierte cada elemento a cadena y los une
        answer = answer.lower().replace('(', '').replace(')', '')

        # Crear un par (tupla) de pregunta y respuesta
        pair = (question, answer)

        # Verificar si el par ya existe en el conjunto
        if pair not in unique_pairs:
            unique_pairs.add(pair)  # Agregar el par al conjunto
            questions.append(question)  # Agregar la pregunta a la lista final
            answers.append(answer)  # Agregar la respuesta a la lista final

    # Nombre del archivo CSV
    nombre_archivo = 'AI/dbs/'+fileName+".csv"

    # Escribir los datos en el archivo CSV
    with open(nombre_archivo, mode='w', newline='',encoding='utf-8') as archivo_csv:
        escritor_csv = csv.writer(archivo_csv)
        
        # Escribir cada par pregunta-respuesta en el archivo CSV
        for pregunta, respuesta in zip(questions, answers):
            escritor_csv.writerow([pregunta, respuesta])
    
    temp_df=pd.read_csv('AI/dbs/'+fileName+".csv",encoding='utf-8')
    temp_df.fillna('vacio',inplace=True)
    temp_df.to_csv('AI/dbs/'+fileName+'.csv',index=False)

    print(f'Se ha creado el archivo CSV "{nombre_archivo}" con éxito.')

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

# Crear un nuevo DataFrame con solo dos columnas
df_final = pd.DataFrame({
    'Pregunta': preguntas,
    'Respuesta': respuestas
})

# Guardar el resultado en un nuevo archivo CSV
df_final.to_csv('AI/dbs/databaseFinal.csv', index=False)

print("Archivos combinados en dos columnas y guardados como 'databaseFinal.csv'")
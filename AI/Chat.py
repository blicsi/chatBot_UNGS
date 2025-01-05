import random
import json

import torch

import pandas as pd

from Model import NeuralNet
from nltk_utils import bag_of_words,tokenize



device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

intents = pd.read_csv("AI/databaseFinal.csv",encoding='utf-8',sep=",")

FILE="AI/inteligencia.pth"
data = torch.load(FILE)

input_size=data["input_size"]
hidden_size=data["hidden_size"]
output_size=data["output_size"]
all_words=data["all_words"]
tags=data["tags"]
model_state=data["model_state"]

model = NeuralNet(input_size,hidden_size,output_size).to(device)
model.load_state_dict(model_state)
model.eval()

bot_name="Sam"
columna_preguntas = intents.iloc[:, 0].tolist()
columna_respuestas = intents.iloc[:, 1].tolist()

def get_response(msg):
    sentence = tokenize(msg)
    X = bag_of_words(sentence,all_words)
    X = X.reshape(1,X.shape[0])
    X = torch.from_numpy(X).to(device)

    output = model (X)
    _, predicted = torch.max(output,dim=1)
    tag = tags [predicted.item()]

    probs = torch.softmax(output,dim=1)
    prob=probs[0][predicted.item()]

    if prob.item()>0.9999:
        for intent in columna_preguntas:
            if tag == columna_preguntas.index(intent):
                respuesta=f"{str(bot_name)}:{str(columna_respuestas[tag])}"
                #print(respuesta)
        return respuesta
    else:
        return "por favor especificar mas datos"  

while True:
    msg=input("you:")
    if msg == "quit":
        break
    sentence = tokenize(msg)
    X = bag_of_words(sentence,all_words)
    X = X.reshape(1,X.shape[0])
    X = torch.from_numpy(X).to(device)

    output = model (X)
    _, predicted = torch.max(output,dim=1)
    tag = tags [predicted.item()]

    probs = torch.softmax(output,dim=1)
    prob=probs[0][predicted.item()]

    if prob.item()>0.9999:
        for intent in columna_preguntas:
            if tag == columna_preguntas.index(intent):
                respuesta=f"{str(bot_name)}:{str(columna_respuestas[tag])}"
                print(respuesta)  
    else:
        print("especifica mas boludo")

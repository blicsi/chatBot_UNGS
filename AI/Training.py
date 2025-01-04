from nltk_utils import tokenize,stem,bag_of_words
import numpy as np
import pandas as pd
import csv

import torch
import torch.nn as nn
from torch.utils.data import Dataset,DataLoader

from Model import NeuralNet

#se guarda en memoria el csv
data = pd.read_csv("better_chatbot/preguntas_respuestas.csv",encoding='utf-8',sep=",")

# Obtener todas las filas de la primera columna como una serie
primera_columna = data.iloc[:, 0].tolist()

all_words = []
tags = []
xy = []

for pregunta in primera_columna:
    tag=primera_columna.index(pregunta)
    tags.append(tag)
    w= tokenize(pregunta)
    all_words.extend(w)
    xy.append((w,tag))

ignore_words = ["!","?",".",","]
all_words=[stem(w) for w in all_words if w not in ignore_words]
all_words= sorted(set(all_words))
tag = sorted (set(tags))

x_train=[]
y_train=[]

for (pattern_sentence, tag) in xy:
    bag=bag_of_words(pattern_sentence,all_words)
    x_train.append(bag)
    
    label = tags.index(tag)
    y_train.append(label) #cross entropy loss

x_train=np.array(x_train)
y_train=np.array(y_train)

#hyper parameters
batch_size= 10
hidden_size=75
output_size=len(tags)
input_size= len(x_train[0])
learning_rate = 0.001
num_epochs= 1000

class ChatDataSet(Dataset):
    def __init__(self):
        self.n_samples = len(x_train)
        self.x_data = x_train
        self.y_data = y_train

    #dataset[idx]
    def __getitem__(self,index):
        return self.x_data[index],self.y_data[index]
    
    def __len__(self):
        return self.n_samples

dataset= ChatDataSet()
train_loader= DataLoader(dataset=dataset,batch_size=batch_size, shuffle=True, num_workers=0)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

model = NeuralNet(input_size,hidden_size,output_size).to(device)

#loss and optimizer
criterion = nn.CrossEntropyLoss()
optimzer = torch.optim.Adam(model.parameters(),lr=learning_rate)

for epoch in range(num_epochs):
    for (words, labels) in train_loader:
        words = words.to(device)
        labels = labels.to(dtype=torch.long).to(device)

        #forward pass
        outputs = model(words)
        loss = criterion(outputs,labels)

        #backward pass
        optimzer.zero_grad()
        loss.backward()
        optimzer.step()
    
    if (epoch+1)%100==0:
        print(f"epoch{epoch+1}/{num_epochs},loss={loss.item():.4f}")

print(f"final loss,loss={loss.item():.4f}")

data = {
    "model_state":model.state_dict(),
    "input_size": input_size,
    "output_size":output_size,
    "hidden_size":hidden_size,
    "all_words":all_words,
    "tags":tags
}

FILE = "better_chatbot/dataMejor.pth"
torch.save(data, FILE)

print(f"training complete. file save to{FILE}")
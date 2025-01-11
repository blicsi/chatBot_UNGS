from datetime import datetime
from nltk_utils import tokenize, stem, bag_of_words
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from Model import NeuralNet

class ChatDataSet(Dataset):
    def __init__(self,x_data,y_data):
        self.n_samples = len(x_train)
        self.x_data = x_data
        self.y_data = y_data

    def __getitem__(self, index):
        return self.x_data[index], self.y_data[index]

    def __len__(self):
        return self.n_samples

if __name__ == '__main__':
    # Cargar el CSV
    data = pd.read_csv("AI/dbs/databaseFinal.csv", encoding='utf-8', sep=",")

    # Obtener la primera columna
    primera_columna = data.iloc[:, 0].tolist()

    all_words = []
    tags = []
    xy = []

    for pregunta in primera_columna:
        tag = primera_columna.index(pregunta)
        tags.append(tag)
        w = tokenize(pregunta)
        all_words.extend(w)
        xy.append((w, tag))

    ignore_words = ["!", "?", ".", ","]
    all_words = [stem(w) for w in all_words if w not in ignore_words]
    all_words = sorted(set(all_words))
    tags = sorted(set(tags))

    x_train = []
    y_train = []

    for (pattern_sentence, tag) in xy:
        bag = bag_of_words(pattern_sentence, all_words)
        x_train.append(bag)
        label = tags.index(tag)
        y_train.append(label)

    x_train = np.array(x_train)
    y_train = np.array(y_train)

    # Hiperparámetros
    batch_size = 10
    hidden_size = 100
    output_size = len(tags)
    input_size = len(x_train[0])
    learning_rate = 0.001
    num_epochs = 1000
    num_workers = 12  # Cambia este valor según los núcleos de tu CPU

    # Crear dataset y dataloader
    dataset = ChatDataSet(x_train,y_train)
    train_loader = DataLoader(dataset=dataset, batch_size=batch_size, shuffle=True, num_workers=num_workers, persistent_workers=True)

    # Configurar el dispositivo
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    # Modelo
    model = NeuralNet(input_size, hidden_size, output_size).to(device)

    # Loss y optimizer
    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)

    # Entrenamiento

    print(datetime.now().strftime("%H:%M:%S"))
    print("empezo a entrenar")
    for epoch in range(num_epochs):
        for (words, labels) in train_loader:
            words = words.to(device)
            labels = labels.to(dtype=torch.long).to(device)

            # Forward pass
            outputs = model(words)
            loss = criterion(outputs, labels)

            # Backward pass
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

        if (epoch + 1) % 100 == 0:
            print(datetime.now().strftime("%H:%M:%S"))
            print(f"epoch {epoch+1}/{num_epochs}, loss = {loss.item():.4f}")

    print(f"final loss, loss = {loss.item():.4f}")

    # Guardar el modelo
    data = {
        "model_state": model.state_dict(),
        "input_size": input_size,
        "output_size": output_size,
        "hidden_size": hidden_size,
        "all_words": all_words,
        "tags": tags,
    }

    FILE = "AI/inteligencia.pth"
    torch.save(data, FILE)
    print(f"training complete. file saved to {FILE}")
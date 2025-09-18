import torch
import numpy as np
import random
import nltk
from nltk.stem import WordNetLemmatizer
import json
import torch.nn as nn

class ChatNet(nn.Module):
    def __init__(self, input_size, hidden_size, output_size):  # <-- FIX typo: __init__
        super(ChatNet, self).__init__()
        self.fc1 = nn.Linear(input_size, hidden_size)
        self.fc2 = nn.Linear(hidden_size, hidden_size)
        self.fc3 = nn.Linear(hidden_size, output_size)
        self.relu = nn.ReLU()
        self.softmax = nn.LogSoftmax(dim=1)

    def forward(self, x):
        x = self.relu(self.fc1(x))
        x = self.relu(self.fc2(x))
        x = self.fc3(x)
        return self.softmax(x)


lemmatizer = WordNetLemmatizer()

def clean_up_sentence(sentence):
    sentence_words = nltk.word_tokenize(sentence)
    sentence_words = [lemmatizer.lemmatize(w.lower()) for w in sentence_words]
    return sentence_words

def bow(sentence, words):
    sentence_words = clean_up_sentence(sentence)
    bag = np.zeros(len(words), dtype=np.float32)
    for s in sentence_words:
        for i, w in enumerate(words):
            if w == s:
                bag[i] = 1
    return bag

def predict_class(sentence, model, words, classes):
    bag_vector = bow(sentence, words)
    input_tensor = torch.tensor(bag_vector.reshape(1, -1), dtype=torch.float32)

    with torch.no_grad():
        output = model(input_tensor)
        probs = torch.exp(output)
        top_prob, top_class = torch.max(probs, dim=1)

    if top_prob.item() < 0.60:  # lower threshold a bit
        return None
    return classes[top_class.item()]

def get_response(sentence, model, words, classes, intents_json):
    intent = predict_class(sentence, model, words, classes)
    if intent is None:
        return "🤔 I'm not sure I understand. Try asking differently."

    for i in intents_json["intents"]:
        if i["tag"] == intent:
            return random.choice(i["responses"])

    return "⚠️ No response found."

# --- Load assets ---
words = np.load("words.npy", allow_pickle=True)
classes = np.load("classes.npy", allow_pickle=True)

model = ChatNet(input_size=len(words), hidden_size=8, output_size=len(classes))
model.load_state_dict(torch.load("chatbot_model.pth"))
model.eval()

with open("alumni_chatbot.json", encoding="utf-8") as f:
    intents = json.load(f)

# Expose for Flask
__all__ = ["get_response", "model", "words", "classes", "intents"]

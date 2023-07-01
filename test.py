import random

def shuffle_names(some_name):
    rand = some_name.copy()
    random.shuffle(rand)
    return rand

names = ["Imran", "Shah", "Denis", "Deniza"]

print(shuffle_names(names))


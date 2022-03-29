import tensorflow as tf
import numpy as np
import os, json
from keras.models import Sequential
from keras.layers import Dense, LSTM, Dropout
from string import punctuation
import globals

sequence_length = 100
batch_size = 128
epochs = 30

filepath = f'{globals.memes_root}/extracted_text.txt'

text = open(filepath, encoding='utf-8').read()
text = text.lower().translate(str.maketrans('', '', punctuation)).replace('\n', ' ')

n_chars = len(text)
vocab = ''.join(sorted(set(text)))
print('unique chars:', vocab)
n_unique_chars = len(vocab)
print("Number of characters:", n_chars)
print("Number of unique characters:", n_unique_chars)

char_to_int = {c: i for i, c in enumerate(vocab)}
int_to_char = {i: c for i, c in enumerate(vocab)}

json.dump(char_to_int, open(f'{globals.memes_root}/char_to_int.json', 'w'))
json.dump(int_to_char, open(f'{globals.memes_root}/int_to_char.json', 'w'))

encoded_text = np.array([char_to_int[x] for x in text])
char_dataset = tf.data.Dataset.from_tensor_slices(encoded_text)

for char in char_dataset.take(8):
    print(char.numpy(), int_to_char[char.numpy()])

sequences = char_dataset.batch(2*sequence_length + 1, drop_remainder=True)

for sequence in sequences.take(2):
    print(''.join([int_to_char[x] for x in sequence.numpy()]))


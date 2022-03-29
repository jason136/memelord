import tensorflow as tf
import numpy as np
import os, json
from keras.models import Sequential
from keras.layers import Dense, LSTM, Dropout
from string import punctuation
import globals

def train():
    sequence_length = 100
    batch_size = 128
    epochs = 30

    filepath = f'{globals.data_path}/extracted_text.txt'

    text = open(filepath, encoding='utf-8').read()
    text = text.replace('\n', ' ')
    #.lower().translate(str.maketrans('', '', punctuation))

    n_chars = len(text)
    vocab = ''.join(sorted(set(text)))
    print('unique chars:', vocab)
    n_unique_chars = len(vocab)
    print("Number of characters:", n_chars)
    print("Number of unique characters:", n_unique_chars)

    char_to_int = {c: i for i, c in enumerate(vocab)}
    int_to_char = {i: c for i, c in enumerate(vocab)}

    json.dump(char_to_int, open(f'{globals.data_path}/char_to_int.json', 'w'))
    json.dump(int_to_char, open(f'{globals.data_path}/int_to_char.json', 'w'))

    encoded_text = np.array([char_to_int[x] for x in text])
    char_dataset = tf.data.Dataset.from_tensor_slices(encoded_text)

    for char in char_dataset.take(8):
        print(char.numpy(), int_to_char[char.numpy()])

    sequences = char_dataset.batch(2*sequence_length + 1, drop_remainder=True)

    for sequence in sequences.take(2):
        print(''.join([int_to_char[x] for x in sequence.numpy()]))

    def split_sample(sample):
        ds = tf.data.Dataset.from_tensors((sample[:sequence_length], sample[sequence_length]))
        for x in range(1, (len(sample)-1) // 2):
            input_ = sample[x: x+sequence_length]
            target = sample[x+sequence_length]
            other_ds = tf.data.Dataset.from_tensors((input_, target))
            ds = ds.concatenate(other_ds)
        return ds

    dataset = sequences.flat_map(split_sample)

    def one_hot_samples(input_, target):
        return tf.one_hot(input_, n_unique_chars), tf.one_hot(target, n_unique_chars)

    dataset = dataset.map(one_hot_samples)

    for element in dataset.take(2):
        print("Input:", ''.join([int_to_char[np.argmax(char_vector)] for char_vector in element[0].numpy()]))
        print("Target:", int_to_char[np.argmax(element[1].numpy())])
        print("Input shape:", element[0].shape)
        print("Target shape:", element[1].shape)
        print("="*50, "\n")

    ds = dataset.repeat().shuffle(1024).batch(batch_size, drop_remainder=True)

    model = Sequential([
        LSTM(256, input_shape=(sequence_length, n_unique_chars), return_sequences=True), 
        Dropout(0.3), 
        LSTM(256), 
        Dense(n_unique_chars, activation='softmax'),

    ])

    model_weights_path = f'{globals.results_path}/meme neutrons-{sequence_length}.h5'
    model.summary()
    model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])

    if not os.path.isdir('results'):
        os.mkdir('results')

    model.fit(ds, steps_per_epoch=(len(encoded_text) - sequence_length) // batch_size, epochs=epochs)
    model.save(model_weights_path)

if __name__ == '__main__':
    train()
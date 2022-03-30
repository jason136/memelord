import tensorflow as tf
import numpy as np
import os, pickle, tqdm
from keras.models import Sequential
from keras.layers import Dense, LSTM, Dropout
from string import punctuation
import globals

def train():
    sequence_length = 100
    batch_size = 128
    epochs = 10

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

    pickle.dump(char_to_int, open(f'{globals.data_path}/char_to_int.pickle', 'wb'))
    pickle.dump(int_to_char, open(f'{globals.data_path}/int_to_char.pickle', 'wb'))

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

def generate(seed):
    sequence_length = 100
    filepath = f'{globals.results_path}/generated.txt'
    basename = os.path.basename(filepath)

    #seed = 'memeism'

    char_to_int = pickle.load(open(f'{globals.data_path}/char_to_int.pickle', 'rb'))
    int_to_char = pickle.load(open(f'{globals.data_path}/int_to_char.pickle', 'rb'))
    vocab_size = len(char_to_int)

    print(char_to_int)
    print(int_to_char)

    model = Sequential([
        LSTM(256, input_shape=(sequence_length, vocab_size), return_sequences=True), 
        Dropout(0.3), 
        LSTM(256), 
        Dense(vocab_size, activation='softmax'),

    ])
    model.load_weights(f'{globals.results_path}/meme neutrons-{sequence_length}.h5')

    s = seed
    n_chars = 400
    generated = ''

    for x in tqdm.tqdm(range(n_chars), 'Generating Text'):
        X = np.zeros((1, sequence_length, vocab_size))
        X = np.zeros((1, sequence_length, vocab_size))
        for t, char in enumerate(seed):
            X[0, (sequence_length - len(seed)) + t, char_to_int[char]] = 1
        predicted = model.predict(X, verbose=0)[0]
        next_index = np.argmax(predicted)
        next_char = int_to_char[next_index]
        generated += next_char
        seed = seed[1:] + next_char
    
    print('Seed: ', s)
    print('Generated Text: \n', generated)

if __name__ == '__main__':

    print('seed for generate or nothing for train: \n')
    selection = input()
    if selection:
        generate(selection)
    else:
        train()

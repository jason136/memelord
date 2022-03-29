import os

memes_path = './memes'
data_path = './data'
results_path = './results'

if not os.path.exists(memes_path):
    os.mkdir(memes_path)
if not os.path.exists(data_path):
    os.mkdir(data_path)
if not os.path.exists(results_path):
    os.mkdir(results_path)


keys = ['titles', 'filenames', 'urls', 'scores', 'timestamps', 'extracted text']

import os
import pandas as pd
import threading, queue
import unicodedata
from PIL import Image
from pytesseract import pytesseract
import globals

number_of_threads = 10
q = queue.Queue()
w = queue.Queue()

extracted_text = []
def worker():
    while True:
        meme = q.get()
        img = Image.open(meme[0]['filenames'][meme[1]])
        data = pytesseract.image_to_data(img, output_type='data.frame')
        data = data[data.conf != -1]
        words = data['text'].tolist()
        confs = data['conf'].tolist()

        text = ''
        for x in range(len(words)):
            word = unicodedata.normalize('NFKD', str(words[x])).encode('ascii', 'ignore').decode('ascii')
            if not word.replace('\n', ' ').strip(): continue
            if round(confs[x], 3) > 50:
                text += word.strip() + ' '
        if text.strip(): 
            text = text.replace('|', 'I')
            extracted_text.append(text)

        print(f'text extracted: {text}')
        w.put([meme[0], meme[1], text])
        q.task_done()

extracted_count = 0
def save():
    while True:
        meme = w.get()
        meme[0]['extracted text'][meme[1]] = meme[2]
        global extracted_count
        extracted_count += 1
        w.task_done()

def main():
    memes_root = globals.memes_root
    dicts = {}

    pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

    for _, dirs, _ in os.walk(memes_root):
        for dir in dirs:
            dicts[dir] = pd.read_csv(f'{memes_root}/{dir}/{dir}.csv', usecols=globals.keys).to_dict(orient='list')

    for i in range(number_of_threads):
        t = threading.Thread(target=worker)
        t.daemon = True
        t.start()
    
    s = threading.Thread(target=save)
    s.daemon = True
    s.start()

    for data in dicts.values():
        for index, text in enumerate(data['extracted text']):
            if not pd.isna(text):
                print(text)
                continue
            q.put([data, index])
    q.join()   
    w.join()

    for date, data in dicts.items():
        dataframe = pd.DataFrame.from_dict(data)
        csv = dataframe.to_csv(f'{memes_root}/{date}/{date}.csv', index=True, header=True)

    print(f"{extracted_count} lines extracted and {len(dicts.keys())} csv's written")
    
    filename = f'{memes_root}/extracted_text.txt'
    lines = []
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            lines = [line.replace('\n', '').strip() for line in f]
        print(lines)

    with open(filename, 'w') as f:
        for text in lines:
            f.write(f'{text}\n')
        for text in extracted_text:
            if text.replace('\n', '').strip() not in lines:
                f.write(f'{text}\n')
    input(f'{filename} written')

if __name__ == '__main__':
    main()
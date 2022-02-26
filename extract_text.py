import os
import pandas as pd
from PIL import Image
from pytesseract import pytesseract
import globals

def main():
    memes_root = globals.memes_root
    dicts = {}

    pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

    for _, dirs, _ in os.walk(memes_root):
        for dir in dirs:
            dicts[dir] = pd.read_csv(f'{memes_root}/{dir}/{dir}.csv', usecols=globals.keys).to_dict(orient='list')

    generated_count = 0
    for data in dicts.values():
        for index, text in enumerate(data['extracted text']):
            if text == '':
                continue
            
            img = Image.open(data['filenames'][index])
            generated_text = pytesseract.image_to_string(img)
            generated_text = generated_text.replace('\n', '').strip()

            data['extracted text'][index] = generated_text
            print(f'text extracted: {generated_text}')
            generated_count += 1

    for date, data in dicts.items():
        dataframe = pd.DataFrame.from_dict(data)
        csv = dataframe.to_csv(f'{memes_root}/{date}/{date}.csv', index=True, header=True)

    input(f"{generated_count} lines extracted and {len(dicts.keys())} csv's written")

if __name__ == '__main__':
    main()
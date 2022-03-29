import os
import pandas as pd
import globals

def main():
    operations = ['delete column']
    print('choose operation:')
    [print(f'{x + 1}: {operation}') for x, operation in enumerate(operations)]
    operation = int(input()) - 1
    print(f'operation: {operation}, {operations[operation]}')

    options = globals.keys
    print('choose option:')
    [print(f'{x + 1}: {option}') for x, option in enumerate(options)]
    option = int(input()) - 1
    print(f'option: {option + 1}, {options[option]}')

    dicts = {}

    for _, dirs, _ in os.walk(globals.memes_path):
        for dir in dirs:
            dicts[dir] = pd.read_csv(f'{globals.memes_path}/{dir}/{dir}.csv').to_dict(orient='list')

    match operation:
        case 0:
            for data in dicts.values():
                for index, _ in enumerate(data[options[option]]):
                    data[options[option]][index] = ''
        case _:
            print('that operation is not available')

    changed_csvs = 0
    for date, data in dicts.items():
        dataframe = pd.DataFrame.from_dict(data)
        csv = dataframe.to_csv(f'{globals.memes_path}/{date}/{date}.csv', index=True, header=True)
        changed_csvs += 1

    input(f"{changed_csvs} csv's written")

if __name__ == '__main__':
    main()
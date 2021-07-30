import json
import pandas as pd
import os


def remove_duplicates_txt(name='links_sanitized.txt'):
    print('Terminado! Verificando se existe linhas duplicadas...')
    lines_seen = set()
    with open(name, "w") as output_file:
        for each_line in open('links.txt', "r"):
            if each_line not in lines_seen:  # check if line is not duplicate
                output_file.write(each_line)
                lines_seen.add(each_line)

    os.remove('links.txt')
    print('Terminado! link duplicados removidos')


def save_to_json(data, filename):
    print('Salvando os dados em JSON')
    with open(f'{filename}.json', 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)


def load_links(file_text):
    print('Iniciando leitura de links...')
    with open(f'{file_text}.txt', 'r') as text:
        return text.readlines()


def JSONtoExcel(filename):
    try:
        print('Iniciando convensão...')
        # temp_df = pd.read_json(f'{filename}.json')
        temp_df = load_json(filename)
        df = pd.json_normalize(temp_df)
        df.to_excel(f'{filename}.xlsx')
        print('Convensão realizada com sucesso!')

    except Exception as error:
        print('Falha na conversão, Arquivo incorreto ou não existe...')


def load_json(json_name):
    with open(f'{json_name}.json','r', encoding="utf-8") as file:
        data = json.load(file)

    return data


def save_to_html(data):
    with open('coment.html', 'w', encoding='utf8') as file:
        file.write(str(data))


def dataToExcel(dataDict, filename):
    df = pd.DataFrame(dataDict)
    df.to_csv(filename, mode="a", index=False, header=not os.path.exists(filename))


def save_index(index):
    with open('index.txt','w') as file:
        file.write(str(index))


def load_index():
    try:
        with open('index.txt') as file:
            data = file.read()
        
        return data
    
    except FileNotFoundError:
        save_index(0)
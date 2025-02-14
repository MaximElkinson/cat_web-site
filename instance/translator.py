from docx import Document
import zipfile, pathlib
import sqlite3





def extract_images(docx):
    # директория для извлечения
    ex_dir = pathlib.Path(f'pic_{docx}')
    if not ex_dir.is_dir():
        ex_dir.mkdir()

    with zipfile.ZipFile(docx) as zf:
        for name in zf.infolist():
            if name.filename.startswith('word/media'):
                # здесь можно задать другие параметры фильтрации,
                # например отобрать картинки с определенном именем,
                # расширением, размером `name.file_size` и т.д.
                if name.filename[-4:] != 'jpeg':
                    name.filename = name.filename.split('.')[0] + '.jpeg'
                zf.extract(name, ex_dir)

def extract_text(docx):
    doc = Document(docx)
    # последовательность всех таблиц документа
    all_tables = doc.tables

    # создаем пустой словарь под данные таблиц
    data_tables = {i:None for i in range(len(all_tables))}
    # проходимся по таблицам
    for i, table in enumerate(all_tables):
        # создаем список строк для таблицы `i` (пока пустые)
        data_tables[i] = [[] for _ in range(len(table.rows))]
        # проходимся по строкам таблицы `i`
        for j, row in enumerate(table.rows):
            # проходимся по ячейкам таблицы `i` и строки `j`
            for cell in row.cells:
                # добавляем значение ячейки в соответствующий
                # список, созданного словаря под данные таблиц
                data_tables[i][j].append(cell.text)

        # смотрим извлеченные данные
        # (по строкам) для таблицы `i`

    return data_tables



connection = sqlite3.connect('animals.db')
cursor = connection.cursor()

extract_images('cats.docx')
text = extract_text('cats.docx')
text_cat = text[0][1:]
text_dog = text[1][1:]

for i in range(len(text_cat)):
    with open(f'pic_cats.docx/word/media/image{i+1}.jpeg', 'rb') as f:
        photo = f.read()
        animal_type_id = 1
        name = text_cat[i][2].replace('\n', '').replace("/", '')
        cursor.execute('INSERT INTO Animal (photo, animal_type_id, name) VALUES (?, ?, ?)', (photo, animal_type_id, name))

for i in range(len(text_dog)):
    with open(f'pic_cats.docx/word/media/image{i+len(text_cat)}.jpeg', 'rb') as f:
        photo = f.read()
        animal_type_id = 2
        name = text_dog[i][2].replace('\n', '').replace("/", '')
        cursor.execute('INSERT INTO Animal (photo, animal_type_id, name) VALUES (?, ?, ?)', (photo, animal_type_id, name))


# Сохраняем изменения и закрываем соединение
connection.commit()
connection.close()
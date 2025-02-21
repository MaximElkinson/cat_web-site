from docx import Document

import zipfile, pathlib


def read_docx(file_path):
    # Открываем файл документа
    doc = Document(file_path)
    text = []

    # Проходим по всем параграфам в документе
    for para in doc.paragraphs:
        # Проверяем стиль параграфа
        style = para.style.name

        # Выводим текст и соответствующий стиль
        text.append([style, para.text])
    return text

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

def write_to_rst(file_path, text):
    extract_images('Администратору.docx')

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write('\n\n')
        pn = 1
        for i in text:
            if i[0] == 'List Paragraph':
                f.write(str(i[1]) + '\n')
                f.write('=' * len(str(i[1])) + '\n\n')
            else:
                words = i[1].split('Рис.')
                f.write(words[0] + '\n\n')
                for j in range(1, len(words)):
                    f.write(f'.. image:: pic_Администратору.docx/word/media/image{pn}.jpeg' + '\n\n')
                    f.write('Рис.' + words[j] + '\n\n')
                    pn += 1

write_to_rst('index.rst', read_docx('Администратору.docx'))


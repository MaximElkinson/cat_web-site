from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from models import db, Animal, Status, Media, Disease, Vaccine, Color, AnimalType, FurType
import pandas as pd
import matplotlib.pyplot as plt
from sqlalchemy import func
from fuzzywuzzy import fuzz
import openpyxl
import sqlite3
from docx import Document
import zipfile, pathlib

app = Flask(__name__)

# Настройка базы данных SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///animals.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Инициализация базы данных и миграций
db.init_app(app)
migrate = Migrate(app, db)


@app.route('/', methods=['POST','GET'])
def index():
    """
        Страница просмотра записей о животных в приюте
        """
    animals = Animal.query.all()
    animals_types = AnimalType.query.all()

    if request.method == 'POST':
        name = request.form['animalname'].lower()
        searchanimaltype = request.form.get('searchanimaltype')
        animals_search = []
        if name != '':
            for animal in animals:
                if fuzz.ratio(animal.name.lower(), name) >= 70:
                    animals_search.append(animal)
            animals = animals_search
        elif searchanimaltype != "кошка/собака":
            type_id = [type.id for type in animals_types if type.name == searchanimaltype][0]
            for animal in animals:
                if animal.animal_type_id == type_id:
                    animals_search.append(animal)
            animals = animals_search


    # Преобразование бинарной последовательности из БД в изображение
    for i in animals:
        with open(f'static/{i.name}.jpg', 'bw') as f:
            f.write(i.photo)
    # Создаём список ссылок на изображения
    links = {i.name: f"static/{i.name}.jpg" for i in animals}
    return render_template('index.html', links=links, animals=animals, animals_types=animals_types)


@app.route('/create', methods=['GET', 'POST'])
def create():
    """
        Страница создания новой записи о животном в приюте
        """
    if request.method == 'POST':
        animal = Animal(
            photo=open(request.form['photo'], 'br').read(),
            animal_type_id=request.form['animal_type_id'],
            name=request.form['name'],
            birth_year=request.form['birth_year'],
            gender=request.form['gender'],
            color_id=request.form['color_id'],
            fur_type_id=request.form['fur_type_id'],
            phenotype=request.form['phenotype'],
            description=request.form['description'],
            history=request.form['history'],
            article_text=request.form['article_text'],
            important=request.form.get('important') == 'on',
            sterilization=request.form.get('sterilization') == 'on',
            chip=request.form.get('chip') == 'on'
        )
        db.session.add(animal)
        db.session.commit()
        return redirect(url_for('index'))

    # Получаем данные для выпадающих списков
    animal_types = AnimalType.query.all()
    colors = Color.query.all()
    fur_types = FurType.query.all()

    return render_template('create.html', animal_types=animal_types, colors=colors, fur_types=fur_types)


@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    """
    Страница редактирования записи о животном в приюте

    :ivar id: индекс животного в базе данных
    :vartype id: int
    """
    animal = Animal.query.get_or_404(id)

    if request.method == 'POST':
        animal.photo = open(request.form['photo'], 'br').read()
        animal.animal_type_id = request.form['animal_type_id']
        animal.name = request.form['name']
        animal.birth_year = request.form['birth_year']
        animal.gender = request.form['gender']
        animal.color_id = request.form['color_id']
        animal.fur_type_id = request.form['fur_type_id']
        animal.phenotype = request.form['phenotype']
        animal.description = request.form['description']
        animal.history = request.form['history']
        animal.article_text = request.form['article_text']

        # Обновляем булевы значения
        animal.important = request.form.get('important') == 'on'
        animal.sterilization = request.form.get('sterilization') == 'on'
        animal.chip = request.form.get('chip') == 'on'

        db.session.commit()

        return redirect(url_for('index'))

    # Получаем данные для выпадающих списков
    animal_types = AnimalType.query.all()
    colors = Color.query.all()
    fur_types = FurType.query.all()

    return render_template('edit.html', animal=animal,
                           animal_types=animal_types, colors=colors, fur_types=fur_types)

@app.route('/detail/<int:id>', methods=['GET', 'POST'])
def animal_detail(id):
    """
        Страница просмотра подробной информации о животном

        :ivar id: индекс животного в базе данных
        :vartype id: int
        """
    animal = Animal.query.get_or_404(id)
    animal_types = AnimalType.query.all()
    colors = Color.query.all()
    fur_types = FurType.query.all()
    link = f"/static/{animal.name}.jpg"

    return render_template('animal_detail.html', animal=animal,
                           animal_types=animal_types, colors=colors, fur_types=fur_types, link = link)


@app.route('/delete/<int:id>')
def delete(id):
    """
        Функия удаления записи о животном в приюте

        :ivar id: индекс животного в базе данных
        :vartype id: int
        """
    animal = Animal.query.get_or_404(id)
    db.session.delete(animal)
    db.session.commit()
    return redirect(url_for('index'))

close_open_list = True
@app.route('/admin', methods=['GET', 'POST'])
def admin():
    """
        Страница редактирования записи о животном в приюте

        :ivar close_open_list: глобальноя переменная-флаг сворачивания и разворачивания списка животных в приюте
        :vartype close_open_list: bool
        """
    global close_open_list
    animals = Animal.query.all()
    animals_types = AnimalType.query.all()
    animal_count = len(animals)
    links = {i.name: f"static/{i.name}.jpg" for i in animals}

    labels = []
    sizes = []

    for type_name, count in (db.session.query(
            AnimalType.name,
            func.count(Animal.id)).join(Animal).group_by(
        AnimalType.name).all()):
        labels.append(type_name)
        sizes.append(count)


    plt.figure(figsize=(10, 6))
    plt.bar(labels, sizes)
    plt.title("Количество животных по типам")
    plt.xlabel("Тип животного")
    plt.ylabel("Количество")
    plt.savefig('static/image.png')


    if request.method == 'POST' and close_open_list:
        name = request.form['animalname'].lower()
        searchanimaltype = request.form.get('searchanimaltype')
        animals_search = []
        if name != '':
            for animal in animals:
                if fuzz.ratio(animal.name.lower(), name) >= 70:
                    animals_search.append(animal)
            animals = animals_search
        elif searchanimaltype != "кошка/собака":
            type_id = [type.id for type in animals_types if type.name == searchanimaltype][0]
            for animal in animals:
                if animal.animal_type_id == type_id:
                    animals_search.append(animal)
            animals = animals_search

    return render_template('admin.html', animals=animals, animal_count=animal_count, links = links, animals_types=animals_types, close_open_list=close_open_list)

@app.route('/close_open_list', methods=['GET', 'POST'])
def close_open_list():
    """
            Функция сворачивания и разворачивания списка животных в приюте

            :ivar close_open_list: глобальноя переменная-флаг сворачивания и разворачивания списка животных в приюте
            :vartype close_open_list: bool
            """
    global close_open_list
    if close_open_list:
        close_open_list = False
    else:
        close_open_list = True
    return redirect(url_for('admin'))

def yes_or_no(parametr):
    """
            Функция преобразования строк "да" и "нет" в соответствующие булевские значения

            :ivar parametr: строка
            :vartype parametr: string
            """
    if parametr == None:
        return False
    elif parametr.lower() == 'да':
        return True
    else:
        return False

@app.route('/import', methods=['POST'])
def import_animals():
    """
                Функция импорта данных о животных в приюте из таблицы xlsx

                """
    if 'file' not in request.files:
        return redirect(request.url)

    file = request.files['file']

    if file.filename == '':
        return redirect(request.url)

    if file:


        connection = sqlite3.connect('instance/animals.db')
        cursor = connection.cursor()
        # читаем excel-файл
        wb = openpyxl.load_workbook(file)

        # печатаем список листов
        sheets = wb.sheetnames
        for sheet in sheets:
            cat_data = wb[sheet]
            name = cat_data['B1'].value
            birth_year = cat_data['B2'].value
            gender = cat_data['B3'].value
            phenotype = cat_data['B4'].value
            color = cat_data['B5'].value
            fur_type = cat_data['B6'].value
            # __________________________________________
            scratching_post = yes_or_no(cat_data['B7'].value)
            lotochek = yes_or_no(cat_data['B8'].value)
            possible_dogs = yes_or_no(cat_data['B9'].value)
            possible_cats = yes_or_no(cat_data['B10'].value)
            sterilization = yes_or_no(cat_data['B11'].value)
            vaccinated = yes_or_no(cat_data['B12'].value)
            chip = yes_or_no(cat_data['B13'].value)
            have_passport = yes_or_no(cat_data['B14'].value)
            free = yes_or_no(cat_data['B15'].value)
            # __________________________________________
            article_text = cat_data['B16'].value
            important = yes_or_no(cat_data['B17'].value)
            history = cat_data['B18'].value
            cursor.execute('''UPDATE Animal SET 
            birth_year = ?,
            gender = ?,
            phenotype = ?, 
            color = ?,
            fur_type = ?, 
            scratching_post = ?, 
            lotochek = ?, 
            possible_dogs = ?, 
            possible_cats = ?, 
            sterilization = ?, 
            vaccinated = ?, 
            chip = ?, 
            have_passport = ?, 
            free = ?, 
            article_text = ?, 
            important = ?, 
            history = ? 
            WHERE name = ?''',
                            (birth_year,
                            gender,
                            phenotype,
                            color,
                            fur_type,
                            scratching_post,
                            lotochek,
                            possible_dogs,
                            possible_cats,
                            sterilization,
                            vaccinated,
                            chip,
                            have_passport,
                            free,
                            article_text,
                            important,
                            history,
                            name))

        connection.commit()
        connection.close()

        return redirect(url_for('admin'))

def extract_images(docx):
    """
                Функция извлечения изображений из документов word

                """
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
    """
                    Функция извлечения текста из документов word

                    """
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


@app.route('/import_docs', methods=['POST'])
def import_animals_docx():
    """
                    Функция импорта информации о животных в приюте из документов word

                    """
    if 'file' not in request.files:
        return redirect(request.url)

    file = request.files['file']

    if file.filename == '':
        return redirect(request.url)

    if file:

        connection = sqlite3.connect('instance/animals.db')
        cursor = connection.cursor()

        extract_images('cats.docx')
        text = extract_text('cats.docx')
        text_cat = text[0][1:]
        text_dog = text[1][1:]

        for i in range(len(text_cat)):
            with open(f'pic_cats.docx/word/media/image{i + 1}.jpeg', 'rb') as f:
                photo = f.read()
                animal_type_id = 1
                name = text_cat[i][2].replace('\n', '').replace("/", '')
                cursor.execute('INSERT INTO Animal (photo, animal_type_id, name) VALUES (?, ?, ?)',
                               (photo, animal_type_id, name))

        for i in range(len(text_dog)):
            with open(f'pic_cats.docx/word/media/image{i + len(text_cat)}.jpeg', 'rb') as f:
                photo = f.read()
                animal_type_id = 2
                name = text_dog[i][2].replace('\n', '').replace("/", '')
                cursor.execute('INSERT INTO Animal (photo, animal_type_id, name) VALUES (?, ?, ?)',
                               (photo, animal_type_id, name))

        connection.commit()
        connection.close()

        return redirect(url_for('admin'))


@app.route('/statistics')
def statistics():
    """
                    Функция генерации графика тип животного-количество животных

                    :return: Изображение графика тип животного-количество животных
                    :rtype: файл формата png

                    """
    labels = []
    sizes = []
    func = []

    for type_name, count in (db.session.query(
            AnimalType.name,
            func.count(Animal.id)).join(Animal).group_by(
        AnimalType.name).all()):
        labels.append(type_name)
        sizes.append(count)

    plt.ion()

    plt.figure(figsize=(10, 6))
    plt.bar(labels, sizes)
    plt.title("Количество животных по типам")
    plt.xlabel("Тип животного")
    plt.ylabel("Количество")
    plt.savefig('image.png')

    return 'image.png'



if __name__ == '__main__':
    with app.app_context():  # Создаем контекст приложения
        db.create_all()
    app.run(debug=True)

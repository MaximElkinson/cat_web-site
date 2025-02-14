import openpyxl
import sqlite3
from os import listdir

def yes_or_no(parametr):
    if parametr == None:
        return False
    elif parametr.lower() == 'да':
        return True
    else:
        return False


connection = sqlite3.connect('animals.db')
cursor = connection.cursor()

for file in listdir():
    if file[-4:] == 'xlsx':
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
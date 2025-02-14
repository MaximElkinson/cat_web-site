from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Status(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

class Media(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(200), nullable=False)

class Disease(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

class Vaccine(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

class Color(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

class AnimalType(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

class FurType(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

class Animal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    photo = db.Column(db.LargeBinary(200))
    animal_type_id = db.Column(db.Integer, db.ForeignKey('animal_type.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    birth_year = db.Column(db.Integer)
    gender = db.Column(db.String(10))
    color = db.Column(db.Text, db.ForeignKey('color.id'))
    fur_type = db.Column(db.Text, db.ForeignKey('fur_type.id'))
    phenotype = db.Column(db.String(100))
    description = db.Column(db.Text)
    history = db.Column(db.Text)
    article_text = db.Column(db.Text)
    important = db.Column(db.Boolean, default=False)
    sterilization = db.Column(db.Boolean, default=False)
    chip = db.Column(db.Boolean, default=False)
    scratching_post = db.Column(db.Boolean, default=False)
    lotochek = db.Column(db.Boolean, default=False)
    possible_dogs = db.Column(db.Boolean, default=False)
    possible_cats = db.Column(db.Boolean, default=False)
    vaccinated = db.Column(db.Boolean, default=False)
    have_passport = db.Column(db.Boolean, default=False)
    free = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f'<Animal {self.name}>'

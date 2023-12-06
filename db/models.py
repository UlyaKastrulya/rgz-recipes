from . import db
from flask_login import UserMixin

class users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), nullable=False, unique=True)
    password = db.Column(db.String(102), nullable=False)
    is_admin = db.Column(db.Boolean, nullable=False)

    def repr(self):
        return f"id:{self.id}, username:{self.username}, is_admin:{self.is_admin}"

class recipes(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    image_url = db.Column(db.String(300), nullable=True)
    ingridients = db.Column(db.String(300), nullable=False)
    steps = db.Column(db.String(300), nullable=False)
    
    def repr(self):
        return f"id:{self.id}, name:{self.name}, image_url:{self.image_url}, ingridients:{self.ingridients}, steps:{self.steps}"
from werkzeug.security import check_password_hash, generate_password_hash
from flask import Flask, Blueprint, render_template, request, make_response, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from db import db
from db.models import users, medicines
from flask_login import login_user, login_required, current_user, logout_user



app = Flask(__name__)


app.secret_key = '123'
user_db = "Julia"
host_ip = "localhost"
host_port = "5432"
database_name = "Recipes_rgz"
password = "123"

app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{user_db}:{password}@{host_ip}:{host_port}/{database_name}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False 
db.init_app(app)



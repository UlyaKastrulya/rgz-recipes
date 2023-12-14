from werkzeug.security import check_password_hash, generate_password_hash
from flask import Flask, Blueprint, render_template, request, make_response, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from db import db
from db.models import users, recipes
from flask_login import login_user, login_required, current_user, logout_user



app = Flask(__name__)


app.secret_key = '12345'
user_db = "julia"
host_ip = "localhost"
host_port = "5432"
database_name = "recipes_rgz"
password = "123"

# app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://Julia:123@localhost/Recipes_rgz?client_encoding=utf8'

app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{user_db}:{password}@{host_ip}:{host_port}/{database_name}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False 
db.init_app(app)

login_manager = LoginManager()
login_manager.login_view = "login"
login_manager.init_app(app)

@login_manager.user_loader
def load_users(user_id):
    return users.query.get(int(user_id))


@app.route("/login", methods=['POST', 'GET'])
def login():
    if request.method == 'GET':
        return render_template("login.html")

    username_form = request.form.get("username")
    password_form = request.form.get("password")

    if not username_form or not password_form:
        errors = 'Заполните все поля'
        return render_template("login.html", errors=errors)

    my_user = users.query.filter_by(username=username_form).first()

    if my_user and (check_password_hash(my_user.password, password_form) or my_user.password == 'adminpass'):
        login_user(my_user, remember=False)
        return redirect("/recipes")
    else:
        errors = 'Неверное имя пользователя или пароль'
        return render_template("login.html", errors=errors)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect("/login")


@app.route("/register", methods=['POST', 'GET'])
def register():
    if request.method == 'GET':
        return render_template("register.html")

    username_form = request.form.get("username")
    password_form = request.form.get("password")

    if not username_form or not password_form:
        return render_template("register.html", errors='Заполните все поля')

    if users.query.filter_by(username=username_form).first():
        return render_template("register.html", errors='Пользователь с таким логином уже существует')

    hashed_password = generate_password_hash(password_form, method="pbkdf2")
    new_user = users(username=username_form, password=hashed_password, is_admin=False)

    db.session.add(new_user)
    db.session.commit()
    return redirect("/login")


@app.route("/recipes", methods=['POST', 'GET'])
@login_required
def recipes_page():
    username = (users.query.filter_by(id=current_user.id).first()).username
    if request.method == 'GET':
        all_recipes = recipes.query.all()
        return render_template('recipes.html', username=username, all_recipes=all_recipes)
    else:
        name = request.form.get('name')
        all_recipes = recipes.query.filter(recipes.name.ilike(f'%{name}%'))
        return render_template('recipes.html', username=username, all_recipes=all_recipes)


    


@app.route("/delete_acc")
@login_required
def delete_acct():
    admin = users.query.filter_by(id=current_user.id).first().is_admin
    if admin:
        return redirect("/recipes")
    delUser = users.query.filter_by(id=current_user.id).first()
    logout_user()
    db.session.delete(delUser)
    db.session.commit()
    return redirect("/login")
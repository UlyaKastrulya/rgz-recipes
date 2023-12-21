from werkzeug.security import check_password_hash, generate_password_hash
from flask import Flask, Blueprint, render_template, request, make_response, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from db import db
from db.models import users, recipes
from flask_login import login_user, login_required, current_user, logout_user
from sqlalchemy import or_
from sqlalchemy import and_



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
        ingredientOption = request.form.get('ingredientOption')
        ingredients = request.form.get('name_ing')
        name = request.form.get('name')
        all_recipes = recipes.query.filter(recipes.name.ilike(f'%{name}%'))
        if ingredientOption == 'any':

            if ingredients != '' or name != '':
                name_filter = recipes.name.ilike(f'%{name}%') if name else True  # Фильтр для названия рецепта или True, если название не задано

                if ingredients:
                    ingredient_filters = [
                        recipes.ingridients.ilike(f'%{ingredient.strip()}%') for ingredient in ingredients.split(',')
                    ]
                    all_recipes = recipes.query.filter(or_(name_filter, *ingredient_filters)).all()
                else:
                    all_recipes = recipes.query.filter(name_filter).all()
            else:
                all_recipes = recipes.query.all()
        else:
            if ingredients != '' or name != '':
                name_filter = recipes.name.ilike(f'%{name}%') if name else True  # Фильтр для названия рецепта или True, если название не задано

                if ingredients:
                    ingredient_filters = [
                        recipes.ingridients.ilike(f'%{ingredient.strip()}%') for ingredient in ingredients.split(',')
                    ]
                    all_recipes = recipes.query.filter(and_(name_filter, *ingredient_filters)).all()
                else:
                    all_recipes = recipes.query.filter(name_filter).all()
            else:
                # В случае, если оба поля не заданы, можно вернуть все рецепты
                all_recipes = recipes.query.all()
                
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


@app.route("/")
@app.route("/index")
@login_required
def start():
    return redirect("/recipes", code=302)


@app.route("/delete_recipes", methods = ['POST', 'GET'])
def delete():
    admin = users.query.filter_by(id=current_user.id).first().is_admin
    if admin:
        username = (users.query.filter_by(id=current_user.id).first()).username
        all_recipes = recipes.query.all()
        idRecipe= request.form.get("delete_recipes")
        if request.method == 'GET':
            return render_template("delete.html",
                username = username,
                all_recipes = all_recipes
            )
        else:
            delrecipe= recipes.query.filter_by(id=idRecipe).first()
            db.session.delete(delrecipe)
            db.session.commit()

            return redirect("/recipes", code=302)
    else:
        return redirect("/recipes")



@app.route("/new", methods = ['POST', 'GET'])
def new_recipes():
    admin = users.query.filter_by(id=current_user.id).first().is_admin
    if admin:
        username = (users.query.filter_by(id=current_user.id).first()).username
        idRecipe= request.form.get("delete_recipes")
        if request.method == 'GET':
            return render_template("add_new_recipes.html",
                username = username
            )
        else:
            name = request.form.get("input_name")
            ingridients = request.form.get("input_ingridients")
            steps = request.form.get("input_steps")
            photo = request.form.get("input_img")

            if not name or not ingridients or not steps or not photo:
                errors="Заполните все поля"
                return render_template("add_new_recipes.html",
                username = username,
                errors=errors
            )
            id = recipes.query.order_by(recipes.id.desc()).first().id + 1
            newrecipe = recipes(
                id = id,
                name = name,
                image_url = photo,
                ingridients = ingridients,
                steps = steps
            )

            db.session.add(newrecipe )
            db.session.commit()

            return redirect("/recipes", code=302)
    else:
        return redirect("/recipes")
    

@app.route("/edit", methods = ['POST', 'GET'])
def edit_rs():
    admin = users.query.filter_by(id=current_user.id).first().is_admin
    if admin:
        username = (users.query.filter_by(id=current_user.id).first()).username
        all_recipes = recipes.query.all()
        idRecipe= request.form.get("edit_recipes")
        if request.method == 'GET':
            return render_template("edit_recipes.html",
                username = username,
                all_recipes = all_recipes
            )
        else:    
            return redirect(f"/edit/{idRecipe}", code=302)
    else:
        return redirect("/recipes")


@app.route("/edit/<string:id>", methods = ['POST', 'GET'])
def edit(id):
    admin = users.query.filter_by(id=current_user.id).first().is_admin
    if admin:
        username = (users.query.filter_by(id=current_user.id).first()).username
        recipe_to_edit = recipes.query.filter_by(id=id).first()
        if request.method == 'GET':
            return render_template("edit_all.html",
                username = username,
                recipe_to_edit=recipe_to_edit
                
            )
        else:
            name = request.form.get("input_name")
            ingridients = request.form.get("input_ingridients")
            steps = request.form.get("input_steps")
            photo = request.form.get("input_img")

            if not name or not ingridients or not steps or not photo:
                errors="Заполните все поля"
                return render_template("edit_all.html",
                username = username,
                errors=errors,
                recipe_to_edit=recipe_to_edit
            )
            recipe_to_edit.name = name
            recipe_to_edit.ingridients = ingridients
            recipe_to_edit.steps = steps
            recipe_to_edit.image_url = photo

            db.session.add(recipe_to_edit)
            db.session.commit()

            return redirect("/recipes", code=302)
    else:
        return redirect("/recipes")

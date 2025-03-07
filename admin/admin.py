import time
import re

from flask import Blueprint, render_template, url_for, redirect, session, request, flash, g
from mako.filters import url_escape

from db import db, Posts, Users, Games, MainMenu
from datetime import datetime, timedelta
from sqlalchemy import func



admin = Blueprint('admin', __name__, template_folder='templates', static_folder='static')

menu = [{'url': '.index', 'title': 'Панель'},
        {'url': '.list_users', 'title': 'Список пользователей'},
        {'url': '.list_games', 'title': 'Список игр'},
        {'url': '.list_menu', 'title': 'Пункты меню'},
        # {'url': '.add_game', 'title': 'Добавить игру'},
        {'url': '.logout', 'title': 'Выйти'}]

def isLogged():
    return True if session.get('admin_logged') else False

def login_admin():
    session['admin_logged'] = 1

def logout_admin():
    session.pop('admin_logged', None)


@admin.route('/')
def index():
    if not isLogged():
        return redirect(url_for('.login'))
    total_users = Users.query.count()
    total_games = Games.query.count()


    today = datetime.now()
    last_week = today - timedelta(days=7)
    user_stats = (
        db.session.query(func.date(Users.time), func.count())
        .filter(Users.time >= last_week)
        .group_by(func.date(Users.time))
        .all
    )
    game_stats = (
        db.session.query(func.date(Games.time), func.count())
        .filter(Games.time >= last_week)
        .group_by(func.date(Games.time))
        .all
    )
    return render_template(
        'admin/index.html',
        menu=menu,
        title='Админ-панель',
        total_users=total_users,
        total_games=total_games,
        user_stats = user_stats,
        game_stats = game_stats,
    )

@admin.route('/login', methods=["POST", "GET"])
def login():
    if isLogged():
        return redirect(url_for('.index'))

    if request.method == "POST":
        if request.form['user'] == "admin" and request.form['psw'] == "12345":
            login_admin()
            return redirect(url_for('.index'))
        else:
            flash("Неверная пара логин/пароль", "error")

    return render_template('admin/login.html', title='Админ-панель')


@admin.route('/logout', methods=["POST", "GET"])
def logout():
    if not isLogged():
        return redirect(url_for('.login'))

    logout_admin()

    return redirect(url_for('.login'))

@admin.route('/list_pubs')
def list_pubs():
    if not isLogged():
        return redirect(url_for('.login'))

    try:
        list = Posts.query.all()
    except Exception as e:
        flash(f'Оштбка получения статей: {str(e)}', 'error')
        list=[]
    return render_template('admin/list_pubs.html', title='Список статей', menu=menu, list=list)

@admin.route('/list_users')
def list_users():
    if not isLogged():
        return redirect(url_for('.login'))
    try:
        list = Users.query.order_by(Users.time.desc()).all()
    except Exception as e:
        flash(f'Ошибка получения пользователей: {str(e)}', 'error')
        list=[]
    return render_template('admin/list_users.html', title='Список пользователей', menu=menu, list=list)
@admin.route('/list_games')
def list_games():
    if not isLogged():
        return redirect(url_for('.login'))

    try:
        games = Games.query.all()
    except Exception as e:
        flash(f'Ошибка получения списка игр: {str(e)}', 'error')
        games = []
    return render_template('admin/list_games.html', title='Список игр', menu=menu, games=games)
@admin.route('/list_menu')
def list_menu():
    if not isLogged():
        return redirect(url_for('.login'))

    try:
        menu_list = MainMenu.query.all()
    except Exception as e:
        flash(f'Ошибка получения списка меню: {str(e)}', 'error')
        menu_list = []
    return render_template('admin/list_menu.html', title='Пункты меню', menu=menu, menu_list=menu_list)
@admin.route('/add_menu', methods=['POST', 'GET'])
def add_menu():
    if not isLogged():
        return redirect(url_for('.login'))
    if request.method == 'POST':
        title = request.form.get('title')
        url = request.form.get('url')


        if not title or not url :
            flash('Все поля должны быть заполнены','error')
        else:
            try:
                new_menu = MainMenu(title=title, url=url)
                db.session.add(new_menu)
                db.session.commit()
                flash('Пукт успешно добавлена', 'success')
                return redirect(url_for('.list_menu'))
            except Exception as e:
                db.session.rollback()
                flash(f'Ошибка добавления пункта: {str(e)}', 'error')
    return render_template('admin/add_menu.html', menu=menu, title='Добавить пункт меню')
@admin.route('/add_game', methods=['POST', 'GET'])
def add_game():
    if not isLogged():
        return redirect(url_for('.login'))
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        link = request.form.get('link')
        cover_file = request.files.get('cover')

        if not title or not description or not cover_file or not link:
            flash('Все поля должны быть заполнены','error')
        else:
            try:
                cover_data = cover_file.read()
                new_game = Games(title=title, description=description, cover=cover_data, link=link)
                db.session.add(new_game)
                db.session.commit()
                flash('Игра успешно добавлена', 'success')
                return redirect(url_for('.list_games'))
            except Exception as e:
                db.session.rollback()
                flash(f'Ошибка добавления игры: {str(e)}', 'error')
    return render_template('admin/add_game.html', menu=menu, title='Добавить игру')

@admin.route('/delete-user/<int:user_id>', methods=['POST', "GET"])
def delete_user(user_id):
    if not isLogged():
        return redirect(url_for('.login'))
    try:
        user= Users.query.get(user_id)
        if user:
            db.session.delete(user)
            db.session.commit()
            flash('Пользователь успешно удален', 'success')
        else:
            flash('Ошибка удаления пользователя', 'error')
    except Exception as e:
        db.session.rollback()
        flash(f'Ошибка удаления пользователя: {str(e)}', 'error')
    return redirect(url_for('.list_users'))

@admin.route('/delete-game/<int:game_id>', methods=['POST', "GET"])
def delete_game(game_id):
    if not isLogged():
        return redirect(url_for('.login'))
    try:
        game= Games.query.get(game_id)
        if game:
            db.session.delete(game)
            db.session.commit()
            flash('Игра успешно удалена', 'success')
        else:
            flash('Игра не найдена', 'error')
    except Exception as e:
        db.session.rollback()
        flash(f'Ошибка удаления игры: {str(e)}', 'error')
    return redirect(url_for('.list_games'))
@admin.route('/delete-menu/<int:menu_id>', methods=['POST', "GET"])
def delete_menu(menu_id):
    if not isLogged():
        return redirect(url_for('.login'))
    try:
        menu_list= MainMenu.query.get(menu_id)
        if menu_list:
            db.session.delete(menu_list)
            db.session.commit()
            flash('Пункт успешно удален', 'success')
        else:
            flash('Пункт не найден', 'error')
    except Exception as e:
        db.session.rollback()
        flash(f'Ошибка удаления пункта: {str(e)}', 'error')
    return redirect(url_for('.list_menu'))



@admin.route('/edit_menu/<int:menu_id>', methods=['POST', 'GET'])
def edit_menu(menu_id):
    if not isLogged():
        return redirect(url_for('.login'))
    menu_list =  MainMenu.query.get(menu_id)
    if not menu_list:
        flash('Пункт меню не найден', 'error')
        return redirect(url_for('.list_menu'))

    if request.method == 'POST':
        title = request.form.get('title')
        url = request.form.get('url')

        if title or url :
            try:
                menu_list.title = title
                menu_list.url = url
                db.session.commit()
                flash('Пукт успешно обновлен', 'success')
                return redirect(url_for('.list_menu'))
            except Exception as e:
                db.session.rollback()
                flash(f'Ошибка обновления пункта: {str(e)}', 'error')
    return render_template('admin/edit_menu.html', menu=menu, title='Редактировать пункт меню', menu_list=menu_list)
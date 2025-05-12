from flask import Flask, render_template, redirect, url_for, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.utils import secure_filename
import os

from forms import ArticleForm, LoginForm, RegistrationForm
from models import db, User, Article
from api import api_bp

# Инициализация приложения
app = Flask(__name__)
app.config['SECRET_KEY'] = 'mysecretkey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOADED_IMAGES_DEST'] = 'static/uploads/images'

# Инициализация базы данных и авторизации
db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Регистрируем API Blueprint
app.register_blueprint(api_bp, url_prefix='/api')

# Главная страница
@app.route('/')
def index():
    articles = Article.query.all()
    return render_template('index.html', articles=articles)

# Страница для создания статьи (только для авторизованных пользователей)
@app.route('/create_article', methods=['GET', 'POST'])
@login_required
def create_article():
    form = ArticleForm()
    if form.validate_on_submit():
        image = form.image.data
        filename = secure_filename(image.filename)
        filepath = os.path.join(app.config['UPLOADED_IMAGES_DEST'], filename)
        image.save(filepath)

        new_article = Article(title=form.title.data, content=form.content.data, image_filename=filename, author_id=current_user.id)
        db.session.add(new_article)
        db.session.commit()

        return redirect(url_for('index'))

    return render_template('create_article.html', form=form)

# Страница для регистрации
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        # Проверяем, существует ли уже пользователь с таким именем
        existing_user = User.query.filter_by(username=form.username.data).first()
        if existing_user:
            return "Username already taken", 400

        # Создаём нового пользователя и хэшируем пароль
        user = User(username=form.username.data)
        user.set_password(form.password.data)

        # Добавляем в базу данных
        db.session.add(user)
        db.session.commit()

        # Перенаправляем на логин
        return redirect(url_for('login'))

    return render_template('register.html', form=form)

# Страница для логина
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            return redirect(url_for('index'))
    return render_template('login.html', form=form)

# Страница для выхода из аккаунта
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

# Страница для отдельной статьи
@app.route('/article/<int:id>')
def article(id):
    article = Article.query.get_or_404(id)
    return render_template('article.html', article=article)

# Загрузка изображений через API (REST)
@app.route('/upload_image', methods=['POST'])
def upload_image():
    image = request.files['image']
    filename = secure_filename(image.filename)
    filepath = os.path.join(app.config['UPLOADED_IMAGES_DEST'], filename)
    image.save(filepath)
    return {'message': 'Image uploaded successfully', 'filename': filename}

# Главный запуск
if __name__ == '__main__':
    app.run(debug=True)
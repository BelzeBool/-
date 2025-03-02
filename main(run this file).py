from flask import Flask, render_template, request, session, redirect, make_response
from user import create_user_table, User
from post import create_post_table, Post
from chat import create_chat_table, ChatMessage
import secrets
import hashlib
from datetime import datetime, timedelta

create_post_table()
create_user_table()
create_chat_table()

app = Flask("main")
app.secret_key = secrets.token_hex(32)


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


@app.route("/")
def index_page():
    posts = Post.get_all()

    # Проверяем куки, если пользователь не в сессии
    if "username" not in session:
        username = request.cookies.get("username")
        if username:
            session["username"] = username

    username = session.get("username", None)
    user = None
    if username:
        user = User.get_user_by_username(username)

    return render_template("index.html", posts=posts, user=user)


@app.route("/registration", methods=["POST", "GET"])
def register_page():
    if request.method == "GET":
        return render_template("register.html")
    if request.method == "POST":
        username = request.form.get("username").lower()
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")

        user = User.get_user_by_username(username)
        if user:
            return render_template(
                "register.html", error="Пользователь с таким ником уже есть"
            )
        
        if password != confirm_password:
            return render_template(
                "register.html", error="Пароли не совпадают"
            )
        
        hashed_password = hash_password(password)
        User.create(username, hashed_password)
        session["username"] = username
        return redirect('/')


@app.route("/login", methods=["POST","GET"])
def login_page():
    if request.method == "GET":
        return render_template("login.html")
    if request.method == "POST":
        username = request.form.get("username").lower()
        password = request.form.get("password")
        remember_me = request.form.get("remember_me")

        user = User.get_user_by_username(username)
        if not user:
            return render_template("login.html", error="Неправильный Логин или пароль.")
        
        hashed_password = hash_password(password)
        if user.password == hashed_password:
            session["username"] = username

            # Устанавливаем куки, если выбрано "Запомнить меня"
            response = make_response(redirect('/'))
            if remember_me:
                expires = datetime.now() + timedelta(days=30)
                response.set_cookie("username", username, expires=expires)
            return response
        else:
            return render_template("login.html", error="Неправильный логин или Пароль.")


@app.route("/logout")
def logout_page():
    session.pop("username", None)
    response = make_response(redirect('/login'))
    response.set_cookie("username", "", expires=0)  # Удаляем куки
    return response


@app.route("/profile")
def profile_page():
    username = session.get("username", None)
    if not username:
        return redirect('/login')
    
    user = User.get_user_by_username(username)
    posts = Post.get_by_author(user.id)
    return render_template("profile.html", user=user, posts=posts)


@app.route("/create_post", methods=["POST", "GET"])
def create_post_page():
    username = session.get("username", None)
    if not username:
        return redirect('/login')
    
    if request.method == "GET":
        return render_template("create_post.html")
    
    if request.method == "POST":
        title = request.form.get("title")
        text = request.form.get("text")
        
        user = User.get_user_by_username(username)
        Post.create(title, text, user.id)
        return redirect('/')


@app.route("/chat", methods=["GET", "POST"])
def chat_page():
    username = session.get("username", None)
    if not username:
        return redirect('/login')
    
    if request.method == "POST":
        message = request.form.get("message")
        user = User.get_user_by_username(username)
        ChatMessage.create(user.id, message)
        return redirect('/chat')
    
    messages = ChatMessage.get_all()
    user = User.get_user_by_username(username)
    return render_template("chat.html", messages=messages, user=user)


@app.route("/user/<int:user_id>")
def user_page(user_id):
    user = User.get_user_by_id(user_id)
    if not user:
        return "Пользователь не найден", 404
    
    posts = Post.get_by_author(user.id)
    return render_template("user.html", user=user, posts=posts)


app.run(host="0.0.0.0", port=8080)
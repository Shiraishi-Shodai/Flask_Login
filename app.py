from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required,  current_user
from flask import Flask, request, redirect, render_template, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__, template_folder="templates")
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///blog.db" #接続先のdbを指定
app.config['SQLALCHEMY_ECHO']=True #sql文等のログを出力
app.config["SECRET_KEY"] = os.urandom(24) #セッション情報を管理するための秘密鍵を指定
db = SQLAlchemy(app) #Flaskアプリケーション内でSQLAlchemyを使用できるようになります

login_manager = LoginManager()
login_manager.init_app(app) #FlaskアプリケーションとLoginManagerを紐づける

# ユーザーテーブルを定義
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    username = db.Column(db.String(50), nullable=True, unique=True) #null,重複を許可しない
    password = db.Column(db.String(25))

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/signup", methods=["GET", "POST"])
def signup():
    
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        user = User(username=username, password=generate_password_hash(password, method="sha256"))
        db.session.add(user)
        db.session.commit()
        return redirect("/login")
    else:
        return render_template("signup.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        # Userテーブルからユーザー名が一致するユーザーを取得
        user = User.query.filter_by(username=username).first()
        if check_password_hash(user.password, password):
            login_user(user) #ログイン
            print(f"ユーザー名:{current_user.username}")
            print(f"パスワード:{current_user.password}")
            return render_template("loginsuccess.html")
    else:
        return render_template("login.html")

@login_manager.user_loader #ログインが必要なページにアクセスした時に呼び出されるコールバック関数
def load_User(user_id):
    print(f"user_id: {user_id}")
    return User.query.filter_by(id=user_id).first()

@app.route("/logout")
@login_required #ログアウト機能がログイン状態で実行されるように指定(関数の上に指定)
def logout():
    logout_user()
    return redirect(url_for("signup")) #url_forを指定し、自分で作った関数にリダイレクト可能にする

# ログインしていないときはindex.htmlに繊維する
@login_manager.unauthorized_handler
def unauthorized():
    return redirect("/")

if __name__ == "__main__":
    app.run(port=8000, debug=True)


from flask import Flask , render_template, request, jsonify
import requests
##### email 
import smtplib 
#### Data Base libraries
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column
##### flask_ckeditor and flask forms
from flask_ckeditor import CKEditor, CKEditorField
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from flask_bootstrap5 import Bootstrap
from wtforms.validators import DataRequired
###for .env 
from dotenv import load_dotenv
import os

my_email = os.getenv("E_MAIL")
email_password = os.getenv("E_MAIL_PASSWORD")
connection = smtplib.SMTP("smtp.gmail.com", port=587)

class Base(DeclarativeBase):
  pass
db = SQLAlchemy(model_class=Base)
class Post(db.Model):
    __tablename__ = "blog_post"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(100), unique=True)
    subtitle: Mapped[str] = mapped_column(String(100),nullable=True) 
    author: Mapped[str] = mapped_column(String(50),nullable=True)
    img_url: Mapped[str] = mapped_column(nullable=True)
    email: Mapped[str] = mapped_column(String(100), nullable=True)
    body: Mapped[str] = mapped_column()
    date: Mapped[str] = mapped_column(nullable=True)
 

app = Flask(__name__)

app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")

###Form
class PostForm(FlaskForm):
    title = StringField('Blog Post Title', validators=[DataRequired()])
    subtitle = StringField('Subtitle', validators=[DataRequired()])
    name = StringField('Your Name', validators=[DataRequired()])
    img_url = StringField('Blog Image URL', validators=[DataRequired()])
    body = CKEditorField('Blog Content', validators=[DataRequired()])  # <--
    submit = SubmitField('Submit')
#figure CKEditor to use a custom version from the CDN
app.config['CKEDITOR_SERVE_LOCAL'] = False  # Use CDN
app.config['CKEDITOR_PKG_TYPE'] = ''  # Package type (e.g., standard, full)
ckeditor = CKEditor(app)

###Data Base
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///posts.db"
db.init_app(app)
with app.app_context():
    db.create_all()


###Routes
@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/contact", methods=["POST", "GET"])
def contact():
    message = "Contact Me"
    if ( request.method =="POST"):
        data = {
            "name" : request.form.get('name'),
            "email" : request.form.get('email'),
            "phone" : request.form.get('phone'),
            "message" : request.form.get('message'),
            }

        connection.starttls()
        connection.login(user=my_email, password=email_password)
        connection.sendmail(from_addr=request.form.get('email') , to_addrs='ptrsiakovou@gmail.com', msg = request.form.get('message') )
        message = "Your Message Received"

    return render_template("contact.html", msg_status = message)

@app.route("/")
def get_all_posts():
    
    all_posts= db.session.execute(db.select(Post)).scalars()
    print(type(all_posts))
   
    return render_template("index.html", data=all_posts)

@app.route("/post/<post_id>")
def post(post_id):
    post= db.get_or_404(Post, post_id)
    return render_template("post.html", data=post)

@app.route("/form-entr", methods=['POST'])
def receive_data():
    name = request.form.get('name')
    email = request.form.get('email')
    phone = request.form.get('phone')
    message = request.form.get('message')
    data = {
        "name" : request.form.get('name'),
        "email" : request.form.get('email'),
        "phone" : request.form.get('phone'),
        "message" : request.form.get('message'),
    }
    return jsonify(data)

@app.route("/new-post", methods=["POST", "GET"])
def new_post():
    
    post_form = PostForm()

    if request.method == "POST":

        user = Post (
            title = request.form.get("title"),
            subtitle = request.form.get("subtitle"),
            author = request.form.get("name"),
            img_url = request.form.get("img_url"),
            body = request.form.get("body"),
            date= '2024',
            email = "g@gmail.com",
        )
        print(request.form.get("name"))
        db.session.add(user)
        db.session.commit()

        return render_template("index.html",  form = post_form)
    
    return render_template("make-post.html",  form = post_form)

if __name__ == "__main__":
    app.run(debug=True)
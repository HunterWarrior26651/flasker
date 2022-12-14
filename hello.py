from enum import unique
from flask import Flask, render_template, flash, request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField, ValidationError
from wtforms.validators import DataRequired, EqualTo, Length
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import date


# Create A Flask Instance
app = Flask(__name__)
# Add Database
# Old SQLite DB
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
# New MySQL DB
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://username:password@localhost/db_name'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:password123@localhost/our_users'
# Secret Key!
app.config['SECRET_KEY'] = "My super secret key that no one is supposed to know"
# Initialize The Database
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Json Thing
@app.route('/date')
def get_current_date():
    favorite_pizza = {
        "John": "Pepperoni", 
        "Mary": "Cheese",
        "Tim": "Mushroom"
    }
    return favorite_pizza
    # return {"Date": date.today()}


# Create Model
class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)
    favorite_color = db.Column(db.String(120))
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    # Do some password stuff!
    password_hash = db.Column(db.String(128))

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute!')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)


    # Create A String
    def __repr__(self):
        return '<Name %r>' % self.name

@app.route('/delete/<int:id>')
def delete(id):
    user_to_delete = Users.query.get_or_404(id)
    name = None
    form = UserForm()

    try:
        db.session.delete(user_to_delete)
        db.session.commit()
        flash("User Deleted Successfully!")

        our_users = Users.query.order_by(Users.date_added)
        return render_template("add_user.html",
        form=form,
        name=name,
        our_users=our_users)
    
    except:
        flash("Whoops! Problem Deleting User...try again!")
        return render_template("add_user.html",
        form=form,
        name=name,
        our_users=our_users)

# Create A Form Class
class UserForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired()])
    favorite_color = StringField("Favorite Color")
    submit = SubmitField("Submit")
    password_hash = PasswordField('Password', validators=[DataRequired(), EqualTo('password_hash2', message='Passwords Must Match!')])
    password_hash2 = PasswordField('Confirm Password', validators=[DataRequired()])

# Update Database Record
@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    form = UserForm()
    name_to_update = Users.query.get_or_404(id)
    if request.method == "POST":
        name_to_update.name = request.form['name']
        name_to_update.email = request.form['email']
        name_to_update.favorite_color = request.form['favorite_color']
        try: 
            db.session.commit()
            flash("User Updated Successfully!")
            return render_template("update.html", form=form, name_to_update = name_to_update)
        except:
            db.session.commit()
            flash("Error! Looks like there was a problem...try again!")
            return render_template("update.html", form=form, name_to_update = name_to_update)
    else:
        return render_template("update.html", form=form, name_to_update = name_to_update, id = id)

class PasswordForm(FlaskForm):
    email = StringField("What's Your Email", validators=[DataRequired()])
    password_hash = PasswordField("What's Your Password", validators=[DataRequired()])
    submit = SubmitField("Submit")

# Create A Form Class
class NamerForm(FlaskForm):
    name = StringField("What's Your Name", validators=[DataRequired()])
    submit = SubmitField("Submit")

# def index():
#     return "<h1>Hello World!</h1>"

# FILTERS
# safe
# capitalize
# lower
# upper
# title
# trim
# striptags

@app.route('/users/add', methods=['GET', 'POST'])
def add_user():
    name = None
    form = UserForm() 
    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first()
        if user is None:
            # Hash the password!!
            hashed_pw = generate_password_hash(form.password_hash.data, "sha256")
            user = Users(name=form.name.data, email=form.email.data, favorite_color=form.favorite_color.data, password_hash=hashed_pw)
            db.session.add(user)
            db.session.commit()
        name = form.name.data
        form.name.data = ''
        form.email.data = ''
        form.favorite_color.data = ''
        form.password_hash = ''

        flash("User Added Successfully!")
    our_users = Users.query.order_by(Users.date_added)
    return render_template("add_user.html",
        form=form,
        name=name,
        our_users=our_users)   
     
# Create a route decorator
@app.route('/')        

def index():
    first_name = "John"
    stuff = "This is bold Text"
    favorite_pizza = ["Pepperoni", "Cheese", "Mushrooms", 41]
    return render_template("index.html", 
        first_name=first_name,
        stuff=stuff,
        favorite_pizza=favorite_pizza)

# localhost:5000/user/John
@app.route('/user/<name>')

def user(name):
    return render_template("user.html", user_name=name)

# Create Custom Error Pages

# Invalid URL
@app.errorhandler(404)
def page_not_found(e):
        return render_template("404.html"), 404

# Internal Server Error
@app.errorhandler(500)
def page_not_found(e):
        return render_template("500.html"), 500

# Create Password Test Page
@app.route('/test_pw', methods=['GET', 'POST'])
def test_pw():
    email = None
    password = None
    pw_to_check = None
    passed = None
    form = PasswordForm()
    # Validate Form
    if form.validate_on_submit():
        email = form.email.data
        password = form.password_hash.data
        # Clear the form
        form.email.data = ''
        form.password_hash.data = ''

        # Lookup User By Email Address
        pw_to_check = Users.query.filter_by(email=email).first()

        # Check Hashed Password
        passed = check_password_hash(pw_to_check.password_hash, password)



    return render_template("test_pw.html",
        email = email,
        password = password,
        pw_to_check = pw_to_check,
        passed = passed,
        form = form)

# Create Name Page
@app.route('/name', methods=['GET', 'POST'])
def name():
    name = None
    form = NamerForm()
    # Validate Form
    if form.validate_on_submit():
        name = form.name.data
        form.name.data = ''
        flash("Form Submitted Successfully!")

    return render_template("name.html",
        name = name,
        form = form)
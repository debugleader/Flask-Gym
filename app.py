from flask import Flask, render_template, url_for, flash, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, login_required, logout_user, current_user, UserMixin
from flask_wtf import FlaskForm
from wtforms import DateField, SubmitField, StringField, PasswordField, IntegerField
from wtforms.validators import DataRequired, Email, InputRequired, length
from werkzeug.security import generate_password_hash, check_password_hash
from flask_admin import Admin, AdminIndexView
from flask_admin.contrib.sqla import ModelView
from datetime import datetime, timedelta
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)

class myModelView(ModelView):
    def is_accessible(self):
        if current_user.is_authenticated:
            return current_user.phoneNumber == 999999
    # def inaccessible_callback(self, name, **kwargs):
    #     return redirect(url_for('login'))

class myAdminIndexView(AdminIndexView):
    def is_accessible(self):
        if current_user.is_authenticated:
            return current_user.phoneNumber == 999999

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('login'))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(30), nullable=False)
    fullName = db.Column(db.String(10), nullable=False)
    phoneNumber = db.Column(db.Integer, nullable=False, unique=True)
    password = db.Column(db.String(100), nullable=False)
    trainerName = db.Column(db.String(10), nullable=True)
    paidAmount = db.Column(db.String(30), nullable=True)
    validDate = db.Column(db.DateTime, nullable=True)
    allowed = db.Column(db.Boolean)

class Classes(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    class_name = db.Column(db.String(30), nullable=False)
    joined_num = db.Column(db.Integer, nullable=False, default=0)
    trainer_name = db.Column(db.String(20), nullable=True)
    class_title = db.Column(db.String(50), nullable=True)
    class_desc = db.Column(db.String(2000), nullable=True)

class Classesinfo(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    class_name = db.Column(db.String(30), nullable=False)
    joined_name = db.Column(db.String(30), nullable=False)

admin = Admin(app, index_view = myAdminIndexView())
admin.add_view(myModelView(User, db.session))
admin.add_view(myModelView(Classes, db.session))
admin.add_view(myModelView(Classesinfo, db.session))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class loginForm(FlaskForm):
    phoneNum = IntegerField("Phone Number", validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired(), length(min=8)])
    submit = SubmitField('Submit')

class registerForm(FlaskForm):
    fullName = StringField("Full name", validators=[DataRequired()])
    email = StringField("Email",  [InputRequired("Please enter your email address."), Email("This field requires a valid email address")])
    phoneNum = IntegerField("Phone Number (Use a unique phone number)", validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired(), length(min=8)])
    submit = SubmitField('Submit')

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/food')
def food():
    return render_template("food.html")

@app.route('/exercises')
def exercises():
    return render_template("exercises.html")

@app.route('/login', methods=['GET', 'POST'])
def login():
    if not current_user.is_authenticated:
        forms = loginForm()
        phoneNum_new = forms.phoneNum.data
        password_new = forms.password.data
        if forms.validate_on_submit():
            user = User.query.filter_by(phoneNumber=phoneNum_new).first()
            if user:
                if check_password_hash(user.password, password_new):
                    login_user(user)
                    y = User.query.filter_by(phoneNumber = current_user.phoneNumber).first()
                    if y.validDate:  
                        answer = y.validDate - datetime.now() 
                        # x = datetime.datetime.now()
                        # z = x.replace(microsecond=0)
                        # y = User.query.filter_by(phoneNumber = current_user.phoneNumber).first()
                        if answer.days <= 0:
                            y.allowed = False
                            db.session.commit()
                    if current_user.is_authenticated:
                        if current_user.phoneNumber == 999999:
                            return redirect(url_for('admin.index'))
                        else:
                            return redirect(url_for('logged'))
            else:
                flash(f"Your phone {phoneNum_new} or password are not correct")
    
        return render_template("login.html", form=forms)
    else:
        return redirect(url_for('logged'))

@app.route('/register', methods=["GET","POST"])
def register():
    forms = registerForm()
    fullName = forms.fullName.data
    email = forms.email.data
    phoneNum = forms.phoneNum.data
    password = forms.password.data
    hashed_password = generate_password_hash(password, method='sha256')
    if forms.validate_on_submit():
        new_user = User(fullName = fullName, email =  email, phoneNumber =  phoneNum, password = hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    
    return render_template("register.html", form=forms)

@app.route('/logout')
@login_required
def logout():
    logout_user()

    return redirect(url_for('login'))

@app.route('/calendar')
def calendar():
    theday = datetime.today().day
    themonth = datetime.today().month
    theyear = datetime.today().year
    theday_num = datetime.today().isoweekday()
    week_day = ['Default', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    theday_name = week_day[theday_num]
    month_names = ["Default","January","February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
    themonth_name = month_names[themonth]
    return render_template("calendar.html", theday = theday, themonth_name = themonth_name, theyear = theyear, theday_name = theday_name)

@app.route('/test')
def test():
    pass
    
@app.route('/not_logged')
def not_logged():
    class1 = Classes.query.filter_by(class_name = 'Class1').first()
    class2 = Classes.query.filter_by(class_name = 'Class2').first()
    class3 = Classes.query.filter_by(class_name = 'Class3').first()
    class4 = Classes.query.filter_by(class_name = 'Class4').first()
    class5 = Classes.query.filter_by(class_name = 'Class5').first()
    class6 = Classes.query.filter_by(class_name = 'Class6').first()
    if not current_user.is_authenticated or current_user.phoneNumber == 999999:
        return render_template('not_logged.html', class1=class1, class2=class2, class3=class3, class4=class4, class5=class5, class6=class6)
    else:
        return redirect(url_for('logged'))

@app.route('/logged')
@login_required
def logged():
    class1 = Classes.query.filter_by(class_name = 'Class1').first()
    class2 = Classes.query.filter_by(class_name = 'Class2').first()
    class3 = Classes.query.filter_by(class_name = 'Class3').first()
    class4 = Classes.query.filter_by(class_name = 'Class4').first()
    class5 = Classes.query.filter_by(class_name = 'Class5').first()
    class6 = Classes.query.filter_by(class_name = 'Class6').first()
    if current_user:
        if current_user.allowed:
            return render_template('logged.html', numb = Classes.query.filter_by(class_name = 'Class1').first(), numbo = Classesinfo.query.filter_by(class_name = 'Class1').all(),class1=class1, class2=class2, class3=class3, class4=class4, class5=class5, class6=class6)
        else:
            return render_template('not_authorized.html', class1=class1, class2=class2, class3=class3, class4=class4, class5=class5, class6=class6)

@app.route('/class1')
@login_required
def class1manage():
    username = current_user.fullName
    class_info = Classesinfo.query.filter_by(joined_name = username).first()
    class_classes = Classes.query.filter_by(class_name = 'Class1').first()
    if class_info:
        if username == class_info.joined_name and class_info.class_name == 'Class1':
            class_classes.joined_num -= 1
            db.session.delete(class_info)
            db.session.commit()
    else:
        class_classes.joined_num += 1
        db.session.add(Classesinfo(class_name = 'Class1', joined_name = username))
        db.session.commit()
    return redirect(url_for('login'))

@app.route('/class2')
@login_required
def class2manage():
    username = current_user.fullName
    class_info = Classesinfo.query.filter_by(joined_name = username).first()
    class_classes = Classes.query.filter_by(class_name = 'Class2').first()
    if class_info:
        if username == class_info.joined_name and class_info.class_name == 'Class2':
            class_classes.joined_num -= 1
            db.session.delete(class_info)
            db.session.commit()
    else:
        class_classes.joined_num += 1
        db.session.add(Classesinfo(class_name = 'Class2', joined_name = username))
        db.session.commit()
    return redirect(url_for('login'))

@app.route('/class3')
@login_required
def class3manage():
    username = current_user.fullName
    class_info = Classesinfo.query.filter_by(joined_name = username).first()
    class_classes = Classes.query.filter_by(class_name = 'Class3').first()
    if class_info:
        if username == class_info.joined_name and class_info.class_name == 'Class3':
            class_classes.joined_num -= 1
            db.session.delete(class_info)
            db.session.commit()
    else:
        class_classes.joined_num += 1
        db.session.add(Classesinfo(class_name = 'Class3', joined_name = username))
        db.session.commit()
    return redirect(url_for('login'))

@app.route('/class4')
@login_required
def class4manage():
    username = current_user.fullName
    class_info = Classesinfo.query.filter_by(joined_name = username).first()
    class_classes = Classes.query.filter_by(class_name = 'Class4').first()
    if class_info:
        if username == class_info.joined_name and class_info.class_name == 'Class4':
            class_classes.joined_num -= 1
            db.session.delete(class_info)
            db.session.commit()
    else:
        class_classes.joined_num += 1
        db.session.add(Classesinfo(class_name = 'Class4', joined_name = username))
        db.session.commit()
    return redirect(url_for('login'))

@app.route('/class5')
@login_required
def class5manage():
    username = current_user.fullName
    class_info = Classesinfo.query.filter_by(joined_name = username).first()
    class_classes = Classes.query.filter_by(class_name = 'Class5').first()
    if class_info:
        if username == class_info.joined_name and class_info.class_name == 'Class5':
            class_classes.joined_num -= 1
            db.session.delete(class_info)
            db.session.commit()
    else:
        class_classes.joined_num += 1
        db.session.add(Classesinfo(class_name = 'Class5', joined_name = username))
        db.session.commit()
    return redirect(url_for('login'))

@app.route('/class6')
@login_required
def class6manage():
    username = current_user.fullName
    class_info = Classesinfo.query.filter_by(joined_name = username).first()
    class_classes = Classes.query.filter_by(class_name = 'Class6').first()
    if class_info:
        if username == class_info.joined_name and class_info.class_name == 'Class6':
            class_classes.joined_num -= 1
            db.session.delete(class_info)
            db.session.commit()
    else:
        class_classes.joined_num += 1
        db.session.add(Classesinfo(class_name = 'Class6', joined_name = username))
        db.session.commit()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run()

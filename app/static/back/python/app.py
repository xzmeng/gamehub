

from flask import Flask, render_template, request
from wtforms import Form, StringField, PasswordField, validators
from flask_login import LoginManager, UserMixin, login_user
from flask import redirect

app = Flask(__name__)
app.secret_key = b'my-secret-key'

login_manager = LoginManager()
login_manager.init_app(app)


class LoginForm(Form):
    name = StringField('username', [validators.length(min=4, max=25)])
    password = PasswordField('password', [validators.length(min=4, max=25)])


class CalendarAdmin(UserMixin):
    """User class for flask-login"""

    def __init__(self, id):
        self.id = id
        self.name = 'admin'
        self.password = 'admin'


@login_manager.user_loader
def load_user(user_id):
    return CalendarAdmin(user_id)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['username'] == 'admin' and request.form['password'] == 'admin':
            test_admin_user = CalendarAdmin('admin')
            login_user(test_admin_user)
            return redirect('./admin')
        else:
            message = 'Login failed'
            return render_template('login.html', message=message)
    else:
        message = 'Test username: admin, password: admin'
        print(12345)
    return render_template('login.html', message=message)

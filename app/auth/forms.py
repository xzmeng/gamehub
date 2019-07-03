from wtforms import Form, validators
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms import ValidationError
from ..models import User


class LoginForm(Form):
    email = StringField('Email', [validators.Length(max=100),
                                  validators.InputRequired()])
    password = PasswordField('Password', [validators.Length(max=100),
                                          validators.InputRequired()])
    remember_me = BooleanField('Keep me logged in')
    submit = SubmitField('Login')


class RegistrationForm(Form):
    name = StringField('Name', [validators.Length(max=100),
                                validators.InputRequired()])
    email = StringField(
        'Email Address',
        [validators.Length(max=100),
         validators.Email(),
         validators.InputRequired(), ]
    )

    password = PasswordField('Password', [validators.EqualTo('password2'),
                                          validators.InputRequired()])
    password2 = PasswordField('Repeat password', [validators.InputRequired()])

    submit = SubmitField('Register')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered!')


class PasswordResetRequestForm(Form):
    email = StringField('Email', validators=[validators.InputRequired(),
                                             validators.Length(max=100),
                                             validators.Email()])
    submit = SubmitField('Reset Password')


class PasswordResetForm(Form):
    password = PasswordField('New Password', validators=[
        validators.InputRequired(),
        validators.EqualTo('password2', message='Passwords must match')])
    password2 = PasswordField('Confirm password', validators=[validators.InputRequired()])
    submit = SubmitField('Reset Password')


class ChangeEmailForm(Form):
    email = StringField('New Email', validators=[validators.InputRequired(),
                                                 validators.Length(max=100),
                                                 validators.Email()])
    password = PasswordField('Password', validators=[validators.InputRequired()])
    submit = SubmitField('Update Email Address')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')
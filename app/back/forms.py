from wtforms import Form, validators, StringField, DateField, FloatField, TextAreaField, SelectField, FileField, \
    PasswordField, SelectMultipleField, ValidationError


class EditGameForm(Form):
    title = StringField('Title', [validators.InputRequired(),
                                  validators.Length(max=100)])

    issued_date = DateField('Issued Date', [validators.InputRequired()])

    publisher = StringField('Publisher', [validators.InputRequired(),
                                          validators.Length(max=100)])

    developer = StringField('Developer', [validators.InputRequired(),
                                          validators.Length(max=100)])

    price = FloatField('Price')

    brief_introduction = TextAreaField('Breif Introduction')

    version = StringField('Version', [validators.InputRequired(),
                                      validators.Length(max=100)])

    genres = SelectMultipleField('Genres',
                                 choices=[('RTS', 'RTS'),
                                          ('ACT', 'ACT'),
                                          ('FPS', 'FPS'),
                                          ('Rhythm', 'Rhythm'),
                                          ('Survival', 'Survival')])


class AddNewGameForm(Form):
    title = StringField('Title', [validators.InputRequired(),
                                  validators.Length(max=100)])

    issued_date = DateField('Issued Date', [validators.InputRequired()])

    publisher = StringField('Publisher', [validators.InputRequired(),
                                          validators.Length(max=100)])

    developer = StringField('Developer', [validators.InputRequired(),
                                          validators.Length(max=100)])

    price = FloatField('Price')

    brief_introduction = TextAreaField('Breif Introduction')

    version = StringField('Version', [validators.InputRequired(),
                                      validators.Length(max=100)])

    genres = SelectMultipleField('Genres',
                                 choices=[('RTS', 'RTS'),
                                          ('ACT', 'ACT'),
                                          ('FPS', 'FPS'),
                                          ('Rhythm', 'Rhythm'),
                                          ('Survival', 'Survival')])

    def validate_rating(self, field):
        if field.data < 0 or field.data > 10:
            raise ValidationError('rating must be between 0 and 10!')


class EditUserForm(Form):
    name = StringField('Name', [validators.InputRequired(),
                                validators.Length(max=100)])
    email = StringField('Email', [validators.InputRequired(),
                                  validators.Length(max=100),
                                  validators.Email()])
    gender = SelectField('Gender', choices=[('M', 'Male'), ('F', 'Female')])

    bill_address = StringField('Bill Address', [validators.InputRequired(),
                                                validators.Length(max=200)])

    personal_introduction = TextAreaField('Personal Introduction')

    phone_no = StringField('Phone Number', [validators.InputRequired(),
                                            validators.Length(max=50)])

    confirmed = SelectField('Confirmed',
                            choices=[(True, 'confirmed'),
                                     (False, 'unconfirmed')],
                            coerce=bool)


class EditProfileForm(Form):
    name = StringField('Name', [validators.InputRequired(),
                                validators.Length(max=100)])

    gender = SelectField('Gender', choices=[('M', 'Male'), ('F', 'Female')])

    bill_address = StringField('Bill Address', [validators.InputRequired(),
                                                validators.Length(max=200)])

    personal_introduction = TextAreaField('Personal Introduction')

    phone_no = StringField('Phone Number', [validators.InputRequired(),
                                            validators.Length(max=50)])

    photo = FileField('Photo')


class ChangePasswordForm(Form):
    old_password = PasswordField('Old password', validators=[validators.InputRequired()])
    password = PasswordField('New password', validators=[
        validators.InputRequired(),
        validators.EqualTo('password2', message='Passwords must match.')])
    password2 = PasswordField('Confirm new password',
                              validators=[validators.InputRequired()])


class RefundProcessForm(Form):
    msg = TextAreaField('Message')
    status = SelectField('accept/reject', choices=[('accepted', 'Accept'), ('rejected', 'Reject')])


class UploadFileForm(Form):
    photo = FileField('Photo')


class EditOrderForm(Form):
    total_cost = FloatField('Total Cost', [validators.InputRequired()])
    bill_address = StringField('Bill Address', [validators.InputRequired()])
    date = DateField('Date', [validators.InputRequired()])

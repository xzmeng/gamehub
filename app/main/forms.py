from wtforms import Form, validators
from wtforms import TextAreaField


class CommentForm(Form):
    body = TextAreaField('Message', [validators.InputRequired()])

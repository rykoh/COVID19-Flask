from flask_wtf import FlaskForm
from wtforms import StringField, TextField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length

class FeedbackForm(FlaskForm):
    """Feedback form."""
    body = TextAreaField('', [
        DataRequired(),
        Length(min=1, message=('Your message is too short.'))])
    submit = SubmitField('Submit')

    

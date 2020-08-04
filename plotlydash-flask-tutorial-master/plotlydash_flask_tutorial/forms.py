from flask_wtf import FlaskForm
from wtforms import StringField, TextField, SubmitField
from wtforms.validators import DataRequired, Length

class FeedbackForm(FlaskForm):
    """Feedback form."""
    body = TextField('', [
        DataRequired(),
        Length(min=1, message=('Your message is too short.'))])
    submit = SubmitField('Submit')

    

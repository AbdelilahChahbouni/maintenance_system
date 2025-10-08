from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired

class MachineForm(FlaskForm):
    name = StringField('Machine Name', validators=[DataRequired()])
    location = StringField('Location')
    submit = SubmitField('Save')

from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length

class IssueForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired(), Length(min=3, max=100)])
    description = TextAreaField("Description", validators=[DataRequired()])
    solution = TextAreaField("Solution")
    submit = SubmitField("Save")
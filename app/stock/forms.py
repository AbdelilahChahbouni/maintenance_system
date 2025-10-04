from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, TextAreaField, SubmitField
from wtforms.validators import DataRequired

class SparePartForm(FlaskForm):
    name = StringField("Part Name", validators=[DataRequired()])
    part_number = StringField("Part Number", validators=[DataRequired()])
    quantity = IntegerField("Quantity", default=0)
    location = StringField("Location")
    description = TextAreaField("Description")
    submit = SubmitField("Save")

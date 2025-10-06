from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SelectField, SubmitField
from wtforms.validators import DataRequired, NumberRange

class ConsumableUsageForm(FlaskForm):
    consumable_name = StringField("Consumable Name", validators=[DataRequired()])
    quantity = IntegerField("Quantity Used", validators=[DataRequired(), NumberRange(min=1)])
    machine_id = SelectField("Machine", coerce=int, choices=[])
    submit = SubmitField("Log Usage")
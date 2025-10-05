from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, TextAreaField, SubmitField , SelectField 
from wtforms.validators import DataRequired , NumberRange
from app.models import SparePart


class SparePartForm(FlaskForm):
    name = StringField("Part Name", validators=[DataRequired()])
    part_number = StringField("Part Number", validators=[DataRequired()])
    quantity = IntegerField("Quantity", default=0)
    location = StringField("Location")
    description = TextAreaField("Description")
    submit = SubmitField("Save")

class TransactionForm(FlaskForm):
    part_id = SelectField("Select Part", coerce=int, validators=[DataRequired()])
    machine_name = StringField("Machine Name", validators=[DataRequired()])
    quantity_used = IntegerField("Quantity Used", validators=[DataRequired(), NumberRange(min=1)])
    submit = SubmitField("Record Transaction")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Populate dropdown with available parts
        self.part_id.choices = [(p.id, f"{p.name} ({p.quantity} in stock)") for p in SparePart.query.all()]

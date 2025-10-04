from flask import Blueprint, render_template, redirect, url_for, flash, request
from app import db
from app.models import SparePart
from .forms import SparePartForm

stock = Blueprint("stock", __name__)

# List Spare Parts
@stock.route("/stocks")
def list_stock():
    parts = SparePart.query.all()
    return render_template("stock/stock_list.html", parts=parts)

# Add Spare Part
@stock.route("/stocks/new", methods=["GET", "POST"])
def add_stock():
    form = SparePartForm()
    if form.validate_on_submit():
        part = SparePart(
            name=form.name.data,
            part_number=form.part_number.data,
            quantity=form.quantity.data,
            location=form.location.data,
            description=form.description.data
        )
        db.session.add(part)
        db.session.commit()
        flash("New spare part added!", "success")
        return redirect(url_for("stock.list_stock"))
    return render_template("stock/add_stock.html", form=form, title="Add Spare Part")

# Edit spare part
@stock.route("/stocks/<int:part_id>/edit", methods=["GET", "POST"])
def edit_stock(part_id):
    part = SparePart.query.get_or_404(part_id)
    form = SparePartForm(obj=part)

    if form.validate_on_submit():
        part.name = form.name.data
        part.quantity = form.quantity.data
        part.location = form.location.data
        part.part_number = form.part_number.data
        part.description = form.description.data
        db.session.commit()
        flash("Spare part updated successfully!", "success")
        return redirect(url_for("stock.list_stock"))

    return render_template("stock/edite_stock.html", form=form, title="Edit Spare Part")

# Delete spare part
@stock.route("/stocks/<int:part_id>/delete", methods=["POST"])
def delete_stock(part_id):
    part = SparePart.query.get_or_404(part_id)
    db.session.delete(part)
    db.session.commit()
    flash("Spare part deleted successfully!", "danger")
    return redirect(url_for("stock.list_stock"))
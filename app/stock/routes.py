from flask import Blueprint, render_template, redirect, url_for, flash, request 
from app import db
from app.models import SparePart , Transaction , Machine 
from .forms import SparePartForm , TransactionForm
from flask_login import current_user , login_required

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


@stock.route("/stocks/out", methods=["GET", "POST"])
# @login_required
def stock_out():
    form = TransactionForm()
    form.machine_name.choices = [(m.id, m.name) for m in Machine.query.all()]
    if form.validate_on_submit():
        part = SparePart.query.get_or_404(form.part_id.data)
        if form.quantity_used.data > part.quantity:
            flash("Not enough stock!", "danger")
        else:
            part.quantity -= form.quantity_used.data
            transaction = Transaction(
                part_id=part.id,
                machine_name=form.machine_name.data,
                quantity_used=form.quantity_used.data,
                user_id=current_user.id
            )
            db.session.add(transaction)
            db.session.commit()
            flash("Transaction recorded!", "success")
            return redirect(url_for("stock.list_stock"))

    return render_template("stock/stock_out.html", form=form, title="Use Spare Part")


@stock.route("/stock_out_list")
def stock_out_list():
    transactions = Transaction.query.order_by(Transaction.date_used.desc()).all()
    return render_template("stock/stock_out_list.html", transactions=transactions, title="Transactions")



@stock.route("/stock_out/<int:transaction_id>/edit", methods=["GET", "POST"])
@login_required
def edit_stock_out(transaction_id):
    transaction = Transaction.query.get_or_404(transaction_id)
    form = TransactionForm(obj=transaction)

    if form.validate_on_submit():
        old_part = transaction.part
        old_qty = transaction.quantity_used

        # If part changed
        if transaction.part_id != form.part_id.data:
            # restore stock to old part
            old_part.quantity += old_qty

            # deduct stock from new part
            new_part = SparePart.query.get_or_404(form.part_id.data)
            if form.quantity_used.data > new_part.quantity:
                flash("Not enough stock in the new part!", "danger")
                return redirect(url_for("stock.edit_stock_out", transaction_id=transaction.id))
            new_part.quantity -= form.quantity_used.data

            transaction.part_id = form.part_id.data
            transaction.quantity_used = form.quantity_used.data
            transaction.machine_name = form.machine_name.data

        else:  # same part
            diff = form.quantity_used.data - old_qty
            if diff > 0:  # need more stock
                if diff > old_part.quantity:
                    flash("Not enough stock to increase quantity!", "danger")
                    return redirect(url_for("stock.edit_stock_out", transaction_id=transaction.id))
                old_part.quantity -= diff
            else:  # returning stock
                old_part.quantity += abs(diff)

            transaction.quantity_used = form.quantity_used.data
            transaction.machine_name = form.machine_name.data

        db.session.commit()
        flash("Transaction updated successfully!", "success")
        return redirect(url_for("stock.stock_out_list"))

    return render_template("stock/edit_stock_out.html", form=form, title="Edit Transaction")



@stock.route("/transactions/<int:transaction_id>/delete", methods=["POST"])
@login_required
def delete_stock_out(transaction_id):
    transaction = Transaction.query.get_or_404(transaction_id)
    part = transaction.part

    # restore stock
    part.quantity += transaction.quantity_used

    db.session.delete(transaction)
    db.session.commit()
    flash("Transaction deleted and stock restored!", "success")
    return redirect(url_for("stock.stock_out_list"))

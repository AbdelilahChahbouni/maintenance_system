from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import current_user, login_required
from app import db
from app.models import ConsumableUsage , Machine
from app.consumables.forms import ConsumableUsageForm

consumables = Blueprint("consumables", __name__)

@consumables.route("/consumables", methods=["GET"])
@login_required
def list_consumables():
    all_usages = ConsumableUsage.query.order_by(ConsumableUsage.date_used.desc()).all()
    return render_template("consumables/consum_list.html", consumables=all_usages)

@consumables.route("/consumables/new", methods=["GET", "POST"])
@login_required
def new_consumable():
    form = ConsumableUsageForm()
    form.machine_id.choices = [(m.id, m.name) for m in Machine.query.all()]
    # form.issue_id.choices = [(0, "None")] + [(i.id, i.title) for i in Issue.query.all()]

    if form.validate_on_submit():
        usage = ConsumableUsage(
            consumable_name=form.consumable_name.data,
            quantity=form.quantity.data,
            machine_id=form.machine_id.data if form.machine_id.data != 0 else None,
            user_id=current_user.id
        )
        db.session.add(usage)
        db.session.commit()
        flash("Consumable usage logged successfully ✅", "success")
        return redirect(url_for("consumables.list_consumables"))

    return render_template("consumables/consum_add.html", form=form, title="Log Consumable")



@consumables.route("/consumables/<int:usage_id>/edit", methods=["GET", "POST"])
@login_required
def edit_consumable(usage_id):
    usage = ConsumableUsage.query.get_or_404(usage_id)
    form = ConsumableUsageForm()
    form.machine_id.choices = [(m.id, m.name) for m in Machine.query.all()]

    if form.validate_on_submit():
        usage.consumable_name = form.consumable_name.data
        usage.quantity = form.quantity.data
        usage.machine_id = form.machine_id.data
        db.session.commit()
        flash("Consumable usage updated successfully ✅", "success")
        return redirect(url_for("consumables.list_consumables"))

    # Pre-fill form fields
    form.consumable_name.data = usage.consumable_name
    form.quantity.data = usage.quantity
    form.machine_id.data = usage.machine_id

    return render_template("consumables/consum_edit.html", title="Edit Consumable", form=form, usage=usage)

# ------------------------------
# Delete consumable usage
# ------------------------------
@consumables.route("/consumables/<int:usage_id>/delete", methods=["POST"])
@login_required
def delete_consumable(usage_id):
    usage = ConsumableUsage.query.get_or_404(usage_id)
    db.session.delete(usage)
    db.session.commit()
    flash("Consumable usage deleted successfully 🗑️", "success")
    return redirect(url_for("consumables.list_consumables"))
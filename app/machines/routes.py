from flask import Blueprint, render_template, redirect, url_for, flash, request
from app import db
from app.models import Machine
from app.machines.forms import MachineForm

machines = Blueprint("machines", __name__)

@machines.route("/machines")
def list_machines():
    all_machines = Machine.query.all()
    return render_template("machines/list_machines.html", machines=all_machines)

@machines.route("/machines/new", methods=["GET", "POST"])
def new_machine():
    form = MachineForm()
    if form.validate_on_submit():
        machine = Machine(
            name=form.name.data,
            location=form.location.data,
            
        )
        db.session.add(machine)
        db.session.commit()
        flash("Machine added successfully!", "success")
        return redirect(url_for("machines.list_machines"))
    return render_template("machines/add_machine.html", form=form, title="Add Machine")

@machines.route("/machines/<int:id>/edit", methods=["GET", "POST"])
def edit_machine(id):
    machine = Machine.query.get_or_404(id)
    form = MachineForm(obj=machine)
    if form.validate_on_submit():
        form.populate_obj(machine)
        db.session.commit()
        flash("Machine updated successfully!", "success")
        return redirect(url_for("machines.list_machines"))
    return render_template("machines/edit_machine.html", form=form, title="Edit Machine")

@machines.route("/machines/<int:id>/delete", methods=["POST"])
def delete_machine(id):
    machine = Machine.query.get_or_404(id)
    db.session.delete(machine)
    db.session.commit()
    flash("Machine deleted successfully!", "info")
    return redirect(url_for("machines.list_machines"))

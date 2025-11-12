from flask import Blueprint, render_template, redirect, url_for, flash, request
from app import db
from app.models import Machine
from app.machines.forms import MachineForm

machines = Blueprint("machines", __name__)

# @machines.route("/machines")
# def list_machines():
#     all_machines = Machine.query.all()
#     return render_template("machines/list_machines.html", machines=all_machines)

@machines.route("/machines", methods=["GET"])
# @login_required
def list_machines():
    search_query = request.args.get("q", "")

    machines = Machine.query

    if search_query:
        machines = machines.filter(
            db.or_(
                Machine.name.ilike(f"%{search_query}%"),
                Machine.location.ilike(f"%{search_query}%")
            )
        )

    machines = machines.order_by(Machine.name.asc()).all()

    return render_template(
        "machines/list_machines.html",
        machines=machines,
        search_query=search_query,
        title="Machines List"
    )










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
    flash("Machine deleted successfully!", "danger")
    return redirect(url_for("machines.list_machines"))

# API 

from flask import request, jsonify
import jwt
from functools import wraps
from config import Config
from datetime import datetime

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        # Token expected in Authorization header
        if "Authorization" in request.headers:
            auth_header = request.headers["Authorization"]
            if auth_header.startswith("Bearer "):
                token = auth_header.split(" ")[1]

        if not token:
            return jsonify({"success": False, "message": "Token is missing!"}), 401

        try:
            data = jwt.decode(token, Config.SECRET_KEY, algorithms=["HS256"])  # ✅ FIXED
            current_user_id = data["user_id"]
        except Exception:
            return jsonify({"success": False, "message": "Token is invalid!"}), 401

        return f(current_user_id, *args, **kwargs)
    return decorated




@machines.route("/api/machines", methods=["GET"])
@token_required
def get_machines(current_user_id):
    machines = Machine.query.all()
    data = [
        {"id": machine.id, "name": machine.name}
        for machine in machines
    ]
    return jsonify(data), 200
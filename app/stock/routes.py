from flask import Blueprint, render_template, redirect, url_for, flash, request , jsonify
from app import db
from app.models import SparePart , Transaction , Machine , User
from .forms import SparePartForm , TransactionForm
from flask_login import current_user , login_required
from datetime import datetime
from app.utils import export_to_pdf , generate_qr_for_part

stock = Blueprint("stock", __name__)

@stock.route('/stock/export/pdf')
def export_stock_pdf():
    items = SparePart.query.all()
    headers = ["#", "Item Name", "Part Number", "Quantity", "Location"]
    rows = [
        [i + 1, item.name, item.part_number , item.quantity, item.location]
        for i, item in enumerate(items)
    ]
    return export_to_pdf("📦 Stock Inventory Report", headers, rows, "stock_report.pdf")



@stock.route("/stocks", methods=["GET"])
def list_stock():
    q = request.args.get("q", "")

    stocks = SparePart.query

    if q:
        stocks = stocks.filter(
            (SparePart.name.ilike(f"%{q}%")) |
            (SparePart.part_number.ilike(f"%{q}%"))
        )

    stocks = stocks.order_by(SparePart.id.desc()).all()

    return render_template(
        "stock/stock_list.html",
        stocks=stocks,
        search_query=q
    )

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

        qr_relpath = generate_qr_for_part(part)
        part.qr_filename = qr_relpath
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
                machine_id=form.machine_name.data,
                quantity_used=form.quantity_used.data,
                user_id=current_user.id
            )
            db.session.add(transaction)
            db.session.commit()
            flash("Transaction recorded!", "success")
            return redirect(url_for("stock.list_stock"))

    return render_template("stock/stock_out.html", form=form, title="Use Spare Part")


@stock.route('/transaction/export/pdf')
def export_stock_transaction_pdf():
    items = Transaction.query.all()
    headers = ["#", "Date", "Part", "Quantity", "Machine","User"]
    rows = [
        [i + 1, item.date_used.strftime("%Y-%m-%d %H:%M") , item.part.name , item.quantity_used, item.machine.name,item.user.username]
        for i, item in enumerate(items)
    ]
    return export_to_pdf("📦 Transactions Inventory Report", headers, rows, "stock_report.pdf")

@stock.route("/stock_out_list", methods=["GET"])
# @login_required
def stock_out_list():
    search_query = request.args.get("q", "")
    date_query = request.args.get("date", "")

    transactions = Transaction.query

    if search_query:
        transactions = transactions.join(SparePart).join(Machine).join(User).filter(
            db.or_(
                SparePart.name.ilike(f"%{search_query}%"),
                Machine.name.ilike(f"%{search_query}%"),
                User.username.ilike(f"%{search_query}%"),
            )
        )

    if date_query:
        try:
            date_obj = datetime.strptime(date_query, "%Y-%m-%d").date()
            transactions = transactions.filter(
                db.func.date(Transaction.date_used) == date_obj
            )
        except ValueError:
            pass

    transactions = transactions.order_by(Transaction.date_used.desc()).all()

    return render_template(
        "stock/stock_out_list.html",
        transactions=transactions,
        search_query=search_query,
        date_query=date_query,
        title="Stock Out List"
    )

@stock.route("/stock_out/<int:transaction_id>/edit", methods=["GET", "POST"])
@login_required
def edit_stock_out(transaction_id):
    transaction = Transaction.query.get_or_404(transaction_id)
    form = TransactionForm(obj=transaction)
    form.machine_name.choices = [(m.id, m.name) for m in Machine.query.all()]


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
                print("Not enough stock in the new part!", "danger")
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
                    print("Not enough stock to increase quantity!", "danger")
                    return redirect(url_for("stock.edit_stock_out", transaction_id=transaction.id))
                old_part.quantity -= diff
            else:  # returning stock
                old_part.quantity += abs(diff)

            transaction.quantity_used = form.quantity_used.data
            transaction.machine_id = form.machine_name.data
        db.session.commit()
        flash("Transaction updated successfully!", "success")
        print("Transaction updated successfully!", "success")
        
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
    flash("Transaction deleted and stock restored!", "danger")
    return redirect(url_for("stock.stock_out_list"))



# transaction OUT using QR Scanner

@stock.route('/scan-transaction')
@login_required
def scan_transaction():
    return render_template('stock/scan_transaction.html')


@stock.route("/process-scan", methods=["POST"])
@login_required
def process_scan():
    data = request.get_json()
    qr_data = data.get("qr_data") if data else None

    if not qr_data:
        return jsonify({"success": False, "message": "No QR data received."}), 400

    # Handle QR format like "PART:3"
    if qr_data.startswith("PART:"):
        try:
            part_id = int(qr_data.split(":")[1])
            part = SparePart.query.get(part_id)
            if not part:
                return jsonify({"success": False, "message": "Part not found."}), 404

            # Redirect user to confirmation form (quantity + machine)
            redirect_url = url_for("stock.confirm_transaction", part_id=part.id)
            return jsonify({"success": True, "message": f"Part '{part.name}' scanned successfully.", "redirect_url": redirect_url})
        except Exception as e:
            print("Error:", e)
            return jsonify({"success": False, "message": "Invalid QR format."}), 400
    else:
        return jsonify({"success": False, "message": "Invalid QR format. Expected 'PART:<id>'."}), 400



@stock.route("/confirm-transaction/<int:part_id>", methods=["GET", "POST"])
@login_required
def confirm_transaction(part_id):
    part = SparePart.query.get_or_404(part_id)
    machines = Machine.query.all()  # Load all machines

    if request.method == "POST":
        machine = request.form.get("machine_id")
        quantity = int(request.form.get("quantity", 0))

        if not machine or quantity <= 0:
            flash("Please enter valid machine and quantity.", "danger")
            return redirect(url_for("stock.confirm_transaction", part_id=part.id))

        if part.quantity < quantity:
            flash("Not enough stock available.", "danger")
            return redirect(url_for("stock.confirm_transaction", part_id=part.id))

        # Create a transaction
        transaction = Transaction(
            part_id=part.id,
            user_id=current_user.id,
            machine_id=machine,
            quantity_used=quantity,
        )
        db.session.add(transaction)

        # Update stock
        part.quantity -= quantity
        db.session.commit()

        flash(f"Transaction completed successfully for part {part.name}.", "success")
        return redirect(url_for("stock.stock_out_list"))

    return render_template("stock/confirm_transaction_qr.html", part=part , machines=machines)


# transaction IN using QR

@stock.route("/scan-transaction-in")
@login_required
def scan_transaction_in():
    """Page to scan QR code for stock IN transactions."""
    return render_template("stock/scan_transaction_in.html")


@stock.route("/process-scan-in", methods=["POST"])
@login_required
def process_scan_in():
    data = request.get_json()
    qr_data = data.get("part_id")

    if not qr_data:
        return jsonify({"success": False, "message": "Invalid QR code data"}), 400

    if qr_data.startswith("PART:"):
        part_id = qr_data.split(":")[1]
        part = SparePart.query.get(part_id)
        if part:
            return jsonify({
                "success": True,
                "message": f"Part found: {part.name}",
                "redirect": url_for("stock.confirm_transaction_in", part_id=part.id)
            })
        else:
            return jsonify({"success": False, "message": "Part not found"}), 404
    else:
        return jsonify({"success": False, "message": "Invalid QR format"}), 400


@stock.route("/confirm-transaction-in/<int:part_id>", methods=["GET", "POST"])
@login_required
def confirm_transaction_in(part_id):
    part = SparePart.query.get_or_404(part_id)

    if request.method == "POST":
        quantity = int(request.form.get("quantity", 0))

        if quantity <= 0:
            flash("Please enter a valid quantity.", "danger")
            return redirect(url_for("stock.confirm_transaction_in", part_id=part.id))

        transaction = Transaction(
            part_id=part.id,
            user_id=current_user.id,
            quantity_used=quantity,
        )

        # ✅ Increase stock
        part.quantity += quantity
        db.session.add(transaction)
        db.session.commit()

        flash(f"Successfully added {quantity} units to {part.name}.", "success")
        return redirect(url_for("stock.list_stock"))

    return render_template("stock/confirm_transaction_in.html", part=part)

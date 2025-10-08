from flask import render_template , Blueprint
from app import db
from app.models import Issue, Transaction, ConsumableUsage, Machine

main = Blueprint("main", __name__)

@main.route('/dashboard')
def dashboard():
    total_issues = Issue.query.count()
    total_consumables = ConsumableUsage.query.count()
    total_transactions = Transaction.query.count()
    total_machines = Machine.query.count()

    recent_issues = Issue.query.order_by(Issue.created_at.desc()).limit(5).all()
    recent_transactions = Transaction.query.order_by(Transaction.date_used.desc()).limit(5).all()
    recent_consumables = ConsumableUsage.query.order_by(ConsumableUsage.date_used.desc()).limit(5).all()

    return render_template(
        'main/dashboard.html',
        total_issues=total_issues,
        total_consumables=total_consumables,
        total_transactions=total_transactions,
        total_machines=total_machines,
        recent_issues=recent_issues,
        recent_transactions=recent_transactions,
        recent_consumables=recent_consumables
    )

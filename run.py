from app import create_app, db
from app.models import User, Issue, SparePart, StockTransaction, ConsumableUsage

app = create_app()

@app.shell_context_processor
def make_shell_context():
    return {
    'db': db,
    'User': User,
    'Issue': Issue,
    'SparePart': SparePart,
    'StockTransaction': StockTransaction,
    'ConsumableUsage': ConsumableUsage,
    }
from flask import Blueprint, render_template
from app.extensions import db
from app.domain.models.barang import Barang
from app.domain.models.kategori import Kategori
from app.domain.models.stock_history import StockHistory

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Renders the main welcome page / dashboard of ElectroStock."""
    # Query metrics from database
    total_barang = Barang.query.count()
    total_stok = db.session.query(db.func.sum(Barang.stok)).scalar() or 0
    jumlah_kategori = Kategori.query.count()

    # Get low stock items (stok <= 5)
    low_stock_items = Barang.query.filter(Barang.stok <= 5).order_by(Barang.stok.asc()).limit(5).all()

    # Get recent stock history movement
    recent_histories = StockHistory.query.order_by(StockHistory.created_at.desc()).limit(5).all()

    return render_template(
        'index.html',
        total_barang=total_barang,
        total_stok=total_stok,
        jumlah_kategori=jumlah_kategori,
        low_stock_items=low_stock_items,
        recent_histories=recent_histories
    )

import logging
from flask import Blueprint, render_template
from app.extensions import db
from app.domain.models.barang import Barang
from app.domain.models.kategori import Kategori

logger = logging.getLogger(__name__)

analytics_bp = Blueprint('analytics', __name__, url_prefix='/analytics')

@analytics_bp.route('/', methods=['GET'])
def index():
    """Renders the Analytics Dashboard with Chart.js charts."""
    try:
        # 1. Pie Chart: Count of items per category
        pie_results = db.session.query(
            Kategori.nama,
            db.func.count(Barang.id)
        ).outerjoin(Barang).group_by(Kategori.id, Kategori.nama).order_by(Kategori.nama.asc()).all()

        pie_labels = [row[0] for row in pie_results]
        pie_data = [row[1] for row in pie_results]

        # 2. Bar Chart: Total stock quantity per category
        bar_results = db.session.query(
            Kategori.nama,
            db.func.coalesce(db.func.sum(Barang.stok), 0)
        ).outerjoin(Barang).group_by(Kategori.id, Kategori.nama).order_by(Kategori.nama.asc()).all()

        bar_labels = [row[0] for row in bar_results]
        bar_data = [int(row[1]) for row in bar_results]

        # 3. Card Low Stock (stok <= 5)
        low_stock_count = Barang.query.filter(Barang.stok <= 5).count()
        low_stock_items = Barang.query.filter(Barang.stok <= 5).order_by(Barang.stok.asc()).all()

    except Exception as e:
        logger.error(f"Error querying analytics data: {e}")
        pie_labels, pie_data = [], []
        bar_labels, bar_data = [], []
        low_stock_count = 0
        low_stock_items = []

    return render_template(
        'analytics/index.html',
        pie_labels=pie_labels,
        pie_data=pie_data,
        bar_labels=bar_labels,
        bar_data=bar_data,
        low_stock_count=low_stock_count,
        low_stock_items=low_stock_items
    )

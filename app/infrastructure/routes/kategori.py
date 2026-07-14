import logging
from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.extensions import db
from app.domain.models.kategori import Kategori

logger = logging.getLogger(__name__)

kategori_bp = Blueprint('kategori', __name__, url_prefix='/kategori')

@kategori_bp.route('/', methods=['GET'])
def index():
    """List all categories with optional search query."""
    search_query = request.args.get('search', '').strip()
    if search_query:
        # Perform case-insensitive search matching Category name
        categories = Kategori.query.filter(Kategori.nama.ilike(f'%{search_query}%')).order_by(Kategori.nama.asc()).all()
    else:
        categories = Kategori.query.order_by(Kategori.nama.asc()).all()
        
    return render_template('kategori/index.html', categories=categories, search_query=search_query)

@kategori_bp.route('/create', methods=['POST'])
def create():
    """Creates a new category with validation."""
    nama = request.form.get('nama', '').strip()

    # Validation: Empty Name
    if not nama:
        flash('Nama kategori tidak boleh kosong!', 'danger')
        return redirect(url_for('kategori.index'))

    # Validation: Duplicate Name
    existing = Kategori.query.filter(Kategori.nama.ilike(nama)).first()
    if existing:
        flash(f"Kategori '{nama}' sudah terdaftar!", 'danger')
        return redirect(url_for('kategori.index'))

    try:
        new_category = Kategori(nama=nama)
        db.session.add(new_category)
        db.session.commit()
        flash(f"Kategori '{nama}' berhasil ditambahkan.", 'success')
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error creating category: {e}")
        flash('Terjadi kesalahan pada sistem saat menyimpan kategori.', 'danger')

    return redirect(url_for('kategori.index'))

@kategori_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
def edit(id):
    """Edits an existing category with validation."""
    category = Kategori.query.get_or_404(id)

    if request.method == 'POST':
        nama = request.form.get('nama', '').strip()

        # Validation: Empty Name
        if not nama:
            flash('Nama kategori tidak boleh kosong!', 'danger')
            return redirect(url_for('kategori.edit', id=id))

        # Validation: Duplicate Name (excluding self)
        existing = Kategori.query.filter(Kategori.nama.ilike(nama), Kategori.id != id).first()
        if existing:
            flash(f"Kategori '{nama}' sudah terdaftar!", 'danger')
            return redirect(url_for('kategori.edit', id=id))

        try:
            category.nama = nama
            db.session.commit()
            flash(f"Kategori berhasil diubah menjadi '{nama}'.", 'success')
            return redirect(url_for('kategori.index'))
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error updating category: {e}")
            flash('Terjadi kesalahan pada sistem saat memperbarui kategori.', 'danger')

    return render_template('kategori/edit.html', category=category)

@kategori_bp.route('/<int:id>/delete', methods=['POST'])
def delete(id):
    """Deletes a category after ensuring it has no associated items."""
    category = Kategori.query.get_or_404(id)

    # Database Integrity Constraint validation
    if category.barang_list:
        flash(f"Kategori '{category.nama}' tidak bisa dihapus karena terdapat {len(category.barang_list)} barang terkait!", 'danger')
        return redirect(url_for('kategori.index'))

    try:
        db.session.delete(category)
        db.session.commit()
        flash(f"Kategori '{category.nama}' berhasil dihapus.", 'success')
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error deleting category: {e}")
        flash('Terjadi kesalahan pada sistem saat menghapus kategori.', 'danger')

    return redirect(url_for('kategori.index'))

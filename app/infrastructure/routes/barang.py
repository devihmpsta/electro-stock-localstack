import os
import logging
from flask import Blueprint, render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename
from app.extensions import db
from app.domain.models.barang import Barang
from app.domain.models.kategori import Kategori
from app.domain.models.stock_history import StockHistory
from app.application.services.storage import StorageService

logger = logging.getLogger(__name__)

barang_bp = Blueprint('barang', __name__, url_prefix='/barang')

# Ensure local uploads directory exists
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_file(filename: str) -> bool:
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@barang_bp.route('/', methods=['GET'])
def index():
    """List all items with search, category filtering, and pagination."""
    search_query = request.args.get('search', '').strip()
    category_id = request.args.get('category_id', type=int)
    page = request.args.get('page', 1, type=int)
    per_page = 5  # Set small page size to showcase pagination

    query = Barang.query

    # Search filter (matches name, code, or brand)
    if search_query:
        query = query.filter(
            db.or_(
                Barang.nama_barang.ilike(f'%{search_query}%'),
                Barang.kode_barang.ilike(f'%{search_query}%'),
                Barang.merk.ilike(f'%{search_query}%')
            )
        )

    # Category filter
    if category_id:
        query = query.filter(Barang.kategori_id == category_id)

    # Order by newest items and paginate
    pagination = query.order_by(Barang.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)
    items = pagination.items

    categories = Kategori.query.order_by(Kategori.nama.asc()).all()

    return render_template(
        'barang/index.html',
        items=items,
        pagination=pagination,
        categories=categories,
        search_query=search_query,
        selected_category=category_id
    )

@barang_bp.route('/create', methods=['GET', 'POST'])
def create():
    """Create a new item with validation and optional local image upload."""
    categories = Kategori.query.order_by(Kategori.nama.asc()).all()

    if request.method == 'POST':
        kode_barang = request.form.get('kode_barang', '').strip()
        nama_barang = request.form.get('nama_barang', '').strip()
        kategori_id = request.form.get('kategori_id', type=int)
        merk = request.form.get('merk', '').strip()
        harga = request.form.get('harga', 0.0, type=float)
        stok = request.form.get('stok', 0, type=int)
        lokasi_rak = request.form.get('lokasi_rak', '').strip()

        # Validation: Kode Barang duplication
        existing = Barang.query.filter_by(kode_barang=kode_barang).first()
        if existing:
            flash(f"Kode barang '{kode_barang}' sudah terdaftar!", 'danger')
            return render_template('barang/form.html', categories=categories, item=None)

        # Handle Photo Upload (Amazon S3 via LocalStack)
        foto_filename = None
        if 'foto' in request.files:
            file = request.files['foto']
            if file and file.filename:
                filename = file.filename
                if allowed_file(filename):
                    ext = filename.rsplit('.', 1)[1].lower()
                    # Safe unique filename based on code
                    safe_code = secure_filename(kode_barang)
                    foto_filename = f"{safe_code}_{os.urandom(4).hex()}.{ext}"
                    
                    # Upload to S3
                    storage = StorageService()
                    storage.upload_file(file, foto_filename)
                else:
                    flash('Format file foto tidak valid! Gunakan png, jpg, jpeg, gif, atau webp.', 'danger')
                    return render_template('barang/form.html', categories=categories, item=None)

        try:
            new_item = Barang(
                kode_barang=kode_barang,
                nama_barang=nama_barang,
                kategori_id=kategori_id,
                merk=merk,
                harga=harga,
                stok=stok,
                lokasi_rak=lokasi_rak,
                foto_s3_key=foto_filename
            )
            db.session.add(new_item)
            db.session.commit()

            # Record initial stock in history if stock > 0
            if stok > 0:
                history = StockHistory(
                    barang_id=new_item.id,
                    jenis_transaksi='masuk',
                    jumlah=stok,
                    keterangan='Input stok awal registrasi barang'
                )
                db.session.add(history)
                db.session.commit()

            flash(f"Barang '{nama_barang}' berhasil ditambahkan.", 'success')
            return redirect(url_for('barang.index'))
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error creating item: {e}")
            flash('Terjadi kesalahan pada sistem saat menyimpan barang.', 'danger')

    return render_template('barang/form.html', categories=categories, item=None)

@barang_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
def edit(id):
    """Edit an existing item with validation, optional stock correction and file upload."""
    item = Barang.query.get_or_404(id)
    categories = Kategori.query.order_by(Kategori.nama.asc()).all()

    if request.method == 'POST':
        kode_barang = request.form.get('kode_barang', '').strip()
        nama_barang = request.form.get('nama_barang', '').strip()
        kategori_id = request.form.get('kategori_id', type=int)
        merk = request.form.get('merk', '').strip()
        harga = request.form.get('harga', 0.0, type=float)
        stok = request.form.get('stok', 0, type=int)
        lokasi_rak = request.form.get('lokasi_rak', '').strip()

        # Validation: Kode Barang duplication (excluding itself)
        existing = Barang.query.filter(Barang.kode_barang == kode_barang, Barang.id != id).first()
        if existing:
            flash(f"Kode barang '{kode_barang}' sudah terdaftar pada barang lain!", 'danger')
            return render_template('barang/form.html', categories=categories, item=item)

        # Handle Photo Upload (Amazon S3 via LocalStack)
        foto_filename = item.foto_s3_key
        if 'foto' in request.files:
            file = request.files['foto']
            if file and file.filename:
                filename = file.filename
                if allowed_file(filename):
                    ext = filename.rsplit('.', 1)[1].lower()
                    safe_code = secure_filename(kode_barang)
                    foto_filename = f"{safe_code}_{os.urandom(4).hex()}.{ext}"
                    
                    # Upload new photo to S3
                    storage = StorageService()
                    storage.upload_file(file, foto_filename)
                    
                    # Delete old photo from S3
                    if item.foto_s3_key:
                        storage.delete_file(item.foto_s3_key)
                else:
                    flash('Format file foto tidak valid! Gunakan png, jpg, jpeg, gif, atau webp.', 'danger')
                    return render_template('barang/form.html', categories=categories, item=item)

        try:
            # Track stock changes for stock movement history
            old_stok = item.stok
            diff = stok - old_stok
            
            item.kode_barang = kode_barang
            item.nama_barang = nama_barang
            item.kategori_id = kategori_id
            item.merk = merk
            item.harga = harga
            item.stok = stok
            item.lokasi_rak = lokasi_rak
            item.foto_s3_key = foto_filename

            db.session.commit()

            # Record stock difference if any
            if diff != 0:
                jenis = 'masuk' if diff > 0 else 'keluar'
                history = StockHistory(
                    barang_id=item.id,
                    jenis_transaksi=jenis,
                    jumlah=abs(diff),
                    keterangan=f"Koreksi stok (Perubahan manual dari {old_stok} ke {stok})"
                )
                db.session.add(history)
                db.session.commit()

            flash(f"Barang '{nama_barang}' berhasil diperbarui.", 'success')
            return redirect(url_for('barang.index'))
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error updating item: {e}")
            flash('Terjadi kesalahan pada sistem saat memperbarui barang.', 'danger')

    return render_template('barang/form.html', categories=categories, item=item)

@barang_bp.route('/<int:id>/delete', methods=['POST'])
def delete(id):
    """Delete an item and its associated local file and history."""
    item = Barang.query.get_or_404(id)

    try:
        # Delete associated stock history records first
        StockHistory.query.filter_by(barang_id=item.id).delete()

        # Delete photo from S3 if exists
        if item.foto_s3_key:
            storage = StorageService()
            storage.delete_file(item.foto_s3_key)

        db.session.delete(item)
        db.session.commit()
        flash(f"Barang '{item.nama_barang}' berhasil dihapus.", 'success')
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error deleting item: {e}")
        flash('Terjadi kesalahan pada sistem saat menghapus barang.', 'danger')

    return redirect(url_for('barang.index'))


@barang_bp.route('/<int:id>/stok', methods=['GET', 'POST'])
def adjust_stock(id):
    """Adjust item stock level (incoming/outgoing) and log transaction details to StockHistory."""
    item = Barang.query.get_or_404(id)

    if request.method == 'POST':
        jenis_transaksi = request.form.get('jenis_transaksi')
        jumlah = request.form.get('jumlah', 0, type=int)
        keterangan = request.form.get('keterangan', '').strip()

        # Validation: Positive amount check
        if jumlah <= 0:
            flash('Jumlah transaksi penyesuaian harus bernilai lebih dari 0!', 'danger')
            return redirect(url_for('barang.adjust_stock', id=id))

        if jenis_transaksi not in ['masuk', 'keluar']:
            flash('Jenis transaksi penyesuaian tidak valid!', 'danger')
            return redirect(url_for('barang.adjust_stock', id=id))

        # Perform stock logic with negative check
        if jenis_transaksi == 'masuk':
            item.stok += jumlah
        elif jenis_transaksi == 'keluar':
            if item.stok - jumlah < 0:
                flash(f"Stok tidak mencukupi! Pengurangan stok sebesar {jumlah} akan membuat stok menjadi negatif ({item.stok - jumlah}).", 'danger')
                return redirect(url_for('barang.adjust_stock', id=id))
            item.stok -= jumlah

        try:
            # Commit updated stock level
            db.session.commit()

            # Record change to history
            history = StockHistory(
                barang_id=item.id,
                jenis_transaksi=jenis_transaksi,
                jumlah=jumlah,
                keterangan=keterangan
            )
            db.session.add(history)
            db.session.commit()

            flash(f"Stok barang '{item.nama_barang}' berhasil disesuaikan ({jenis_transaksi} {jumlah}).", 'success')
            return redirect(url_for('barang.index'))
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error adjusting stock of item {id}: {e}")
            flash('Terjadi kesalahan pada sistem saat memproses perubahan stok.', 'danger')

    return render_template('barang/adjust_stock.html', item=item)

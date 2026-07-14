import logging
from flask import Blueprint, render_template, redirect, url_for, request, session, flash
from app.extensions import db
from app.domain.models.user import User

logger = logging.getLogger(__name__)

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Handles user login."""
    if 'user_id' in session:
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if not username or not password:
            flash('Username dan password wajib diisi!', 'danger')
            return render_template('login.html')

        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            session['user_id'] = user.id
            session['username'] = user.username
            session['role'] = user.role
            logger.info(f"User '{username}' successfully logged in.")
            return redirect(url_for('main.index'))
        else:
            flash('Username atau password salah!', 'danger')

    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    """Handles user logout."""
    username = session.get('username')
    session.pop('user_id', None)
    session.pop('username', None)
    session.pop('role', None)
    logger.info(f"User '{username}' logged out.")
    return redirect(url_for('auth.login'))

def seed_default_user():
    """Seeds a default admin user if the user table is empty."""
    try:
        # Check if table user is empty
        if User.query.count() == 0:
            logger.info("No users found in database. Seeding default 'admin' user...")
            admin = User(username='admin', role='admin')
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            logger.info("Default 'admin' user seeded with password 'admin123'.")
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error seeding default user: {e}")

def seed_dummy_data():
    """Seeds sample categories, items, and stock history if they do not exist."""
    from app.domain.models.kategori import Kategori
    from app.domain.models.barang import Barang
    from app.domain.models.stock_history import StockHistory
    from datetime import datetime, timedelta, timezone

    try:
        if Kategori.query.count() == 0:
            logger.info("No categories found. Seeding dummy categories...")
            categories = [
                Kategori(nama="Laptop & PC"),
                Kategori(nama="Smartphone & Tablet"),
                Kategori(nama="Audio & Wearables"),
                Kategori(nama="Aksesoris & Storage"),
                Kategori(nama="Peralatan Rumah Tangga")
            ]
            for cat in categories:
                db.session.add(cat)
            db.session.commit()
            logger.info("Dummy categories seeded.")

        if Barang.query.count() == 0:
            logger.info("No items found. Seeding dummy items...")
            categories = Kategori.query.all()
            cat_map = {cat.nama: cat.id for cat in categories}

            items = [
                Barang(kode_barang="LP-ASUS-01", nama_barang="Asus ROG Zephyrus G14", kategori_id=cat_map["Laptop & PC"], merk="Asus", harga=24500000.00, stok=12, lokasi_rak="A-01"),
                Barang(kode_barang="LP-MAC-02", nama_barang="MacBook Air M3 13-inch", kategori_id=cat_map["Laptop & PC"], merk="Apple", harga=18999000.00, stok=8, lokasi_rak="A-02"),
                Barang(kode_barang="SP-IPH-01", nama_barang="iPhone 15 Pro Max 256GB", kategori_id=cat_map["Smartphone & Tablet"], merk="Apple", harga=22999000.00, stok=4, lokasi_rak="B-01"),
                Barang(kode_barang="SP-SAM-02", nama_barang="Samsung Galaxy S24 Ultra", kategori_id=cat_map["Smartphone & Tablet"], merk="Samsung", harga=21499000.00, stok=2, lokasi_rak="B-02"),
                Barang(kode_barang="AU-SONY-01", nama_barang="Sony WH-1000XM5 Headphone", kategori_id=cat_map["Audio & Wearables"], merk="Sony", harga=4599000.00, stok=15, lokasi_rak="C-01"),
                Barang(kode_barang="AU-APP-02", nama_barang="Apple AirPods Pro Gen 2", kategori_id=cat_map["Audio & Wearables"], merk="Apple", harga=3899000.00, stok=3, lokasi_rak="C-02"),
                Barang(kode_barang="ST-SND-01", nama_barang="SanDisk Extreme Portable SSD 1TB", kategori_id=cat_map["Aksesoris & Storage"], merk="SanDisk", harga=1750000.00, stok=25, lokasi_rak="D-01"),
                Barang(kode_barang="ST-WD-02", nama_barang="WD My Passport 2TB", kategori_id=cat_map["Aksesoris & Storage"], merk="Western Digital", harga=1250000.00, stok=1, lokasi_rak="D-02")
            ]
            for item in items:
                db.session.add(item)
            db.session.commit()
            logger.info("Dummy items seeded.")

        if StockHistory.query.count() == 0:
            logger.info("No stock histories found. Seeding dummy stock history...")
            items = Barang.query.all()
            for idx, item in enumerate(items):
                # Initial entry
                h1 = StockHistory(
                    barang_id=item.id,
                    jenis_transaksi="masuk",
                    jumlah=item.stok + (2 if idx % 2 == 0 else 0),
                    keterangan="Stok awal inventaris",
                    created_at=datetime.now(timezone.utc) - timedelta(days=5)
                )
                db.session.add(h1)
                
                # Transaction entry
                if idx % 2 == 0:
                    h2 = StockHistory(
                        barang_id=item.id,
                        jenis_transaksi="keluar",
                        jumlah=2,
                        keterangan="Penjualan toko online",
                        created_at=datetime.now(timezone.utc) - timedelta(days=2)
                    )
                    db.session.add(h2)
            db.session.commit()
            logger.info("Dummy stock histories seeded.")
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error seeding dummy data: {e}")

from app.extensions import db
from datetime import datetime, timezone


class Barang(db.Model):
    """Barang (item) dalam inventaris ElectroStock."""

    __tablename__ = 'barang'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    kode_barang = db.Column(db.String(50), nullable=False, unique=True, index=True)
    nama_barang = db.Column(db.String(200), nullable=False)
    kategori_id = db.Column(
        db.Integer, db.ForeignKey('kategori.id'), nullable=False, index=True
    )
    merk = db.Column(db.String(100), nullable=True)
    harga = db.Column(db.Numeric(precision=15, scale=2), nullable=False, default=0)
    stok = db.Column(db.Integer, nullable=False, default=0)
    lokasi_rak = db.Column(db.String(50), nullable=True)
    foto_s3_key = db.Column(db.String(500), nullable=True)
    created_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    kategori = db.relationship('Kategori', back_populates='barang_list')
    stock_histories = db.relationship(
        'StockHistory', back_populates='barang', lazy='select'
    )

    def __init__(
        self,
        kode_barang: str,
        nama_barang: str,
        kategori_id: int | None,
        merk: str | None = None,
        harga: float = 0.0,
        stok: int = 0,
        lokasi_rak: str | None = None,
        foto_s3_key: str | None = None,
        **kwargs
    ):
        super().__init__(**kwargs)
        setattr(self, 'kode_barang', kode_barang)
        setattr(self, 'nama_barang', nama_barang)
        setattr(self, 'kategori_id', kategori_id)
        setattr(self, 'merk', merk)
        setattr(self, 'harga', harga)
        setattr(self, 'stok', stok)
        setattr(self, 'lokasi_rak', lokasi_rak)
        setattr(self, 'foto_s3_key', foto_s3_key)



    def __repr__(self) -> str:
        return f'<Barang {self.kode_barang} – {self.nama_barang}>'


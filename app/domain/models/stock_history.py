from app.extensions import db
from datetime import datetime, timezone


class StockHistory(db.Model):
    """Riwayat pergerakan stok barang."""

    __tablename__ = 'stock_history'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    barang_id = db.Column(
        db.Integer, db.ForeignKey('barang.id'), nullable=False, index=True
    )
    jenis_transaksi = db.Column(
        db.String(20), nullable=False
    )  # e.g. 'masuk', 'keluar', 'koreksi'
    jumlah = db.Column(db.Integer, nullable=False)
    keterangan = db.Column(db.Text, nullable=True)
    created_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    barang = db.relationship('Barang', back_populates='stock_histories')

    def __init__(
        self,
        barang_id: int,
        jenis_transaksi: str,
        jumlah: int,
        keterangan: str | None = None,
        created_at: datetime | None = None,
        **kwargs
    ):
        super().__init__(**kwargs)
        setattr(self, 'barang_id', barang_id)
        setattr(self, 'jenis_transaksi', jenis_transaksi)
        setattr(self, 'jumlah', jumlah)
        setattr(self, 'keterangan', keterangan)
        setattr(self, 'created_at', created_at)



    def __repr__(self) -> str:
        return f'<StockHistory barang_id={self.barang_id} {self.jenis_transaksi} {self.jumlah}>'


from app.extensions import db
from datetime import datetime, timezone


class Kategori(db.Model):
    """Kategori barang elektronik."""

    __tablename__ = 'kategori'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nama = db.Column(db.String(100), nullable=False, unique=True)
    created_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    barang_list = db.relationship(
        'Barang', back_populates='kategori', lazy='select'
    )

    def __init__(self, nama: str, **kwargs):
        super().__init__(**kwargs)
        setattr(self, 'nama', nama)



    def __repr__(self) -> str:
        return f'<Kategori {self.nama}>'


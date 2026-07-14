from app.extensions import db
from datetime import datetime, timezone
from werkzeug.security import generate_password_hash, check_password_hash


class User(db.Model):
    """User aplikasi ElectroStock."""

    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(80), nullable=False, unique=True, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(
        db.String(20), nullable=False, default='staff'
    )  # e.g. 'admin', 'staff'
    created_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    def __init__(self, username: str, role: str = 'staff', password_hash: str | None = None, **kwargs):
        super().__init__(**kwargs)
        setattr(self, 'username', username)
        setattr(self, 'role', role)
        setattr(self, 'password_hash', password_hash)



    def set_password(self, password: str) -> None:
        """Hash and set the user's password."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        """Check the password against the stored hash."""
        return check_password_hash(self.password_hash, password)

    def __repr__(self) -> str:
        return f'<User {self.username} ({self.role})>'


# user_model.py

import hashlib
import secrets
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    salt = db.Column(db.String(32), nullable=False)  # 16-byte salt in hex
    password_hash = db.Column(db.String(64), nullable=False)  # SHA-256 hash in hex

    def __repr__(self):
        return f'<User {self.username}>'

    @staticmethod
    def _hash_password(password: str, salt: str) -> str:
        """Hashes a password with the given salt using SHA-256."""
        salt_bytes = bytes.fromhex(salt)
        hash_obj = hashlib.sha256()
        hash_obj.update(salt_bytes)
        hash_obj.update(password.encode('utf-8'))
        return hash_obj.hexdigest()

    def set_password(self, password: str):
        """Hashes and sets the user's password."""
        self.salt = secrets.token_hex(16)  # Generate a random 16-byte salt
        self.password_hash = self._hash_password(password, self.salt)

    def check_password(self, password: str) -> bool:
        """Checks the provided password against the stored hash."""
        return self._hash_password(password, self.salt) == self.password_hash

    @classmethod
    def delete_user(cls, username: str) -> None:
        """Delete a user by username."""
        user = cls.query.filter_by(username=username).first()
        if user:
            db.session.delete(user)
            db.session.commit()

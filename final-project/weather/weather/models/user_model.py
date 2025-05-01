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
        """Return a string representation of the User instance.
        Returns:
            str: A string in the format '<User username>'."""
        return f'<User {self.username}>'

    @staticmethod
    def _hash_password(password: str, salt: str) -> str:
        """
        Hash a password using SHA-256 with the provided salt.
        Args:
            password (str): The plaintext password to hash.
            salt (str): A hex-encoded salt string.
        Returns:
            str: A SHA-256 hash of the salted password in hexadecimal format.
        """
        salt_bytes = bytes.fromhex(salt)
        hash_obj = hashlib.sha256()
        hash_obj.update(salt_bytes)
        hash_obj.update(password.encode('utf-8'))
        return hash_obj.hexdigest()

    def set_password(self, password: str):
        """
        Generate a new salt and hash the given password, storing both.
        Args:
            password (str): The plaintext password to set for the user.
        """
        self.salt = secrets.token_hex(16)  # Generate a random 16-byte salt
        self.password_hash = self._hash_password(password, self.salt)

    def check_password(self, password: str) -> bool:
        """
        Verify that the provided password matches the stored hash.
        Args:
            password (str): The plaintext password to verify.
        Returns:
            bool: True if the password is correct, False otherwise.
        """
        return self._hash_password(password, self.salt) == self.password_hash

    @classmethod
    def delete_user(cls, username: str) -> None:
        """
        Delete a user from the database by their username.
        Args:
            username (str): The username of the user to delete.
        """
        user = cls.query.filter_by(username=username).first()
        if user:
            db.session.delete(user)
            db.session.commit()

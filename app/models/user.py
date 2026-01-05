import bcrypt
import jwt
from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import Optional


@dataclass
class User:
    username: str
    password_hash: bytes

    def verify_password(self, password: str) -> bool:
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash)

    def generate_jwt(self, secret: str, expiration_minutes: int) -> str:
        payload = {
            'sub': self.username,
            'iat': datetime.utcnow(),
            'exp': datetime.utcnow() + timedelta(minutes=expiration_minutes),
        }
        return jwt.encode(payload, secret, algorithm='HS256')


# demo single user
_password = b'admin'
ADMIN_USER = User(
    username='admin',
    password_hash=bcrypt.hashpw(_password, bcrypt.gensalt()),
)


def authenticate(username: str, password: str) -> Optional[User]:
    if username == ADMIN_USER.username and ADMIN_USER.verify_password(password):
        return ADMIN_USER
    return None

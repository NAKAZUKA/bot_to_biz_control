from sqlalchemy.orm import Session
from models import User, SessionLocal


class Database:
    def __init__(self):
        self.db = SessionLocal()

    def add_user(self, telegram_id: int, username: str, first_name: str, last_name: str, email: str):
        user = self.db.query(User).filter(User.telegram_id == telegram_id).first()
        if not user:
            user = User(
                telegram_id=telegram_id,
                username=username,
                first_name=first_name,
                last_name=last_name,
                email=email
            )
            self.db.add(user)
            self.db.commit()

    def add_token(self, telegram_id: int, token: str):
        user = self.db.query(User).filter(User.telegram_id == telegram_id).first()
        if user:
            user.access_token = token
            self.db.commit()

    def get_token(self, telegram_id: int) -> str:
        user = self.db.query(User).filter(User.telegram_id == telegram_id).first()
        if user:
            return user.access_token
        return None

    def close(self):
        self.db.close()

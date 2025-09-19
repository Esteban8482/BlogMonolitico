from db_connector import db, User
from typing import Optional, List


def get_user_or_404(user_id: int) -> Optional[User]:
    return User.query.get_or_404(user_id)


def update_user_bio(user: User, bio: str) -> None:
    user.bio = bio
    db.session.commit()


def is_user_owner(user: User, current) -> bool:
    return current and current.id == user.id

import json
import os

USERS_FILE = "users.json"


def _load_users() -> list:
    if not os.path.exists(USERS_FILE):
        return []
    try:
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return []


def _save_users(users: list) -> None:
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, ensure_ascii=False, indent=2)


def check_users() -> None:
    users = _load_users()


def get_users_count() -> int:
    return len(_load_users())


def add_user_db(user_id: int | None, username: str | None) -> None:
    if not username:
        return
    users = _load_users()
    for user in users:
        if user.get("user_id") == user_id:
            if username:
                user["username"] = username
                _save_users(users)
            return
    users.append(
        {
            "user_id": user_id,
            "username": username,
            "answers": {},
            "completed": False,
        }
    )
    _save_users(users)


def update_user_answer(user_id: int | None, username: str | None, field: str, value: str) -> None:
    users = _load_users()
    for user in users:
        if user.get("user_id") == user_id:
            answers = user.setdefault("answers", {})
            answers[field] = value
            if username:
                user["username"] = username
            _save_users(users)
            return

    if not username:
        return

    users.append(
        {
            "user_id": user_id,
            "username": username,
            "answers": {field: value},
            "completed": False,
        }
    )
    _save_users(users)


def is_user_completed(user_id: int | None) -> bool:
    if user_id is None:
        return False
    users = _load_users()
    for user in users:
        if user.get("user_id") == user_id:
            answers = user.get("answers", {})
            required_fields = ("age", "income", "occupation", "motivation")
            return all(field in answers for field in required_fields) or user.get("completed") is True
    return False


def mark_user_completed(user_id: int | None, username: str | None) -> None:
    if user_id is None:
        return
    users = _load_users()
    for user in users:
        if user.get("user_id") == user_id:
            if username:
                user["username"] = username
            user["completed"] = True
            _save_users(users)
            return
    users.append(
        {
            "user_id": user_id,
            "username": username,
            "answers": {},
            "completed": True,
        }
    )
    _save_users(users)
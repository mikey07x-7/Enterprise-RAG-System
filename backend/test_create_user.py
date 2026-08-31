from passlib.context import CryptContext

from database.database import SessionLocal
from models.user import User


pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
)


USERNAME = "devuser"
EMAIL = "devuser@localhost"
PASSWORD = "DevPassword123!"


def main():

    db = SessionLocal()

    try:
        # Check whether the user already exists
        existing_user = (
            db.query(User)
            .filter(
                (User.username == USERNAME)
                | (User.email == EMAIL)
            )
            .first()
        )

        if existing_user:
            print("User already exists.")
            print(f"ID       : {existing_user.id}")
            print(f"Username : {existing_user.username}")
            print(f"Email    : {existing_user.email}")
            return

        # Hash password
        hashed_password = pwd_context.hash(PASSWORD)

        # Create user
        user = User(
            username=USERNAME,
            email=EMAIL,
            hashed_password=hashed_password,
            is_active=True,
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        print("=" * 50)
        print("DEVELOPMENT USER CREATED")
        print("=" * 50)
        print(f"ID       : {user.id}")
        print(f"Username : {user.username}")
        print(f"Email    : {user.email}")
        print(f"Password : {PASSWORD}")
        print("=" * 50)

    except Exception as exc:

        db.rollback()

        print("ERROR:")
        print(exc)

    finally:
        db.close()


if __name__ == "__main__":
    main()
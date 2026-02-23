import datetime
import hashlib
import os
import sys

from pymongo import MongoClient


def add_admin(username, password, email):
    """
    Adds a new admin user to the database.
    """
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        print("Error: DATABASE_URL environment variable not set.")
        sys.exit(1)

    try:
        client = MongoClient(database_url)
        db = client["message"]

        if db.mb_user.find_one({"uname": username}):
            print(f"Error: User '{username}' already exists.")
            sys.exit(1)

        if db.mb_user.find_one({"email": email}):
            print(f"Error: Email '{email}' already exists.")
            sys.exit(1)

        db.mb_user.insert_one(
            {
                "uname": username,
                "upass": hashlib.sha256(password.encode()).hexdigest(),
                "email": email,
                "reg_time": datetime.datetime.now(),
                "last_login_time": datetime.datetime.now(),
                "priv": 3,  # 3: super admin (hide&mark)
                "state": 1,  # 1: normal
            }
        )
        print(f"Admin user '{username}' created successfully.")
    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python add_admin.py <username> <password> <email>")
        sys.exit(1)

    add_admin(sys.argv[1], sys.argv[2], sys.argv[3])

"""Create the initial local admin account interactively (never commit credentials)."""
from getpass import getpass
from modules.auth import create_user, DEFAULT_USERS_FILE


def main():
    print("Bootstrap local analyst administrator")
    username = input("Admin username: ").strip()
    password = getpass("Password (12+ characters): ")
    confirm = getpass("Confirm password: ")
    if password != confirm:
        raise SystemExit("Passwords do not match.")
    create_user(username, password, "admin")
    print(f"Admin account created in {DEFAULT_USERS_FILE}")


if __name__ == "__main__":
    main()

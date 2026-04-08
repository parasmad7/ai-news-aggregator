from app.runner import run_all
from app.database.create_tables import init_db

def main():
    init_db()
    run_all()

if __name__ == "__main__":
    main()

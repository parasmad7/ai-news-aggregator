from app.runner import run_all
from app.database.create_tables import create_tables

def main():
    create_tables()
    run_all()

if __name__ == "__main__":
    main()

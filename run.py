from app import create_app, db

app = create_app()

@app.cli.command()
def create_tables():
    """Create database tables."""
    db.create_all()
    print("Database tables created.")

if __name__ == "__main__":
    app.run(debug=True)
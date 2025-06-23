from app import create_app, db

app = create_app()

@app.cli.command()
def create_tables():
    """Create database tables."""
    db.create_all()
    print("Database tables created.")

if __name__ == "__main__":
    import os
    port = int(os.environ.get('PORT', 5001))
    # Use different settings for production vs development
    if os.environ.get('HEROKU'):
        app.run(host='0.0.0.0', port=port, debug=False)
    else:
        app.run(host='127.0.0.1', port=port, debug=True)
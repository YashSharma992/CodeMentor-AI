"""Development entry point for CodeMentor AI."""
from codementor import create_app

app = create_app()

if __name__ == "__main__":
    app.run()

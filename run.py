"""
Entry point for the FitWell agent server.
Run with:  python run.py
"""

from dotenv import load_dotenv
load_dotenv()

from app import create_app

app = create_app()

import os

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5001))
    print(f"Starting FitWell server on http://localhost:{port}")
    app.run(debug=True, port=port)

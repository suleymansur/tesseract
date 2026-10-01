"""
run.py
------
Uygulamanin giris noktasi. Fabrikadan uygulamayi alir ve calistirir.

Yerel gelistirme:   python run.py
Uretim (Render):     gunicorn run:app
"""

from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

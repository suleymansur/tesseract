"""
app/__init__.py
----------------
MODUL E - Uygulama fabrikasi (application factory).

Ayarlari, CORS'u, veritabanini ve rotalari bir araya getiren
create_app() fonksiyonu burada tanimlanir.
"""

from flask import Flask, jsonify
from flask_cors import CORS

from config import get_config
from app.database import init_db
from app.routes import pages_bp, api_bp


def create_app():
    """
    Tesseract AI Flask uygulamasini olusturup dondurur.

    Sira onemlidir:
        1) ayarlari yukle
        2) CORS'u ac
        3) veritabanini hazirla (init_db)
        4) blueprint'leri kaydet
        5) uygulamayi dondur
    """
    app = Flask(__name__)

    # 1) Ayarlari yukle
    app.config.from_object(get_config())

    # 2) CORS ac (Wix sitesinden gelen isteklere izin vermek icin)
    origins = app.config.get("CORS_ORIGINS", "*")
    if origins != "*":
        origins = [o.strip() for o in origins.split(",")]
    CORS(app, resources={r"/api/*": {"origins": origins}})

    # 3) Veritabanini hazirla ('leads' tablosu yoksa olusturur)
    init_db(app)

    # 4) Blueprint'leri kaydet
    app.register_blueprint(pages_bp)
    app.register_blueprint(api_bp, url_prefix="/api")

    # Sunucunun canli olup olmadigini kontrol etmek icin basit bir uc nokta
    @app.route("/health")
    def health():
        return jsonify({"durum": "aktif", "servis": "Tesseract AI"}), 200

    return app

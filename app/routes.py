"""
routes.py
---------
MODUL D - HTTP rotalari (kontrolcu / controller).

Bu dosyada SQL veya AI kodu OLMAYACAK. Sadece gelen istegi
karsilar, basit dogrulama yapar ve dogru katmanin (database
veya ai_service) fonksiyonunu cagirir.

Iki Blueprint kullanilir:
    pages_bp -> tarayicida gorunen sayfalar (/, /dashboard)
    api_bp   -> JSON doenen API uc noktalari (/api/...)
"""

from flask import Blueprint, jsonify, render_template, request

from app.database import lead_ekle, tum_leadler
from app.services.ai_service import ai_service, AIServiceError

pages_bp = Blueprint("pages", __name__)
api_bp = Blueprint("api", __name__)


# ---------------------------------------------------------------------
# SAYFALAR
# ---------------------------------------------------------------------

@pages_bp.route("/")
def index():
    """Ziyaretcilerin gordugu karsilama / sohbet sayfasi."""
    return render_template("index.html")


@pages_bp.route("/dashboard")
def dashboard():
    """Isletme sahibinin lead kayitlarini gordugu yonetim paneli."""
    return render_template("dashboard.html")


# ---------------------------------------------------------------------
# API UC NOKTALARI
# ---------------------------------------------------------------------

@api_bp.route("/sohbet", methods=["POST"])
def sohbet():
    """
    Ziyaretcinin mesajini alir, yapay zeka servisinden yanit uretir.

    Beklenen govde (JSON): { "mesaj": "...", "gecmis": [...] (opsiyonel) }
    Basarili yanit (200): { "basari": true, "cevap": "..." }
    Hata (400): eksik veri | Hata (503): AI servisi cevap veremedi
    """
    data = request.get_json(silent=True) or {}
    mesaj = (data.get("mesaj") or "").strip()
    gecmis = data.get("gecmis", [])

    if not mesaj:
        return jsonify({"basari": False, "hata": "Mesaj alani zorunludur."}), 400

    try:
        cevap = ai_service.yanit_uret(mesaj, gecmis)
    except AIServiceError as e:
        return jsonify({
            "basari": False,
            "hata": "Yapay zeka servisine su anda ulasilamiyor.",
            "detay": str(e),
        }), 503

    return jsonify({"basari": True, "cevap": cevap}), 200


@api_bp.route("/leads", methods=["POST"])
def lead_olustur():
    """
    Yeni bir musteri adayi (lead) kaydeder.

    Beklenen govde (JSON):
        { "isim": "...", "telefon": "...", "mesaj": "..." (opsiyonel),
          "kurum_turu": "..." (opsiyonel) }
    Basarili yanit (201): { "basari": true, "id": <int> }
    Hata (400): isim veya telefon eksikse
    """
    data = request.get_json(silent=True) or {}
    isim = (data.get("isim") or "").strip()
    telefon = (data.get("telefon") or "").strip()
    mesaj = (data.get("mesaj") or "").strip() or None
    kurum_turu = (data.get("kurum_turu") or "").strip() or None

    if not isim or not telefon:
        return jsonify({
            "basari": False,
            "hata": "isim ve telefon alanlari zorunludur.",
        }), 400

    try:
        yeni_id = lead_ekle(isim, telefon, mesaj, kurum_turu)
    except Exception as e:
        return jsonify({
            "basari": False,
            "hata": "Kayit olusturulurken bir sorun olustu.",
            "detay": str(e),
        }), 503

    return jsonify({"basari": True, "id": yeni_id}), 201


@api_bp.route("/leads", methods=["GET"])
def lead_listele():
    """Tum lead kayitlarini (en yeniden en eskiye) JSON olarak dondurur."""
    try:
        leadler = tum_leadler()
    except Exception as e:
        return jsonify({
            "basari": False,
            "hata": "Kayitlar getirilirken bir sorun olustu.",
            "detay": str(e),
        }), 503

    return jsonify({"basari": True, "leadler": leadler}), 200

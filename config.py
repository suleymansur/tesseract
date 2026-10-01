"""
config.py
---------
MODUL A - Yapilandirma katmani.

Tum ayarlar ve gizli anahtarlar burada, tek merkezde toplanir.
Hicbir yerde dogrudan os.environ.get() cagrisi YAPILMAZ; her ayara
sadece bu dosyadaki Config siniflari uzerinden erisilir.
"""

import os
from dotenv import load_dotenv

# .env dosyasini en basta yukluyoruz; aksi halde asagidaki
# os.environ.get() cagrilari .env'deki degerleri goremez.
load_dotenv()


class Config:
    """Ortak (hem gelistirme hem uretimde gecerli) temel ayarlar."""

    # --- Flask temel ayarlari ---
    SECRET_KEY = os.environ.get("SECRET_KEY", "gelistirme-icin-guvensiz-varsayilan-anahtar")
    DEBUG = False
    TESTING = False

    # --- Veritabani ---
    DATABASE_URL = os.environ.get("DATABASE_URL", "tesseract.db")

    # --- Yapay Zeka Servisi ---
    AI_PROVIDER = os.environ.get("AI_PROVIDER", "groq")
    GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
    GROQ_MODEL = os.environ.get("GROQ_MODEL", "llama-3.1-8b-instant")

    # --- CORS: Wix sitesinin adresi (virgulle birden fazla girilebilir) ---
    CORS_ORIGINS = os.environ.get("CORS_ORIGINS", "*")

    # --- Yapay zekanin kisiligini ve gorevini tanimlayan sistem talimati ---
    # NOT: Konuya (sirkete) ozel degisen TEK yer burasidir.
    BUSINESS_CONTEXT = """Sen Tesseract Teknoloji'nin yapay zeka asistanisin.

Tesseract; hastane, okul, askeri tesis, kamu kurumu/devlet dairesi, banka,
ofis ve sirket binalari icin haberlesme, guvenlik ve veri altyapisi
cozumleri ureten bir teknoloji sirketidir.

Sunulan urun aileleri:
- Switch: Bina ici ag omurgasini olusturan yonetilebilir agu cihazlari.
- Router: Kurumlar arasi ve internet baglantisini yoneten yonlendiriciler.
- Access Point (AP): Kurum ici kablosuz agu (Wi-Fi) kapsama cozumleri.
- NVR (Network Video Recorder): Guvenlik kameralarindan gelen goruntuleri
  aga baglayip kayit altina alan sistemler.
- Storage: Kayitlarin, loglarin ve kurumsal verinin guvenli ve olceklenebilir
  bicimde saklandigi depolama cozumleri.
- Bu donanimlarin yonetimi icin gelistirilen ozel izleme ve yonetim yazilimlari.

Gorevlerin:
1. Ziyaretciyi karsila ve hangi tur kurumu temsil ettigini ogren
   (ornegin: hastane, okul, askeriye, kamu kurumu, banka, ofis/sirket).
2. Kurum turune gore hangi urun ailesinin (Switch, Router, Access Point,
   NVR, Storage) neden onemli olabilecegini kisaca, teknik ama anlasilir
   bir dille aciklar.
3. Kesin fiyat veya teknik taahhut verme; bunun icin bir Tesseract cozum
   muhendisinin kendileriyle iletisime gececegini belirt.
4. Sohbetin uygun bir noktasinda, nazik bir sekilde ad ve telefon
   bilgilerini birakmalarini rica et.
5. Her zaman profesyonel, guven veren ve kurumsal bir uslup kullan.
6. Sadece Turkce konus.
"""


class DevelopmentConfig(Config):
    """Gelistirme ortami: hata ayiklama acik."""

    DEBUG = True


class ProductionConfig(Config):
    """Uretim (Render) ortami: hata ayiklama kapali."""

    DEBUG = False


# Ortam adindan (FLASK_ENV) ilgili yapilandirma sinifini secen sozluk.
config_by_name = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
}


def get_config():
    """Ortam degiskenine gore dogru Config sinifini dondurur."""
    env_name = os.environ.get("FLASK_ENV", "development")
    return config_by_name.get(env_name, DevelopmentConfig)

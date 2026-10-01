"""
database.py
------------
MODUL B - Veritabani katmani.

SQL SADECE bu dosyada yazilir. Baska hicbir dosyada (routes.py,
ai_service.py vb.) dogrudan SQL sorgusu OLMAMALIDIR.

Tablo semasi (leads):
    id          -> otomatik artan birincil anahtar
    isim        -> zorunlu, potansiyel musterinin adi
    telefon     -> zorunlu, iletisim numarasi
    mesaj       -> opsiyonel, ziyaretcinin birakmak istedigi not
    kurum_turu  -> opsiyonel ozel alan: hastane / okul / askeriye /
                   kamu / banka / ofis vb. (Tesseract'a ozel kisisellestirme)
    tarih       -> otomatik, kaydin olusturuldugu zaman damgasi
"""

import sqlite3
from flask import current_app, g


def get_db():
    """
    Mevcut istek (request) icin bir veritabani baglantisi dondurur.
    Flask'in 'g' nesnesi sayesinde ayni istek icinde tekrar tekrar
    yeni baglanti acilmaz; ayni baglanti tekrar kullanilir.

    row_factory = sqlite3.Row sayesinde satirlara hem index hem de
    sutun adiyla (row['isim'] gibi) erisebiliriz.
    """
    if "db" not in g:
        g.db = sqlite3.connect(current_app.config["DATABASE_URL"])
        g.db.row_factory = sqlite3.Row
    return g.db


def close_db(e=None):
    """Istek bittiginde acik kalan veritabani baglantisini kapatir."""
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db(app):
    """
    'leads' tablosunu -eger yoksa- olusturur.
    create_app() icinde, app context'i acilarak cagrilmalidir:

        with app.app_context():
            init_db(app)
    """
    with app.app_context():
        db = get_db()
        db.execute(
            """
            CREATE TABLE IF NOT EXISTS leads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                isim TEXT NOT NULL,
                telefon TEXT NOT NULL,
                mesaj TEXT,
                kurum_turu TEXT,
                tarih TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        db.commit()

    # Baglanti istek disinda acildigi icin manuel kapatiyoruz.
    app.teardown_appcontext(close_db)


def lead_ekle(isim, telefon, mesaj=None, kurum_turu=None):
    """
    Yeni bir lead (musteri adayi) kaydi ekler.

    GUVENLIK: Degerler asla SQL metnine dogrudan eklenmez (string
    birlestirme YASAK). Bunun yerine '?' yer tutuculari ve ayri bir
    parametre listesi kullanilir; bu SQL Injection'a karsi zorunlu
    korumadir.

    Donus: yeni eklenen kaydin id'si (int)
    """
    db = get_db()
    cursor = db.execute(
        """
        INSERT INTO leads (isim, telefon, mesaj, kurum_turu)
        VALUES (?, ?, ?, ?)
        """,
        (isim, telefon, mesaj, kurum_turu),
    )
    db.commit()
    return cursor.lastrowid


def tum_leadler():
    """
    Tum lead kayitlarini en yeniden en eskiye dogru sirali dondurur.
    Her kayit bir sozluk (dict) olarak dondurulur; boylece routes.py
    bu veriyi dogrudan JSON'a cevirebilir.
    """
    db = get_db()
    rows = db.execute(
        "SELECT id, isim, telefon, mesaj, kurum_turu, tarih "
        "FROM leads ORDER BY id DESC"
    ).fetchall()
    return [dict(row) for row in rows]

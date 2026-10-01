# Tesseract AI — Kurumsal Lead Toplama Sistemi

Tesseract; hastane, okul, askeri tesis, kamu kurumu, banka, ofis ve şirket
binaları için **Switch, Router, Access Point, NVR ve Storage** çözümleri
üreten bir teknoloji şirketidir. Bu proje, ziyaretçilerle yapay zekâ
üzerinden sohbet edip iletişim bilgilerini (lead) toplayan, yeniden
kullanılabilir bir backend + arayüz sistemidir.

## Mimari

```
tesseract_ai/
├── run.py                  ← Sunucuyu başlatan giriş noktası
├── config.py                ← Tüm ayarlar, anahtarlar, BUSINESS_CONTEXT
├── requirements.txt
├── .env.example              ← Kopyalayıp .env yapın ve doldurun
├── .gitignore
└── app/
    ├── __init__.py           ← create_app() fabrikası
    ├── database.py            ← SQL SADECE burada
    ├── routes.py               ← HTTP rotaları (sadece yönlendirme)
    ├── templates/
    │   ├── index.html          ← Karşılama sayfası (sohbet + form)
    │   └── dashboard.html      ← Yönetim paneli (lead tablosu)
    └── services/
        └── ai_service.py       ← Yapay zekâ çağrıları SADECE burada
```

**Mimari sözleşme:** `database.py` dışında hiçbir yerde SQL yok.
`ai_service.py` dışında hiçbir yerde yapay zekâ API çağrısı yok.
`routes.py` sadece bu iki katmanın fonksiyonlarını çağırır.

## Kurulum (yerel)

```bash
# 1) Sanal ortam
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate

# 2) Bağımlılıklar
pip install -r requirements.txt

# 3) Ortam değişkenleri
cp .env.example .env
# .env dosyasını açıp GROQ_API_KEY değerinizi girin
# (console.groq.com üzerinden ücretsiz alınabilir)

# 4) Çalıştırma
python run.py
```

Tarayıcıda:
- `http://localhost:5000/` → Karşılama / sohbet sayfası
- `http://localhost:5000/dashboard` → Yönetim paneli
- `http://localhost:5000/health` → Canlılık kontrolü

> **Not:** `GROQ_API_KEY` girilmezse sistem çökmez; sohbet uç noktası
> otomatik olarak "demo modu" mesajı döner. Bu, `ai_service.py` içinde
> `_demo_modu_yaniti()` ile sağlanır.

## API Uç Noktaları

| Metod | Yol | Görev |
|---|---|---|
| GET | `/` | Karşılama sayfası |
| GET | `/dashboard` | Yönetim paneli |
| GET | `/health` | Sunucu canlılık kontrolü |
| POST | `/api/sohbet` | `{mesaj, gecmis}` alır, AI yanıtı döner |
| POST | `/api/leads` | `{isim, telefon, mesaj?, kurum_turu?}` alır, kayıt oluşturur |
| GET | `/api/leads` | Tüm lead kayıtlarını listeler |

`kurum_turu` alanı, yönergedeki "isteğe bağlı kişiselleştirme" kuralına
göre eklenmiş özel bir sütundur (Hastane, Okul, Askeriye, Kamu Kurumu,
Banka, Ofis/Şirket vb.).

## Test

```bash
python run.py
curl http://localhost:5000/health
curl -X POST http://localhost:5000/api/leads \
  -H "Content-Type: application/json" \
  -d '{"isim":"Ahmet Yılmaz","telefon":"05551234567","kurum_turu":"Hastane"}'
curl http://localhost:5000/api/leads
```

## GitHub'a Yükleme

```bash
git init
git add .
git commit -m "Tesseract AI - ilk sürüm"
git branch -M main
git remote add origin <kendi-repo-linkiniz>
git push -u origin main
```

⚠️ **`.env` dosyasının deponuzda görünmediğinden emin olun.**
`.gitignore` bunu zaten hariç tutar; push sonrası GitHub'da kontrol edin.

## Render'da Yayınlama

1. Render'da yeni bir **Web Service** oluşturun, bu GitHub deposunu bağlayın.
2. **Build Command:** `pip install -r requirements.txt`
3. **Start Command:** `gunicorn run:app`
4. **Environment** sekmesinden `.env` içindeki tüm değişkenleri
   (`SECRET_KEY`, `GROQ_API_KEY`, `GROQ_MODEL`, `DATABASE_URL`,
   `CORS_ORIGINS`, `FLASK_ENV=production`) tek tek ekleyin.
5. Dağıtım tamamlanınca `<render-adresiniz>/health` adresinin
   `{"durum":"aktif"}` döndüğünü doğrulayın.

## Wix Velo Entegrasyonu (opsiyonel frontend hedefi)

Bu proje `index.html` / `dashboard.html` ile çalışan tam bir arayüz
içerir; Render'a deploy ettikten sonra doğrudan kullanılabilir. Yönergede
istenen Wix Velo hedefleniyorsa, Wix tarafında aynı uç noktalara
`wix-fetch` ile istek atan bir sayfa kurulabilir:

```js
// Wix Velo - örnek sohbet çağrısı
import { fetch } from 'wix-fetch';

export function sohbetGonder(mesaj, gecmis) {
  return fetch('https://<render-adresiniz>/api/sohbet', {
    method: 'post',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ mesaj, gecmis })
  }).then(res => res.json());
}
```

Alan adlarının (`mesaj`, `isim`, `telefon`, `kurum_turu`) backend ile
birebir aynı kalması kritik önemdedir.

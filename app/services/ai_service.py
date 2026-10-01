"""
ai_service.py
-------------
MODUL C - Yapay zeka servis katmani.

Bu dosya Flask, HTTP veya veritabani kavramlarini BILMEZ.
Sadece kullanici mesajini alir, Groq API'sine gonderir ve yaniti
dondurur. Yapay zeka API cagrisi SADECE burada yapilir.

Bu izolasyon sayesinde ileride saglayici degistirmek (Groq -> Gemini
gibi) sadece bu dosyayi degistirmeyi gerektirir; routes.py etkilenmez.
"""

import requests
from flask import current_app


class AIServiceError(Exception):
    """AI servisiyle ilgili hatalarda firlatilan ozel istisna sinifi."""
    pass


class AIService:
    """Groq (veya benzeri) bir LLM saglayicisiyla konusan servis sinifi."""

    GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

    def _sistem_talimatini_al(self):
        """
        config.py icindeki BUSINESS_CONTEXT metnini okuyan yardimci metot.
        Boylece sirketin 'kimligi' tek bir yerden (config) yonetilir.
        """
        return current_app.config["BUSINESS_CONTEXT"]

    def _demo_modu_yaniti(self, mesaj):
        """
        GROQ_API_KEY tanimli degilse (ornegin oturum oncesi kurulum
        tamamlanmadiysa) programin comesi yerine bilgilendirici bir
        'demo modu' yaniti dondurur.
        """
        return (
            "[DEMO MODU] Yapay zeka anahtari (GROQ_API_KEY) tanimli "
            "degil. Gercek yanitlar icin .env dosyaniza Groq API "
            f"anahtarinizi ekleyin.\n\nAlinan mesajiniz: \"{mesaj}\""
        )

    def yanit_uret(self, mesaj, gecmis=None):
        """
        Kullanicinin mesajini ve konusma gecmisini alir, Groq'tan
        uretilen yaniti dondurur.

        Parametreler:
            mesaj (str): Kullanicinin yeni mesaji.
            gecmis (list[dict] | None): Onceki mesajlar. Her ogenin
                {'role': 'user'|'assistant', 'content': '...'} formatinda
                olmasi beklenir.

        Donus:
            str: Yapay zekanin uzerdigi yanit metni.

        Hata:
            AIServiceError: Istek basarisiz olursa firlatilir.
        """
        api_key = current_app.config.get("GROQ_API_KEY")

        if not api_key:
            return self._demo_modu_yaniti(mesaj)

        gecmis = gecmis or []

        # Groq'a gonderilecek mesaj dizisi: once sistem talimati,
        # sonra gecmis mesajlar, en sonda yeni kullanici mesaji.
        messages = [{"role": "system", "content": self._sistem_talimatini_al()}]
        messages.extend(gecmis)
        messages.append({"role": "user", "content": mesaj})

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": current_app.config.get("GROQ_MODEL", "llama-3.1-8b-instant"),
            "messages": messages,
            "temperature": 0.6,
        }

        try:
            response = requests.post(
                self.GROQ_URL, headers=headers, json=payload, timeout=20
            )
            response.raise_for_status()
        except requests.RequestException as e:
            # Dis servis cagrisi try-except ile sarilmali kurali burada uygulanir.
            raise AIServiceError(f"Groq API cagrisi basarisiz oldu: {e}") from e

        try:
            data = response.json()
            return data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, ValueError) as e:
            raise AIServiceError(f"Groq yaniti beklenmeyen formatta: {e}") from e


# Modulun geri kalaninda import edilecek tek bir ornek (singleton).
ai_service = AIService()

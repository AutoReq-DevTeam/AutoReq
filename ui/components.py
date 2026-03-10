"""
ui/components.py — Görsel Parça Deposu (UI Bileşenleri)
Sahibi: Üye 4 (Arayüz ve Entegrasyon)

Senin Görevin:
Web sayfasında tekrar tekrar kullanacağımız butonları, uyarı kutularını veya renkli rozetleri (badge) her seferinde baştan yazmak yorucudur.
Burası senin tependeki rafın. Burada "Kırmızı Uyarı Kutusu", "İndirme Butonu" gibi küçük görsel parçalar (fonksiyonlar) yapacaksın.
Diğer sayfalarda da sadece bu fonksiyonu çağırıp parçayı Lego gibi yerine takacaksın.

Çıktı: "Tekrar kullanılabilir, küçük ve şık arayüz parçacıkları."
"""

import streamlit as st


def req_card(req_id: str, text: str, req_type: str):
    """Tek bir gereksinimi kart formatında gösterir."""
    # TODO: Üye 4 — Kart tasarımı (st.container + st.columns kombinasyonu)
    color = "🟢" if req_type == "FUNCTIONAL" else "🔵"
    st.markdown(f"**{color} [{req_id}]** {text}")


def priority_badge(priority: str):
    """Öncelik etiketi (HIGH / MEDIUM / LOW) gösterir."""
    colors = {"HIGH": "🔴", "MEDIUM": "🟡", "LOW": "🟢"}
    icon = colors.get(priority, "⚪")
    st.markdown(f"{icon} `{priority}`")


def download_button(label: str, data: bytes, filename: str, mime: str):
    """Standart indirme butonu wrapper'ı."""
    st.download_button(
        label=label,
        data=data,
        file_name=filename,
        mime=mime,
        use_container_width=True,
    )

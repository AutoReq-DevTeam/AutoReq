from fpdf import FPDF
import os

# GÖREV: SRS PDF Motoru Altyapısı (Font Hatası Giderilmiş Versiyon)
class SRSGenerator(FPDF):
    def header(self):
        # Logo Kontrolü
        current_dir = os.path.dirname(os.path.abspath(__file__))
        logo_path = os.path.join(current_dir, "logo.png")
        if os.path.exists(logo_path):
            self.image(logo_path, 10, 8, 33) 
            self.ln(10)

        # Başlık - Bold font kullanıyoruz
        self.set_font('TurkishArial', 'B', 15)
        self.cell(0, 10, 'Yazılım Gereksinim Spesifikasyonu (SRS)', border=False, ln=1, align='C')
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        # Hata buradaydı: İtalik font yüklü değilse normal fontu kullan diyoruz
        try:
            self.set_font('TurkishArial', 'I', 8)
        except:
            self.set_font('TurkishArial', '', 8)
        self.cell(0, 10, f'Sayfa {self.page_no()}/{{nb}}', align='C')

def generate_srs():
    pdf = SRSGenerator()
    
    # --- TÜRKÇE FONT YÜKLEME ---
    font_path = r"C:\Windows\Fonts\arial.ttf"
    font_bold_path = r"C:\Windows\Fonts\arialbd.ttf"
    font_italic_path = r"C:\Windows\Fonts\ariali.ttf" # İtalik dosyasını da ekledik
    
    if os.path.exists(font_path):
        pdf.add_font('TurkishArial', '', font_path, uni=True)
        pdf.add_font('TurkishArial', 'B', font_bold_path, uni=True)
        if os.path.exists(font_italic_path):
            pdf.add_font('TurkishArial', 'I', font_italic_path, uni=True)
        pdf.set_font("TurkishArial", size=12)
    else:
        pdf.set_font("Helvetica", size=12)
    
    pdf.alias_nb_pages()
    pdf.add_page()

    titles = [
        "1. Giriş (Introduction)", "2. Kapsam (Scope)", "3. Genel Açıklama", 
        "4. Fonksiyonel Gereksinimler", "5. Kullanıcı Özellikleri",
        "6. Kısıtlamalar", "7. Varsayımlar ve Bağımlılıklar",
        "8. Veri Gereksinimleri", "9. Dış Arayüz Gereksinimleri", "10. Kalite Özellikleri"
    ]

    for title in titles:
        pdf.set_font("TurkishArial", 'B', 14) if os.path.exists(font_path) else pdf.set_font("Helvetica", 'B', 14)
        pdf.cell(0, 10, txt=title, ln=True)
        pdf.set_font("TurkishArial", size=12) if os.path.exists(font_path) else pdf.set_font("Helvetica", size=12)
        pdf.multi_cell(0, 10, txt="Bu bölüm otomatik analiz sonuçlarıyla doldurulacaktır.\n")
        pdf.ln(5)

    current_dir = os.path.dirname(os.path.abspath(__file__))
    output_path = os.path.join(current_dir, "srs_taslak.pdf")
    
    pdf.output(output_path)
    print(f"\n[BAŞARILI] PDF oluşturuldu: {output_path}")
    
    # Otomatik açma
    try:
        os.startfile(output_path)
    except:
        pass

if __name__ == "__main__":
    generate_srs()
from fpdf import FPDF
import os
from loguru import logger

from core.models import AnalysisReport

_log = logger.bind(module="srs_generator")


class SRSGenerator(FPDF):
    def header(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        logo_path = os.path.join(current_dir, "logo.png")

        if os.path.exists(logo_path):
            self.image(logo_path, 10, 8, 33)
            self.ln(10)

        self.set_font('TurkishArial', 'B', 15)
        self.cell(0, 10, 'Yazılım Gereksinim Spesifikasyonu (SRS)', ln=True, align='C')
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        try:
            self.set_font('TurkishArial', 'I', 8)
        except:
            self.set_font('TurkishArial', '', 8)

        self.cell(0, 10, f'Sayfa {self.page_no()}/{{nb}}', align='C')


def _load_fonts(pdf: FPDF):
    font_path = r"C:\Windows\Fonts\arial.ttf"
    font_bold = r"C:\Windows\Fonts\arialbd.ttf"
    font_italic = r"C:\Windows\Fonts\ariali.ttf"

    if os.path.exists(font_path):
        pdf.add_font('TurkishArial', '', font_path, uni=True)
        pdf.add_font('TurkishArial', 'B', font_bold, uni=True)

        if os.path.exists(font_italic):
            pdf.add_font('TurkishArial', 'I', font_italic, uni=True)

        pdf.set_font("TurkishArial", size=12)
        return True
    else:
        pdf.set_font("Helvetica", size=12)
        return False


def _section_title(pdf, title, has_font):
    pdf.set_font("TurkishArial", 'B', 14) if has_font else pdf.set_font("Helvetica", 'B', 14)
    pdf.cell(0, 10, title, ln=True)
    pdf.ln(2)


def _section_text(pdf, text, has_font):
    pdf.set_font("TurkishArial", size=12) if has_font else pdf.set_font("Helvetica", size=12)
    pdf.multi_cell(0, 8, text)
    pdf.ln(4)


# 🔥 ANA FONKSİYON (SENİN GÖREVİNİN KALBİ)
def generate_srs(report: AnalysisReport, user_stories: list[dict]):
    pdf = SRSGenerator()
    has_font = _load_fonts(pdf)

    pdf.alias_nb_pages()
    pdf.add_page()

    # 1️⃣ GİRİŞ
    _section_title(pdf, "1. Giriş (Introduction)", has_font)
    _section_text(pdf, f"Proje Adı: {getattr(report, 'project_name', 'AutoReq')}", has_font)

    # 2️⃣ KAPSAM
    _section_title(pdf, "2. Kapsam (Scope)", has_font)
    _section_text(pdf, "Bu doküman sistem gereksinimlerini otomatik analiz sonucu oluşturur.", has_font)

    # 3️⃣ FONKSİYONEL GEREKSİNİMLER
    _section_title(pdf, "3. Fonksiyonel Gereksinimler", has_font)

    # --- HATA BURADAYDI, DÜZELTİLDİ ---
    # report.functional_requirements yerine report.parsed_doc.requirements kullanıyoruz
    requirements = []
    if hasattr(report, "parsed_doc") and hasattr(report.parsed_doc, "requirements"):
        requirements = report.parsed_doc.requirements
    
    for req in requirements:
        text = getattr(req, "text", str(req))
        _section_text(pdf, f"- {text}", has_font)

    # 4️⃣ GAP (EKSİKLER) 🔥
    _section_title(pdf, "4. Eksik Gereksinimler (Gap Analysis)", has_font)

    for gap in getattr(report, "gaps", []):
        if isinstance(gap, dict):
            gap_text = f"- {gap.get('missing_area')}\nÖneri: {gap.get('suggestion')}"
        else:
            gap_text = f"- {str(gap)}"
        _section_text(pdf, gap_text, has_font)

    # 5️⃣ USER STORIES 🔥 (EN ÖNEMLİ KISIM)
    _section_title(pdf, "5. User Stories", has_font)

    for story in user_stories:
        # full_story varsa doğrudan onu kullanalım, yoksa birleştirelim
        text = story.get('full_story')
        if not text:
            text = (
                f"As a {story.get('role')}, "
                f"I want {story.get('goal')} "
                f"so that {story.get('benefit')}"
            )
        _section_text(pdf, text, has_font)

        ac_list = story.get("acceptance_criteria", [])
        for ac in ac_list:
            _section_text(pdf, f"   • {ac}", has_font)

    # 6️⃣ NON-FUNCTIONAL (varsa)
    _section_title(pdf, "6. Non-Functional Requirements", has_font)
    
    # Non-functional gereksinimler genelde classifier üzerinden geldiği için filtreleyerek çekiyoruz
    nf_reqs = [r for r in requirements if getattr(r, "category", "").lower() != "functional"]
    
    for req in nf_reqs:
        text = getattr(req, "text", str(req))
        _section_text(pdf, f"- {text}", has_font)

    # 📁 OUTPUT
    current_dir = os.path.dirname(os.path.abspath(__file__))
    output_path = os.path.join(current_dir, "generated", "srs_output.pdf")

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    pdf.output(output_path)
    _log.info("SRS PDF oluşturuldu: {}", output_path)

    try:
        os.startfile(output_path)
    except:
        pass
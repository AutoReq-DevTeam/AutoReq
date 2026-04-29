"""
outputs/srs_generator.py — ISO/IEC/IEEE 29148 Uyumlu Dinamik SRS PDF Üreticisi
Sorumlu: Halise İncir

Açıklama:
AnalysisReport nesnesinden gelen gerçek veriyi ISO/IEC/IEEE 29148 standardındaki
10 ana bölümü olan bir SRS PDF'e dönüştürür.

Kullanım:
    # Streamlit/app.py içinden:
    from outputs.srs_generator import generate_srs
    path = generate_srs(report)                         # outputs/generated/srs_<timestamp>.pdf
    path = generate_srs(report, my_path)                # özel yol
    path = generate_srs(report, draft_watermark=True)   # DRAFT filigranı ile

    # CLI olarak (eski davranış — boş demo PDF):
    python outputs/srs_generator.py

Bilinen Sınırlamalar:
    - os.startfile() yalnızca Windows'ta çalışır; diğer platformlarda sessizce atlanır.

Değişiklikler (Issue #23):
    - PDF metadata (title, author, subject, creator, creation_date) eklendi.
    - Opsiyonel draft_watermark parametresi eklendi.
    - outputs/fonts/ dizininden DejaVuSans.ttf yükleme desteği eklendi.
"""

from __future__ import annotations

import os
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from fpdf import FPDF
from loguru import logger

_log = logger.bind(module="srs_generator")

# ---------------------------------------------------------------------------
# Cross-platform Türkçe Font Çözücü
# ---------------------------------------------------------------------------

_FONT_CANDIDATES: List[Path] = [
    # Windows
    Path(r"C:\Windows\Fonts\arial.ttf"),
    # macOS (standard + supplemental)
    Path("/System/Library/Fonts/Supplemental/Arial.ttf"),
    Path("/Library/Fonts/Arial.ttf"),
    # Linux (Debian/Ubuntu)
    Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
    Path("/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"),
    # Fedora/RHEL
    Path("/usr/share/fonts/dejavu/DejaVuSans.ttf"),
]

_FONT_BOLD_CANDIDATES: List[Path] = [
    Path(r"C:\Windows\Fonts\arialbd.ttf"),
    Path("/System/Library/Fonts/Supplemental/Arial Bold.ttf"),
    Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"),
    Path("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"),
    Path("/usr/share/fonts/dejavu/DejaVuSans-Bold.ttf"),
]


def _resolve_font(candidates: List[Path]) -> Optional[Path]:
    """Aday listesindeki ilk mevcut font dosyasını döndürür.

    Args:
        candidates: Kontrol edilecek font dosyası yolları.

    Returns:
        Optional[Path]: Varsa ilk bulunan font yolu, yoksa None.
    """
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return None


def _resolve_turkish_font_path() -> tuple[Optional[Path], Optional[Path]]:
    """İşletim sistemine göre Türkçe destekli font yollarını çözer.

    Returns:
        tuple[Optional[Path], Optional[Path]]:
            (regular_font_path, bold_font_path) — bulunamazsa None.
    """
    regular = _resolve_font(_FONT_CANDIDATES)
    bold = _resolve_font(_FONT_BOLD_CANDIDATES)

    if regular:
        _log.debug("Font bulundu | regular={}", regular)
    else:
        _log.warning(
            "Türkçe font bulunamadı; Helvetica kullanılacak (karakter bozulması olabilir)."
        )

    return regular, bold


# ---------------------------------------------------------------------------
# Fonts dizininden font yükleme (Issue #23)
# ---------------------------------------------------------------------------

_FONTS_DIR: Path = Path(__file__).parent / "fonts"

# outputs/fonts/ dizinindeki adayları BAŞA ekle (paketlenmiş fontlar öncelikli)
_BUNDLED_FONT_CANDIDATES: List[Path] = [
    _FONTS_DIR / "DejaVuSans.ttf",
    _FONTS_DIR / "NotoSans-Regular.ttf",
]
_BUNDLED_BOLD_CANDIDATES: List[Path] = [
    _FONTS_DIR / "DejaVuSans-Bold.ttf",
    _FONTS_DIR / "NotoSans-Bold.ttf",
]


# ---------------------------------------------------------------------------
# SRS PDF Sınıfı
# ---------------------------------------------------------------------------


class SRSGenerator(FPDF):
    """ISO/IEC/IEEE 29148 uyumlu SRS PDF üreticisi.

    FPDF'yi miras alır; header/footer özelleştirmesi sağlar.
    """

    def __init__(
        self,
        font_regular: Optional[Path] = None,
        font_bold: Optional[Path] = None,
        draft_watermark: bool = False,
    ) -> None:
        """SRSGenerator başlatıcı.

        Args:
            font_regular: Normal ağırlık için font dosya yolu.
            font_bold: Kalın ağırlık için font dosya yolu.
            draft_watermark: True ise her sayfaya 'DRAFT — AutoReq Generated' filigranı ekler.
        """
        super().__init__()
        self._font_regular = font_regular
        self._font_bold = font_bold
        self._font_name = "TurkishFont"
        self._has_custom_font = False
        self._draft_watermark = draft_watermark

    def _load_fonts(self) -> None:
        """Font dosyalarını FPDF'ye kaydeder.

        Dosya bulunamazsa Helvetica fallback'e geçer.
        """
        if self._font_regular and self._font_regular.exists():
            try:
                self.add_font(self._font_name, "", str(self._font_regular), uni=True)
                if self._font_bold and self._font_bold.exists():
                    self.add_font(self._font_name, "B", str(self._font_bold), uni=True)
                self._has_custom_font = True
            except Exception as exc:  # pragma: no cover
                _log.warning("Font yüklenemedi, Helvetica kullanılacak | hata={}", exc)
                self._has_custom_font = False
        else:
            self._has_custom_font = False

    def _set_font_normal(self, size: int = 12) -> None:
        """Normal ağırlıkta font ayarla.

        Args:
            size: Punto boyutu.
        """
        if self._has_custom_font:
            self.set_font(self._font_name, "", size)
        else:
            self.set_font("Helvetica", "", size)

    def _set_font_bold(self, size: int = 12) -> None:
        """Kalın ağırlıkta font ayarla.

        Args:
            size: Punto boyutu.
        """
        if self._has_custom_font:
            self.set_font(self._font_name, "B", size)
        else:
            self.set_font("Helvetica", "B", size)

    def header(self) -> None:
        """Her sayfanın üstüne logo ve başlık ekler."""
        current_dir = Path(__file__).parent
        logo_path = current_dir / "logo.png"
        if logo_path.exists():
            self.image(str(logo_path), 10, 8, 33)
            self.ln(10)

        self._set_font_bold(15)
        self.cell(0, 10, "Yazılım Gereksinim Spesifikasyonu (SRS)", border=False, ln=1, align="C")
        self.ln(5)

        # DRAFT filigranı (Issue #23)
        if self._draft_watermark:
            self._add_watermark()

    def footer(self) -> None:
        """Her sayfanın altına sayfa numarası ekler."""
        self.set_y(-15)
        self._set_font_normal(8)
        self.cell(0, 10, f"Sayfa {self.page_no()}/{{nb}}", align="C")

    def _add_watermark(self) -> None:
        """Sayfaya yarı saydam DRAFT filigranı ekler.

        İkincil bir cell ile sayfanın ortasına gri renkte 45 derece döndürülmüş
        metin simüle edilir (FPDF doğrudan döndürme desteklemediğinden köşegen konuma
        yerleştirilir).
        """
        self.set_text_color(200, 200, 200)  # açık gri
        self._set_font_bold(28)
        # Sayfanın yaklaşık ortasına konumlan
        page_width = self.w
        page_height = self.h
        x_center = page_width / 2 - 55
        y_center = page_height / 2 - 8
        self.set_xy(x_center, y_center)
        self.cell(0, 10, "DRAFT -- AutoReq Generated", border=False, ln=False)
        # Rengi sıfırla
        self.set_text_color(0, 0, 0)

    def set_metadata(
        self,
        title: str = "Software Requirements Specification",
        author: str = "AutoReq",
        subject: str = "SRS - ISO/IEC/IEEE 29148:2018",
        creator: str = "AutoReq PDF Generator",
        creation_date: Optional[str] = None,
    ) -> None:
        """PDF belge metadata alanlarını doldurur (Issue #23).

        Not: fpdf 1.7.x metadata'yı latin-1 ile kodlar. Bu nedenle
        tüm metadata string'leri ASCII-safe olmalıdır (özel Unicode karakterler
        UnicodeEncodeError'a yol açar).

        Args:
            title: Belge başlığı (ASCII-safe).
            author: Yazar (varsayılan: AutoReq).
            subject: Konu açıklaması (ASCII-safe).
            creator: Oluşturucu araç (ASCII-safe).
            creation_date: ISO 8601 tarih string'i (None ise şu an kullanılır).
        """
        if creation_date is None:
            creation_date = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
        self.set_title(title)
        self.set_author(author)
        self.set_subject(subject)
        self.set_creator(creator)
        # FPDF2 set_creation_date destekler; eski versiyonlar için try/except
        try:
            self.set_creation_date(creation_date)  # type: ignore[arg-type]
        except (AttributeError, TypeError):
            _log.debug("set_creation_date desteklenmiyor; atlanıyor.")

    def add_section_title(self, title: str) -> None:
        """Bölüm başlığı satırı ekler.

        Args:
            title: Bölüm başlığı metni.
        """
        self._set_font_bold(14)
        self.cell(0, 10, txt=title, ln=True)
        self.ln(2)

    def add_body_text(self, text: str) -> None:
        """Normal gövde metni ekler.

        Args:
            text: Eklenecek metin.
        """
        self._set_font_normal(11)
        self.multi_cell(0, 8, txt=text)
        self.ln(4)

    def add_bullet_item(self, text: str, indent: int = 10) -> None:
        """Madde işaretli liste öğesi ekler.

        Args:
            text: Madde metni.
            indent: Girintisi (mm).
        """
        self._set_font_normal(11)
        self.set_x(self.get_x() + indent)
        self.multi_cell(0, 7, txt=f"• {text}")

    def add_table_row(self, cells: List[str], widths: Optional[List[int]] = None) -> None:
        """Basit tablo satırı ekler.

        Args:
            cells: Hücre metinleri listesi.
            widths: Hücre genişlikleri (mm). None ise eşit dağıtılır.
        """
        if widths is None:
            w = int(self.w - self.l_margin - self.r_margin) // len(cells)
            widths = [w] * len(cells)
        self._set_font_normal(10)
        for cell_text, width in zip(cells, widths):
            self.cell(width, 8, txt=str(cell_text)[:60], border=1)
        self.ln()


# ---------------------------------------------------------------------------
# Bölüm Doldurucu Helper'lar
# ---------------------------------------------------------------------------


def _render_intro_section(pdf: SRSGenerator, project_name: str = "AutoReq Projesi") -> None:
    """1. Giriş bölümünü doldurur.

    Args:
        pdf: SRS PDF nesnesi.
        project_name: Proje adı.
    """
    pdf.add_section_title("1. Giriş (Introduction)")
    pdf.add_body_text(
        f"Bu belge, '{project_name}' yazılım projesine ait Yazılım Gereksinim "
        "Spesifikasyonunu (SRS) içermektedir. ISO/IEC/IEEE 29148:2018 standardına "
        "uygun olarak otomatik üretilmiştir."
    )
    pdf.add_body_text(
        f"Oluşturulma Tarihi: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    )


def _render_scope_section(pdf: SRSGenerator, total_req: int) -> None:
    """2. Kapsam bölümünü doldurur.

    Args:
        pdf: SRS PDF nesnesi.
        total_req: Toplam gereksinim sayısı.
    """
    pdf.add_section_title("2. Kapsam (Scope)")
    pdf.add_body_text(
        f"Bu SRS belgesi {total_req} gereksinim cümlesini kapsamaktadır. "
        "Gereksinimler AutoReq NLP + LLM analiz pipeline'ı tarafından işlenmiştir."
    )


def _render_overview_section(pdf: SRSGenerator) -> None:
    """3. Genel Açıklama bölümünü doldurur.

    Args:
        pdf: SRS PDF nesnesi.
    """
    pdf.add_section_title("3. Genel Açıklama")
    pdf.add_body_text(
        "Sistem, kullanıcıların doğal dildeki gereksinim metinlerini yapılandırılmış "
        "yazılım gereksinim belgelerine dönüştürmesini sağlar."
    )


def _render_functional_section(pdf: SRSGenerator, report: "AnalysisReport") -> None:
    """4. Fonksiyonel Gereksinimler bölümünü gerçek verilerle doldurur.

    Args:
        pdf: SRS PDF nesnesi.
        report: Analiz raporu.
    """
    pdf.add_section_title("4. Fonksiyonel Gereksinimler")

    functional = [
        req for req in report.parsed_doc.requirements if req.req_type == "FUNCTIONAL"
    ]

    if not functional:
        pdf.add_body_text("Bu belgede fonksiyonel gereksinim tespit edilmedi.")
        return

    # Tablo başlığı
    pdf.add_table_row(["ID", "Metin", "Öncelik"], widths=[25, 130, 25])

    for req in functional:
        priority = req.priority or "MEDIUM"
        text = req.text.strip()
        if len(text) > 80:
            text = text[:77] + "..."
        pdf.add_table_row([req.id, text, priority], widths=[25, 130, 25])

    pdf.ln(4)


def _render_actors_section(pdf: SRSGenerator, report: "AnalysisReport") -> None:
    """5. Kullanıcı Özellikleri / Aktörler bölümünü doldurur.

    Args:
        pdf: SRS PDF nesnesi.
        report: Analiz raporu.
    """
    pdf.add_section_title("5. Kullanıcı Özellikleri")

    all_actors: set = set()
    for req in report.parsed_doc.requirements:
        all_actors.update(req.actors)

    if not all_actors:
        pdf.add_body_text("Sistemde tespit edilen aktör bulunmamaktadır.")
        return

    pdf.add_body_text("Sistemde tespit edilen aktörler:")
    for actor in sorted(all_actors):
        pdf.add_bullet_item(actor)
    pdf.ln(2)


def _render_constraints_section(pdf: SRSGenerator) -> None:
    """6. Kısıtlamalar bölümünü doldurur.

    Args:
        pdf: SRS PDF nesnesi.
    """
    pdf.add_section_title("6. Kısıtlamalar")
    pdf.add_body_text(
        "Sistem, Google Gemini API erişimi gerektirmektedir. "
        "Türkçe dil desteği Stanza NLP modeli ile sağlanmaktadır."
    )


def _render_assumptions_section(pdf: SRSGenerator) -> None:
    """7. Varsayımlar ve Bağımlılıklar bölümünü doldurur.

    Args:
        pdf: SRS PDF nesnesi.
    """
    pdf.add_section_title("7. Varsayımlar ve Bağımlılıklar")
    pdf.add_body_text(
        "Gereksinimler Türkçe dilinde girilmiştir. "
        "API anahtarı ve internet bağlantısı analiz için gereklidir."
    )


def _render_data_section(pdf: SRSGenerator, report: "AnalysisReport") -> None:
    """8. Veri Gereksinimleri bölümünü doldurur.

    Args:
        pdf: SRS PDF nesnesi.
        report: Analiz raporu.
    """
    pdf.add_section_title("8. Veri Gereksinimleri")

    all_objects: set = set()
    for req in report.parsed_doc.requirements:
        all_objects.update(req.objects)

    if all_objects:
        pdf.add_body_text("Sistemde tespit edilen veri nesneleri:")
        for obj in sorted(all_objects):
            pdf.add_bullet_item(obj)
    else:
        pdf.add_body_text("Sistemde veri nesnesi tespit edilemedi.")
    pdf.ln(2)


def _render_interfaces_section(pdf: SRSGenerator) -> None:
    """9. Dış Arayüz Gereksinimleri bölümünü doldurur.

    Args:
        pdf: SRS PDF nesnesi.
    """
    pdf.add_section_title("9. Dış Arayüz Gereksinimleri")
    pdf.add_body_text(
        "Sistem, Streamlit tabanlı web arayüzü üzerinden erişilebilir. "
        "Harici arayüz olarak Google Gemini API kullanılmaktadır."
    )


def _render_nfr_section(pdf: SRSGenerator, report: "AnalysisReport") -> None:
    """10. Kalite Özellikleri (NFR) bölümünü gerçek verilerle doldurur.

    Args:
        pdf: SRS PDF nesnesi.
        report: Analiz raporu.
    """
    pdf.add_section_title("10. Kalite Özellikleri")

    non_functional = [
        req for req in report.parsed_doc.requirements if req.req_type == "NON_FUNCTIONAL"
    ]

    if not non_functional:
        pdf.add_body_text("Bu belgede fonksiyonel olmayan gereksinim tespit edilmedi.")
        return

    pdf.add_table_row(["ID", "Metin", "Öncelik"], widths=[25, 130, 25])
    for req in non_functional:
        priority = req.priority or "MEDIUM"
        text = req.text.strip()
        if len(text) > 80:
            text = text[:77] + "..."
        pdf.add_table_row([req.id, text, priority], widths=[25, 130, 25])

    pdf.ln(4)


def _render_conflicts_section(pdf: SRSGenerator, report: "AnalysisReport") -> None:
    """Tespit Edilen Çelişkiler bölümünü doldurur (yalnızca veri varsa).

    Args:
        pdf: SRS PDF nesnesi.
        report: Analiz raporu.
    """
    if not report.conflicts:
        return

    pdf.add_section_title("11. Tespit Edilen Çelişkiler")
    pdf.add_body_text(
        f"Analizde {len(report.conflicts)} adet çelişki tespit edilmiştir."
    )

    for idx, conflict in enumerate(report.conflicts, start=1):
        req_ids = conflict.get("req_ids", [])
        reason = conflict.get("reason", "(Açıklama yok.)")
        severity = conflict.get("severity", "medium")
        ids_str = ", ".join(req_ids) if isinstance(req_ids, list) else str(req_ids)

        pdf.add_bullet_item(
            f"Çelişki #{idx} ({severity}) — Gereksinimler: {ids_str}"
        )
        pdf.add_body_text(f"  Gerekçe: {reason[:300]}")

    pdf.ln(4)


# ---------------------------------------------------------------------------
# Ana Üretim Fonksiyonu
# ---------------------------------------------------------------------------


def generate_srs(
    report: Optional["AnalysisReport"] = None,
    output_path: Optional[Path] = None,
    draft_watermark: bool = False,
) -> Path:
    """AnalysisReport'tan ISO/IEC/IEEE 29148 uyumlu SRS PDF üretir.

    Geriye dönük uyumluluk için report=None çağrısı da kabul edilir;
    bu durumda statik bir demo PDF üretilir.

    Args:
        report: NLP ve LLM analizleri tamamlanmış rapor nesnesi.
                None verilirse statik demo PDF üretilir.
        output_path: Çıktı PDF yolu. None ise outputs/generated/srs_{timestamp}.pdf
                     konumuna yazılır.
        draft_watermark: True ise her sayfaya 'DRAFT — AutoReq Generated' filigranı eklenir.

    Returns:
        Path: Üretilen PDF dosyasının tam yolu.
    """
    # outputs/generated/ klasörünü oluştur
    generated_dir = Path(__file__).parent / "generated"
    generated_dir.mkdir(parents=True, exist_ok=True)

    if output_path is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = generated_dir / f"srs_{timestamp}.pdf"

    output_path = Path(output_path)

    # Font çözümü — bundled fontlar öncelikli (Issue #23)
    bundled_regular = _resolve_font(_BUNDLED_FONT_CANDIDATES)
    bundled_bold = _resolve_font(_BUNDLED_BOLD_CANDIDATES)

    if bundled_regular:
        font_regular, font_bold = bundled_regular, bundled_bold
    else:
        font_regular, font_bold = _resolve_turkish_font_path()

    pdf = SRSGenerator(
        font_regular=font_regular,
        font_bold=font_bold,
        draft_watermark=draft_watermark,
    )
    pdf._load_fonts()

    # PDF Metadata (Issue #23)
    # Not: fpdf 1.7.x latin-1 kullaniyor; metadata ASCII-safe olmali.
    project_name = "AutoReq Projesi"
    pdf.set_metadata(
        title=f"SRS - {project_name}",
        author="AutoReq",
        subject="Software Requirements Specification - ISO/IEC/IEEE 29148:2018",
        creator="AutoReq PDF Generator v1.0",
    )

    pdf.alias_nb_pages()
    pdf.add_page()

    if report is not None:
        _log.info(
            "Dinamik SRS üretimi başlatıldı | gereksinim_sayısı={}",
            len(report.parsed_doc.requirements),
        )
        total_req = len(report.parsed_doc.requirements)
        _render_intro_section(pdf)
        _render_scope_section(pdf, total_req)
        _render_overview_section(pdf)
        _render_functional_section(pdf, report)
        _render_actors_section(pdf, report)
        _render_constraints_section(pdf)
        _render_assumptions_section(pdf)
        _render_data_section(pdf, report)
        _render_interfaces_section(pdf)
        _render_nfr_section(pdf, report)
        _render_conflicts_section(pdf, report)
    else:
        # Geriye dönük uyumluluk: statik demo
        _log.info("Statik demo SRS üretiliyor (report=None).")
        static_titles = [
            "1. Giriş (Introduction)",
            "2. Kapsam (Scope)",
            "3. Genel Açıklama",
            "4. Fonksiyonel Gereksinimler",
            "5. Kullanıcı Özellikleri",
            "6. Kısıtlamalar",
            "7. Varsayımlar ve Bağımlılıklar",
            "8. Veri Gereksinimleri",
            "9. Dış Arayüz Gereksinimleri",
            "10. Kalite Özellikleri",
        ]
        for title in static_titles:
            pdf.add_section_title(title)
            pdf.add_body_text("Bu bölüm otomatik analiz sonuçlarıyla doldurulacaktır.")
            pdf.ln(3)

    pdf.output(str(output_path))
    _log.info("SRS PDF oluşturuldu | yol={}", output_path)

    # Yalnızca Windows'ta otomatik aç
    if sys.platform == "win32":
        try:
            os.startfile(str(output_path))
        except Exception:
            pass

    return output_path


# ---------------------------------------------------------------------------
# CLI giriş noktası (geriye dönük uyu
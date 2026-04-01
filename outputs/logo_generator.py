from PIL import Image, ImageDraw, ImageFont
import os

def create_autoreq_logo():
    # 300x100 piksellik şeffaf bir resim oluştur
    width, height = 300, 100
    image = Image.new('RGBA', (width, height), (255, 255, 255, 0))
    draw = ImageDraw.Draw(image)

    # Kurumsal Mavi Renk
    corporate_blue = (0, 64, 128, 255)

    # Windows Arial Fontunu Kullan
    font_path = r"C:\Windows\Fonts\arialbd.ttf"
    if not os.path.exists(font_path):
        font = ImageFont.load_default()
    else:
        font = ImageFont.truetype(font_path, 45)

    # Metni Çiz
    draw.text((50, 25), "AutoReq", font=font, fill=corporate_blue)

    # ÖNEMLİ: srs_generator.py ile aynı klasöre kaydet
    current_dir = os.path.dirname(os.path.abspath(__file__))
    logo_path = os.path.join(current_dir, "logo.png")
    image.save(logo_path)
    print(f"\n[TAMAM] Logo şuraya oluşturuldu: {logo_path}")

if __name__ == "__main__":
    create_autoreq_logo()
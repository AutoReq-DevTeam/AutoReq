import os
import urllib.request
from pathlib import Path

def download_fonts():
    fonts_dir = Path(__file__).parent
    fonts_dir.mkdir(parents=True, exist_ok=True)
    
    urls = {
        "DejaVuSans.ttf": "https://raw.githubusercontent.com/Setasign/tFPDF/master/font/unifont/DejaVuSans.ttf",
        "DejaVuSans-Bold.ttf": "https://raw.githubusercontent.com/Setasign/tFPDF/master/font/unifont/DejaVuSans-Bold.ttf",
    }
    
    for filename, url in urls.items():
        target_path = fonts_dir / filename
        if not target_path.exists():
            print(f"Downloading {filename} from {url}...")
            try:
                urllib.request.urlretrieve(url, target_path)
                print(f"Successfully downloaded {filename}.")
            except Exception as e:
                print(f"Failed to download {filename}: {e}")
        else:
            print(f"{filename} already exists, skipping download.")

if __name__ == "__main__":
    download_fonts()

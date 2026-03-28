"""
SafeSite Drohne – Hilfsfunktionen
Bildkonvertierung, Dateihandling, etc.
"""
import os
import tempfile
import cv2
from PIL import Image


def convert_image_if_needed(img_path: str) -> str:
    """Konvertiert HEIC/HEIF und problematische Formate nach JPEG."""
    try:
        if img_path.lower().endswith((".heic", ".heif")):
            # Versuche mit PIL
            try:
                img = Image.open(img_path)
                if img.mode != "RGB":
                    img = img.convert("RGB")
                new_path = img_path.rsplit(".", 1)[0] + ".jpg"
                img.save(new_path, "JPEG", quality=95)
                _try_remove(img_path)
                return new_path
            except Exception:
                pass
            # Versuche mit OpenCV
            try:
                arr = cv2.imread(img_path, cv2.IMREAD_COLOR)
                if arr is not None and arr.size > 0:
                    new_path = img_path.rsplit(".", 1)[0] + ".jpg"
                    cv2.imwrite(new_path, arr, [cv2.IMWRITE_JPEG_QUALITY, 95])
                    _try_remove(img_path)
                    return new_path
            except Exception:
                pass
            return img_path

        # Andere Formate: Prüfe ob RGB-Konvertierung nötig
        try:
            img = Image.open(img_path)
            if img.mode in ("RGBA", "P"):
                rgb = Image.new("RGB", img.size, (255, 255, 255))
                if img.mode == "RGBA":
                    rgb.paste(img, mask=img.split()[3])
                else:
                    rgb.paste(img)
                new_path = img_path.rsplit(".", 1)[0] + "_rgb.jpg"
                rgb.save(new_path, "JPEG", quality=95)
                if img_path != new_path:
                    _try_remove(img_path)
                return new_path
        except Exception:
            pass
        return img_path

    except Exception:
        return img_path


def save_uploaded_file(uploaded_file) -> str:
    """Speichert ein Streamlit UploadedFile als temporäre Datei."""
    ext = os.path.splitext(uploaded_file.name)[1].lower()
    ext_map = {
        ".heic": ".heic", ".heif": ".heic",
        ".jpg": ".jpg", ".jpeg": ".jpg",
        ".png": ".png", ".webp": ".webp",
        ".mp4": ".mp4", ".mov": ".mov", ".avi": ".avi",
    }
    suffix = ext_map.get(ext, ext if ext else ".jpg")
    t = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    for chunk in iter(lambda: uploaded_file.read(8192), b""):
        t.write(chunk)
    t.close()
    return t.name


def cleanup_temp_files(paths: list):
    """Löscht temporäre Dateien."""
    for p in paths:
        _try_remove(p)


def _try_remove(path: str):
    try:
        if os.path.exists(path):
            os.remove(path)
    except Exception:
        pass

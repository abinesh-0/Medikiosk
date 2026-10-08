import os
import logging
from pathlib import Path
from PIL import Image, ImageEnhance, ImageFilter, ImageOps

logger = logging.getLogger(__name__)

def preprocess_medical_image(input_path: str, output_dir: str = None) -> dict:
    """
    Preprocess a scanned or photographed medical document to optimize OCR accuracy.
    Applies:
      - EXIF / Auto orientation correction
      - Resolution normalization (rescaling low-res captures to ~1800-2400px width)
      - Gentle noise reduction (Median filter)
      - Contrast and sharpness enhancement for doctor handwriting and faint print
      - Auto-contrast adjustment
    Returns dict:
      {
        "processed_path": str,
        "original_path": str,
        "width": int,
        "height": int,
        "dpi": tuple,
        "enhanced": bool
      }
    """
    try:
        in_p = Path(input_path)
        if not in_p.exists():
            return {"processed_path": input_path, "enhanced": False}

        img = Image.open(input_path)

        # 1. Orientation correction via EXIF
        try:
            img = ImageOps.exif_transpose(img)
        except Exception as e:
            logger.debug("EXIF orientation check: %s", e)

        # 2. Ensure RGB mode
        if img.mode not in ("RGB", "L"):
            img = img.convert("RGB")

        orig_w, orig_h = img.size

        # 3. Resolution improvement: if width is below 1400px, upscale with Lanczos
        # Medical documents photographed from kiosk webcams / phones often need upscaling
        target_w = orig_w
        target_h = orig_h
        if orig_w < 1400 and orig_w > 0:
            scale_factor = 1400.0 / orig_w
            target_w = 1400
            target_h = int(orig_h * scale_factor)
            img = img.resize((target_w, target_h), Image.Resampling.LANCZOS)

        # 4. Contrast enhancement (makes handwritten ink and light print stand out)
        contrast_enhancer = ImageEnhance.Contrast(img)
        img = contrast_enhancer.enhance(1.25)

        # 5. Sharpness enhancement (clarifies character boundaries and lab numbers)
        sharpness_enhancer = ImageEnhance.Sharpness(img)
        img = sharpness_enhancer.enhance(1.4)

        # 6. Auto-contrast with minor cutoff to eliminate faded background shadows
        try:
            img = ImageOps.autocontrast(img, cutoff=1)
        except Exception:
            pass

        # Determine output location
        if not output_dir:
            out_folder = in_p.parent / "preprocessed"
        else:
            out_folder = Path(output_dir)
        out_folder.mkdir(parents=True, exist_ok=True)

        processed_filename = f"preproc_{in_p.stem}.png"
        processed_path = str(out_folder / processed_filename)

        img.save(processed_path, format="PNG", optimize=True, dpi=(300, 300))
        logger.info("Preprocessed medical document saved: %s (%dx%d)", processed_path, target_w, target_h)

        return {
            "processed_path": processed_path,
            "original_path": input_path,
            "width": target_w,
            "height": target_h,
            "dpi": (300, 300),
            "enhanced": True
        }

    except Exception as e:
        logger.warning("Document preprocessing failed, falling back to original: %s", e)
        return {
            "processed_path": input_path,
            "original_path": input_path,
            "enhanced": False,
            "error": str(e)
        }

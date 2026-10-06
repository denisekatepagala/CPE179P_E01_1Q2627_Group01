import re

import cv2
import numpy as np
import pytesseract

from fastapi import FastAPI, File, UploadFile, HTTPException
from transformers import (
    AutoTokenizer,
    AutoModelForSeq2SeqLM,
)


app = FastAPI(
    title="English-Tagalog Translation API",
    description="Tesseract OCR and English-to-Tagalog translation API",
    version="1.0.0",
)


# ============================================================
# SETTINGS
# ============================================================

pytesseract.pytesseract.tesseract_cmd = (
    r"C:\Users\cristel\Downloads\CPE179P_Project\tesseract.exe"
)

TRANSLATION_MODEL = "Helsinki-NLP/opus-mt-en-tl"


# ============================================================
# LOAD TRANSLATION MODEL
# ============================================================

print()
print("===================================")
print("LOADING TRANSLATION MODEL")
print("===================================")

print("Model:", TRANSLATION_MODEL)
print("Please wait...")

tokenizer = AutoTokenizer.from_pretrained(
    TRANSLATION_MODEL
)

translation_model = AutoModelForSeq2SeqLM.from_pretrained(
    TRANSLATION_MODEL
)

print("Translation model loaded successfully!")


# ============================================================
# IMAGE PREPROCESSING
# ============================================================

def preprocess_image(image):

    gray = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2GRAY
    )

    gray = cv2.resize(
        gray,
        None,
        fx=3,
        fy=3,
        interpolation=cv2.INTER_CUBIC
    )

    gray = cv2.GaussianBlur(
        gray,
        (3, 3),
        0
    )

    processed = cv2.adaptiveThreshold(
        gray,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        31,
        11
    )

    return processed


# ============================================================
# OCR ENGINE
# ============================================================

def ocr_engine(image):

    text = pytesseract.image_to_string(
        image,
        config="--psm 12 --oem 3"
    )

    lines = []

    for line in text.splitlines():

        line = line.strip()

        if line:
            lines.append(line)

    text = " ".join(lines)

    return text.strip()


# ============================================================
# CLEAN OCR
# ============================================================

def clean_ocr_text(text):

    text = " ".join(text.split())

    text = text.replace("—~", "-")
    text = text.replace("~—", "-")
    text = text.replace("~~", "-")

    text = text.replace("—", "-")
    text = text.replace("–", "-")

    text = text.replace(" .", ".")
    text = text.replace(" ,", ",")
    text = text.replace(" :", ":")
    text = text.replace(" ;", ";")

    text = text.replace("..", ".")
    text = text.replace("::", ":")

    return text.strip()


# ============================================================
# TRANSLATE ONE SENTENCE
# ============================================================

def translate_sentence(text):

    if not text.strip():
        return ""

    inputs = tokenizer(
        text,
        return_tensors="pt",
        truncation=True,
        max_length=128
    )

    outputs = translation_model.generate(
        **inputs,
        max_length=128,
        num_beams=5
    )

    translated = tokenizer.decode(
        outputs[0],
        skip_special_tokens=True
    )

    return translated.strip()


# ============================================================
# TRANSLATION ENGINE
# ============================================================

def translate_to_tagalog(text):

    reference_pattern = (
        r"\b[A-Z][a-z]+\s+\d+\s*:\s*\d+\b"
    )

    reference_match = re.search(
        reference_pattern,
        text
    )

    reference = None

    if reference_match:

        reference = reference_match.group(
            0
        ).strip()

        translation_text = text.replace(
            reference,
            ""
        ).strip()

    else:

        translation_text = text

    translation_text = translation_text.rstrip(
        " -—~"
    ).strip()

    sentences = re.split(
        r"(?<=[.!?])\s+",
        translation_text
    )

    translated_sentences = []

    for sentence in sentences:

        sentence = sentence.strip()

        if not sentence:
            continue

        translated = translate_sentence(
            sentence
        )

        if translated:
            translated_sentences.append(
                translated
            )

    result = " ".join(
        translated_sentences
    )

    if reference:

        if result:
            result += " - " + reference

        else:
            result = reference

    return result


# ============================================================
# ROOT
# ============================================================

@app.get("/")
def root():

    return {
        "message": "English-Tagalog Translation API is running."
    }


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/health")
def health():

    return {
        "status": "ok"
    }


# ============================================================
# OCR ENDPOINT
# ============================================================

@app.post("/ocr")
async def ocr_endpoint(
    file: UploadFile = File(...)
):

    try:

        image_data = await file.read()

        image_array = np.frombuffer(
            image_data,
            np.uint8
        )

        image = cv2.imdecode(
            image_array,
            cv2.IMREAD_COLOR
        )

        if image is None:

            raise HTTPException(
                status_code=400,
                detail="Unable to read image."
            )

        processed = preprocess_image(
            image
        )

        english_text = ocr_engine(
            processed
        )

        english_text = clean_ocr_text(
            english_text
        )

        return {
            "english_text": english_text
        }

    except HTTPException:
        raise

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=str(error)
        )


# ============================================================
# TRANSLATION ENDPOINT
# ============================================================

@app.post("/translate")
async def translate_endpoint(
    file: UploadFile = File(...)
):

    try:

        image_data = await file.read()

        image_array = np.frombuffer(
            image_data,
            np.uint8
        )

        image = cv2.imdecode(
            image_array,
            cv2.IMREAD_COLOR
        )

        if image is None:

            raise HTTPException(
                status_code=400,
                detail="Unable to read image."
            )

        processed = preprocess_image(
            image
        )

        english_text = ocr_engine(
            processed
        )

        english_text = clean_ocr_text(
            english_text
        )

        if not english_text:

            return {
                "english_text": "",
                "tagalog_text": "",
                "message": "No text detected."
            }

        tagalog_text = translate_to_tagalog(
            english_text
        )

        return {
            "english_text": english_text,
            "tagalog_text": tagalog_text
        }

    except HTTPException:
        raise

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=str(error)
        )
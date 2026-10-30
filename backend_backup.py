import os
import re
import joblib
import fitz

from email import policy
from email.parser import BytesParser
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from preprocessing import clean_text


# =========================================================
# EMAIL GUARDIAN - FASTAPI BACKEND
# =========================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

MODEL_PATH = os.path.join(
    BASE_DIR, "archive", "models", "phishing_model.pkl"
)

VECTORIZER_PATH = os.path.join(
    BASE_DIR, "archive", "models", "vectorizer.pkl"
)

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
ALLOWED_EXTENSIONS = {".eml", ".txt", ".pdf"}

app = FastAPI(
    title="Email Guardian API",
    description="AI-powered phishing email detection",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


# =========================================================
# LOAD EXISTING TRAINED MODEL
# =========================================================

try:
    model = joblib.load(MODEL_PATH)
    vectorizer = joblib.load(VECTORIZER_PATH)
except Exception as exc:
    raise RuntimeError(
        "Could not load the trained model or vectorizer. "
        "Check archive/models/phishing_model.pkl and "
        "archive/models/vectorizer.pkl."
    ) from exc


# =========================================================
# EXTRACT EMAIL CONTENT
# =========================================================

def extract_email(filename: str, file_bytes: bytes) -> dict:
    extension = os.path.splitext(filename)[1].lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise ValueError("Only EML, TXT, and PDF files are supported.")

    if not file_bytes:
        raise ValueError("The uploaded file is empty.")

    if len(file_bytes) > MAX_FILE_SIZE:
        raise ValueError("File size must not exceed 10 MB.")

    # PDF FILE
    if extension == ".pdf":
        try:
            with fitz.open(stream=file_bytes, filetype="pdf") as document:
                if document.page_count > 100:
                    raise ValueError(
                        "PDF cannot contain more than 100 pages."
                    )

                body = "\n".join(
                    page.get_text() for page in document
                )

            if not body.strip():
                raise ValueError(
                    "No readable text was found in the PDF."
                )

            return {
                "subject": filename,
                "sender": "Not available — uploaded PDF",
                "receiver": "Not available",
                "date": "Not available",
                "body": body,
            }

        except ValueError:
            raise
        except Exception as exc:
            raise ValueError(
                "Could not read this PDF. Ensure it is a valid PDF "
                "containing extractable text."
            ) from exc

    # EML FILE
    if extension == ".eml":
        try:
            message = BytesParser(
                policy=policy.default
            ).parsebytes(file_bytes)
        except Exception as exc:
            raise ValueError("Could not parse the EML file.") from exc

        body_parts = []

        if message.is_multipart():
            for part in message.walk():
                if part.get_content_disposition() == "attachment":
                    continue

                if part.get_content_type() == "text/plain":
                    try:
                        content = part.get_content()
                        if isinstance(content, str):
                            body_parts.append(content)
                    except Exception:
                        continue
        else:
            try:
                content = message.get_content()
                if isinstance(content, str):
                    body_parts.append(content)
            except Exception:
                pass

        body = "\n".join(body_parts)

        # Fallback for emails containing HTML but no plain-text part.
        if not body.strip():
            html_parts = []

            for part in message.walk():
                if part.get_content_disposition() == "attachment":
                    continue

                if part.get_content_type() == "text/html":
                    try:
                        content = part.get_content()
                        if isinstance(content, str):
                            html_parts.append(content)
                    except Exception:
                        continue

            body = "\n".join(
                re.sub(r"<[^>]+>", " ", html)
                for html in html_parts
            )

        return {
            "subject": str(message.get("subject", "(No subject)")),
            "sender": str(message.get("from", "Unknown")),
            "receiver": str(message.get("to", "Unknown")),
            "date": str(message.get("date", "Unknown")),
            "body": body,
        }

    # TXT FILE
    try:
        body = file_bytes.decode("utf-8-sig")
    except UnicodeDecodeError:
        body = file_bytes.decode("latin-1")

    return {
        "subject": filename,
        "sender": "Not available — uploaded TXT",
        "receiver": "Not available",
        "date": "Not available",
        "body": body,
    }


# =========================================================
# PREDICTION HELPERS
# =========================================================

def classify_prediction(prediction):
    """
    Convert common model labels into a consistent result.
    Unknown labels are not silently classified as safe.
    """
    label = str(prediction).strip().lower()

    if any(word in label for word in ("phishing", "phish", "malicious")):
        return "Phishing"

    if any(word in label for word in ("legitimate", "benign", "safe", "ham")):
        return "Legitimate"

    if label in {"1", "1.0"}:
        return "Phishing"

    if label in {"0", "0.0"}:
        return "Legitimate"

    return "Unknown"


def get_confidence(features, prediction):
    """
    Return model probability when supported.
    Otherwise, return None rather than inventing a confidence score.
    """
    if not hasattr(model, "predict_proba"):
        return None

    try:
        probabilities = model.predict_proba(features)[0]
        classes = list(model.classes_)
        predicted_index = classes.index(prediction)
        return round(float(probabilities[predicted_index]) * 100, 2)
    except (ValueError, AttributeError, IndexError, TypeError):
        return None


# =========================================================
# API ROUTES
# =========================================================

@app.get("/")
def home():
    return {
        "status": "online",
        "application": "Email Guardian",
        "message": "Phishing detection API is running.",
    }


@app.get("/api/health")
def health():
    return {
        "status": "healthy",
        "model_loaded": model is not None,
        "vectorizer_loaded": vectorizer is not None,
    }


@app.post("/api/analyze")
async def analyze_email(file: UploadFile = File(...)):
    filename = file.filename or "uploaded_file"

    try:
        file_bytes = await file.read()

        email_data = extract_email(filename, file_bytes)
        original_text = email_data["body"]

        if not original_text.strip():
            raise ValueError(
                "The uploaded file does not contain readable email text."
            )

        # Use the project's existing preprocessing function.
        cleaned_text = clean_text(original_text)

        if not cleaned_text or not cleaned_text.strip():
            raise ValueError(
                "No usable text remains after preprocessing."
            )

        # Transform text using the existing trained vectorizer.
        features = vectorizer.transform([cleaned_text])

        # Run the trained classification model.
        prediction = model.predict(features)[0]
        result = classify_prediction(prediction)
        confidence = get_confidence(features, prediction)

        # Extract URLs from original content for display.
        urls = list(
            dict.fromkeys(
                re.findall(
                    r"""https?://[^\s<>"']+""",
                    original_text,
                    flags=re.IGNORECASE,
                )
            )
        )

        return {
            "success": True,
            "filename": filename,
            "prediction": result,
            "confidence": confidence,
            "subject": email_data["subject"],
            "sender": email_data["sender"],
            "receiver": email_data["receiver"],
            "date": email_data["date"],
            "body_preview": original_text[:1000],
            "urls_found": urls,
            "url_count": len(urls),
            "message": (
                "Analysis completed."
                if result != "Unknown"
                else (
                    "The model returned a label that this API "
                    "does not recognize. Check the model's class labels."
                )
            ),
        }

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Analysis failed: {str(exc)}",
        ) from exc

    finally:
        await file.close()
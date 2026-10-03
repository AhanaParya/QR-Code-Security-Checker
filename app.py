from flask import Flask, render_template, request
import cv2
import os

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


def is_suspicious(url):
    reasons = []

    if not url.startswith("https://"):
        reasons.append("Website is not using HTTPS.")

    if "@" in url:
        reasons.append("Contains '@' symbol.")

    if len(url) > 75:
        reasons.append("URL is unusually long.")

    suspicious_words = [
        "login",
        "verify",
        "update",
        "bank",
        "secure",
        "account"
    ]

    for word in suspicious_words:
        if word in url.lower():
            reasons.append(f"Contains suspicious keyword: {word}")

    return reasons


@app.route("/", methods=["GET", "POST"])
def index():
    qr_data = ""
    result = ""
    reasons = []

    if request.method == "POST":
        file = request.files["file"]

        if file:
            path = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
            file.save(path)

            img = cv2.imread(path)

            detector = cv2.QRCodeDetector()
            qr_data, points, _ = detector.detectAndDecode(img)

            if qr_data:
                reasons = is_suspicious(qr_data)

                if reasons:
                    result = "⚠️ Suspicious Link"
                else:
                    result = "✅ Safe Link"
            else:
                qr_data = "No QR Code Found"

    return render_template(
        "index.html",
        qr_data=qr_data,
        result=result,
        reasons=reasons
    )


if __name__ == "__main__":
    app.run(debug=True)
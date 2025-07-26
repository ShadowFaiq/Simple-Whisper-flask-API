from flask import Flask, jsonify, request
from whisper_transcribe_fn import whisper_transcribe_fn
import os

UPLOAD_FOLDER = 'uploads'

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route('/healthz')
def healthz():
    return "OK", 200


@app.after_request
def after_request(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    response.headers["Access-Control-Allow-Methods"] = "GET,PUT,POST,DELETE"
    return response


@app.route('/', methods=['GET'])
def get_data():
    print("📡 Received GET request to /")
    return jsonify({"message": "Hello from Whisper API!"})


@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        # Debug incoming request
        print("📥 Incoming files:", request.files)

        if 'file' not in request.files:
            print("❌ No file part in request")
            return jsonify({"error": "No file provided"}), 400

        file = request.files['file']
        if file.filename == '':
            print("❌ No file selected")
            return jsonify({"error": "No file selected"}), 400

        # Ensure uploads folder exists
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

        # Save file
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)
        print(f"✅ File saved to: {filepath}")

        # Transcribe the file
        try:
            result = whisper_transcribe_fn(filepath)
            print("📝 Transcription successful")
            return jsonify(result), 200
        except Exception as e:
            print("❌ Transcription failed:", str(e))
            return jsonify({"error": "Transcription error", "details": str(e)}), 500

    except Exception as e:
        print("❌ Unexpected server error:", str(e))
        return jsonify({"error": "Server error", "details": str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5678)


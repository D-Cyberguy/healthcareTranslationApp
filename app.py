from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import openai
from deep_translator import GoogleTranslator
from gtts import gTTS
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# 🔒 Secure: Set OpenAI API Key from Environment Variables
openai.api_key = os.getenv("OPENAI_API_KEY")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/translate', methods=['POST'])
def translate_text():
    try:
        data = request.get_json()
        text = data.get('text', '').strip()
        target_lang = data.get('target_lang', 'en').strip()
        
        if not text:
            return jsonify({'error': 'No text provided for translation'}), 400

        translated_text = GoogleTranslator(source='auto', target=target_lang).translate(text)
        return jsonify({'translated_text': translated_text})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/text-to-speech', methods=['POST'])
def text_to_speech():
    try:
        data = request.get_json()
        text = data.get('text', '').strip()
        target_lang = data.get('target_lang', 'en').strip()

        if not text:
            return jsonify({'error': 'No text provided for speech synthesis'}), 400

        audio_file = os.path.join("static", "translated_audio.mp3")
        
        # Ensure static directory exists
        os.makedirs("static", exist_ok=True)
        
        # Remove existing file if present
        if os.path.exists(audio_file):
            os.remove(audio_file)

        tts = gTTS(text=text, lang=target_lang)
        tts.save(audio_file)

        return jsonify({'audio_url': f"/{audio_file}"})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)

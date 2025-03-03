from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import openai  # AI-powered Speech-to-Text
from deep_translator import GoogleTranslator  # Fix for googletrans issues
from gtts import gTTS
import os
from dotenv import load_dotenv  # Load environment variables from .env file

load_dotenv()

app = Flask(__name__)

# 🔒 Secure: Set OpenAI API Key from Environment Variables
openai.api_key = os.getenv("OPENAI_API_KEY")  

@app.route('/')
def index():
    return render_template('index.html')

# 🎤 AI-Powered Speech-to-Text (With Real-Time Translation)
@app.route('/speech-to-text', methods=['POST'])
def speech_to_text():
    try:
        audio_file = request.files['audio']
        
        # Save audio temporarily
        temp_audio_path = "temp_audio.wav"
        audio_file.save(temp_audio_path)

        # Process with OpenAI Whisper
        with open(temp_audio_path, "rb") as audio:
            response = openai.Audio.transcribe("whisper-1", audio)

        transcript = response.get('text', '')

        # 🌍 Auto-Translate While Transcribing
        target_lang = request.form.get("target_lang", "en")  # Default to English
        translated_text = GoogleTranslator(source='auto', target=target_lang).translate(transcript)

        print(f"Original: {transcript} → Translated: {translated_text}")  # Debugging Output

        return jsonify({'transcript': transcript, 'translated_text': translated_text})
    except Exception as e:
        print(f"Speech-to-Text Error: {e}")
        return jsonify({'error': str(e)}), 500

# 🌍 Real-Time Translation API
@app.route('/translate', methods=['POST'])
def translate_text():
    try:
        data = request.json
        text = data.get('text', '')
        target_lang = data.get('target_lang', 'en')

        if not text:
            return jsonify({'error': 'No text provided for translation'}), 400

        translated_text = GoogleTranslator(source='auto', target=target_lang).translate(text)

        print(f"Translated: {translated_text}")  # Debugging Output

        return jsonify({'translated_text': translated_text})
    except Exception as e:
        print(f"Translation Error: {e}")
        return jsonify({'error': str(e)}), 500

# 🔊 Text-to-Speech API (Real-Time Playback)
@app.route('/text-to-speech', methods=['POST'])
def text_to_speech():
    try:
        data = request.json
        text = data['text']
        target_lang = data.get('target_lang', 'en')  # Default to English

        if not text:
            return jsonify({'error': 'No text provided for speech synthesis'}), 400

        audio_file = "static/translated_audio.mp3"

        # Delete old audio file to prevent caching issues
        if os.path.exists(audio_file):
            os.remove(audio_file)

        tts = gTTS(text=text, lang=target_lang)
        tts.save(audio_file)

        return jsonify({'audio_url': f"/static/translated_audio.mp3"})
    except Exception as e:
        print(f"TTS Error: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run()

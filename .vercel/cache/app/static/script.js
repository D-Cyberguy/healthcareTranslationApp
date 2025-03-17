const BASE_URL = "http://127.0.0.1:5000";
let recognition;

// 🌍 Supported Languages
const LANGUAGES = {
    'en': 'English', 'es': 'Spanish', 'fr': 'French', 'de': 'German', 'zh-cn': 'Chinese',
    'ja': 'Japanese', 'ko': 'Korean', 'ru': 'Russian', 'ar': 'Arabic', 'it': 'Italian',
    'hi': 'Hindi', 'pt': 'Portuguese', 'nl': 'Dutch', 'tr': 'Turkish', 'sv': 'Swedish',
    'pl': 'Polish', 'vi': 'Vietnamese', 'th': 'Thai', 'he': 'Hebrew', 'id': 'Indonesian'
};

// 🎯 Populate language dropdowns
window.onload = function () {
    const inputLangSelect = document.getElementById('input-language');
    const outputLangSelect = document.getElementById('output-language');

    Object.keys(LANGUAGES).forEach(code => {
        const option1 = new Option(LANGUAGES[code], code);
        const option2 = new Option(LANGUAGES[code], code);
        inputLangSelect.add(option1);
        outputLangSelect.add(option2);
    });

    // Set default values
    inputLangSelect.value = "en";  // Default to English
    outputLangSelect.value = "es"; // Default to Spanish
};

// 🎤 Start Live Speech Recording
document.getElementById('start-recording').addEventListener('click', () => {
    if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
        alert("Your browser does not support speech recognition. Please use Chrome or Edge.");
        return;
    }

    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    recognition = new SpeechRecognition();
    recognition.lang = document.getElementById('input-language').value;
    recognition.continuous = true;
    recognition.interimResults = false;

    recognition.start();
    document.getElementById('transcript').value = "Listening...";

    recognition.onresult = async (event) => {
        const transcript = event.results[event.results.length - 1][0].transcript;
        document.getElementById('transcript').value = transcript;

        // 🌍 Send transcript to the backend for translation
        const targetLang = document.getElementById('output-language').value;
        try {
            const response = await fetch(`${BASE_URL}/translate`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ text: transcript, target_lang: targetLang })
            });

            const data = await response.json();
            console.log("Translation API Response:", data);  // Debugging Output

            if (data.translated_text) {
                document.getElementById('translation').value = data.translated_text;
            } else {
                document.getElementById('translation').value = "Translation failed!";
            }
        } catch (error) {
            console.error("Translation Error:", error);
            document.getElementById('translation').value = "Error fetching translation!";
        }
    };

    recognition.onerror = (event) => {
        console.error("Speech recognition error:", event.error);
    };
});

// ⏹ Stop Recording Manually
document.getElementById('stop-recording').addEventListener('click', () => {
    if (recognition) {
        recognition.stop();
        document.getElementById('transcript').value = "Recording stopped.";
    }
});

// 🔊 Speak Translated Text
document.getElementById('speak-translation').addEventListener('click', async () => {
    const textToSpeak = document.getElementById('translation').value;
    if (!textToSpeak) {
        alert("No translated text available to speak.");
        return;
    }

    try {
        const response = await fetch(`${BASE_URL}/text-to-speech`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text: textToSpeak })
        });

        const data = await response.json();

        // Append timestamp to prevent caching issues
        const audio = new Audio(`${data.audio_url}?t=${new Date().getTime()}`);
        audio.play();
    } catch (error) {
        console.error("Error playing translation:", error);
        alert("Error playing translation audio.");
    }
});

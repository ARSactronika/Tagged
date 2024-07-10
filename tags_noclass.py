from flask import Flask, request, jsonify, render_template_string, send_from_directory
import os
from cachetools import TTLCache
import aiohttp
import asyncio
import re

# Define the classes with tags
classes_with_tags = {
    'airblow': ['burst', 'air', 'quick'],
    'Blast': ['loud', 'explosion', 'boom'],
    'Cracklings': ['sharp', 'cracking', 'small'],
    'Cracks': ['loud', 'cracking', 'noise'],
    'Deep combustion': ['intense', 'combustion', 'deep'],
    'Explosion': ['large', 'explosion', 'boom'],
    'Flames': ['burning', 'flames', 'fire'],
    'Ignition': ['starting', 'fire', 'ignition'],
    'Sharp combustion': ['sharp', 'combustion', 'fire'],
    'Spark': ['small', 'spark', 'fire'],
    'Volcano eruption': ['volcanic', 'eruption', 'lava'],
    'Boiling': ['hot', 'water', 'bubbles'],
    'Dive': ['jumping', 'water', 'splash'],
    'Freeze': ['cold', 'ice', 'solid'],
    'Pouring': ['liquid', 'flowing', 'pour'],
    'Heavy rain': ['heavy', 'rain', 'downpour'],
    'Light rain': ['light', 'rain', 'drizzle'],
    'Moderate rain': ['medium', 'rain', 'shower'],
    'Splash': ['water', 'splashing', 'wet'],
    'Long air pressure': ['long', 'pressure', 'steady'],
    'Moderate air pressure': ['medium', 'pressure', 'moderate'],
    'Short air pressure': ['short', 'pressure', 'brief'],
    'Vapour': ['steam', 'vapor', 'gas'],
    'Air whoosh': ['grainy', 'whoosh', 'long'],
    'Moderate grainy whoosh': ['grainy', 'whoosh', 'medium'],
    'Short grainy whoosh': ['grainy', 'whoosh', 'short'],
    'Long slick whoosh': ['slick', 'whoosh', 'long'],
    'Moderate slick whoosh': ['slick', 'whoosh', 'medium'],
    'Short slick whoosh': ['slick', 'whoosh', 'short'],
    'Wind': ['air', 'movement', 'blow'],
    'Land cracking': ['crack', 'ground', 'break'],
    'Earthquake': ['tremor', 'quake', 'shake'],
    'Rock slide': ['rocks', 'sliding', 'landslide'],
    'Tremor': ['small', 'quake', 'vibration'],
    'Buzz': ['electrical', 'buzzing', 'continuous'],
    'Electrocution': ['shock', 'electrocution', 'danger'],
    'Shock-arcs': ['arcs', 'electric', 'jolt'],
    'Big thunderbolt': ['large', 'thunder', 'bolt'],
    'Moderate thunderbolt': ['medium', 'thunder', 'bolt'],
    'Small thunderbolt': ['small', 'thunder', 'bolt'],
    'Zap': ['quick', 'shock', 'jolt'],
    'Breath': ['breathing', 'air', 'inhale'],
    'Chills': ['cold', 'shiver', 'goosebumps'],
    'Heartbeat': ['heart', 'pulse', 'beat'],
    'Stabbing': ['knife', 'attack', 'pierce'],
    'Tachycardia': ['fast', 'heartbeat', 'rapid'],
    'Wound': ['injury', 'blood'],
    'Footsteps': ['walking', 'steps', 'footfall'],
    'Breaking glass': ['glass', 'breaking', 'shatter'],
    'Metal collision': ['metal', 'collision', 'impact'],
    'Plastic collision': ['plastic', 'collision', 'impact'],
    'Rubber collision': ['rubber', 'collision', 'impact'],
    'Wood collision': ['wood', 'collision', 'impact'],
    'Metal friction': ['metal', 'friction', 'scrape'],
    'Plastic friction': ['plastic', 'friction', 'rub'],
    'Rubber friction': ['rubber', 'friction', 'grip'],
    'Wood friction': ['wood', 'friction', 'scrape'],
    'Alarm': ['alert', 'sound', 'warning'],
    'Bouncy click': ['bouncy', 'click', 'springy'],
    'Resonant click': ['resonant', 'click', 'echo'],
    'Rough click': ['rough', 'click', 'harsh'],
    'Engine': ['motor', 'engine', 'power'],
    'Pump': ['liquid', 'pump', 'flow'],
    'Rumble': ['deep', 'rumble', 'vibration'],
    'Scratch': ['surface', 'scratch', 'scrape'],
    'Translate': ['move', 'translate', 'shift'],
    'Zip': ['fast', 'zip', 'quick'],
    'Wipers': ['window', 'wipers', 'swish'],
    'Biohazard': ['danger', 'bio', 'hazard'],
    'Disintegration': ['break', 'apart', 'vanish'],
    'Energy burst': ['energy', 'burst', 'powerful'],
    'Healing': ['recover', 'health', 'repair'],
    'Injured': ['hurt', 'injury', 'pain'],
    'Madness': ['crazy', 'insane', 'psychotic'],
    'Magic spell': ['spell', 'magic', 'enchant'],
    'Materialisation': ['appear', 'materialize', 'form'],
    'Poison': ['toxic', 'poison', 'venom'],
    'Teleportation': ['move', 'teleport', 'instant'],
    'Time freeze': ['stop', 'time', 'freeze'],
    'Time travel': ['move', 'time', 'travel'],
    'Time warp': ['distort', 'time', 'warp'],
    'Comet': ['space', 'comet', 'meteor'],
    'Pulse': ['energy', 'pulse', 'wave'],
    'Sparkles': ['shine', 'sparkle', 'glow'],
    'Buttons': ['press', 'button', 'click'],
    'Hover': ['hover', 'ui', 'pointer'],
    'Notifications': ['alert', 'ui', 'notification'],
    'Scroll': ['move', 'scroll', 'navigate'],
    'Slider': ['slide', 'ui', 'adjust'],
    'Snap': ['snap', 'ui', 'click'],
    'Swipe': ['swipe', 'ui', 'gesture'],
    'Grenade': ['explosive', 'grenade', 'boom'],
    'Knives': ['sharp', 'knife', 'stab'],
    'Machinegun': ['automatic', 'gun', 'rapid-fire'],
    'Pistol': ['small', 'gun', 'handgun'],
    'Rifles': ['long', 'gun', 'rifle'],
    'Shotgun': ['spread', 'gun', 'shotgun'],
    'Smgs': ['submachine', 'gun', 'rapid'],
    'Sniper': ['long', 'gun', 'sniper'],
    'Bullet': ['ammo', 'bullet', 'projectile']
}

# Define the classes for position classification
position_classes = ["front", "back", "right", "left", "top", "bottom"]

# Define the Hugging Face API endpoint and API key
API_URL = "https://api-inference.huggingface.co/models/facebook/bart-large-mnli"
API_KEY = "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"  # Hugging Face API key

# Initialize Flask app
app = Flask(__name__)

# Authentication key
AUTH_KEY = 'my_secret_auth_key'

# Directory containing the .wav files
AUDIO_DIR = "audio_files"
os.makedirs(AUDIO_DIR, exist_ok=True)

# Caching mechanism
cache = TTLCache(maxsize=100, ttl=300)

# Define the HTML template for the interactive interface
html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Text to Haptics</title>
</head>
<body>
    <h1>Text to Haptics</h1>
    <form id="classify-form">
        <label for="text">Enter text:</label><br><br>
        <input type="text" id="text" name="text" size="50"><br><br>
        <input type="submit" value="Classify">
    </form>
    <h2>Result:</h2>
    <p id="result"></p>
    <audio id="audio-player" controls></audio>
    <script>
        document.getElementById('classify-form').onsubmit = async function(event) {
            event.preventDefault();
            const text = document.getElementById('text').value;
            const response = await fetch('/classify', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': '{{ auth_key }}'
                },
                body: JSON.stringify({ text: text })
            });
            const result = await response.json();
            const resultElement = document.getElementById('result');
            const audioPlayer = document.getElementById('audio-player');
            
            if (result.sub_class && result.position) {
                resultElement.innerText = `Subclass: ${result.sub_class}, Position: ${result.position}, First Position: ${result.first_position}, Second Position: ${result.second_position}`;
                audioPlayer.src = `/audio/${result.sub_class}.wav`;
                audioPlayer.play();
                console.log(`Classified as: Subclass: ${result.sub_class}, Position: ${result.position}, First Position: ${result.first_position}, Second Position: ${result.second_position}`);
            } else {
                resultElement.innerText = `Error: ${result.error}`;
                audioPlayer.src = '';
            }
        }
    </script>
</body>
</html>
"""

# Function to classify text using Hugging Face API
async def classify_text(session, text, candidate_labels):
    headers = {
        'Authorization': f'Bearer {API_KEY}',
        'Content-Type': 'application/json'
    }
    payload = {
        "inputs": text,
        "parameters": {
            "candidate_labels": candidate_labels
        }
    }
    async with session.post(API_URL, headers=headers, json=payload) as response:
        if response.status == 200:
            result = await response.json()
            predicted_class = result['labels'][0]
            return predicted_class, result['scores'][0]
        else:
            raise Exception(f"API request failed with status code {response.status}: {await response.text()}")

# Function to classify text in chunks
async def classify_text_in_chunks(session, text, candidate_labels):
    best_class = None
    best_score = -1
    chunk_size = 10
    for i in range(0, len(candidate_labels), chunk_size):
        chunk = candidate_labels[i:i+chunk_size]
        predicted_class, score = await classify_text(session, text, chunk)
        if score > best_score:
            best_score = score
            best_class = predicted_class
    return best_class

# Function to preprocess text
def preprocess_text(text):
    text = text.lower()
    text = re.sub(r'\s+', ' ', text)
    return text

# Function to extract positions based on keywords
def extract_positions(text):
    pattern = re.compile(r'\b(front|back|left|right|top|bottom)\b')
    positions = pattern.findall(text)
    return positions

# Function to determine the first and second positions
def determine_positions(positions):
    if len(positions) >= 2:
        first_position = positions[0]
        second_position = positions[1]
    else:
        first_position = None
        second_position = None
    return first_position, second_position

# Serve the HTML interface
@app.route('/')
def index():
    return render_template_string(html_template, auth_key=AUTH_KEY)

# Define the API endpoint
@app.route('/classify', methods=['POST'])
async def classify():
    auth_key = request.headers.get('Authorization')
    if auth_key != AUTH_KEY:
        return jsonify({'error': 'Unauthorized access'}), 401

    data = request.get_json()
    text = data.get('text', '')
    if not text:
        return jsonify({'error': 'No text provided'}), 400

    cache_key = text
    if cache_key in cache:
        return jsonify(cache[cache_key])

    async with aiohttp.ClientSession() as session:
        try:
            # Classify the subclass with tags
            class_tags = [f"{cls}: {' '.join(tags)}" for cls, tags in classes_with_tags.items()]
            sub_class = await classify_text_in_chunks(session, text, class_tags)
            sub_class_name = sub_class.split(":")[0]

            # Determine position
            position = await classify_text_in_chunks(session, text, position_classes)

            # Detect transitions
            preprocessed_text = preprocess_text(text)
            positions = extract_positions(preprocessed_text)
            first_position, second_position = determine_positions(positions)

            result = {
                'sub_class': sub_class_name,
                'position': position,
                'first_position': first_position,
                'second_position': second_position
            }
            cache[cache_key] = result
            return jsonify(result)
        except Exception as e:
            return jsonify({'error': str(e)}), 500

# Serve audio files
@app.route('/audio/<filename>')
def serve_audio(filename):
    return send_from_directory(AUDIO_DIR, filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)

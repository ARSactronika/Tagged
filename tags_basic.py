from flask import Flask, request, jsonify, render_template_string, send_from_directory
import os
from cachetools import TTLCache
import aiohttp
import asyncio
import re

# Define the class hierarchy with tags
class_hierarchy = {
    'Fire': {
        'tags': ['explosion', 'combustion', 'flames', 'ignition'],
        'subclasses': {
            'Airblow': ['burst', 'air'],
            'Blast': ['loud', 'explosion'],
            'Cracklings': ['sharp', 'cracking'],
            'Cracks': ['loud', 'cracking'],
            'Deep combustion': ['intense', 'combustion'],
            'Explosion': ['large', 'explosion'],
            'Flames': ['burning', 'flames'],
            'Ignition': ['starting', 'fire'],
            'Sharp combustion': ['sharp', 'combustion'],
            'Spark': ['small', 'spark'],
            'Volcano-eruption': ['volcanic', 'eruption']
        }
    },
    'Water': {
        'tags': ['liquid', 'movement', 'splash'],
        'subclasses': {
            'Boiling': ['hot', 'water'],
            'Dive': ['jumping', 'water'],
            'Freeze': ['cold', 'ice'],
            'Pouring': ['liquid', 'flowing'],
            'Rain-flow-heavy': ['heavy', 'rain'],
            'Rain-flow-light': ['light', 'rain'],
            'Rain-flow-medium': ['medium', 'rain'],
            'Splash': ['water', 'splashing']
        }
    },
    'Air': {
        'tags': ['wind', 'pressure', 'movement'],
        'subclasses': {
            'Pressure-long': ['long', 'pressure'],
            'Pressure-med': ['medium', 'pressure'],
            'Pressure-short': ['short', 'pressure'],
            'Vapour': ['steam', 'vapor'],
            'Whoosh-grainy-long': ['grainy', 'whoosh', 'long'],
            'Whoosh-grainy-med': ['grainy', 'whoosh', 'medium'],
            'Whoosh-grainy-short': ['grainy', 'whoosh', 'short'],
            'Whoosh-slick-long': ['slick', 'whoosh', 'long'],
            'Whoosh-slick-med': ['slick', 'whoosh', 'medium'],
            'Whoosh-slick-short': ['slick', 'whoosh', 'short'],
            'Wind': ['air', 'movement']
        }
    },
    'Land': {
        'tags': ['earth', 'movement', 'ground'],
        'subclasses': {
            'Cracking': ['crack', 'ground'],
            'Earthquake': ['tremor', 'quake'],
            'Rockslide': ['rocks', 'sliding'],
            'Tremor': ['small', 'quake']
        }
    },
    'Electrical': {
        'tags': ['electricity', 'shock', 'buzz'],
        'subclasses': {
            'Buzz': ['electrical', 'buzzing'],
            'Electrocution': ['shock', 'electrocution'],
            'Shock-arcs': ['arcs', 'electric'],
            'Spark': ['small', 'spark'],
            'Thunderbolt-big': ['large', 'thunder'],
            'Thunderbolt-medium': ['medium', 'thunder'],
            'Thunderbolt-small': ['small', 'thunder'],
            'Zap': ['quick', 'shock']
        }
    },
    'Living': {
        'tags': ['biological', 'life', 'body'],
        'subclasses': {
            'Breath': ['breathing', 'air'],
            'Chills': ['cold', 'shiver'],
            'Heartbeat': ['heart', 'pulse'],
            'Stabbing': ['knife', 'attack'],
            'Tachycardia': ['fast', 'heartbeat'],
            'Wound': ['injury', 'cut'],
            'Footsteps': ['walking', 'steps']
        }
    },
    'Materials': {
        'tags': ['material', 'interaction', 'friction'],
        'subclasses': {
            'Breaking-glass': ['glass', 'breaking'],
            'Collision-metal': ['metal', 'collision'],
            'Collision-plastic': ['plastic', 'collision'],
            'Collision-rubber': ['rubber', 'collision'],
            'Collision-wood': ['wood', 'collision'],
            'Friction-metal': ['metal', 'friction'],
            'Friction-plastic': ['plastic', 'friction'],
            'Friction-rubber': ['rubber', 'friction'],
            'Friction-wood': ['wood', 'friction']
        }
    },
    'Mechanics': {
        'tags': ['machine', 'movement', 'operation'],
        'subclasses': {
            'Alarm': ['alert', 'sound'],
            'Click-bouncy': ['bouncy', 'click'],
            'Click-resonant': ['resonant', 'click'],
            'Click-rough': ['rough', 'click'],
            'Engine': ['motor', 'engine'],
            'Pump': ['liquid', 'pump'],
            'Rumble': ['deep', 'rumble'],
            'Scratch': ['surface', 'scratch'],
            'Translate': ['move', 'translate'],
            'Zip': ['fast', 'zip'],
            'Wipers': ['window', 'wipers']
        }
    },
    'Character': {
        'tags': ['fantasy', 'action', 'state'],
        'subclasses': {
            'Biohazard': ['danger', 'bio'],
            'Disintegration': ['break', 'apart'],
            'Energy-burst': ['energy', 'burst'],
            'Healing': ['recover', 'health'],
            'Injured': ['hurt', 'injury'],
            'Madness': ['crazy', 'insane'],
            'Magic-spell': ['spell', 'magic'],
            'Materialisation': ['appear', 'materialize'],
            'Poison': ['toxic', 'poison'],
            'Teleportation': ['move', 'teleport'],
            'Time-freeze': ['stop', 'time'],
            'Time-travel': ['move', 'time'],
            'Time-warp': ['distort', 'time'],
            'Comet': ['space', 'comet'],
            'Pulse': ['energy', 'pulse'],
            'Sparkles': ['shine', 'sparkle']
        }
    },
    'Interface': {
        'tags': ['ui', 'interaction', 'click'],
        'subclasses': {
            'Buttons': ['press', 'button'],
            'Hover': ['hover', 'ui'],
            'Notifications': ['alert', 'ui'],
            'Scroll': ['move', 'scroll'],
            'Slider': ['slide', 'ui'],
            'Snap': ['snap', 'ui'],
            'Swipe': ['swipe', 'ui']
        }
    },
    'Weapons': {
        'tags': ['weapon', 'attack', 'gun'],
        'subclasses': {
            'Grenade': ['explosive', 'grenade'],
            'Knifes': ['sharp', 'knife'],
            'Machinegun': ['automatic', 'gun'],
            'Pistol': ['small', 'gun'],
            'Rifles': ['long', 'gun'],
            'Shotgun': ['spread', 'gun'],
            'Smgs': ['submachine', 'gun'],
            'Sniper': ['long', 'gun'],
            'Bullet': ['ammo', 'bullet']
        }
    }
}

# Extract main classes
main_classes = list(class_hierarchy.keys())

# Define tags for main classes
main_class_tags = [f"{main_class}: {' '.join(details['tags'])}" for main_class, details in class_hierarchy.items()]

# Extract subclasses for each main class
subclass_tags = {main_class: [f"{subclass}: {' '.join(tags)}" for subclass, tags in details['subclasses'].items()] for main_class, details in class_hierarchy.items()}

# Define the classes for position classification
position_classes = ["front", "back", "right", "left","top", "bottom"]

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
            
            if (result.main_class && result.sub_class && result.position) {
                resultElement.innerText = `Main Class: ${result.main_class}, Subclass: ${result.sub_class}, Position: ${result.position}, First Position: ${result.first_position}, Second Position: ${result.second_position}`;
                audioPlayer.src = `/audio/${result.sub_class}.wav`;
                audioPlayer.play();
                console.log(`Classified as: ${result.main_class}, Subclass: ${result.sub_class}, Position: ${result.position}, First Position: ${result.first_position}, Second Position: ${result.second_position}`);
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

    data = request.get_json()  # Synchronous method, no await
    text = data.get('text', '')
    if not text:
        return jsonify({'error': 'No text provided'}), 400

    cache_key = text
    if cache_key in cache:
        return jsonify(cache[cache_key])

    async with aiohttp.ClientSession() as session:
        try:
            # Step 1: Classify the main class with tags
            main_class = await classify_text_in_chunks(session, text, main_class_tags)
            main_class_name = main_class.split(":")[0]

            # Step 2: Classify the subclass within the determined main class with tags
            sub_class_candidates = subclass_tags[main_class_name]
            sub_class = await classify_text_in_chunks(session, text, sub_class_candidates)
            sub_class_name = sub_class.split(":")[0]

            # Step 3: Determine position
            position = await classify_text_in_chunks(session, text, position_classes)

            # Step 4: Detect transitions
            preprocessed_text = preprocess_text(text)
            positions = extract_positions(preprocessed_text)
            first_position, second_position = determine_positions(positions)

            result = {
                'main_class': main_class_name,
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

import os
from flask import Flask, request, jsonify, send_file
import tempfile
import shutil
from datetime import datetime
import numpy as np
import soundfile as sf
from kokoro_onnx import Kokoro
from misaki import espeak
from misaki.espeak import EspeakG2P
import io

# Configuración del servicio
HOST = os.getenv("FLASK_HOST", "0.0.0.0")
PORT = int(os.getenv("FLASK_PORT", 5002))
DEFAULT_LANGUAGE = os.getenv("DEFAULT_LANGUAGE", "es")  # Español por defecto
DEFAULT_VOICE = os.getenv("DEFAULT_VOICE", "ef_dora")  # Voz por defecto para español
DEBUG_AUDIO = os.getenv("DEBUG_AUDIO", "true").lower() == "true"  # Guardar audio para debug

# Rutas de los modelos
MODEL_PATH = "/app/models/kokoro-v1.0.onnx"
VOICES_PATH = "/app/models/voices-v1.0.bin"

# Crear directorio para audio de debug
DEBUG_DIR = "/app/debug_audio"
if DEBUG_AUDIO and not os.path.exists(DEBUG_DIR):
    os.makedirs(DEBUG_DIR, exist_ok=True)

print(f"[*] Iniciando Kokoro TTS v1.0 optimizado para español")
print(f"[*] Idioma por defecto: {DEFAULT_LANGUAGE}")
print(f"[*] Voz por defecto: {DEFAULT_VOICE}")
print(f"[*] Debug de audio: {'ACTIVADO' if DEBUG_AUDIO else 'DESACTIVADO'}")
if DEBUG_AUDIO:
    print(f"[*] Directorio de debug: {DEBUG_DIR}")

# Cargar modelo Kokoro v1.0
try:
    # Configurar GPU para ONNX Runtime si está disponible
    import onnxruntime as ort
    import os
    
    # Verificar si CUDA está disponible
    cuda_available = 'CUDAExecutionProvider' in ort.get_available_providers()
    
    if cuda_available:
        print(f"[*] GPU/CUDA detectada, configurando ONNX Runtime para GPU")
        # Configurar variable de entorno para kokoro-onnx
        os.environ['ONNX_PROVIDER'] = 'CUDAExecutionProvider'
        kokoro = Kokoro(MODEL_PATH, VOICES_PATH)
        print(f"[*] Kokoro v1.0 cargado exitosamente con GPU desde {MODEL_PATH}")
    else:
        print(f"[*] GPU/CUDA no disponible, usando CPU")
        # Asegurar que use CPU
        os.environ['ONNX_PROVIDER'] = 'CPUExecutionProvider'
        kokoro = Kokoro(MODEL_PATH, VOICES_PATH)
        print(f"[*] Kokoro v1.0 cargado exitosamente con CPU desde {MODEL_PATH}")
        
except Exception as e:
    print(f"[!] Error al cargar Kokoro v1.0: {e}")
    kokoro = None

# Configurar G2P (Grapheme-to-Phoneme) para diferentes idiomas
g2p_processors = {}

def get_g2p_processor(language):
    """Obtiene o crea el procesador G2P para un idioma específico"""
    if language not in g2p_processors:
        try:
            if language == "es":
                fallback = espeak.EspeakFallback(british=False)
                g2p_processors[language] = EspeakG2P(language="es")
            elif language == "en":
                fallback = espeak.EspeakFallback(british=False)
                g2p_processors[language] = EspeakG2P(language="en")
            elif language == "fr":
                fallback = espeak.EspeakFallback(british=False)
                g2p_processors[language] = EspeakG2P(language="fr")
            elif language == "it":
                fallback = espeak.EspeakFallback(british=False)
                g2p_processors[language] = EspeakG2P(language="it")
            else:
                # Fallback para otros idiomas
                fallback = espeak.EspeakFallback(british=False)
                g2p_processors[language] = EspeakG2P(language="en")
        except Exception as e:
            print(f"[!] Error creando G2P para {language}: {e}")
            # Fallback a inglés
            fallback = espeak.EspeakFallback(british=False)
            g2p_processors[language] = EspeakG2P(language="en")
    
    return g2p_processors[language]

app = Flask(__name__)

# Mapeo de idiomas para Kokoro v1.0
LANGUAGE_MAP = {
    'es': 'e',  # Spanish
    'en': 'a',  # American English
    'fr': 'f',  # French
    'it': 'i',  # Italian
    'pt': 'p',  # Brazilian Portuguese
    'hi': 'h',  # Hindi
    'ja': 'j',  # Japanese
    'zh': 'z'   # Mandarin Chinese
}

# Voces disponibles en Kokoro v1.0 organizadas por idioma
AVAILABLE_VOICES = {
    'es': [  # Español
        'ef_dora',    # Voz femenina en español
        'em_alex',    # Voz masculina en español
        'em_santa'    # Voz masculina alternativa en español
    ],
    'en': [  # Inglés Americano
        'af_heart', 'af_alloy', 'af_aoede', 'af_bella', 'af_jessica', 'af_kore', 
        'af_nicole', 'af_nova', 'af_river', 'af_sarah', 'af_sky',
        'am_adam', 'am_echo', 'am_liam', 'am_michael', 'am_onyx', 'am_puck', 
        'am_sage', 'am_shimmer',
        # Inglés Británico
        'bf_alice', 'bf_emma', 'bf_isabella', 'bf_lily',
        'bm_daniel', 'bm_george', 'bm_lewis', 'bm_william'
    ],
    'fr': [  # Francés
        'ff_siwis'
    ],
    'hi': [  # Hindi
        'hf_alpha', 'hf_beta', 'hm_omega', 'hm_psi'
    ],
    'it': [  # Italiano
        'if_sara', 'im_nicola'
    ],
    'pt': [  # Portugués brasileño
        'pf_dora', 'pm_alex', 'pm_santa'
    ],
    'ja': [  # Japonés
        'jf_alpha', 'jf_gongitsune', 'jf_nezumi', 'jf_tebukuro', 'jm_kumo'
    ],
    'zh': [  # Chino mandarín
        'zf_xiaobei', 'zf_xiaoni', 'zf_xiaoxiao', 'zf_xiaoyi',
        'zm_yunjian', 'zm_yunxi', 'zm_yunxia', 'zm_yunyang'
    ]
}

# Voces recomendadas por idioma
VOICE_RECOMMENDATIONS = {
    'es': {  # Español
        'female': ['ef_dora'],
        'male': ['em_alex', 'em_santa'],
        'default': 'ef_dora'
    },
    'en': {  # Inglés
        'female': ['af_bella', 'af_heart', 'af_nicole', 'bf_emma'],
        'male': ['am_michael', 'am_adam', 'bm_george'],
        'default': 'af_bella'
    },
    'fr': {  # Francés
        'female': ['ff_siwis'],
        'male': [],
        'default': 'ff_siwis'
    },
    'hi': {  # Hindi
        'female': ['hf_alpha', 'hf_beta'],
        'male': ['hm_omega', 'hm_psi'],
        'default': 'hf_alpha'
    },
    'it': {  # Italiano
        'female': ['if_sara'],
        'male': ['im_nicola'],
        'default': 'if_sara'
    },
    'pt': {  # Portugués
        'female': ['pf_dora'],
        'male': ['pm_alex', 'pm_santa'],
        'default': 'pf_dora'
    },
    'ja': {  # Japonés
        'female': ['jf_alpha', 'jf_gongitsune', 'jf_nezumi', 'jf_tebukuro'],
        'male': ['jm_kumo'],
        'default': 'jf_alpha'
    },
    'zh': {  # Chino
        'female': ['zf_xiaobei', 'zf_xiaoni', 'zf_xiaoxiao', 'zf_xiaoyi'],
        'male': ['zm_yunjian', 'zm_yunxi', 'zm_yunxia', 'zm_yunyang'],
        'default': 'zf_xiaobei'
    }
}

def get_optimal_voice_for_language(language, voice=None, gender_preference=None):
    """Selecciona la voz óptima según el idioma y preferencias"""
    
    # Obtener voces disponibles para el idioma
    lang_voices = AVAILABLE_VOICES.get(language, AVAILABLE_VOICES['es'])
    
    # Si se especifica una voz, validarla
    if voice and voice in lang_voices:
        return voice
    
    # Obtener recomendaciones para el idioma
    lang_recommendations = VOICE_RECOMMENDATIONS.get(language, VOICE_RECOMMENDATIONS['es'])
    
    # Si se especifica preferencia de género
    if gender_preference in ['female', 'male'] and gender_preference in lang_recommendations:
        recommended_voices = lang_recommendations[gender_preference]
        for recommended_voice in recommended_voices:
            if recommended_voice in lang_voices:
                return recommended_voice
    
    # Devolver la voz por defecto del idioma
    default_voice = lang_recommendations.get('default', DEFAULT_VOICE)
    if default_voice in lang_voices:
        return default_voice
    
    # Fallback a la primera voz disponible del idioma
    if lang_voices:
        return lang_voices[0]
    
    # Fallback final
    return DEFAULT_VOICE

def synthesize_with_kokoro_v1(text, language="es", voice="ef_dora", speed=1.0):
    """Sintetiza audio usando Kokoro v1.0 con ONNX Runtime"""
    try:
        if kokoro is None:
            raise Exception("Kokoro v1.0 no disponible")
        
        print(f"[DEBUG] Sintetizando con Kokoro v1.0: lang={language}, voice={voice}, speed={speed}")
        
        # Obtener procesador G2P para el idioma
        g2p = get_g2p_processor(language)
        
        # Convertir texto a fonemas
        phonemes, _ = g2p(text)
        print(f"[DEBUG] Fonemas generados: {phonemes[:100]}...")
        
        # Generar audio usando Kokoro v1.0
        samples, sample_rate = kokoro.create(phonemes, voice, is_phonemes=True, speed=speed)
        
        print(f"[DEBUG] Audio generado: {len(samples)} muestras a {sample_rate}Hz")
        
        return samples, sample_rate
        
    except Exception as e:
        print(f"[!] Error en Kokoro v1.0: {e}")
        # Fallback a síntesis simple
        return synthesize_fallback(text, speed)

def synthesize_fallback(text, speed=1.0):
    """Síntesis de respaldo usando espeak (más básica pero funcional)"""
    import subprocess
    
    try:
        # Usar espeak como fallback
        temp_file = tempfile.mktemp(suffix=".wav")
        cmd = [
            "espeak", 
            "-s", str(int(175 * speed)),  # Velocidad
            "-v", "es",  # Idioma español
            "-w", temp_file,  # Output file
            text
        ]
        
        subprocess.run(cmd, check=True, capture_output=True)
        
        # Leer el archivo generado
        audio_data, sample_rate = sf.read(temp_file)
        os.unlink(temp_file)
        
        return audio_data, sample_rate
    except Exception as e:
        print(f"[!] Error en fallback: {e}")
        # Generar silencio como último recurso
        duration = len(text.split()) * 0.5  # ~0.5s por palabra
        sample_rate = 22050
        silence = np.zeros(int(duration * sample_rate))
        return silence, sample_rate

@app.route("/synthesize", methods=["POST"])
def synthesize():
    data = request.get_json()
    
    if not data or "text" not in data:
        return jsonify({"error": "No text provided"}), 400

    text = data.get("text", "").strip()
    if not text:
        return jsonify({"error": "Empty text"}), 400

    # Obtener parámetros
    language = data.get("language", DEFAULT_LANGUAGE)
    requested_voice = data.get("voice")
    speed = float(data.get("speed", 1.0))
    gender_preference = data.get("gender_preference")  # 'female', 'male', o None
    
    # Seleccionar voz óptima para el idioma
    voice = get_optimal_voice_for_language(language, requested_voice, gender_preference)
    
    print(f"[*] Sintetizando (Kokoro v1.0): '{text[:50]}...' [Lang: {language}, Voz: {voice}, Speed: {speed}]")

    try:
        # Síntesis con Kokoro v1.0
        audio_data, sample_rate = synthesize_with_kokoro_v1(text, language, voice, speed)
        
        # Generar archivo temporal
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
        temp_path = tempfile.mktemp(suffix=".wav")
        
        # Guardar audio
        sf.write(temp_path, audio_data, sample_rate)

        # Guardar audio para debug si está activado
        debug_filename = None
        if DEBUG_AUDIO:
            debug_filename = f"kokoro_v1_{timestamp}.wav"
            debug_path = os.path.join(DEBUG_DIR, debug_filename)
            shutil.copy2(temp_path, debug_path)
            print(f"[DEBUG] Audio guardado: {debug_filename}")

        # Enviar el archivo de audio
        return send_file(temp_path, 
                        mimetype="audio/wav", 
                        as_attachment=True,
                        download_name=f"kokoro_v1_{timestamp}.wav")

    except Exception as e:
        print(f"[!] Error en síntesis: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/synthesize_json", methods=["POST"])
def synthesize_json():
    """Endpoint que devuelve respuesta JSON con metadata en lugar del archivo"""
    data = request.get_json()
    
    if not data or "text" not in data:
        return jsonify({"error": "No text provided"}), 400

    text = data.get("text", "").strip()
    if not text:
        return jsonify({"error": "Empty text"}), 400

    # Obtener parámetros
    language = data.get("language", DEFAULT_LANGUAGE)
    requested_voice = data.get("voice")
    speed = float(data.get("speed", 1.0))
    gender_preference = data.get("gender_preference")
    
    # Seleccionar voz óptima
    voice = get_optimal_voice_for_language(language, requested_voice, gender_preference)
    
    print(f"[*] Sintetizando JSON (Kokoro v1.0): '{text[:50]}...' [Lang: {language}, Voice: {voice}]")

    try:
        # Síntesis con Kokoro v1.0
        audio_data, sample_rate = synthesize_with_kokoro_v1(text, language, voice, speed)
        
        # Calcular duración
        duration = len(audio_data) / sample_rate

        # Guardar audio para debug si está activado
        debug_filename = None
        if DEBUG_AUDIO:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
            debug_filename = f"kokoro_v1_{timestamp}.wav"
            debug_path = os.path.join(DEBUG_DIR, debug_filename)
            sf.write(debug_path, audio_data, sample_rate)
            print(f"[DEBUG] Audio guardado: {debug_filename}")

        response_data = {
            "success": True,
            "text": text,
            "language": language,
            "voice": voice,
            "audio_duration": duration,
            "sample_rate": sample_rate,
            "model": "kokoro-v1.0",
            "speed": speed
        }
        
        if DEBUG_AUDIO and debug_filename:
            response_data["debug_audio_file"] = debug_filename
            response_data["debug_audio_url"] = f"/debug/audio/{debug_filename}"

        return jsonify(response_data)

    except Exception as e:
        print(f"[!] Error en síntesis: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/voices", methods=["GET"])
def list_voices():
    """Lista las voces disponibles en Kokoro v1.0 organizadas por idioma"""
    language = request.args.get("language", "all")
    
    if language == "all":
        # Devolver todas las voces organizadas por idioma
        return jsonify({
            "voices_by_language": AVAILABLE_VOICES,
            "recommendations": VOICE_RECOMMENDATIONS,
            "default_voice": DEFAULT_VOICE,
            "total_voices": sum(len(voices) for voices in AVAILABLE_VOICES.values()),
            "model_version": "v1.0"
        })
    else:
        # Devolver voces para un idioma específico
        voices = AVAILABLE_VOICES.get(language, [])
        recommendations = VOICE_RECOMMENDATIONS.get(language, {})
        return jsonify({
            "language": language,
            "voices": voices,
            "recommendations": recommendations,
            "total": len(voices),
            "model_version": "v1.0"
        })

@app.route("/languages", methods=["GET"])
def list_languages():
    """Lista los idiomas soportados"""
    return jsonify({
        "supported_languages": list(LANGUAGE_MAP.keys()),
        "language_names": {
            'es': 'Español',
            'en': 'English',
            'fr': 'Français',
            'it': 'Italiano',
            'pt': 'Português',
            'hi': 'हिन्दी',
            'ja': '日本語',
            'zh': '中文'
        },
        "default_language": DEFAULT_LANGUAGE,
        "voices_per_language": {lang: len(voices) for lang, voices in AVAILABLE_VOICES.items()},
        "model_version": "v1.0"
    })

@app.route("/batch_synthesize", methods=["POST"])
def batch_synthesize():
    """Síntesis por lotes - múltiples textos de una vez"""
    data = request.get_json()
    
    if not data or "texts" not in data:
        return jsonify({"error": "No texts array provided"}), 400

    texts = data.get("texts", [])
    if not texts:
        return jsonify({"error": "Empty texts array"}), 400

    # Parámetros comunes
    language = data.get("language", DEFAULT_LANGUAGE)
    requested_voice = data.get("voice")
    speed = float(data.get("speed", 1.0))
    gender_preference = data.get("gender_preference")
    
    # Seleccionar voz óptima
    voice = get_optimal_voice_for_language(language, requested_voice, gender_preference)

    print(f"[*] Síntesis por lotes: {len(texts)} textos")

    results = []
    total_duration = 0

    for i, text in enumerate(texts):
        text = text.strip()
        if not text:
            results.append({"error": "Empty text", "index": i})
            continue

        try:
            # Síntesis
            audio_data, sample_rate = synthesize_with_kokoro_v1(text, language, voice, speed)
            duration = len(audio_data) / sample_rate
            total_duration += duration

            # Debug
            debug_filename = None
            if DEBUG_AUDIO:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
                debug_filename = f"batch_v1_{i}_{timestamp}.wav"
                debug_path = os.path.join(DEBUG_DIR, debug_filename)
                sf.write(debug_path, audio_data, sample_rate)

            result = {
                "index": i,
                "text": text,
                "success": True,
                "duration": duration,
                "sample_rate": sample_rate
            }
            
            if DEBUG_AUDIO and debug_filename:
                result["debug_audio_file"] = debug_filename
                result["debug_audio_url"] = f"/debug/audio/{debug_filename}"
                
            results.append(result)

        except Exception as e:
            results.append({
                "index": i,
                "text": text,
                "success": False,
                "error": str(e)
            })

    successful = sum(1 for r in results if r.get("success", False))
    
    return jsonify({
        "results": results,
        "total_texts": len(texts),
        "successful": successful,
        "total_duration": total_duration,
        "model": "kokoro-v1.0",
        "voice": voice,
        "language": language
    })

@app.route("/debug/audio/<filename>", methods=["GET"])
def get_debug_audio(filename):
    """Obtiene un archivo de audio de debug"""
    if not DEBUG_AUDIO:
        return jsonify({"error": "Debug audio disabled"}), 404
    
    file_path = os.path.join(DEBUG_DIR, filename)
    if os.path.exists(file_path):
        return send_file(file_path, mimetype="audio/wav")
    else:
        return jsonify({"error": "File not found"}), 404

@app.route("/debug/audio", methods=["GET"])
def list_debug_audio():
    """Lista los archivos de audio de debug"""
    if not DEBUG_AUDIO:
        return jsonify({"error": "Debug audio disabled"}), 404
    
    try:
        files = []
        for filename in os.listdir(DEBUG_DIR):
            if filename.endswith('.wav'):
                file_path = os.path.join(DEBUG_DIR, filename)
                stat = os.stat(file_path)
                files.append({
                    "filename": filename,
                    "size": stat.st_size,
                    "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                    "url": f"/debug/audio/{filename}"
                })
        
        return jsonify({
            "debug_files": sorted(files, key=lambda x: x["created"], reverse=True),
            "total_files": len(files)
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/health", methods=["GET"])
def health():
    """Health check del servicio"""
    return jsonify({
        "status": "healthy",
        "model": "kokoro-v1.0",
        "model_status": "loaded" if kokoro is not None else "error",
        "model_path": MODEL_PATH,
        "voices_path": VOICES_PATH,
        "available_voices": sum(len(voices) for voices in AVAILABLE_VOICES.values()),
        "supported_languages": len(LANGUAGE_MAP),
        "default_language": DEFAULT_LANGUAGE,
        "default_voice": DEFAULT_VOICE,
        "debug_audio_enabled": DEBUG_AUDIO,
        "version": "1.0"
    })

if __name__ == "__main__":
    app.run(host=HOST, port=PORT, debug=False) 
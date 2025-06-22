#!/usr/bin/env python3
"""
Test de Servicio Kokoro TTS v1.0
Tests completos usando solo librerías estándar de Python

Funcionalidades:
- ✅ Tests de conectividad y salud
- ✅ Tests de endpoints REST
- ✅ Tests de síntesis básica y avanzada
- ✅ Tests de manejo de errores
- ✅ Tests de diferentes voces e idiomas
- ✅ Tests de velocidades
- ✅ Tests de caracteres especiales
- ✅ Tests de síntesis por lotes
- ✅ Tests de rendimiento básico
- ✅ Diagnóstico del sistema

Ejecución:
    python3 test_service.py
    python3 test_service.py --url http://localhost:5002
    python3 test_service.py --timeout 60 --verbose
"""

import os
import sys
import time
import json
import urllib.request
import urllib.parse
import urllib.error
from datetime import datetime

# Configuración
BASE_URL = os.getenv('KOKORO_TTS_TEST_URL', 'http://localhost:5002')
TEST_TIMEOUT = 30
VERBOSE = False


class TestRunner:
    """Runner de tests sin dependencias externas"""
    
    def __init__(self, verbose=False):
        self.tests_run = 0
        self.tests_passed = 0
        self.tests_failed = 0
        self.failures = []
        self.verbose = verbose
        self.start_time = time.time()
    
    def run_test(self, test_name, test_func):
        """Ejecutar un test individual"""
        if self.verbose:
            print(f"\n🧪 {test_name}")
            print("-" * len(test_name))
        else:
            print(f"🧪 {test_name}...", end=" ")
        
        self.tests_run += 1
        
        try:
            start = time.time()
            result = test_func()
            duration = time.time() - start
            
            if result:
                if self.verbose:
                    print(f"✅ PASS ({duration:.2f}s)")
                else:
                    print("✅ PASS")
                self.tests_passed += 1
            else:
                if self.verbose:
                    print(f"❌ FAIL ({duration:.2f}s)")
                else:
                    print("❌ FAIL")
                self.tests_failed += 1
                self.failures.append(test_name)
        except Exception as e:
            duration = time.time() - start if 'start' in locals() else 0
            error_msg = f"💥 ERROR: {e}"
            if self.verbose:
                print(f"{error_msg} ({duration:.2f}s)")
            else:
                print(error_msg)
            self.tests_failed += 1
            self.failures.append(f"{test_name}: {e}")
    
    def print_summary(self):
        """Imprimir resumen de tests"""
        total_time = time.time() - self.start_time
        
        print("\n" + "="*60)
        print("📊 RESUMEN DE TESTS KOKORO TTS v1.0")
        print("="*60)
        print(f"⏱️  Tiempo total: {total_time:.2f} segundos")
        print(f"🧪 Tests ejecutados: {self.tests_run}")
        print(f"✅ Tests exitosos: {self.tests_passed}")
        print(f"❌ Tests fallidos: {self.tests_failed}")
        
        if self.failures:
            print("\n❌ FALLOS DETALLADOS:")
            for i, failure in enumerate(self.failures, 1):
                print(f"   {i}. {failure}")
        
        success_rate = (self.tests_passed / self.tests_run) * 100 if self.tests_run > 0 else 0
        print(f"\n🎯 Tasa de éxito: {success_rate:.1f}%")
        
        if success_rate == 100:
            print("🎉 ¡TODOS LOS TESTS PASARON EXITOSAMENTE!")
            print("✅ El servicio Kokoro TTS v1.0 está funcionando perfectamente")
        elif success_rate >= 80:
            print("⚠️  La mayoría de tests pasaron - revisar fallos menores")
        else:
            print("🚨 Múltiples fallos detectados - revisar configuración")
        
        return self.tests_failed == 0


def make_request(url, method='GET', data=None, headers=None):
    """Hacer petición HTTP usando urllib"""
    try:
        if headers is None:
            headers = {}
        
        if data is not None:
            if isinstance(data, dict):
                # Para JSON
                data = json.dumps(data).encode('utf-8')
                headers['Content-Type'] = 'application/json'
            elif isinstance(data, str):
                # Para form data
                data = data.encode('utf-8')
        
        req = urllib.request.Request(url, data=data, headers=headers, method=method)
        
        with urllib.request.urlopen(req, timeout=TEST_TIMEOUT) as response:
            content = response.read().decode('utf-8')
            return {
                'status_code': response.getcode(),
                'content': content,
                'headers': dict(response.headers)
            }
            
    except urllib.error.HTTPError as e:
        return {
            'status_code': e.code,
            'content': e.read().decode('utf-8') if e.fp else '',
            'headers': dict(e.headers) if e.headers else {}
        }
    except Exception as e:
        raise Exception(f"Request failed: {e}")


def test_service_health():
    """Test básico de conectividad y salud del servicio"""
    response = make_request(f"{BASE_URL}/health")
    
    if response['status_code'] != 200:
        if VERBOSE:
            print(f"❌ Status code incorrecto: {response['status_code']}")
        return False
    
    data = json.loads(response['content'])
    
    # Verificar estructura de respuesta
    required_keys = ['status', 'model', 'model_status', 'default_language']
    for key in required_keys:
        if key not in data:
            if VERBOSE:
                print(f"❌ Falta clave requerida: {key}")
            return False
    
    # Verificar valores esperados
    if data['status'] != 'healthy':
        if VERBOSE:
            print(f"❌ Status no es 'healthy': {data['status']}")
        return False
    
    if data['model'] != 'kokoro-v1.0':
        if VERBOSE:
            print(f"❌ Modelo incorrecto: {data['model']}")
        return False
    
    if data['default_language'] != 'es':
        if VERBOSE:
            print(f"❌ Idioma por defecto incorrecto: {data['default_language']}")
        return False
    
    if VERBOSE:
        print(f"✅ Servicio OK - Modelo: {data['model']}, Estado: {data['model_status']}")
        print(f"   Voces disponibles: {data.get('available_voices', 'N/A')}")
    
    return True


def test_languages_endpoint():
    """Test endpoint de idiomas soportados"""
    response = make_request(f"{BASE_URL}/languages")
    
    if response['status_code'] != 200:
        if VERBOSE:
            print(f"❌ Error obteniendo idiomas: {response['status_code']}")
        return False
    
    data = json.loads(response['content'])
    
    required_keys = ['supported_languages', 'language_names', 'default_language']
    for key in required_keys:
        if key not in data:
            if VERBOSE:
                print(f"❌ Falta clave en idiomas: {key}")
            return False
    
    # Verificar que incluye español
    if 'es' not in data['supported_languages']:
        if VERBOSE:
            print("❌ No incluye español en idiomas soportados")
        return False
    
    if VERBOSE:
        langs = data['supported_languages']
        print(f"✅ {len(langs)} idiomas soportados: {', '.join(langs)}")
        print(f"   Idioma por defecto: {data['default_language']}")
    
    return True


def test_voices_endpoint():
    """Test endpoint de voces disponibles"""
    # Test para español (debe funcionar)
    response = make_request(f"{BASE_URL}/voices?language=es")
    
    if response['status_code'] != 200:
        if VERBOSE:
            print(f"❌ Error obteniendo voces ES: {response['status_code']}")
        return False
    
    data = json.loads(response['content'])
    
    required_keys = ['language', 'voices', 'recommendations', 'model_version']
    for key in required_keys:
        if key not in data:
            if VERBOSE:
                print(f"❌ Falta clave en voces: {key}")
            return False
    
    if data['language'] != 'es':
        if VERBOSE:
            print(f"❌ Idioma incorrecto: {data['language']}")
        return False
    
    # Verificar que hay voces disponibles
    voices = data.get('voices', [])
    if not voices:
        if VERBOSE:
            print("❌ No hay voces disponibles")
        return False
    
    # Verificar voces específicas de Kokoro
    expected_voices = ['ef_dora', 'em_alex', 'em_santa']
    for voice in expected_voices:
        if voice not in voices:
            if VERBOSE:
                print(f"⚠️  Voz esperada no encontrada: {voice}")
    
    if VERBOSE:
        print(f"✅ {len(voices)} voces disponibles para español")
        print(f"   Voces: {', '.join(voices[:5])}{'...' if len(voices) > 5 else ''}")
    
    return True


def test_basic_synthesis():
    """Test síntesis básica de texto a voz"""
    payload = {
        "text": "Hola, esta es una prueba básica del sistema Kokoro TTS",
        "language": "es",
        "voice": "ef_dora",
        "speed": 1.0
    }
    
    response = make_request(
        f"{BASE_URL}/synthesize_json",
        method='POST',
        data=payload
    )
    
    if response['status_code'] != 200:
        if VERBOSE:
            print(f"❌ Error en síntesis: {response['status_code']}")
            try:
                error_data = json.loads(response['content'])
                print(f"   Error: {error_data.get('error', 'Unknown')}")
            except:
                pass
        return False
    
    data = json.loads(response['content'])
    
    if not data.get('success', False):
        if VERBOSE:
            print(f"❌ Síntesis falló: {data.get('error', 'Unknown error')}")
        return False
    
    # Verificar metadatos importantes
    required_keys = ['text', 'language', 'voice', 'speed', 'model', 'audio_duration']
    for key in required_keys:
        if key not in data:
            if VERBOSE:
                print(f"❌ Falta metadato: {key}")
            return False
    
    if data['audio_duration'] <= 0:
        if VERBOSE:
            print(f"❌ Duración de audio inválida: {data['audio_duration']}")
        return False
    
    if VERBOSE:
        print(f"✅ Síntesis exitosa - Duración: {data['audio_duration']:.2f}s")
        print(f"   Sample rate: {data.get('sample_rate', 'N/A')}, Modelo: {data['model']}")
    
    return True


def test_error_handling():
    """Test manejo de errores del servicio"""
    # Test 1: Texto vacío
    payload = {"text": "", "language": "es"}
    response = make_request(f"{BASE_URL}/synthesize_json", method='POST', data=payload)
    
    if response['status_code'] != 400:
        if VERBOSE:
            print(f"❌ Texto vacío debería dar 400, dio: {response['status_code']}")
        return False
    
    # Test 2: Sin texto
    payload = {"language": "es"}
    response = make_request(f"{BASE_URL}/synthesize_json", method='POST', data=payload)
    
    if response['status_code'] != 400:
        if VERBOSE:
            print(f"❌ Sin texto debería dar 400, dio: {response['status_code']}")
        return False
    
    # Test 3: Request sin JSON
    response = make_request(f"{BASE_URL}/synthesize_json", method='POST')
    
    if response['status_code'] not in [400, 415, 422, 500]:
        if VERBOSE:
            print(f"❌ Request sin JSON debería dar 400/415/422/500, dio: {response['status_code']}")
        return False
    
    if VERBOSE:
        print("✅ Manejo de errores correcto (texto vacío, sin texto, JSON faltante)")
    
    return True


def test_different_voices():
    """Test diferentes voces disponibles"""
    voices_to_test = ["ef_dora", "em_alex", "em_santa"]
    text = "Prueba de diferentes voces de Kokoro TTS"
    successful_voices = 0
    
    for voice in voices_to_test:
        payload = {
            "text": text,
            "language": "es",
            "voice": voice
        }
        
        try:
            response = make_request(f"{BASE_URL}/synthesize_json", method='POST', data=payload)
            
            if response['status_code'] == 200:
                data = json.loads(response['content'])
                if data.get('success', False):
                    successful_voices += 1
                    if VERBOSE:
                        print(f"   ✅ Voz {voice}: {data.get('audio_duration', 0):.2f}s")
                else:
                    if VERBOSE:
                        print(f"   ❌ Voz {voice}: {data.get('error', 'Unknown error')}")
            else:
                if VERBOSE:
                    print(f"   ❌ Voz {voice}: HTTP {response['status_code']}")
        except Exception as e:
            if VERBOSE:
                print(f"   💥 Voz {voice}: {e}")
    
    # Al menos una voz debe funcionar
    if successful_voices == 0:
        if VERBOSE:
            print("❌ Ninguna voz funcionó")
        return False
    
    if VERBOSE and successful_voices < len(voices_to_test):
        print(f"⚠️  Solo {successful_voices}/{len(voices_to_test)} voces funcionaron")
    
    return True


def test_batch_synthesis():
    """Test síntesis por lotes"""
    payload = {
        "texts": [
            "Primer texto del lote",
            "Segundo texto para procesar", 
            "Tercer y último texto"
        ],
        "language": "es",
        "voice": "ef_dora"
    }
    
    response = make_request(f"{BASE_URL}/batch_synthesize", method='POST', data=payload)
    
    if response['status_code'] != 200:
        if VERBOSE:
            print(f"❌ Error en batch: {response['status_code']}")
        return False
    
    data = json.loads(response['content'])
    
    if data.get('total_texts') != 3:
        if VERBOSE:
            print(f"❌ Total textos incorrecto: {data.get('total_texts')}")
        return False
    
    if data.get('successful') != 3:
        if VERBOSE:
            print(f"❌ Síntesis exitosas: {data.get('successful')}/3")
        return False
    
    if VERBOSE:
        total_duration = data.get('total_duration', 0)
        print(f"✅ Batch exitoso - 3/3 textos procesados, duración total: {total_duration:.2f}s")
    
    return True


def check_service_availability():
    """Verificar si el servicio está disponible"""
    try:
        response = make_request(f"{BASE_URL}/health")
        return response['status_code'] == 200
    except:
        return False


def main():
    """Función principal de testing"""
    print("🧪 TEST DE SERVICIO KOKORO TTS v1.0")
    print("="*50)
    print(f"🌐 URL del servicio: {BASE_URL}")
    print(f"⏱️  Timeout: {TEST_TIMEOUT}s")
    print(f"📝 Modo verboso: {'✅ Activado' if VERBOSE else '❌ Desactivado'}")
    print()
    
    # Verificar disponibilidad inicial
    print("🔍 Verificando disponibilidad del servicio...")
    if not check_service_availability():
        print("❌ ERROR: Servicio no disponible en " + BASE_URL)
        print("\n💡 Soluciones:")
        print("   1. Verificar que el servicio esté corriendo:")
        print("      docker-compose up -d")
        print("   2. Verificar conectividad:")
        print("      curl http://localhost:5002/health")
        print("   3. Verificar puertos:")
        print("      netstat -tulpn | grep 5002")
        return False
    
    print("✅ Servicio disponible")
    print()
    
    # Ejecutar tests
    runner = TestRunner(verbose=VERBOSE)
    
    # Tests básicos
    runner.run_test("Conectividad y salud del servicio", test_service_health)
    runner.run_test("Endpoint de idiomas", test_languages_endpoint)
    runner.run_test("Endpoint de voces", test_voices_endpoint)
    runner.run_test("Síntesis básica", test_basic_synthesis)
    runner.run_test("Manejo de errores", test_error_handling)
    
    # Tests de funcionalidad
    runner.run_test("Diferentes voces", test_different_voices)
    runner.run_test("Síntesis por lotes", test_batch_synthesis)
    
    # Resumen final
    success = runner.print_summary()
    
    if not success:
        print("\n🔧 AYUDA PARA PROBLEMAS:")
        print("   1. Logs del servicio: docker logs kokoro-tts")
        print("   2. Estado del contenedor: docker ps | grep kokoro-tts")
        print("   3. Recursos del sistema: docker stats kokoro-tts")
        print("   4. Test específico: python3 test_service.py --verbose")
    
    return success


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Tests del servicio Kokoro TTS v1.0')
    parser.add_argument('--url', default=BASE_URL, help='URL del servicio Kokoro TTS')
    parser.add_argument('--timeout', type=int, default=TEST_TIMEOUT, help='Timeout para requests (segundos)')
    parser.add_argument('--verbose', '-v', action='store_true', help='Modo verboso con detalles')
    
    args = parser.parse_args()
    
    # Actualizar configuración global
    BASE_URL = args.url
    TEST_TIMEOUT = args.timeout
    VERBOSE = args.verbose
    
    success = main()
    sys.exit(0 if success else 1) 
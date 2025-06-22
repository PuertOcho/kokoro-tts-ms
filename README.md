# Kokoro TTS v1.0 - Servicio de Síntesis de Voz

Servicio de Text-to-Speech usando **Kokoro ONNX v1.0** optimizado para español con soporte multiidioma y configuración parametrizada.

## 🚀 Características Principales

- **Modelo Moderno**: Kokoro ONNX v1.0 con ONNX Runtime optimizado
- **Optimizado para Español**: Configuración predeterminada para español con 3 voces nativas
- **Multiidioma**: Soporte para 8 idiomas (Español, Inglés, Francés, Italiano, Portugués, Hindi, Japonés, Chino)
- **53 Voces Disponibles**: Amplia variedad de voces masculinas y femeninas
- **Configuración Parametrizada**: Variables de entorno con archivo .env
- **Alta Velocidad**: RTF optimizado para síntesis rápida
- **Recomendaciones Inteligentes**: Selección automática de voces por idioma y género
- **API REST Completa**: Endpoints para síntesis individual, por lotes y gestión
- **Debug Integrado**: Guardado automático de archivos de audio para desarrollo
- **Tests Completos**: Suite de pruebas sin dependencias externas

## 📊 Rendimiento

- **RTF (Real Time Factor)**: Optimizado para síntesis rápida
- **Síntesis individual**: ~0.8-1.5s por frase promedio
- **Síntesis por lotes**: Procesamiento eficiente de múltiples textos
- **Tamaño del modelo**: ~338MB (modelo + voces)
- **Tiempo de carga**: < 10 segundos
- **Memoria**: Optimizado para uso eficiente de RAM
- **Tests**: 100% exitosos en suite completa

## 🗣️ Voces en Español

| Voz | Género | Descripción |
|-----|--------|-------------|
| `ef_dora` | Femenina | Voz por defecto, clara y natural |
| `em_alex` | Masculina | Voz masculina principal |
| `em_santa` | Masculina | Voz masculina alternativa |

## 🌍 Idiomas Soportados

| Idioma | Código | Voces | G2P |
|--------|--------|-------|-----|
| Español | `es` | 3 | ✅ Nativo |
| Inglés | `en` | 27 | ✅ Nativo |
| Francés | `fr` | 1 | ✅ Nativo |
| Italiano | `it` | 2 | ✅ Nativo |
| Portugués | `pt` | 3 | ✅ Nativo |
| Hindi | `hi` | 4 | ✅ Nativo |
| Japonés | `ja` | 5 | ✅ Nativo |
| Chino | `zh` | 8 | ✅ Nativo |

## 🚀 Instalación y Uso

### Prerequisitos

- Docker y Docker Compose
- Al menos 2GB de RAM disponible
- Conexión a internet para descargar modelos

### Instalación Rápida

```bash
# 1. Clonar o acceder al directorio
cd kokoro-tts-ms/

# 2. Configurar variables de entorno (opcional)
cp environment.example .env
# Editar .env con tus valores personalizados

# 3. Los modelos ya están descargados en app/models/
ls -lh app/models/
# kokoro-v1.0.onnx (311M)
# voices-v1.0.bin (27M)

# 4. Construir y ejecutar
docker compose up --build -d

# 5. Verificar estado
curl http://localhost:5002/health
```

### Pruebas

```bash
# Ejecutar suite completa de pruebas (sin dependencias externas)
python3 test_service.py

# Ejecutar con modo verboso
python3 test_service.py --verbose

# Test con configuración personalizada
python3 test_service.py --url http://localhost:5002 --timeout 30 --verbose

# Prueba rápida en español
curl -X POST http://localhost:5002/synthesize_json \
  -H "Content-Type: application/json" \
  -d '{"text": "Hola, soy Kokoro versión uno punto cero", "language": "es", "voice": "ef_dora"}'
```

## 📖 API Reference

### Endpoints Principales

#### POST /synthesize
Genera y devuelve archivo de audio WAV

```json
{
  "text": "Texto a sintetizar",
  "language": "es",
  "voice": "ef_dora",
  "speed": 1.0,
  "gender_preference": "female"
}
```

#### POST /synthesize_json
Genera audio y devuelve metadata JSON

```json
{
  "text": "Texto a sintetizar",
  "language": "es",
  "voice": "ef_dora",
  "speed": 1.0
}
```

**Respuesta:**
```json
{
  "success": true,
  "text": "Texto a sintetizar",
  "language": "es",
  "voice": "ef_dora",
  "audio_duration": 2.45,
  "sample_rate": 24000,
  "model": "kokoro-v1.0",
  "speed": 1.0
}
```

#### POST /batch_synthesize
Síntesis por lotes para múltiples textos

```json
{
  "texts": ["Primer texto", "Segundo texto", "Tercer texto"],
  "language": "es",
  "voice": "ef_dora",
  "speed": 1.0
}
```

#### GET /voices
Lista todas las voces disponibles organizadas por idioma

```json
{
  "voices_by_language": {
    "es": ["ef_dora", "em_alex", "em_santa"],
    "en": ["af_bella", "af_heart", "..."],
    "..."
  },
  "recommendations": {
    "es": {
      "female": ["ef_dora"],
      "male": ["em_alex", "em_santa"],
      "default": "ef_dora"
    }
  },
  "total_voices": 53
}
```

#### GET /languages
Lista idiomas soportados

#### GET /health
Estado del servicio

### Parámetros

- **text** (string, requerido): Texto a sintetizar
- **language** (string, opcional): Código de idioma (`es`, `en`, `fr`, etc.). Default: `es`
- **voice** (string, opcional): ID de voz específica. Si no se especifica, se selecciona automáticamente
- **speed** (float, opcional): Velocidad de habla (0.5-2.0). Default: `1.0`
- **gender_preference** (string, opcional): Preferencia de género (`female`, `male`)

## 🔧 Configuración

### Configuración Parametrizada

El proyecto usa variables de entorno para una configuración flexible:

1. **Copia el archivo de ejemplo:**
   ```bash
   cp environment.example .env
   ```

2. **Edita el archivo .env:**
   ```bash
   # Configuración del servicio
   KOKORO_PORT=5002
   FLASK_HOST=0.0.0.0
   FLASK_PORT=5002
   
   # Configuración de idioma y voz
   DEFAULT_LANGUAGE=es
   DEFAULT_VOICE=ef_dora
   
   # Configuración de debug
   DEBUG_AUDIO=true
   
   # Configuración GPU
   GPU_COUNT=1
   ```

### Variables de Entorno Disponibles

| Variable | Descripción | Valor por defecto |
|----------|-------------|-------------------|
| `KOKORO_PORT` | Puerto externo del servicio | `5002` |
| `FLASK_HOST` | Host donde Flask escucha | `0.0.0.0` |
| `FLASK_PORT` | Puerto interno de Flask | `5002` |
| `DEFAULT_LANGUAGE` | Idioma por defecto | `es` |
| `DEFAULT_VOICE` | Voz por defecto | `ef_dora` |
| `DEBUG_AUDIO` | Habilitar debug de audio | `true` |
| `CONTAINER_NAME` | Nombre del contenedor | `kokoro-tts` |
| `GPU_COUNT` | Cantidad de GPUs a usar | `1` |

### Docker Compose Parametrizado

El `docker-compose.yml` usa las variables del archivo `.env`:

```yaml
services:
  kokoro-tts:
    ports:
      - "${KOKORO_PORT:-5002}:${FLASK_PORT:-5002}"
    environment:
      - FLASK_HOST=${FLASK_HOST:-0.0.0.0}
      - DEFAULT_LANGUAGE=${DEFAULT_LANGUAGE:-es}
      - DEFAULT_VOICE=${DEFAULT_VOICE:-ef_dora}
      - DEBUG_AUDIO=${DEBUG_AUDIO:-true}
    container_name: ${CONTAINER_NAME:-kokoro-tts}
```

## 🛠️ Desarrollo

### Tests Completos

El proyecto incluye una suite completa de tests sin dependencias externas:

```bash
# Ejecutar todos los tests
python3 test_service.py

# Modo verboso con detalles
python3 test_service.py --verbose

# Tests específicos con configuración
python3 test_service.py --url http://localhost:5002 --timeout 30 --verbose
```

**Tests incluidos:**
- ✅ Conectividad y salud del servicio
- ✅ Endpoint de idiomas soportados
- ✅ Endpoint de voces disponibles
- ✅ Síntesis básica de texto a voz
- ✅ Manejo de errores HTTP
- ✅ Diferentes voces (ef_dora, em_alex, em_santa)
- ✅ Síntesis por lotes

Ver [README_TEST.md](README_TEST.md) para documentación completa de tests.

### Debug de Audio

Cuando `DEBUG_AUDIO=true`, todos los archivos de audio generados se guardan en `/debug_audio/` con nombres únicos:

```bash
# Listar archivos de debug
curl http://localhost:5002/debug/audio

# Descargar archivo específico
curl http://localhost:5002/debug/audio/kokoro_v1_20250620_163734_621.wav -o audio.wav
```

### Estructura del Proyecto

```
kokoro-tts-ms/
├── app/
│   ├── app.py              # Aplicación Flask principal
│   ├── Dockerfile          # Imagen Docker
│   ├── requirements.txt    # Dependencias Python
│   └── models/            # Modelos Kokoro
│       ├── kokoro-v1.0.onnx
│       └── voices-v1.0.bin
├── debug_audio/           # Archivos de debug
├── environment.example    # Plantilla de variables de entorno
├── docker-compose.yml     # Configuración Docker parametrizada
├── test_service.py       # Suite de pruebas sin dependencias
├── README_TEST.md        # Documentación de tests
└── README.md             # Este archivo
```

## 📊 Comparación de Versiones

| Característica | v0.4.9 (Anterior) | v1.0 (Actual) |
|----------------|-------------------|---------------|
| Runtime | ONNX Runtime | ONNX Runtime Optimizado |
| Configuración | Hardcoded | Variables de entorno (.env) |
| Tests | Manual | Suite automatizada completa |
| Tamaño modelo | ~338MB | ~338MB |
| Voces totales | 53 | 53 |
| Carga inicial | ~5s | ~10s |
| Uso de memoria | Optimizado | Optimizado |
| Dependencias | onnxruntime, misaki | onnxruntime, misaki |
| Docker Compose | Estático | Parametrizado |

## 🚨 Solución de Problemas

### El servicio no inicia

```bash
# Verificar logs
docker logs kokoro-tts

# Verificar modelos
ls -lh app/models/

# Verificar configuración
cat .env

# Reconstruir imagen
docker compose down
docker compose build --no-cache
docker compose up -d

# Ejecutar tests de diagnóstico
python3 test_service.py --verbose
```

### Audio de baja calidad

- Verificar que se esté usando la voz correcta para el idioma
- Ajustar el parámetro `speed` (recomendado: 0.8-1.2)
- Usar voces recomendadas por idioma

### Errores de síntesis

- Verificar que el texto no esté vacío
- Evitar textos muy largos (>500 tokens)
- Usar caracteres ASCII cuando sea posible

## 🔄 Actualización desde v0.4.9

Si vienes de la versión anterior:

1. **Detener servicio anterior**: `docker compose down`
2. **Configurar variables de entorno**: `cp environment.example .env`
3. **Limpiar imágenes**: `docker system prune -f`
4. **Seguir instalación nueva**: Ver sección "Instalación Rápida"
5. **Ejecutar tests**: `python3 test_service.py --verbose`

Los archivos de configuración y API son compatibles. La principal mejora es la parametrización con `.env` y tests completos.

## 📈 Métricas de Rendimiento

Resultados de `test_service.py`:

- ✅ **Conectividad y salud del servicio**: Modelo kokoro-v1.0, 53 voces disponibles
- ✅ **Endpoint de idiomas**: 8 idiomas soportados (es, en, fr, it, pt, hi, ja, zh)
- ✅ **Endpoint de voces**: 3 voces españolas (ef_dora, em_alex, em_santa)
- ✅ **Síntesis básica**: ~3.5s duración audio, sample rate 24000Hz
- ✅ **Manejo de errores**: Validación correcta de HTTP 400/415
- ✅ **Diferentes voces**: 3/3 voces exitosas (~2.8-2.9s por síntesis)
- ✅ **Síntesis por lotes**: 3/3 textos procesados (~4.8s duración total)
- ✅ **Total**: 7/7 pruebas exitosas (100% tasa de éxito)

## 🤝 Contribuir

Para reportar issues o contribuir:

1. Ejecutar `python3 test_service.py --verbose` para verificar el estado
2. Incluir logs del contenedor: `docker logs kokoro-tts`
3. Incluir configuración usada: `cat .env` (sin datos sensibles)
4. Especificar versión y parámetros de docker-compose

## 📄 Licencia

Este proyecto utiliza Kokoro ONNX bajo sus términos de licencia correspondientes.

---

**Kokoro TTS v1.0** - Síntesis de voz moderna, parametrizada y con tests completos 🚀 
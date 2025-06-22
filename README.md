# Kokoro TTS v0.4.9 - Servicio de Síntesis de Voz

Servicio de Text-to-Speech usando **Kokoro ONNX v0.4.9** optimizado para español con soporte multiidioma.

## 🚀 Características Principales

- **Modelo Moderno**: Kokoro ONNX v0.4.9 con ONNX Runtime (más rápido y ligero)
- **Optimizado para Español**: Configuración predeterminada para español con 3 voces nativas
- **Multiidioma**: Soporte para 8 idiomas (Español, Inglés, Francés, Italiano, Portugués, Hindi, Japonés, Chino)
- **53 Voces Disponibles**: Amplia variedad de voces masculinas y femeninas
- **Alta Velocidad**: RTF promedio de 0.25x (4x más rápido que tiempo real)
- **Recomendaciones Inteligentes**: Selección automática de voces por idioma y género
- **API REST Completa**: Endpoints para síntesis individual, por lotes y gestión
- **Debug Integrado**: Guardado automático de archivos de audio para desarrollo

## 📊 Rendimiento

- **RTF (Real Time Factor)**: 0.25x promedio (menor es mejor)
- **Eficiencia por lotes**: 3.59x tiempo real
- **Tamaño del modelo**: ~338MB (modelo + voces)
- **Tiempo de carga**: < 5 segundos
- **Memoria**: Optimizado para uso eficiente de RAM

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
cd kokoro/

# 2. Los modelos ya están descargados en app/models/
ls -lh app/models/
# kokoro-v1.0.onnx (311M)
# voices-v1.0.bin (27M)

# 3. Construir y ejecutar
docker compose up --build -d

# 4. Verificar estado
curl http://localhost:5002/health
```

### Pruebas

```bash
# Ejecutar suite completa de pruebas
python3 test_kokoro_v1.py

# Prueba rápida en español
curl -X POST http://localhost:5002/synthesize_json \
  -H "Content-Type: application/json" \
  -d '{"text": "Hola, soy Kokoro versión cero punto cuatro punto nueve", "language": "es", "voice": "ef_dora"}'
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

### Variables de Entorno

```bash
FLASK_HOST=0.0.0.0
FLASK_PORT=5002
DEFAULT_LANGUAGE=es
DEFAULT_VOICE=ef_dora
DEBUG_AUDIO=true
```

### Docker Compose

```yaml
version: '3.8'
services:
  kokoro-tts:
    build:
      context: ./app
    ports:
      - "5002:5002"
    volumes:
      - ./app/models:/app/models:ro
      - ./debug_audio:/app/debug_audio
    environment:
      - DEFAULT_LANGUAGE=es
      - DEFAULT_VOICE=ef_dora
      - DEBUG_AUDIO=true
```

## 🛠️ Desarrollo

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
kokoro/
├── app/
│   ├── app.py              # Aplicación Flask principal
│   ├── Dockerfile          # Imagen Docker
│   ├── requirements.txt    # Dependencias Python
│   └── models/            # Modelos Kokoro
│       ├── kokoro-v1.0.onnx
│       └── voices-v1.0.bin
├── debug_audio/           # Archivos de debug
├── docker-compose.yml     # Configuración Docker
├── test_kokoro_v1.py     # Suite de pruebas
└── README.md             # Este archivo
```

## 📊 Comparación de Versiones

| Característica | v0.19 (Anterior) | v0.4.9 (Actual) |
|----------------|------------------|-----------------|
| Runtime | PyTorch + CUDA | ONNX Runtime |
| Tamaño modelo | ~2GB | ~338MB |
| RTF promedio | 0.03x | 0.25x |
| Voces totales | 45 | 53 |
| Carga inicial | ~30s | ~5s |
| Uso de memoria | Alto | Optimizado |
| Dependencias | torch, torchaudio | onnxruntime, misaki |

## 🚨 Solución de Problemas

### El servicio no inicia

```bash
# Verificar logs
docker logs kokoro-tts-v1

# Verificar modelos
ls -lh app/models/

# Reconstruir imagen
docker compose down
docker compose build --no-cache
docker compose up -d
```

### Audio de baja calidad

- Verificar que se esté usando la voz correcta para el idioma
- Ajustar el parámetro `speed` (recomendado: 0.8-1.2)
- Usar voces recomendadas por idioma

### Errores de síntesis

- Verificar que el texto no esté vacío
- Evitar textos muy largos (>500 tokens)
- Usar caracteres ASCII cuando sea posible

## 🔄 Actualización desde v0.19

Si vienes de la versión anterior:

1. **Detener servicio anterior**: `docker compose down`
2. **Limpiar imágenes**: `docker system prune -f`
3. **Seguir instalación nueva**: Ver sección "Instalación Rápida"

Los archivos de configuración y API son compatibles.

## 📈 Métricas de Rendimiento

Resultados de `test_kokoro_v1.py`:

- ✅ **Health Check**: Servicio funcionando
- ✅ **Voces en Español**: 3/3 exitosas (RTF: 0.25x)
- ✅ **Cambio de Idiomas**: 4/4 idiomas exitosos
- ✅ **Recomendaciones**: 4/4 exitosas
- ✅ **Síntesis por Lotes**: 3.59x eficiencia tiempo real
- ✅ **Total**: 6/6 pruebas exitosas

## 🤝 Contribuir

Para reportar issues o contribuir:

1. Ejecutar `test_kokoro_v1.py` para verificar el estado
2. Incluir logs del contenedor en el reporte
3. Especificar versión y configuración usada

## 📄 Licencia

Este proyecto utiliza Kokoro ONNX bajo sus términos de licencia correspondientes.

---

**Kokoro TTS v0.4.9** - Síntesis de voz moderna, rápida y optimizada para español 🚀 
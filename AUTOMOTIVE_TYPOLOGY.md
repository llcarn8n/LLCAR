# Automobile Typology Analysis

## Overview

LLCAR includes a powerful **Automobile Typology Analysis** feature that automatically detects and classifies automotive-related content in transcriptions. This feature is particularly useful for analyzing:

- **Automotive diagnostic videos** (mechanic-customer discussions)
- **Vehicle review content** (test drives, comparisons)
- **Technical training materials** (repair procedures, maintenance guides)
- **Sales consultations** (vehicle features, specifications)
- **Automotive podcasts and discussions**

## Features

The Automobile Typology Analyzer detects and classifies:

### 1. **Vehicle Types**
Identifies the category of vehicles mentioned:
- **Sedan** (седан, 轿车)
- **SUV** (внедорожник, кроссовер, 越野车)
- **Truck** (грузовик, пикап, 卡车)
- **Van** (фургон, минивэн, 面包车)
- **Coupe** (купе, 双门轿车)
- **Convertible** (кабриолет, 敞篷车)
- **Wagon** (универсал, 旅行车)
- **Hatchback** (хэтчбек, 掀背车)
- **Sports Car** (спорткар, 跑车)
- **Motorcycle** (мотоцикл, 摩托车)
- **Electric Vehicle** (электромобиль, 电动车)
- **Hybrid** (гибрид, 混合动力车)

### 2. **Manufacturers**
Detects mentions of automobile brands:
- **American**: Ford, Chevrolet, Tesla, GMC, Dodge, Chrysler, Cadillac, Jeep, Ram
- **Japanese**: Toyota, Honda, Nissan, Mazda, Subaru, Mitsubishi, Suzuki, Lexus, Acura, Infiniti
- **German**: Volkswagen, Mercedes-Benz, BMW, Audi, Porsche, Opel
- **Korean**: Hyundai, Kia, Genesis
- **French**: Renault, Peugeot, Citroën
- **Italian**: Fiat, Ferrari, Lamborghini, Maserati, Alfa Romeo
- **British**: Land Rover, Jaguar, Mini, Bentley, Rolls-Royce, Aston Martin
- **Chinese**: BYD, Geely, NIO, XPeng, Li Auto, Great Wall
- **Russian**: Lada (Лада), GAZ (ГАЗ), UAZ (УАЗ), KAMAZ (КАМАЗ), VAZ (ВАЗ)
- **Swedish**: Volvo, Saab
- **Czech**: Skoda (Škoda)

### 3. **Models**
Recognizes popular vehicle models:
- Toyota: Camry, Corolla, RAV4, Prius, Highlander, Tacoma, Tundra, Land Cruiser
- Honda: Civic, Accord, CR-V, Pilot, Fit, Odyssey
- Ford: F-150, Mustang, Explorer, Escape, Focus, Fusion
- Tesla: Model S, Model 3, Model X, Model Y, Cybertruck
- BMW: 3 Series, 5 Series, 7 Series, X3, X5, X7
- Mercedes: C-Class, E-Class, S-Class, GLA, GLC, GLE
- Russian: Vesta (Веста), Granta (Гранта), Niva (Нива), Kalina (Калина), Priora (Приора)

### 4. **Systems & Components**
Identifies automotive systems being discussed:
- **Engine** (двигатель, мотор, 发动机)
- **Transmission** (коробка передач, трансмиссия, 变速箱)
- **Brakes** (тормоза, 刹车)
- **Suspension** (подвеска, 悬挂)
- **Exhaust** (выхлоп, 排气)
- **Fuel System** (топливная система, 燃油系统)
- **Electrical System** (электрика, 电气系统)
- **Cooling System** (радиатор, охлаждение, 冷却系统)
- **Steering** (рулевое управление, 转向)
- **Battery** (аккумулятор, 电池)

### 5. **Diagnostic Terms**
Detects maintenance and diagnostic terminology:
- **Malfunction** (неисправность, 故障)
- **Noise** (шум, 噪音)
- **Vibration** (вибрация, 振动)
- **Leak** (утечка, 泄漏)
- **Overheating** (перегрев, 过热)
- **Warning Light** (контрольная лампа, 警告灯)
- **Oil Change** (замена масла, 换油)
- **Repair** (ремонт, 修理)
- **Maintenance** (обслуживание, 保养)

## Configuration

### Enabling/Disabling Automotive Analysis

In `config.yaml`:

```yaml
# Automotive typology settings
automotive:
  # Enable automotive typology analysis
  enabled: true  # Set to false to disable
  # Minimum automotive mentions threshold for segment classification
  mention_threshold: 1
```

### Configuration Parameters

- **`enabled`** (default: `true`): Enable or disable automotive analysis globally
- **`mention_threshold`** (default: `1`): Minimum number of automotive mentions required to classify a segment as automotive-related

## Usage

### Command Line

Automotive analysis is **enabled by default**. It runs automatically when processing videos or audio:

```bash
# Process video with automotive analysis (default)
python main.py --video mechanic_consultation.mp4

# Automotive analysis will be included in JSON output
python main.py --video car_review.mp4 --formats json
```

To disable automotive analysis, edit `config.yaml` and set `automotive.enabled: false`.

### Python API

```python
from src.automotive_typology import AutomotiveTypologyAnalyzer

# Initialize analyzer
analyzer = AutomotiveTypologyAnalyzer(language="en")

# Analyze single text
text = "I bought a new Tesla Model 3 electric car. The battery is excellent."
result = analyzer.analyze_text(text)

print(f"Vehicle types: {result['vehicle_types']}")  # ['electric']
print(f"Manufacturers: {result['manufacturers']}")  # ['tesla']
print(f"Models: {result['models']}")  # ['model 3']
print(f"Systems: {result['systems']}")  # ['battery']

# Analyze transcription segments
segments = [
    {'speaker': 'SPEAKER_00', 'start': 0.0, 'end': 5.0,
     'text': 'The engine is overheating and making noise'},
    {'speaker': 'SPEAKER_01', 'start': 5.0, 'end': 10.0,
     'text': 'We need to check the cooling system immediately'}
]

analysis = analyzer.analyze_segments(segments)
print(analysis['summary'])  # Summary of all detected entities
```

## Output Format

Automotive analysis results are included in the JSON output:

```json
{
  "metadata": {
    "video_path": "/path/to/video.mp4",
    "language": "en",
    "processing_time": 45.23
  },
  "automotive_typology": {
    "summary": {
      "vehicle_types": [
        {"type": "sedan", "count": 5},
        {"type": "suv", "count": 2}
      ],
      "manufacturers": [
        {"manufacturer": "toyota", "count": 8},
        {"manufacturer": "honda", "count": 3}
      ],
      "models": [
        {"model": "camry", "count": 5},
        {"model": "civic", "count": 3}
      ],
      "systems": [
        {"system": "engine", "count": 12},
        {"system": "transmission", "count": 6}
      ],
      "diagnostic_terms": [
        {"term": "repair", "count": 7},
        {"term": "maintenance", "count": 4}
      ],
      "total_automotive_segments": 45,
      "total_segments": 156
    },
    "segments": [
      {
        "segment_index": 0,
        "speaker": "SPEAKER_00",
        "start": 0.5,
        "end": 3.2,
        "automotive_mentions": 3,
        "detected_entities": {
          "vehicle_types": ["sedan"],
          "manufacturers": ["toyota"],
          "models": ["camry"],
          "systems": [],
          "diagnostic_terms": []
        }
      }
    ]
  }
}
```

## Use Cases

### 1. Automotive Diagnostic Analysis
Identify which vehicle systems are being discussed in mechanic-customer consultations:

```bash
python main.py --video diagnostic_session.mp4 --language en
```

The output will show:
- Most frequently mentioned systems (e.g., "engine", "transmission")
- Diagnostic issues discussed (e.g., "overheating", "leak", "noise")
- Vehicle information (make, model, type)

### 2. Vehicle Review Processing
Extract key information from car review videos:

```bash
python main.py --video car_review_2024.mp4 --formats json
```

Results include:
- Vehicles being reviewed (manufacturers, models, types)
- Features discussed (systems, components)
- Comparison mentions

### 3. Training Material Analysis
Analyze automotive training videos for content indexing:

```bash
python main.py --video mechanic_training.mp4 --language ru
```

### 4. Sales Consultation Insights
Process sales consultation recordings to understand customer interests:

```bash
python main.py --audio sales_call.wav --formats json csv
```

## Multi-Language Support

Automotive typology works seamlessly across **English**, **Russian**, and **Chinese**:

### English Example
```bash
python main.py --video english_review.mp4 --language en
# Detects: "Toyota Camry sedan", "engine", "repair"
```

### Russian Example
```bash
python main.py --video russian_diagnostic.mp4 --language ru
# Detects: "Лада Веста", "двигатель", "ремонт"
```

### Chinese Example
```bash
python main.py --video chinese_review.mp4 --language zh
# Detects: "轿车", "发动机", "修理"
```

## Performance

Automotive typology analysis adds minimal overhead to the processing pipeline:
- **Processing time**: <1% increase
- **Memory usage**: <10MB additional
- **Accuracy**: High precision for common automotive terms

The analyzer uses optimized pattern matching and supports both exact matches and word stem detection for inflected languages (Russian).

## Limitations

1. **Model Coverage**: Currently includes ~100+ popular models. Less common or regional models may not be detected.
2. **Language-Specific Forms**: Russian and Chinese detection handles common word forms but may miss rare grammatical variations.
3. **Context Sensitivity**: The analyzer detects mentions but doesn't understand context (e.g., negative vs. positive mentions).
4. **Specialized Terminology**: Highly technical or brand-specific component names may not be recognized.

## Future Enhancements

Planned improvements:
- [ ] Expanded model database with more regional vehicles
- [ ] Sentiment analysis for automotive mentions
- [ ] Part number recognition
- [ ] VIN (Vehicle Identification Number) detection
- [ ] Automated repair procedure extraction
- [ ] Integration with automotive knowledge graphs

## Troubleshooting

### No automotive entities detected
**Problem**: Processing automotive content but no entities are detected.

**Solutions**:
1. Verify `automotive.enabled: true` in `config.yaml`
2. Check transcription quality - poor transcription may miss key terms
3. Review the detected language - ensure it matches the audio
4. Verify the content actually contains automotive terminology

### False positives
**Problem**: Non-automotive content incorrectly classified as automotive.

**Solutions**:
1. Increase `mention_threshold` in config to require more mentions
2. Review the transcription for homonyms (words with multiple meanings)
3. Filter results by checking `total_automotive_mentions` count

### Missing specific brands/models
**Problem**: Your specific vehicle brand or model isn't detected.

**Solutions**:
1. The database focuses on popular models - less common models may not be included
2. You can extend the `MANUFACTURERS` and `MODELS` sets in `src/automotive_typology.py`
3. Submit a feature request to add specific brands/models

## Examples

See the test file `test_automotive_typology.py` for comprehensive usage examples:

```bash
python test_automotive_typology.py
```

## Related Documentation

- [README.md](README.md) - Main project documentation
- [QUICKSTART.md](QUICKSTART.md) - Quick start guide
- [MODELS.md](MODELS.md) - Supported transcription models
- [FAQ.md](FAQ.md) - Frequently asked questions

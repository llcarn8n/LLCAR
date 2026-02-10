"""
Automotive Typology Module
Detects and classifies automobile mentions in transcribed text.
Provides comprehensive vehicle type classification for diagnostic and analysis purposes.
"""

import re
import logging
from typing import List, Dict, Any, Set, Tuple
from collections import defaultdict

logger = logging.getLogger(__name__)


class AutomotiveTypologyAnalyzer:
    """Analyzes transcribed text for automobile-related entities and classifications."""

    # Vehicle Types Classification
    VEHICLE_TYPES = {
        'sedan': ['sedan', 'седан', '轿车'],
        'suv': ['suv', 'внедорожник', 'кроссовер', 'crossover', 'SUV', '越野车'],
        'truck': ['truck', 'pickup', 'грузовик', 'пикап', '卡车', '皮卡'],
        'van': ['van', 'minivan', 'фургон', 'минивэн', '面包车', '货车'],
        'coupe': ['coupe', 'купе', '双门轿车'],
        'convertible': ['convertible', 'cabriolet', 'кабриолет', '敞篷车'],
        'wagon': ['wagon', 'estate', 'универсал', 'station wagon', '旅行车'],
        'hatchback': ['hatchback', 'хэтчбек', '掀背车'],
        'sports_car': ['sports car', 'спортивный автомобиль', 'спорткар', '跑车'],
        'motorcycle': ['motorcycle', 'мотоцикл', 'bike', '摩托车'],
        'electric': ['electric car', 'EV', 'электромобиль', '电动车'],
        'hybrid': ['hybrid', 'гибрид', '混合动力车']
    }

    # Major Automobile Manufacturers
    MANUFACTURERS = {
        # American
        'ford', 'chevrolet', 'chevy', 'dodge', 'gmc', 'tesla', 'chrysler', 'cadillac', 'jeep', 'ram',
        # Japanese
        'toyota', 'honda', 'nissan', 'mazda', 'subaru', 'mitsubishi', 'suzuki', 'lexus', 'acura', 'infiniti',
        # German
        'volkswagen', 'vw', 'mercedes', 'mercedes-benz', 'bmw', 'audi', 'porsche', 'opel',
        # Korean
        'hyundai', 'kia', 'genesis',
        # French
        'renault', 'peugeot', 'citroën', 'citroen',
        # Italian
        'fiat', 'ferrari', 'lamborghini', 'maserati', 'alfa romeo',
        # British
        'land rover', 'jaguar', 'mini', 'bentley', 'rolls-royce', 'aston martin',
        # Chinese
        'byd', 'geely', 'nio', 'xpeng', 'li auto', 'great wall',
        # Russian (both Latin and Cyrillic)
        'lada', 'лада', 'газ', 'gaz', 'уаз', 'uaz', 'камаз', 'kamaz', 'ваз', 'vaz',
        # Swedish
        'volvo', 'saab',
        # Czech
        'skoda', 'škoda'
    }

    # Common Automobile Models (selected popular models)
    MODELS = {
        # Toyota
        'camry', 'corolla', 'rav4', 'prius', 'highlander', 'tacoma', 'tundra', 'land cruiser',
        # Honda
        'civic', 'accord', 'cr-v', 'pilot', 'fit', 'odyssey',
        # Ford
        'f-150', 'mustang', 'explorer', 'escape', 'focus', 'fusion',
        # Tesla
        'model s', 'model 3', 'model x', 'model y', 'cybertruck',
        # BMW
        '3 series', '5 series', '7 series', 'x3', 'x5', 'x7',
        # Mercedes
        'c-class', 'e-class', 's-class', 'gla', 'glc', 'gle',
        # Russian (both Latin and Cyrillic)
        'веста', 'vesta', 'гранта', 'granta', 'нива', 'niva', 'калина', 'kalina', 'приора', 'priora'
    }

    # Automotive Systems and Components
    SYSTEMS = {
        'engine': ['engine', 'motor', 'двигатель', 'мотор', '发动机'],
        'transmission': ['transmission', 'gearbox', 'коробка передач', 'трансмиссия', '变速箱'],
        'brakes': ['brakes', 'тормоза', '刹车'],
        'suspension': ['suspension', 'подвеска', '悬挂'],
        'exhaust': ['exhaust', 'выхлоп', 'выхлопная система', '排气'],
        'fuel_system': ['fuel system', 'топливная система', '燃油系统'],
        'electrical': ['electrical system', 'электрика', '电气系统'],
        'cooling': ['cooling system', 'radiator', 'радиатор', 'охлаждение', '冷却系统'],
        'steering': ['steering', 'рулевое управление', '转向'],
        'battery': ['battery', 'аккумулятор', '电池']
    }

    # Common Automotive Issues/Diagnostics Terms
    DIAGNOSTIC_TERMS = {
        'malfunction': ['malfunction', 'неисправность', 'failure', 'отказ', '故障'],
        'noise': ['noise', 'шум', 'звук', '噪音'],
        'vibration': ['vibration', 'вибрация', 'тряска', '振动'],
        'leak': ['leak', 'утечка', 'течь', '泄漏'],
        'overheating': ['overheating', 'перегрев', '过热'],
        'warning_light': ['warning light', 'check engine', 'контрольная лампа', 'индикатор', '警告灯'],
        'oil_change': ['oil change', 'замена масла', '换油'],
        'repair': ['repair', 'ремонт', 'fix', '修理'],
        'maintenance': ['maintenance', 'обслуживание', 'service', '保养']
    }

    def __init__(self, language: str = "en"):
        """
        Initialize AutomotiveTypologyAnalyzer.

        Args:
            language: Language code ('en', 'ru', 'zh')
        """
        self.language = language
        self._compile_patterns()
        logger.info(f"AutomotiveTypologyAnalyzer initialized for language: {language}")

    def _compile_patterns(self):
        """Compile regex patterns for efficient matching."""
        # Create case-insensitive patterns for manufacturers and models
        self.manufacturer_patterns = []
        for manufacturer in self.MANUFACTURERS:
            pattern = re.compile(r'\b' + re.escape(manufacturer) + r'\b', re.IGNORECASE)
            self.manufacturer_patterns.append((manufacturer, pattern))

        self.model_patterns = []
        for model in self.MODELS:
            pattern = re.compile(r'\b' + re.escape(model) + r'\b', re.IGNORECASE)
            self.model_patterns.append((model, pattern))

    def analyze_text(self, text: str) -> Dict[str, Any]:
        """
        Analyze text for automotive entities and classifications.

        Args:
            text: Input text to analyze

        Returns:
            Dictionary containing detected automotive entities
        """
        if not text:
            return self._empty_result()

        result = {
            'vehicle_types': self._detect_vehicle_types(text),
            'manufacturers': self._detect_manufacturers(text),
            'models': self._detect_models(text),
            'systems': self._detect_systems(text),
            'diagnostic_terms': self._detect_diagnostic_terms(text),
            'total_automotive_mentions': 0
        }

        # Calculate total mentions
        result['total_automotive_mentions'] = (
            len(result['vehicle_types']) +
            len(result['manufacturers']) +
            len(result['models']) +
            len(result['systems']) +
            len(result['diagnostic_terms'])
        )

        return result

    def analyze_segments(self, segments: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze transcription segments for automotive content.

        Args:
            segments: List of transcription segments

        Returns:
            Comprehensive automotive typology analysis
        """
        # Aggregate results across all segments
        aggregated = {
            'vehicle_types': defaultdict(int),
            'manufacturers': defaultdict(int),
            'models': defaultdict(int),
            'systems': defaultdict(int),
            'diagnostic_terms': defaultdict(int)
        }

        segment_analyses = []

        for segment in segments:
            text = segment.get('text', '')
            analysis = self.analyze_text(text)

            # Store per-segment analysis
            segment_analysis = {
                'segment_index': len(segment_analyses),
                'speaker': segment.get('speaker'),
                'start': segment.get('start'),
                'end': segment.get('end'),
                'automotive_mentions': analysis['total_automotive_mentions'],
                'detected_entities': {
                    'vehicle_types': analysis['vehicle_types'],
                    'manufacturers': analysis['manufacturers'],
                    'models': analysis['models'],
                    'systems': analysis['systems'],
                    'diagnostic_terms': analysis['diagnostic_terms']
                }
            }
            segment_analyses.append(segment_analysis)

            # Aggregate counts
            for vtype in analysis['vehicle_types']:
                aggregated['vehicle_types'][vtype] += 1
            for manufacturer in analysis['manufacturers']:
                aggregated['manufacturers'][manufacturer] += 1
            for model in analysis['models']:
                aggregated['models'][model] += 1
            for system in analysis['systems']:
                aggregated['systems'][system] += 1
            for term in analysis['diagnostic_terms']:
                aggregated['diagnostic_terms'][term] += 1

        # Convert defaultdicts to sorted lists
        summary = {
            'vehicle_types': sorted(
                [{'type': k, 'count': v} for k, v in aggregated['vehicle_types'].items()],
                key=lambda x: x['count'],
                reverse=True
            ),
            'manufacturers': sorted(
                [{'manufacturer': k, 'count': v} for k, v in aggregated['manufacturers'].items()],
                key=lambda x: x['count'],
                reverse=True
            ),
            'models': sorted(
                [{'model': k, 'count': v} for k, v in aggregated['models'].items()],
                key=lambda x: x['count'],
                reverse=True
            ),
            'systems': sorted(
                [{'system': k, 'count': v} for k, v in aggregated['systems'].items()],
                key=lambda x: x['count'],
                reverse=True
            ),
            'diagnostic_terms': sorted(
                [{'term': k, 'count': v} for k, v in aggregated['diagnostic_terms'].items()],
                key=lambda x: x['count'],
                reverse=True
            ),
            'total_automotive_segments': sum(1 for s in segment_analyses if s['automotive_mentions'] > 0),
            'total_segments': len(segments)
        }

        return {
            'summary': summary,
            'segments': segment_analyses
        }

    def _detect_vehicle_types(self, text: str) -> List[str]:
        """Detect vehicle types mentioned in text."""
        detected = set()
        text_lower = text.lower()

        for vtype, keywords in self.VEHICLE_TYPES.items():
            for keyword in keywords:
                if keyword.lower() in text_lower:
                    detected.add(vtype)
                    break

        return sorted(list(detected))

    def _detect_manufacturers(self, text: str) -> List[str]:
        """Detect automobile manufacturers mentioned in text."""
        detected = set()
        text_lower = text.lower()

        for manufacturer, pattern in self.manufacturer_patterns:
            # Try pattern matching first
            if pattern.search(text):
                detected.add(manufacturer)
            # For Russian manufacturers, also check if the stem appears anywhere
            # (handles cases like "Ладу" vs "Лада")
            elif manufacturer in ['лада', 'ваз'] and manufacturer[:3] in text_lower:
                detected.add(manufacturer)
            elif manufacturer in ['газ'] and manufacturer in text_lower:
                detected.add(manufacturer)
            elif manufacturer in ['уаз'] and manufacturer in text_lower:
                detected.add(manufacturer)

        return sorted(list(detected))

    def _detect_models(self, text: str) -> List[str]:
        """Detect automobile models mentioned in text."""
        detected = set()
        text_lower = text.lower()

        for model, pattern in self.model_patterns:
            # Try pattern matching first
            if pattern.search(text):
                detected.add(model)
            # For Russian models, also check if the stem appears anywhere
            # (handles cases like "Весту" vs "Веста")
            elif model in ['веста', 'гранта', 'нива', 'калина', 'приора']:
                # Check if the first 4 characters of the model appear in text
                if len(model) >= 4 and model[:4] in text_lower:
                    detected.add(model)

        return sorted(list(detected))

    def _detect_systems(self, text: str) -> List[str]:
        """Detect automotive systems mentioned in text."""
        detected = set()
        text_lower = text.lower()

        for system, keywords in self.SYSTEMS.items():
            for keyword in keywords:
                if keyword.lower() in text_lower:
                    detected.add(system)
                    break

        return sorted(list(detected))

    def _detect_diagnostic_terms(self, text: str) -> List[str]:
        """Detect diagnostic/maintenance terms in text."""
        detected = set()
        text_lower = text.lower()

        for term, keywords in self.DIAGNOSTIC_TERMS.items():
            for keyword in keywords:
                if keyword.lower() in text_lower:
                    detected.add(term)
                    break

        return sorted(list(detected))

    def _empty_result(self) -> Dict[str, Any]:
        """Return empty analysis result."""
        return {
            'vehicle_types': [],
            'manufacturers': [],
            'models': [],
            'systems': [],
            'diagnostic_terms': [],
            'total_automotive_mentions': 0
        }

    def is_automotive_related(self, text: str, threshold: int = 1) -> bool:
        """
        Check if text is automotive-related based on mention threshold.

        Args:
            text: Input text
            threshold: Minimum number of automotive mentions to consider text as automotive-related

        Returns:
            True if text contains automotive content above threshold
        """
        analysis = self.analyze_text(text)
        return analysis['total_automotive_mentions'] >= threshold

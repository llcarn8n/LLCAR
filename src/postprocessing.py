"""
Post-processing Module
Cleans text, removes filler words, extracts keywords, performs NER, and automotive typology analysis.
"""

import re
import logging
from typing import List, Dict, Any, Set, Optional
from sklearn.feature_extraction.text import TfidfVectorizer
from summa import keywords as summa_keywords
from .automotive_typology import AutomotiveTypologyAnalyzer

logger = logging.getLogger(__name__)

_nltk_data_ensured = False


def _ensure_nltk_data():
    """Download required NLTK data once on first use."""
    global _nltk_data_ensured
    if _nltk_data_ensured:
        return
    import nltk
    for resource, name in [('tokenizers/punkt', 'punkt'), ('corpora/stopwords', 'stopwords')]:
        try:
            nltk.data.find(resource)
        except LookupError:
            nltk.download(name, quiet=True)
    _nltk_data_ensured = True


class TextPostProcessor:
    """Post-processes transcribed text."""

    # Single-word fillers (checked per word)
    RUSSIAN_SINGLE_FILLERS = {
        'ну', 'вот', 'это', 'типа', 'короче', 'значит', 'собственно',
        'слушай', 'знаешь', 'понимаешь', 'видишь', 'эээ', 'ммм', 'ааа'
    }

    ENGLISH_SINGLE_FILLERS = {
        'um', 'uh', 'basically', 'actually', 'literally', 'well', 'so',
        'right', 'okay', 'like'
    }

    CHINESE_SINGLE_FILLERS = {
        '嗯', '啊', '呃', '对'
    }

    # Multi-word filler phrases (removed via regex substitution)
    RUSSIAN_PHRASE_FILLERS = [
        'как бы', 'в общем', 'то есть', 'так сказать', 'в принципе'
    ]

    ENGLISH_PHRASE_FILLERS = [
        'you know', 'i mean', 'sort of', 'kind of'
    ]

    CHINESE_PHRASE_FILLERS = [
        '那个', '这个', '就是', '然后'
    ]

    # Curated Russian profanity word stems for censoring
    RUSSIAN_PROFANITY_STEMS = [
        'хуй', 'хуе', 'хуя', 'хуё', 'пизд', 'блят', 'бляд', 'блядь',
        'ебат', 'ёбан', 'ебан', 'ебну', 'ебал', 'ебло', 'ёбан',
        'сука', 'сучк', 'сучар', 'пидор', 'пидар', 'залуп', 'муда',
        'мудак', 'мудил', 'дерьм', 'жопа', 'жоп',
    ]

    def __init__(self, language: str = "en", remove_fillers: bool = True, remove_profanity: bool = True):
        """
        Initialize TextPostProcessor.

        Args:
            language: Language code ('en', 'ru', 'zh')
            remove_fillers: Whether to remove filler words
            remove_profanity: Whether to censor profanity
        """
        _ensure_nltk_data()

        self.language = language
        self.remove_fillers = remove_fillers
        self.remove_profanity = remove_profanity

        # Select filler words based on language
        if language == "ru":
            self.single_fillers = self.RUSSIAN_SINGLE_FILLERS
            self.phrase_fillers = self.RUSSIAN_PHRASE_FILLERS
        elif language == "zh":
            self.single_fillers = self.CHINESE_SINGLE_FILLERS
            self.phrase_fillers = self.CHINESE_PHRASE_FILLERS
        else:
            self.single_fillers = self.ENGLISH_SINGLE_FILLERS
            self.phrase_fillers = self.ENGLISH_PHRASE_FILLERS

        # Build profanity pattern from curated word list
        if language == "ru" and self.RUSSIAN_PROFANITY_STEMS:
            escaped = [re.escape(stem) for stem in self.RUSSIAN_PROFANITY_STEMS]
            self._profanity_pattern = re.compile(
                r'\b\w*(?:' + '|'.join(escaped) + r')\w*\b', re.IGNORECASE
            )
        else:
            self._profanity_pattern = None

        logger.info(f"TextPostProcessor initialized for language: {language}")

    def clean_text(self, text: str) -> str:
        """
        Clean text by removing fillers, profanity, and extra whitespace.

        Args:
            text: Input text

        Returns:
            Cleaned text
        """
        if not text:
            return ""

        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()

        # Remove filler words
        if self.remove_fillers:
            text = self._remove_fillers(text)

        # Censor profanity
        if self.remove_profanity and self._profanity_pattern:
            text = self._censor_profanity(text)

        # Remove duplicate consecutive words
        text = self._remove_duplicates(text)

        # Clean up punctuation
        text = re.sub(r'\s+([.,!?;:])', r'\1', text)
        text = re.sub(r'([.,!?;:])\1+', r'\1', text)

        return text.strip()

    def _remove_fillers(self, text: str) -> str:
        """Remove filler words and phrases from text."""
        # First remove multi-word phrases (longest first to avoid partial matches)
        for phrase in sorted(self.phrase_fillers, key=len, reverse=True):
            pattern = re.compile(r'\b' + re.escape(phrase) + r'\b', re.IGNORECASE)
            text = pattern.sub('', text)

        # Then remove single-word fillers
        words = text.split()
        cleaned_words = [w for w in words if w.lower() not in self.single_fillers]
        return ' '.join(cleaned_words)

    def _censor_profanity(self, text: str) -> str:
        """Censor profanity using curated word list."""
        return self._profanity_pattern.sub('***', text)

    def _remove_duplicates(self, text: str) -> str:
        """Remove consecutive duplicate words."""
        words = text.split()
        if not words:
            return ""

        cleaned = [words[0]]
        for i in range(1, len(words)):
            if words[i].lower() != words[i - 1].lower():
                cleaned.append(words[i])

        return ' '.join(cleaned)

    def process_segments(self, segments: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Process all transcription segments.

        Args:
            segments: List of transcription segments

        Returns:
            List of processed segments
        """
        processed_segments = []

        for segment in segments:
            processed_segment = segment.copy()
            processed_segment["text"] = self.clean_text(segment.get("text", ""))
            processed_segment["original_text"] = segment.get("text", "")
            processed_segments.append(processed_segment)

        return processed_segments


class KeywordExtractor:
    """Extracts keywords from text using TF-IDF and TextRank."""

    def __init__(self, language: str = "en"):
        """
        Initialize KeywordExtractor.

        Args:
            language: Language code ('en', 'ru', 'zh')
        """
        self.language = language

    def extract_tfidf_keywords(
        self,
        texts: List[str],
        top_n: int = 10,
        max_features: int = 100
    ) -> List[Dict[str, float]]:
        """
        Extract keywords using TF-IDF.

        Args:
            texts: List of text documents (each segment as a separate document)
            top_n: Number of top keywords to extract
            max_features: Maximum number of features for TF-IDF

        Returns:
            List of keyword dictionaries with scores
        """
        if not texts or all(not t.strip() for t in texts):
            return []

        # Filter out empty texts
        docs = [t for t in texts if t.strip()]
        if not docs:
            return []

        try:
            vectorizer = TfidfVectorizer(
                max_features=max_features,
                stop_words='english' if self.language == 'en' else None,
                ngram_range=(1, 2)
            )

            # Each segment is a separate document for proper IDF calculation
            tfidf_matrix = vectorizer.fit_transform(docs)

            # Average TF-IDF scores across all documents
            feature_names = vectorizer.get_feature_names_out()
            avg_scores = tfidf_matrix.mean(axis=0).A1

            # Sort by score
            keyword_scores = sorted(
                zip(feature_names, avg_scores),
                key=lambda x: x[1],
                reverse=True
            )

            return [
                {"keyword": kw, "score": float(score)}
                for kw, score in keyword_scores[:top_n]
            ]

        except Exception as e:
            logger.error(f"Error extracting TF-IDF keywords: {e}")
            return []

    def extract_textrank_keywords(
        self,
        text: str,
        top_n: int = 10,
        ratio: float = 0.2
    ) -> List[str]:
        """
        Extract keywords using TextRank algorithm.

        Args:
            text: Input text
            top_n: Number of top keywords to extract
            ratio: Ratio of keywords to extract from text

        Returns:
            List of keywords
        """
        if not text.strip():
            return []

        try:
            # Use summa library for TextRank
            keywords_str = summa_keywords.keywords(
                text,
                ratio=ratio,
                words=top_n,
                split=True
            )

            return keywords_str if keywords_str else []

        except Exception as e:
            logger.error(f"Error extracting TextRank keywords: {e}")
            return []

    def extract_keywords_from_segments(
        self,
        segments: List[Dict[str, Any]],
        method: str = "tfidf",
        top_n: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Extract keywords from transcription segments.

        Args:
            segments: List of transcription segments
            method: Extraction method ('tfidf' or 'textrank')
            top_n: Number of top keywords

        Returns:
            List of keywords with metadata
        """
        texts = [seg.get("text", "") for seg in segments]

        if method == "tfidf":
            return self.extract_tfidf_keywords(texts, top_n)
        elif method == "textrank":
            combined_text = ' '.join(texts)
            keywords_list = self.extract_textrank_keywords(combined_text, top_n)
            return [{"keyword": kw, "score": None} for kw in keywords_list]
        else:
            logger.warning(f"Unknown method: {method}. Using TF-IDF.")
            return self.extract_tfidf_keywords(texts, top_n)


class ComprehensivePostProcessor:
    """Comprehensive post-processing including text cleaning, keywords, and automotive analysis."""

    def __init__(
        self,
        language: str = "en",
        remove_fillers: bool = True,
        remove_profanity: bool = True,
        extract_keywords: bool = True,
        keyword_method: str = "tfidf",
        top_keywords: int = 10,
        enable_automotive_analysis: bool = True
    ):
        """
        Initialize ComprehensivePostProcessor.

        Args:
            language: Language code ('en', 'ru', 'zh')
            remove_fillers: Whether to remove filler words
            remove_profanity: Whether to censor profanity
            extract_keywords: Whether to extract keywords
            keyword_method: Keyword extraction method ('tfidf' or 'textrank')
            top_keywords: Number of top keywords to extract
            enable_automotive_analysis: Whether to perform automotive typology analysis
        """
        self.language = language
        self.extract_keywords = extract_keywords
        self.keyword_method = keyword_method
        self.top_keywords = top_keywords
        self.enable_automotive_analysis = enable_automotive_analysis

        # Initialize sub-processors
        self.text_processor = TextPostProcessor(language, remove_fillers, remove_profanity)
        self.keyword_extractor = KeywordExtractor(language) if extract_keywords else None
        self.automotive_analyzer = AutomotiveTypologyAnalyzer(language) if enable_automotive_analysis else None

        logger.info(
            f"ComprehensivePostProcessor initialized: "
            f"language={language}, keywords={extract_keywords}, automotive={enable_automotive_analysis}"
        )

    def process(self, segments: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Perform comprehensive post-processing on transcription segments.

        Args:
            segments: List of transcription segments

        Returns:
            Dictionary containing processed segments, keywords, and automotive analysis
        """
        result = {
            'segments': [],
            'keywords': [],
            'automotive_typology': None
        }

        # Process text in segments
        processed_segments = self.text_processor.process_segments(segments)
        result['segments'] = processed_segments

        # Extract keywords
        if self.extract_keywords and self.keyword_extractor:
            result['keywords'] = self.keyword_extractor.extract_keywords_from_segments(
                processed_segments,
                method=self.keyword_method,
                top_n=self.top_keywords
            )

        # Perform automotive typology analysis
        if self.enable_automotive_analysis and self.automotive_analyzer:
            result['automotive_typology'] = self.automotive_analyzer.analyze_segments(processed_segments)

        return result

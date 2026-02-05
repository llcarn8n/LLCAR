"""
Post-processing Module
Cleans text, removes filler words, extracts keywords, and performs NER.
"""

import re
import logging
from typing import List, Dict, Any, Set
from sklearn.feature_extraction.text import TfidfVectorizer
from summa import keywords as summa_keywords
import nltk

logger = logging.getLogger(__name__)

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt', quiet=True)

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords', quiet=True)


class TextPostProcessor:
    """Post-processes transcribed text."""

    # Russian filler words and profanity patterns
    RUSSIAN_FILLERS = {
        'ну', 'вот', 'это', 'как бы', 'типа', 'короче', 'в общем',
        'то есть', 'значит', 'так сказать', 'в принципе', 'собственно',
        'слушай', 'знаешь', 'понимаешь', 'видишь', 'эээ', 'ммм', 'ааа'
    }

    # English filler words
    ENGLISH_FILLERS = {
        'um', 'uh', 'like', 'you know', 'i mean', 'basically', 'actually',
        'literally', 'sort of', 'kind of', 'well', 'so', 'right', 'okay'
    }

    # Chinese filler words (simplified)
    CHINESE_FILLERS = {
        '嗯', '啊', '呃', '那个', '这个', '就是', '然后', '对'
    }

    # Profanity placeholder pattern
    PROFANITY_PATTERN = re.compile(r'\b\w*[бпхё][ляуеёаоыэяию]*[тдцксзжшщчх][ьъ]?\w*\b', re.IGNORECASE)

    def __init__(self, language: str = "en", remove_fillers: bool = True, remove_profanity: bool = True):
        """
        Initialize TextPostProcessor.

        Args:
            language: Language code ('en', 'ru', 'zh')
            remove_fillers: Whether to remove filler words
            remove_profanity: Whether to censor profanity
        """
        self.language = language
        self.remove_fillers = remove_fillers
        self.remove_profanity = remove_profanity

        # Select filler words based on language
        if language == "ru":
            self.fillers = self.RUSSIAN_FILLERS
        elif language == "zh":
            self.fillers = self.CHINESE_FILLERS
        else:
            self.fillers = self.ENGLISH_FILLERS

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
        if self.remove_profanity and self.language == "ru":
            text = self._censor_profanity(text)

        # Remove duplicate consecutive words
        text = self._remove_duplicates(text)

        # Clean up punctuation
        text = re.sub(r'\s+([.,!?;:])', r'\1', text)
        text = re.sub(r'([.,!?;:])\1+', r'\1', text)

        return text.strip()

    def _remove_fillers(self, text: str) -> str:
        """Remove filler words from text."""
        words = text.split()
        cleaned_words = [w for w in words if w.lower() not in self.fillers]
        return ' '.join(cleaned_words)

    def _censor_profanity(self, text: str) -> str:
        """Censor profanity in Russian text."""
        # Simple pattern-based censoring (can be improved with dedicated libraries)
        return self.PROFANITY_PATTERN.sub('***', text)

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
            texts: List of text documents
            top_n: Number of top keywords to extract
            max_features: Maximum number of features for TF-IDF

        Returns:
            List of keyword dictionaries with scores
        """
        if not texts or all(not t.strip() for t in texts):
            return []

        try:
            vectorizer = TfidfVectorizer(
                max_features=max_features,
                stop_words='english' if self.language == 'en' else None,
                ngram_range=(1, 2)
            )

            # Combine texts for TF-IDF
            combined_text = ' '.join(texts)
            tfidf_matrix = vectorizer.fit_transform([combined_text])

            # Get feature names and scores
            feature_names = vectorizer.get_feature_names_out()
            scores = tfidf_matrix.toarray()[0]

            # Sort by score
            keyword_scores = sorted(
                zip(feature_names, scores),
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

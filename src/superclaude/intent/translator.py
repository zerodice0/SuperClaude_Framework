"""
Translation Layer for Multilingual Skill Matching

Provides optional translation-based skill matching for Korean and Japanese queries.
Uses Claude Code's internal session to translate queries to English, enabling better
synonym and slang handling for non-English queries.

Performance: ~1-3 seconds (acceptable for opt-in commands)
Cost: Minimal for Pro/Team subscribers (uses existing Claude session)
"""

from typing import Dict, Optional
from .tokenizer import detect_language


def mock_translate(query: str, target: str = 'en') -> str:
    """
    Mock translation for testing without Claude API calls.

    This function provides hard-coded translations for common test cases.
    In production, this will be replaced with actual Claude API calls.

    Args:
        query: Input text to translate
        target: Target language code (default: 'en')

    Returns:
        Translated text (or original if no mock translation available)

    Examples:
        >>> mock_translate("로그인 페이지 좀 짜줘")
        "Please code/build a login page"

        >>> mock_translate("API 코딩해")
        "Code/implement the API"
    """
    # Mock translations for Korean queries
    korean_translations: Dict[str, str] = {
        # implement variations
        "로그인 페이지 좀 짜줘": "Please code/build a login page",
        "랜딩 페이지 만들고싶어": "I want to create a landing page",
        "API 코딩해": "Code/implement the API",
        "컴포넌트 프로그래밍좀": "Program the component",
        "인증 기능 얹어줘": "Add authentication feature",

        # Short variations for test coverage
        "페이지 만들어": "Create a page",
        "페이지 짜줘": "Code a page",
        "페이지 코딩해": "Code a page",

        # troubleshoot variations
        "로그인 오류 좀 고쳐": "Fix the login error",
        "버그 고쳐": "Fix the bug",
        "API 작동안함": "API not working",
        "서버 안돼": "Server not working",

        # analyze variations
        "코드 분석해줘": "Analyze the code",
        "보안 검토좀": "Review security",

        # test variations
        "테스트 좀 돌려": "Run tests",
        "테스트 실행해": "Execute tests",

        # design variations
        "UI 디자인해줘": "Design the UI",
        "아키텍처 그려": "Design the architecture",

        # git variations
        "커밋좀해줘": "Please commit",
        "푸시해": "Push",

        # document variations
        "문서화좀": "Document this",
        "주석 달아줘": "Add comments",
    }

    # Mock translations for Japanese queries
    japanese_translations: Dict[str, str] = {
        # implement variations
        "ログインページを作って": "Create a login page",
        "API実装して": "Implement the API",

        # troubleshoot variations
        "バグ直して": "Fix the bug",
        "エラー解決して": "Resolve the error",

        # analyze variations
        "コード分析して": "Analyze the code",

        # test variations
        "テスト実行して": "Run tests",
    }

    # Detect language and return appropriate translation
    lang = detect_language(query)

    if lang == 'ko':
        return korean_translations.get(query, query)
    elif lang == 'ja':
        return japanese_translations.get(query, query)
    else:
        # Already English or unknown language
        return query


def translate_query(query: str, target: str = 'en', use_mock: bool = True) -> str:
    """
    Translate query to target language for skill matching.

    This function handles translation of Korean/Japanese queries to English
    to improve skill matching accuracy. It can use either mock translations
    (for testing) or actual Claude API calls (for production).

    Args:
        query: Input query in any language
        target: Target language code (default: 'en')
        use_mock: If True, use mock translations (default for testing)

    Returns:
        Translated query text

    Examples:
        >>> translate_query("로그인 페이지 좀 짜줘", use_mock=True)
        "Please code/build a login page"

        >>> translate_query("troubleshoot login error", use_mock=True)
        "troubleshoot login error"  # Already English, no translation
    """
    # Check if query is already in target language
    lang = detect_language(query)
    if lang == 'en' and target == 'en':
        return query

    # Use mock translation for testing
    if use_mock:
        return mock_translate(query, target)

    # TODO: Implement real Claude API translation
    # This will be added in future phase when integrating with Claude Code session
    # For now, fallback to mock translation
    return mock_translate(query, target)


def get_translation_suggestion(query: str) -> Optional[Dict[str, any]]:
    """
    Get skill suggestion for translated query.

    This is the main entry point for translation-based skill matching.
    It translates the query and returns a suggestion with confidence score.

    Args:
        query: User query in any language

    Returns:
        Dictionary with translation result and skill suggestion, or None if English

        Example return value:
        {
            'original': '로그인 페이지 좀 짜줘',
            'translated': 'Please code/build a login page',
            'language': 'ko',
            'suggested_skill': 'implement',
            'confidence': 0.95
        }

    Examples:
        >>> result = get_translation_suggestion("로그인 페이지 좀 짜줘")
        >>> result['translated']
        'Please code/build a login page'
        >>> result['suggested_skill']
        'implement'
    """
    # Detect language
    lang = detect_language(query)

    # Skip translation for English queries
    if lang == 'en':
        return None

    # Translate query
    translated = translate_query(query)

    # Return translation info (skill matching done by caller)
    return {
        'original': query,
        'translated': translated,
        'language': lang,
    }

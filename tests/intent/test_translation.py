"""
Tests for Translation-based Skill Matching

Validates that Korean/Japanese queries can be translated to English
and matched to appropriate skills with high confidence.
"""

import pytest
from pathlib import Path
from superclaude.intent.translator import (
    mock_translate,
    translate_query,
    get_translation_suggestion,
)
from superclaude.intent import SkillMatcher


class TestMockTranslation:
    """Test mock translation functionality."""

    def test_korean_implement_variations(self):
        """Test Korean variations of 'implement' action."""
        test_cases = [
            ("로그인 페이지 좀 짜줘", "code", "build", "login page"),
            ("랜딩 페이지 만들고싶어", "create", "landing page"),
            ("API 코딩해", "code", "implement", "API"),
            ("컴포넌트 프로그래밍좀", "program", "component"),
            ("인증 기능 얹어줘", "add", "authentication"),
        ]

        for korean_query, *expected_keywords in test_cases:
            translated = mock_translate(korean_query)
            assert translated != korean_query, f"Should translate: {korean_query}"
            # Check that at least one expected keyword appears
            assert any(kw in translated.lower() for kw in expected_keywords), \
                f"Translation '{translated}' should contain one of: {expected_keywords}"

    def test_korean_troubleshoot_variations(self):
        """Test Korean variations of 'troubleshoot' action."""
        test_cases = [
            ("로그인 오류 좀 고쳐", "fix", "login", "error"),
            ("버그 고쳐", "fix", "bug"),
            ("API 작동안함", "API", "not working"),
            ("서버 안돼", "server", "not working"),
        ]

        for korean_query, *expected_keywords in test_cases:
            translated = mock_translate(korean_query)
            assert translated != korean_query
            assert any(kw in translated.lower() for kw in expected_keywords)

    def test_korean_other_skills(self):
        """Test Korean queries for various other skills."""
        test_cases = [
            ("코드 분석해줘", "analyze", "code"),
            ("테스트 좀 돌려", "run", "test"),
            ("UI 디자인해줘", "design", "UI"),
            ("커밋좀해줘", "commit"),
            ("문서화좀", "document"),
        ]

        for korean_query, *expected_keywords in test_cases:
            translated = mock_translate(korean_query)
            assert translated != korean_query
            assert any(kw in translated.lower() for kw in expected_keywords)

    def test_japanese_translations(self):
        """Test Japanese query translations."""
        test_cases = [
            ("ログインページを作って", "create", "login page"),
            ("API実装して", "implement", "API"),
            ("バグ直して", "fix", "bug"),
            ("エラー解決して", "resolve", "error"),
        ]

        for japanese_query, *expected_keywords in test_cases:
            translated = mock_translate(japanese_query)
            assert translated != japanese_query
            assert any(kw in translated.lower() for kw in expected_keywords)

    def test_english_passthrough(self):
        """Test that English queries pass through unchanged."""
        english_queries = [
            "troubleshoot login error",
            "implement user authentication",
            "analyze code quality",
        ]

        for query in english_queries:
            translated = mock_translate(query)
            assert translated == query, "English should not be translated"


class TestTranslateQuery:
    """Test translate_query function."""

    def test_translate_korean_with_mock(self):
        """Test Korean translation with mock mode."""
        query = "로그인 페이지 좀 짜줘"
        translated = translate_query(query, use_mock=True)

        assert translated != query
        assert "login page" in translated.lower()

    def test_translate_japanese_with_mock(self):
        """Test Japanese translation with mock mode."""
        query = "ログインページを作って"
        translated = translate_query(query, use_mock=True)

        assert translated != query
        assert "login page" in translated.lower()

    def test_translate_english_no_change(self):
        """Test that English queries are not translated."""
        query = "implement user authentication"
        translated = translate_query(query, use_mock=True)

        assert translated == query, "English should not be translated"

    def test_translate_unknown_korean_fallback(self):
        """Test unknown Korean query returns original."""
        query = "알수없는한글쿼리"
        translated = translate_query(query, use_mock=True)

        # Should return original if no mock translation available
        assert translated == query


class TestGetTranslationSuggestion:
    """Test get_translation_suggestion function."""

    def test_korean_query_suggestion(self):
        """Test translation suggestion for Korean query."""
        query = "로그인 페이지 좀 짜줘"
        result = get_translation_suggestion(query)

        assert result is not None
        assert result['original'] == query
        assert result['translated'] != query
        assert result['language'] == 'ko'
        assert 'login page' in result['translated'].lower()

    def test_japanese_query_suggestion(self):
        """Test translation suggestion for Japanese query."""
        query = "ログインページを作って"
        result = get_translation_suggestion(query)

        assert result is not None
        assert result['original'] == query
        assert result['translated'] != query
        assert result['language'] == 'ja'

    def test_english_query_no_suggestion(self):
        """Test that English queries return None."""
        query = "implement user authentication"
        result = get_translation_suggestion(query)

        assert result is None, "English queries should not return suggestions"


class TestTranslationWithSkillMatching:
    """Integration tests for translation + skill matching."""

    @pytest.fixture
    def matcher(self):
        """Create SkillMatcher instance."""
        skills_dir = Path(__file__).parents[2] / "skills"
        return SkillMatcher(skills_dir)

    def test_korean_implement_slang_matching(self, matcher):
        """Test Korean slang '짜줘' matches implement skill via translation."""
        # Original query with slang (not in keywords)
        korean_query = "로그인 페이지 좀 짜줘"

        # Translate first
        translated = translate_query(korean_query)

        # Match translated query
        result = matcher.match(translated)

        # Should match implement skill with high confidence
        assert len(result.matches) > 0
        top_match = result.matches[0]
        assert top_match.skill.name == "implement"
        assert top_match.confidence >= 0.60, \
            f"Expected confidence >= 0.60, got {top_match.confidence}"

    def test_korean_troubleshoot_slang_matching(self, matcher):
        """Test Korean slang '작동안함' matches troubleshoot via translation."""
        korean_query = "API 작동안함"
        translated = translate_query(korean_query)
        result = matcher.match(translated)

        assert len(result.matches) > 0
        # Should match troubleshoot skill
        skill_names = [m.skill.name for m in result.matches]
        assert "troubleshoot" in skill_names

    def test_korean_coding_verb_matching(self, matcher):
        """Test Korean '코딩해' matches implement skill via translation."""
        korean_query = "API 코딩해"
        translated = translate_query(korean_query)
        result = matcher.match(translated)

        assert len(result.matches) > 0
        skill_names = [m.skill.name for m in result.matches]
        assert "implement" in skill_names

    def test_japanese_implement_matching(self, matcher):
        """Test Japanese query matches implement skill via translation."""
        japanese_query = "ログインページを作って"
        translated = translate_query(japanese_query)
        result = matcher.match(translated)

        assert len(result.matches) > 0
        skill_names = [m.skill.name for m in result.matches]
        assert "implement" in skill_names

    def test_translation_improves_confidence(self, matcher):
        """Test that translation improves confidence for slang queries."""
        # Query with slang that's NOT in keywords
        korean_slang = "로그인 페이지 좀 짜줘"

        # Direct match (without translation) - should be low or no match
        direct_result = matcher.match(korean_slang)
        direct_confidence = direct_result.matches[0].confidence if direct_result.matches else 0.0

        # Translated match - should be higher
        translated = translate_query(korean_slang)
        translated_result = matcher.match(translated)
        translated_confidence = translated_result.matches[0].confidence if translated_result.matches else 0.0

        # Translation should significantly improve confidence
        assert translated_confidence > direct_confidence, \
            f"Translation confidence ({translated_confidence}) should be > direct ({direct_confidence})"

    def test_translation_coverage_improvement(self, matcher):
        """Test that translation expands Korean synonym coverage."""
        # Queries with different synonyms for "implement"
        korean_queries = [
            "페이지 만들어",  # 만들다 - in keywords ✅
            "페이지 짜줘",     # 짜다 - slang, NOT in keywords ❌
            "페이지 코딩해",   # 코딩하다 - NOT in keywords ❌
        ]

        # All should match implement after translation
        for query in korean_queries:
            translated = translate_query(query)
            result = matcher.match(translated)

            assert len(result.matches) > 0, f"No matches for: {query} → {translated}"
            skill_names = [m.skill.name for m in result.matches]
            assert "implement" in skill_names, \
                f"Should match implement for: {query} → {translated}"


class TestTranslationPerformance:
    """Performance and edge case tests."""

    def test_translation_handles_mixed_language(self):
        """Test mixed Korean-English queries."""
        query = "API 코딩해"  # Mixed: API (English) + 코딩해 (Korean)
        translated = translate_query(query)

        assert "api" in translated.lower()
        assert "code" in translated.lower() or "implement" in translated.lower()

    def test_translation_handles_empty_string(self):
        """Test empty string handling."""
        query = ""
        translated = translate_query(query)

        assert translated == query

    def test_translation_handles_whitespace(self):
        """Test whitespace-only string handling."""
        query = "   "
        translated = translate_query(query)

        assert translated == query

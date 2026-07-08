"""
Testes para DatingAIAnalyzer (framework/instances/dating/strategies/ai_analyzer.py).

Estes testes NÃO fazem nenhuma chamada de rede já que o GeminiAIAnalyzer real é
substituído por um dublê (fake) injetado no construtor.

"""

from __future__ import annotations

from framework.ai.exceptions import AIAnalysisError
from framework.instances.demo_models import DemoObject
from framework.instances.dating.strategies.ai_analyzer import (
    DatingAIAnalyzer,
    _DEMO_FALLBACK_ATTRIBUTES,
)


class _FakeGeminiAnalyzer:
    """Dublê de GeminiAIAnalyzer controlável pelo teste."""

    def __init__(self, *, result=None, error=None):
        self.result = result
        self.error = error
        self.calls: list[tuple] = []

    def analyze_photo(self, photo, prompt=None):
        self.calls.append((photo, prompt))
        if self.error:
            raise self.error
        return self.result


def test_delegates_to_gemini_and_returns_real_attributes_on_success():
    """Quando o Gemini responde com sucesso, o resultado real é devolvido."""
    expected = [{"attribute_token": "personality.adventurous", "strength": 0.75}]
    fake = _FakeGeminiAnalyzer(result=expected)
    analyzer = DatingAIAnalyzer(gemini_analyzer=fake)
    photo = DemoObject(id=1, image="profile.jpg")

    attributes = analyzer.analyze_photo(photo, prompt="Analise este perfil.")

    assert attributes == expected
    assert fake.calls == [(photo, "Analise este perfil.")]


def test_falls_back_to_demo_attributes_when_gemini_call_fails():
    """
    Se a chamada real ao Gemini falhar (ex.: ambiente de demo sem imagem
    real), o analisador não deve quebrar o fluxo: ele registra um aviso e
    retorna os atributos de demonstração.
    """
    fake = _FakeGeminiAnalyzer(error=AIAnalysisError("boom"))
    analyzer = DatingAIAnalyzer(gemini_analyzer=fake)
    photo = DemoObject(id=2, image="profile.jpg")

    attributes = analyzer.analyze_photo(photo)

    assert attributes == _DEMO_FALLBACK_ATTRIBUTES
    assert fake.calls == [(photo, None)]


def test_default_construction_wires_up_the_real_photo_analysis_config(monkeypatch):
    """
    Sem um analyzer injetado, a classe deve montar (sob demanda) um
    GeminiAIAnalyzer real, configurado com DatingPhotoAnalysisConfig — não
    mais com o mock antigo.

    GEMINI_API_KEY é um valor fictício apenas para permitir a construção do
    cliente offline (genai.configure/GenerativeModel não fazem chamada de
    rede); nenhuma requisição real é feita neste teste.
    """
    monkeypatch.setenv("GEMINI_API_KEY", "dummy-key-for-tests")
    analyzer = DatingAIAnalyzer()
    gemini_analyzer = analyzer._get_gemini_analyzer()

    from framework.ai.gemini_ai_analyzer import GeminiAIAnalyzer
    from framework.instances.dating.photo_analysis_config import (
        DatingPhotoAnalysisConfig,
    )

    assert isinstance(gemini_analyzer, GeminiAIAnalyzer)
    assert isinstance(gemini_analyzer.config, DatingPhotoAnalysisConfig)


def test_missing_api_key_falls_back_instead_of_crashing(monkeypatch):
    """
    Regressão: sem GEMINI_API_KEY no ambiente, DatingAIAnalyzer() não deve
    lançar exceção ao ser construído (isso quebraria `demo.py` e
    `create_dating_app()` de imediato). A falha só deve aparecer, de forma
    controlada, quando analyze_photo() é chamado — e nesse caso o fallback
    de demonstração deve ser usado.
    """
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.delenv("GEMINI_MODEL", raising=False)

    analyzer = DatingAIAnalyzer()  # não deve lançar
    photo = DemoObject(id=3, image="profile.jpg")

    attributes = analyzer.analyze_photo(photo)

    assert attributes == _DEMO_FALLBACK_ATTRIBUTES

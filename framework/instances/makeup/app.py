from framework.ai.gemini_ai_analyzer import GeminiAIAnalyzer
from framework.framework import HomeMatchFramework
from framework.search.gemini_query_interpreter import GeminiQueryInterpreter

from framework.instances.makeup.ai_config import MakeupAIConfig
from framework.instances.makeup.search_config import MakeupSearchConfig
from framework.instances.makeup.attribute_storage import MakeupAttributeStorage
from framework.instances.makeup.repositories.user_repository import MakeupUserRepository
from framework.instances.makeup.repositories.post_repository import MakeupPostRepository
from framework.instances.makeup.repositories.photo_repository import MakeupPhotoRepository
from framework.instances.makeup.strategies.match_score import MakeupMatchScoreStrategy
from framework.instances.makeup.strategies.search_pool import MakeupSearchPool


def create_makeup_app(
    *,
    ai_analyzer=None,
    query_interpreter=None,
) -> HomeMatchFramework:

    if ai_analyzer is None:
        ai_analyzer = GeminiAIAnalyzer(
            config=MakeupAIConfig(),
        )

    if query_interpreter is None:
        search_config = MakeupSearchConfig()

        query_interpreter = GeminiQueryInterpreter(
            prompt=search_config.get_prompt(),
            schema=search_config.get_schema(),
        )

    return HomeMatchFramework(
        user_repository=MakeupUserRepository(),
        post_repository=MakeupPostRepository(),
        photo_repository=MakeupPhotoRepository(),
        attribute_storage=MakeupAttributeStorage(),
        ai_analyzer=ai_analyzer,
        query_interpreter=query_interpreter,
        match_score_strategy=MakeupMatchScoreStrategy(),
        search_pool=MakeupSearchPool(),
    )

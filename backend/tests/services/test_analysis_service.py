import pytest
import io
import json
from backend.services.analysis_service import AnalysisService
from backend.api.models import PreparationAnalysis

pytestmark = pytest.mark.asyncio


@pytest.fixture
def service(mocker):
    """
    Фикстура для создания экземпляра AnalysisService с "замоканными"
    внешними зависимостями в __init__.
    """
    mocker.patch("assemblyai.settings.api_key")
    mocker.patch("googleapiclient.discovery.build")
    return AnalysisService()


async def test_analyze_preparation_success(service, mocker):
    """
    Тест: Успешное выполнение пайплайна подготовки к интервью.
    Проверяем, что сервис корректно вызывает всех агентов и парсит финальный JSON.
    """
    mock_csv_content = "Категория,Грейд,Требование\nQA,Senior,Опыт"
    mocker.patch("builtins.open", mocker.mock_open(read_data=mock_csv_content))

    mock_agent_1_output = json.dumps({"candidate_info": {"first_name": "Иван"}})
    mock_agent_2_output = json.dumps({
        "candidate_info": {"first_name": "Иван"},
        "assessment": {"grade": "Senior"}
    })
    mock_agent_3_output = json.dumps({
        "report": {
            "first_name": "Иван", "last_name": "Иванов",
            "matching_table": [], "candidate_profile": "QA, Senior",
            "conclusion": {
                "summary": "Ок", "recommendations": "Нет",
                "interview_topics": [], "values_assessment": "Соответствует"
            }
        }
    })

    async def async_generator(text):
        yield type("Event", (), {"content": type("Content", (), {"parts": [type("Part", (), {"text": text})]})})()

    mock_runner_instance = mocker.MagicMock()
    mock_runner_instance.run_async.side_effect = [
        async_generator(mock_agent_1_output),
        async_generator(mock_agent_2_output),
        async_generator(mock_agent_3_output),
    ]
    mocker.patch("backend.services.analysis_service.Runner", return_value=mock_runner_instance)

    mock_session_instance = mocker.MagicMock()
    mock_session_instance.create_session = mocker.AsyncMock()

    mocker.patch("backend.services.analysis_service.InMemorySessionService", return_value=mock_session_instance)

    mocker.patch.object(service, '_set_google_api_key')

    cv_file = io.BytesIO("Тестовое резюме".encode('utf-8'))

    result = await service.analyze_preparation(
        profile="Тестовый профиль",
        cv_file=cv_file,
        filename="cv.txt"
    )

    assert isinstance(result, PreparationAnalysis)
    assert result.report.first_name == "Иван"
    assert result.report.conclusion.summary == "Ок"
    assert mock_runner_instance.run_async.call_count == 3
    # Проверяем, что метод создания сессии был вызван
    mock_session_instance.create_session.assert_awaited_once()


def test_get_google_drive_file_id_success(service):
    """
    Тест: Успешное извлечение ID из ссылки Google Drive.
    """
    link = "https://drive.google.com/file/d/1a2b3c4d5e6f7g8h9i0j/view?usp=sharing"
    file_id = service._get_google_drive_file_id(link)
    assert file_id == "1a2b3c4d5e6f7g8h9i0j"


def test_get_google_drive_file_id_failure(service):
    """
    Тест: Некорректная ссылка на Google Drive.
    """
    link = "https://google.com"
    with pytest.raises(ValueError, match="Некорректная ссылка на Google Drive"):
        service._get_google_drive_file_id(link)

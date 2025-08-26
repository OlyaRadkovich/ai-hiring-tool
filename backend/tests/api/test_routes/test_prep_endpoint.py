import io


def test_analyze_preparation_success(client, mocker):
    """
    Тест: Успешный запрос с корректными данными.
    """
    mock_analyze_preparation = mocker.AsyncMock(return_value={
        "message": "Анализ успешно завершен",
        "report": {
            "first_name": "Тест", "last_name": "Тестов",
            "matching_table": [], "candidate_profile": "QA, Junior",
            "conclusion": {
                "summary": "Все отлично", "recommendations": "Нет",
                "interview_topics": [], "values_assessment": "Соответствует"
            }
        }
    })

    mocker.patch(
        "backend.services.analysis_service.AnalysisService.analyze_preparation",
        new=mock_analyze_preparation
    )

    cv_content = "Это тестовое CV в текстовом файле.".encode('utf-8')
    files = {'cv_file': ('test_cv.txt', io.BytesIO(cv_content), 'text/plain')}
    data = {'profile': 'Это тестовые требования к вакансии.'}

    response = client.post("/api/prep/", files=files, data=data)

    assert response.status_code == 200
    json_response = response.json()
    assert json_response["report"]["first_name"] == "Тест"


def test_analyze_preparation_invalid_file_type(client):
    """
    Тест: Загрузка файла с недопустимым расширением.
    """
    files = {'cv_file': ('test_cv.zip', io.BytesIO(b"zip content"), 'application/zip')}
    data = {'profile': 'Требования'}

    response = client.post("/api/prep/", files=files, data=data)

    assert response.status_code == 400
    assert "Недопустимый тип файла" in response.json()["detail"]


def test_analyze_preparation_service_internal_error(client, mocker):
    """
    Тест: Внутренняя ошибка в сервисе анализа.
    """
    mocker.patch(
        "backend.services.analysis_service.AnalysisService.analyze_preparation",
        side_effect=Exception("Что-то пошло не так в AI")
    )

    files = {'cv_file': ('test_cv.pdf', io.BytesIO(b"%PDF-"), 'application/pdf')}
    data = {'profile': 'Требования'}

    response = client.post("/api/prep/", files=files, data=data)

    assert response.status_code == 500
    assert "Произошла ошибка при анализе" in response.json()["detail"]

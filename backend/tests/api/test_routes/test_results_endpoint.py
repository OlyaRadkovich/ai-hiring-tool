import io


def test_analyze_results_success(client, mocker):
    """
    Тест: Успешный анализ результатов интервью.
    Проверяем, что эндпоинт возвращает статус 200 и корректные данные.
    """
    mock_analyze = mocker.AsyncMock(return_value={
        "message": "Анализ результатов успешно завершен",
        "transcription": "Полный текст интервью...",
        "scores": {"technical": 90, "communication": 85, "leadership": 70, "cultural": 95, "overall": 85},
        "strengths": ["Отличные технические навыки"],
        "concerns": ["Немного нервничал в начале"],
        "recommendation": "Нанимать",
        "reasoning": "Кандидат показал глубокие знания.",
        "topicsDiscussed": ["Python", "AsyncIO", "Базы данных"]
    })

    mocker.patch(
        "backend.services.analysis_service.AnalysisService.analyze_results",
        new=mock_analyze
    )

    files = {'matrix_file': ('matrix.csv', io.BytesIO(b"Kompetenciya,Ocenka\nPython,5"), 'text/csv')}
    data = {'video_link': 'https://drive.google.com/file/d/some_fake_id/view'}

    response = client.post("/api/results/", files=files, data=data)

    assert response.status_code == 200
    json_response = response.json()
    assert json_response["recommendation"] == "Нанимать"
    assert json_response["scores"]["technical"] == 90


def test_download_report_success(client, mocker):
    """
    Тест: Успешная загрузка отчета в формате DOCX.
    Проверяем статус 200 и правильность заголовков ответа.
    """
    docx_content = io.BytesIO(b"word file content placeholder")

    mocker.patch(
        "backend.services.analysis_service.AnalysisService.create_docx_report",
        return_value=docx_content
    )

    request_data = {
        "message": "Это тестовое сообщение для Pydantic",  # <-- ДОБАВЛЕНО
        "transcription": "текст",
        "scores": {"technical": 90, "communication": 85, "leadership": 70, "cultural": 95, "overall": 85},
        "strengths": [],
        "concerns": [],
        "recommendation": "Нанимать",
        "reasoning": "",
        "topicsDiscussed": []
    }

    response = client.post("/api/results/export", json=request_data)

    assert response.status_code == 200
    assert "application/vnd.openxmlformats-officedocument.wordprocessingml.document" in response.headers['content-type']
    assert response.content == docx_content.getvalue()


def test_analyze_results_service_error(client, mocker):
    """
    Тест: Внутренняя ошибка в сервисе при анализе результатов.
    Проверяем, что эндпоинт корректно возвращает 500.
    """
    mocker.patch(
        "backend.services.analysis_service.AnalysisService.analyze_results",
        side_effect=Exception("Ошибка при транскрипции")
    )

    files = {'matrix_file': ('matrix.csv', io.BytesIO(b"Kompetenciya,Ocenka"), 'text/csv')}
    data = {'video_link': 'https://drive.google.com/file/d/some_fake_id/view'}

    response = client.post("/api/results/", files=files, data=data)

    assert response.status_code == 500
    assert "Произошла внутренняя ошибка сервера" in response.json()["detail"]

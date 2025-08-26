import pytest
from fastapi import HTTPException
from unittest.mock import MagicMock
from backend.utils.validators import FileValidator


@pytest.fixture
def mock_upload_file():
    """
    Фикстура для создания мокового объекта UploadFile.
    Мы можем изменять его атрибуты в каждом тесте.
    """
    return MagicMock()


def test_validate_file_size_success(mock_upload_file):
    """
    Тест: Размер файла в пределах нормы.
    Ожидаем, что исключение НЕ будет вызвано.
    """
    mock_upload_file.size = 5 * 1024 * 1024  # 5MB
    try:
        FileValidator.validate_file_size(mock_upload_file)
    except HTTPException:
        pytest.fail("validate_file_size() вызвала HTTPException для файла корректного размера")


def test_validate_file_size_too_large(mock_upload_file):
    """
    Тест: Размер файла превышает лимит.
    Ожидаем HTTPException со статусом 413.
    """
    mock_upload_file.size = 15 * 1024 * 1024  # 15MB
    with pytest.raises(HTTPException) as excinfo:
        FileValidator.validate_file_size(mock_upload_file)
    assert excinfo.value.status_code == 413
    assert "File size exceeds" in excinfo.value.detail


def test_validate_cv_extension_success(mock_upload_file):
    """
    Тест: У CV файла корректное расширение (.pdf, .doc, .docx).
    Ожидаем, что исключение НЕ будет вызвано.
    """
    # Проверяем все разрешенные расширения
    for ext in ['.pdf', '.doc', '.docx']:
        mock_upload_file.filename = f"resume{ext}"
        try:
            FileValidator.validate_file_extension(mock_upload_file, 'cv')
        except HTTPException:
            pytest.fail(f"validate_file_extension() вызвала ошибку для разрешенного типа {ext}")


def test_validate_cv_extension_invalid(mock_upload_file):
    """
    Тест: У CV файла некорректное расширение (.txt).
    Ожидаем HTTPException со статусом 400.
    """
    mock_upload_file.filename = "resume.txt"
    with pytest.raises(HTTPException) as excinfo:
        FileValidator.validate_file_extension(mock_upload_file, 'cv')
    assert excinfo.value.status_code == 400
    assert "Invalid file type" in excinfo.value.detail


def test_validate_matrix_file_success(mock_upload_file):
    """
    Тест: Комплексная проверка файла матрицы (размер и расширение).
    Ожидаем, что исключение НЕ будет вызвано.
    """
    mock_upload_file.filename = "competency_matrix.xlsx"
    mock_upload_file.size = 2 * 1024 * 1024  # 2MB
    try:
        FileValidator.validate_matrix_file(mock_upload_file)
    except HTTPException:
        pytest.fail("validate_matrix_file() вызвала ошибку для корректного файла")


def test_validate_matrix_file_failure(mock_upload_file):
    """
    Тест: Комплексная проверка файла матрицы (неверное расширение).
    Ожидаем HTTPException от проверки расширения.
    """
    mock_upload_file.filename = "matrix.zip"
    mock_upload_file.size = 2 * 1024 * 1024
    with pytest.raises(HTTPException) as excinfo:
        FileValidator.validate_matrix_file(mock_upload_file)
    assert excinfo.value.status_code == 400

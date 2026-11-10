"""CLI-приложение для настройки параметров визуализатора графа."""
import csv
import sys
from pathlib import Path
from urllib.parse import urlparse

# Константы (защита от магических чисел и строк)
VALID_MODES = {"remote", "local"}
VALID_EXTS = {".png", ".svg", ".pdf", ".jpg"}


class CLI:
    """Класс для загрузки и проверки конфигурации из CSV."""

    def __init__(self, config_path="src/csv_config.csv"):
        """Инициализация и загрузка параметров."""
        self.config_path = config_path
        self.params = {}
        self.params = self.load_csv()

    def load_csv(self):
        """Загружает параметры из CSV-файла."""
        params = {}
        try:
            with open(self.config_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                if not reader.fieldnames or "parameter" not in reader.fieldnames:
                    raise KeyError("В CSV нет колонки 'parameter'")
                
                for row in reader:
                    key = row['parameter'].strip()
                    val = row['value'].strip()
                    params[key] = val
                    
        except FileNotFoundError:
            print(f"[ОШИБКА] Файл не найден: {self.config_path}")
            sys.exit(1)
        except KeyError as err:
            print(f"[ОШИБКА] Неверный формат CSV: {err}")
            sys.exit(1)
        return params

    def print_params(self):
        """Выводит все параметры в формате ключ - значение."""
        print("Параметры конфигурации:")
        for key in sorted(self.params):
            print(f"  {key}: {self.params[key]}")

    def validate_params(self):
        """Проверяет корректность всех заданных параметров."""
        required = {"package_name", "repo", "repo_mode", 
                    "package_version", "output_image"}
        
        missing = required - self.params.keys()
        if missing:
            raise ValueError(f"Отсутствуют параметры: {', '.join(missing)}")

        self._validate_name()
        self._validate_version()
        self._validate_image()
        self._validate_repo()

    def _validate_name(self):
        """Проверяет имя пакета."""
        name = self.params.get("package_name", "")
        if not name:
            raise ValueError("Параметр 'package_name' не может быть пустым")

    def _validate_version(self):
        """Проверяет версию пакета."""
        version = self.params.get("package_version", "")
        if not version:
            raise ValueError("Параметр 'package_version' не может быть пустым")
        if not any(char.isdigit() for char in version):
            raise ValueError("Версия должна содержать хотя бы одну цифру")

    def _validate_image(self):
        """Проверяет расширение выходного файла."""
        image = self.params.get("output_image", "")
        if not image:
            raise ValueError("Параметр 'output_image' не может быть пустым")
        
        ext = Path(image).suffix.lower()
        if ext not in VALID_EXTS:
            raise ValueError(
                f"Недопустимый формат файла: {ext}. "
                f"Разрешены: {', '.join(VALID_EXTS)}"
            )

    def _validate_repo(self):
        """Проверяет репозиторий в зависимости от режима работы."""
        mode = self.params.get("repo_mode", "").lower()
        repo = self.params.get("repo", "")

        if not mode:
            raise ValueError("Параметр 'repo_mode' не может быть пустым")
        if mode not in VALID_MODES:
            raise ValueError(
                f"Режим '{mode}' не поддерживается. "
                f"Доступны: {', '.join(VALID_MODES)}"
            )

        if not repo:
            raise ValueError("Параметр 'repo' не может быть пустым")

        if mode == "local":
            if not Path(repo).exists():
                raise FileNotFoundError(f"Путь не существует: {repo}")
        
        if mode == "remote":
            parsed = urlparse(repo)
            if parsed.scheme not in ("http", "https") or not parsed.netloc:
                raise ValueError(f"Некорректный URL репозитория: {repo}")


if __name__ == "__main__":
    # Запуск Этапа 1: Чтение конфига и валидация
    cli = CLI(config_path="src/csv_config.csv")
    
    try:
        cli.validate_params()
    except Exception as err:
        # Перехватываем ошибки валидации и выходим с кодом 2
        print(f"\n[ОШИБКА КОНФИГА] {err}", file=sys.stderr)
        sys.exit(2)
        
    # Требование 3: Вывод параметров при запуске
    cli.print_params()
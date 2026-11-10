"""Модуль второго этапа: извлечение зависимостей из Alpine APKINDEX."""
import sys
import io
import tarfile
import urllib.request
from pathlib import Path
from st_1 import CLI

MIN_LINE_LEN = 3
KEY_IDX = 0
SEP_IDX = 1
VAL_IDX = 2
TAG_NAME = "P"
TAG_VER = "V"
TAG_DEPS = "D"


def download_index(repo_url: str):
    """Скачивает или загружает локальный APKINDEX.tar.gz."""
    if repo_url.startswith(("http://", "https://")):
        if not repo_url.endswith("APKINDEX.tar.gz"):
            repo_url = repo_url.rstrip("/") + "/APKINDEX.tar.gz"
        print(f"[ИНФО] Скачивание индекса: {repo_url}")
        
        try:
            with urllib.request.urlopen(repo_url) as response:
                return io.BytesIO(response.read())
        except Exception as error:
            raise RuntimeError(f"Ошибка скачивания: {error}")
    
    print(f"[ИНФО] Чтение локального файла: {repo_url}")
    tar_path = Path(repo_url)
    if not tar_path.exists():
        raise FileNotFoundError(f"Файл не найден: {repo_url}")
    return tar_path


def extract_apkindex(tar_bytes):
    """Извлекает текстовое содержимое файла APKINDEX из архива."""
    with tarfile.open(fileobj=tar_bytes, mode="r:gz") as tar:
        for member in tar.getmembers():
            if member.name.endswith("APKINDEX"):
                file_obj = tar.extractfile(member)
                if file_obj:
                    return file_obj.read().decode("utf-8")
    raise ValueError("В архиве не найден файл APKINDEX")


def parse_blocks(content: str):
    """Разбирает текст APKINDEX на список словарей (пакетов)."""
    packages = []
    current_pkg = {}
    
    for line in content.splitlines():
        line = line.strip()
        if not line:
            if current_pkg:
                packages.append(current_pkg)
                current_pkg = {}
            continue
        
        if len(line) >= MIN_LINE_LEN and line[SEP_IDX] == ":":
            key = line[KEY_IDX]
            value = line[VAL_IDX:].strip()
            current_pkg[key] = value
            
    if current_pkg:
        packages.append(current_pkg)
    return packages


def find_dependencies(packages: list, name: str, version: str):
    """Ищет пакет по имени и версии, возвращает его зависимости."""
    available_versions = []
    
    for pkg in packages:
        if pkg.get(TAG_NAME) == name:
            available_versions.append(pkg.get(TAG_VER))
            if pkg.get(TAG_VER) == version:
                deps_str = pkg.get(TAG_DEPS, "")
                return deps_str.split() if deps_str else []

    if not available_versions:
        raise ValueError(f"Пакет '{name}' не найден.")
    raise ValueError(
        f"Версия '{version}' не найдена. Доступны: "
        f"{', '.join(available_versions)}"
    )


def get_direct_dependencies(name: str, version: str, repo_url: str):
    """Получает список прямых зависимостей."""
    tar_bytes = download_index(repo_url)
    content = extract_apkindex(tar_bytes)
    packages = parse_blocks(content)
    return find_dependencies(packages, name, version)


def main():
    """Точка входа для второго этапа."""
    cli = CLI(config_path="src/csv_config.csv")
    
    try:
        cli.validate_params()
    except Exception as err:
        print(f"\n[ОШИБКА КОНФИГА] {err}", file=sys.stderr)
        sys.exit(2)
        
    print("--- Этап 2: Сбор данных ---")
    
    try:
        pkg_name = cli.params.get('package_name')
        pkg_ver = cli.params.get('package_version')
        repo = cli.params.get('repo')
        
        deps = get_direct_dependencies(pkg_name, pkg_ver, repo)
        
        print(f"\nПрямые зависимости пакета '{pkg_name}' ({pkg_ver}):")
        if not deps:
            print("  (нет зависимостей)")
        else:
            for dep in deps:
                print(f"  - {dep}")
                
    except Exception as err:
        print(f"\n[ОШИБКА ДАННЫХ] {err}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
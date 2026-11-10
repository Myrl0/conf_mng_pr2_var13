import urllib.request
import tarfile
import io
from pathlib import Path


def get_direct_dependencies(package_name: str, version: str, repo_url: str) -> list[str]:
    # 1. Загружаем данные (из сети или с диска)
    if repo_url.startswith(("http://", "https://")):
        if not repo_url.endswith("APKINDEX.tar.gz"):
            repo_url = repo_url.rstrip("/") + "/APKINDEX.tar.gz"
        
        print(f"[ИНФО] Скачивание индекса из: {repo_url} ...")
        try:
            with urllib.request.urlopen(repo_url) as response:
                tar_bytes = io.BytesIO(response.read())
        except Exception as e:
            raise RuntimeError(f"Не удалось скачать индекс: {e}")
    else:
        print(f"[ИНФО] Чтение локального индекса: {repo_url} ...")
        tar_bytes = Path(repo_url)
        if not tar_bytes.exists():
            raise FileNotFoundError(f"Локальный файл не найден: {repo_url}")

    # 2. Открываем архив и ищем файл APKINDEX
    with tarfile.open(fileobj=tar_bytes, mode="r:gz") as tar:
        apkindex_member = None
        for member in tar.getmembers():
            if member.name == "APKINDEX" or member.name.endswith("/APKINDEX"):
                apkindex_member = member
                break

        if not apkindex_member:
            raise ValueError("В архиве не найден файл APKINDEX")

        f = tar.extractfile(apkindex_member)
        if not f:
            raise ValueError("Не удалось извлечь APKINDEX")
        
        # Декодируем и разбиваем на строки (учитывая и \n, и \r\n)
        content = f.read().decode("utf-8")
        lines = content.splitlines()

    # 3. Парсим блоки построчно (самый надежный способ)
    packages = []
    current_pkg = {}
    
    for line in lines:
        line = line.strip()
        if not line:
            if current_pkg:
                packages.append(current_pkg)
                current_pkg = {}
            continue
        
        if len(line) >= 3 and line[1] == ":":
            key = line[0]
            value = line[2:].strip()
            current_pkg[key] = value
            
    if current_pkg:  # Добавляем последний пакет, если файл не кончается пустой строкой
        packages.append(current_pkg)

    print(f"[ИНФО] Всего пакетов в индексе: {len(packages)}")

    # 4. Ищем нужный пакет
    available_versions = []
    for pkg in packages:
        if pkg.get("P") == package_name:
            available_versions.append(pkg.get("V"))
            if pkg.get("V") == version:
                deps_str = pkg.get("D", "")
                if not deps_str:
                    return []
                return deps_str.split()

    # 5. Если пакет не найден или версия не совпала
    if not available_versions:
        raise ValueError(f"Пакет '{package_name}' вообще не найден в индексе.")
    else:
        raise ValueError(
            f"Пакет '{package_name}' найден, но версии '{version}' нет.\n"
            f"Доступные версии: {', '.join(available_versions)}"
        )
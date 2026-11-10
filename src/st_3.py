"""Модуль третьего этапа: DFS без рекурсии для графа зависимостей."""
import json
import sys
from pathlib import Path

from st_1 import CLI
from st_2 import download_index, extract_apkindex, parse_blocks


def load_test_graph(file_path: str) -> dict:
    """Загружает тестовый граф из JSON-файла."""
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Файл не найден: {file_path}")
    
    with open(path, 'r', encoding='utf-8') as file:
        return json.load(file)


def build_alpine_graph(repo_url: str) -> dict:
    """Строит полный словарь зависимостей из реального Alpine репозитория."""
    tar_bytes = download_index(repo_url)
    content = extract_apkindex(tar_bytes)
    packages = parse_blocks(content)
    
    graph = {}
    for pkg in packages:
        name = pkg.get("P")
        deps_str = pkg.get("D", "")
        if name:
            graph[name] = deps_str.split() if deps_str else []
    return graph


def build_transitive_graph(start_node: str, graph: dict) -> dict:
    """Строит граф зависимостей с помощью итеративного DFS (без рекурсии)."""
    if start_node not in graph:
        raise ValueError(f"Пакет '{start_node}' отсутствует в графе.")
    
    transitive_graph = {}
    visited = set()
    stack = [start_node]

    while stack:
        current = stack.pop()
        
        if current in visited:
            continue
        
        visited.add(current)
        
        deps = graph.get(current, [])
        transitive_graph[current] = deps

        for dep in deps:
            if dep not in visited:
                stack.append(dep)
                
    return transitive_graph


def print_graph(graph: dict):
    """Выводит граф в формате 'Узел -> [Зависимости]'."""
    print("\nГраф транзитивных зависимостей:")
    for node in sorted(graph.keys()):
        deps = graph[node]
        print(f"  {node} -> {deps}")


def main():
    """Точка входа для третьего этапа."""
    cli = CLI(config_path="src/csv_config.csv")
    
    try:
        cli.validate_params()
    except Exception as err:
        print(f"\n[ОШИБКА КОНФИГА] {err}", file=sys.stderr)
        sys.exit(2)

    pkg_name = cli.params.get('package_name')
    repo = cli.params.get('repo')
    mode = cli.params.get('repo_mode').lower()

    print("--- Этап 3: Построение графа (DFS) ---")
    
    try:
        # 1. Загружаем граф в зависимости от режима
        if mode == "local":
            print(f"[ИНФО] Режим тестирования. Файл: {repo}")
            graph = load_test_graph(repo)
        else:
            print(f"[ИНФО] Режим remote. Скачивание Alpine: {repo}")
            graph = build_alpine_graph(repo)

        # 2. Запускаем DFS
        print(f"[ИНФО] Запуск DFS для пакета: {pkg_name}")
        trans_graph = build_transitive_graph(pkg_name, graph)
        
        # 3. Выводим результат
        print_graph(trans_graph)
        
    except Exception as err:
        print(f"\n[ОШИБКА ДАННЫХ] {err}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
"""Модуль четвертого этапа: поиск обратных зависимостей."""
import sys
from st_1 import CLI
from st_3 import (
    load_test_graph, 
    build_alpine_graph, 
    build_transitive_graph,
    print_graph
)


def invert_graph(graph: dict) -> dict:
    """Инвертирует граф (A->B становится B->A) для поиска обратных связей."""
    inverted = {}
    for node, deps in graph.items():
        if node not in inverted:
            inverted[node] = []
            
        for dep in deps:
            if dep not in inverted:
                inverted[dep] = []
            inverted[dep].append(node)
            
    return inverted


def main():
    """Точка входа для четвертого этапа."""
    cli = CLI(config_path="tests/csv_config_test.csv")
    
    try:
        cli.validate_params()
    except Exception as err:
        print(f"\n[ОШИБКА КОНФИГА] {err}", file=sys.stderr)
        sys.exit(2)

    pkg_name = cli.params.get('package_name')
    repo = cli.params.get('repo')
    mode = cli.params.get('repo_mode').lower()

    print("--- Этап 4: Поиск обратных зависимостей ---")
    
    try:
        if mode == "local":
            print(f"[ИНФО] Режим тестирования. Файл: {repo}")
            graph = load_test_graph(repo)
        else:
            print(f"[ИНФО] Режим remote. Скачивание Alpine: {repo}")
            graph = build_alpine_graph(repo)

        print(f"[ИНФО] Инвертирование графа для поиска обратных зависимостей")
        inverted_graph = invert_graph(graph)
        
        if pkg_name not in inverted_graph:
            raise ValueError(f"Пакет '{pkg_name}' отсутствует в графе.")

        print(f"[ИНФО] Запуск DFS для пакета: {pkg_name}")
        reverse_deps = build_transitive_graph(pkg_name, inverted_graph)
        
        print_graph(reverse_deps)
        
    except Exception as err:
        print(f"\n[ОШИБКА ДАННЫХ] {err}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
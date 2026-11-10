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
        # Инициализируем пустой список для текущего узла
        if node not in inverted:
            inverted[node] = []
            
        # Меняем направление: если А зависит от Б, то Б зависит от А
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
        # 1. Загружаем исходный граф (как в 3-м этапе)
        if mode == "local":
            print(f"[ИНФО] Режим тестирования. Файл: {repo}")
            graph = load_test_graph(repo)
        else:
            print(f"[ИНФО] Режим remote. Скачивание Alpine: {repo}")
            graph = build_alpine_graph(repo)

        # 2. Инвертируем граф
        print(f"[ИНФО] Инвертирование графа для поиска обратных зависимостей...")
        inverted_graph = invert_graph(graph)
        
        # Проверка, есть ли вообще такой пакет в графе
        if pkg_name not in inverted_graph:
            raise ValueError(f"Пакет '{pkg_name}' отсутствует в графе.")

        # 3. Запускаем DFS из 3-го этапа, но уже на инвертированном графе
        print(f"[ИНФО] Запуск DFS для пакета: {pkg_name}")
        reverse_deps = build_transitive_graph(pkg_name, inverted_graph)
        
        # 4. Выводим результат
        print_graph(reverse_deps)
        
    except Exception as err:
        print(f"\n[ОШИБКА ДАННЫХ] {err}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
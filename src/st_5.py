"""Модуль пятого этапа: визуализация графа в PlantUML и SVG."""
import subprocess
import sys
from pathlib import Path

from st_1 import CLI
from st_3 import (
    load_test_graph,
    build_alpine_graph,
    build_transitive_graph,
)


def graph_to_plantuml(graph: dict) -> str:
    """Преобразует словарь графа в текст PlantUML."""
    lines = ["@startuml", "skinparam linetype ortho"]
    
    node_ids = {}
    counter = 0
    
    for node, deps in graph.items():
        if node not in node_ids:
            node_ids[node] = f"n{counter}"
            counter += 1
            lines.append(f'rectangle "{node}" as {node_ids[node]}')
            
        for dep in deps:
            if dep not in node_ids:
                node_ids[dep] = f"n{counter}"
                counter += 1
                lines.append(f'rectangle "{dep}" as {node_ids[dep]}')

    for node, deps in graph.items():
        for dep in deps:
            lines.append(f"{node_ids[node]} --> {node_ids[dep]}")
            
    lines.append("@enduml")
    return "\n".join(lines)


def generate_svg(puml_text: str, output_svg: Path):
    """Сохраняет .puml и вызывает plantuml для генерации SVG."""
    puml_file = output_svg.with_suffix(".puml")
    puml_file.write_text(puml_text, encoding="utf-8")
    
    try:
        subprocess.run(
            ["plantuml", "-tsvg", str(puml_file)],
            check=True,
            capture_output=True,
            text=True,
        )
    except FileNotFoundError:
        raise RuntimeError(
            "PlantUML не найден. Установите: brew install plantuml"
        )
    except subprocess.CalledProcessError as err:
        raise RuntimeError(f"Ошибка PlantUML: {err.stderr}")
        
    print(f"[ИНФО] SVG сохранён: {output_svg}")


def main():
    """Точка входа для пятого этапа."""
    cli = CLI(config_path="tests/csv_config_st5.csv")
    try:
        cli.validate_params()
    except Exception as err:
        print(f"\n[ОШИБКА КОНФИГА] {err}", file=sys.stderr)
        sys.exit(2)

    pkg_name = cli.params.get("package_name")
    repo = cli.params.get("repo")
    mode = cli.params.get("repo_mode").lower()
    out_image = Path(cli.params.get("output_image"))

    print("--- Этап 5: Визуализация графа ---")
    
    try:
        if mode == "local":
            graph = load_test_graph(repo)
        else:
            graph = build_alpine_graph(repo)

        trans_graph = build_transitive_graph(pkg_name, graph)
        
        puml_text = graph_to_plantuml(trans_graph)
        
        generate_svg(puml_text, out_image)
        
    except Exception as err:
        print(f"\n[ОШИБКА ДАННЫХ] {err}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
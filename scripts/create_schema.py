"""生成一个 Pydantic 模型，并写入包导入。公共 schema 在 server/schema，子图 schema 在 server/schema/<子图>。"""

from scaffold import (
    ask_name,
    ask_subgraph,
    create_module,
    kind_parent,
    load_template,
    pascal_case,
)


def main():
    """询问子图与模块名，生成禁止多余字段的 BaseModel。"""
    subgraph = ask_subgraph()
    module_name = ask_name("schema 模块名: ", "creative_requirement")
    class_name = pascal_case(module_name)
    content = (
        load_template("schema.py.tmpl")
        .replace("{{name}}", module_name)
        .replace("{{class_name}}", class_name)
    )
    create_module(kind_parent("schema", subgraph), module_name, content, class_name)


if __name__ == "__main__":
    main()

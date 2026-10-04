"""在 server/schema 下生成一个 Pydantic 模型，并写入包导入。"""

from scaffold import ROOT, ask_name, create_module, load_template, pascal_case


def main():
    """询问模块名，生成禁止多余字段的 BaseModel。"""
    module_name = ask_name("schema 模块名: ", "creative_requirement")
    class_name = pascal_case(module_name)
    content = (
        load_template("schema.py.tmpl")
        .replace("{{name}}", module_name)
        .replace("{{class_name}}", class_name)
    )
    create_module(ROOT / "server" / "schema", module_name, content, class_name)


if __name__ == "__main__":
    main()

"""在 server/model 下生成一个文本模型实现，并写入包导入。"""

from scaffold import ROOT, ask_name, create_module, load_template, pascal_case


def main():
    """询问模块名，生成带 analyze_requirement 的模型类。"""
    module_name = ask_name("模型模块名: ", "ark_text_model")
    class_name = pascal_case(module_name)
    content = load_template("model.py.tmpl").replace("{{class_name}}", class_name)
    create_module(ROOT / "server" / "model", module_name, content, class_name)
    print("如需按 TEXT_MODEL_PROVIDER 选用，请把它接到 server/model/build_text_model.py")


if __name__ == "__main__":
    main()

"""在指定目录下生成一个带默认模板的 Python 模块，并写入包导入。"""

from scaffold import ask_name, ask_parent, create_module, load_template


def main():
    """询问位置和名字，生成模块并更新所在包的导入。"""
    parent = ask_parent()
    module_name = ask_name()
    content = load_template("module.py.tmpl").replace("{{name}}", module_name)
    create_module(parent, module_name, content)


if __name__ == "__main__":
    main()

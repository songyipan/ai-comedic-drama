"""在 server/nodes 下生成一个工作流节点，并写入包导入。"""

from scaffold import ROOT, ask_name, create_module, load_template


def main():
    """询问节点名，生成接收状态并返回部分更新的函数。"""
    module_name = ask_name("节点名: ", "receive_idea")
    content = load_template("node.py.tmpl").replace("{{name}}", module_name)
    create_module(ROOT / "server" / "nodes", module_name, content)


if __name__ == "__main__":
    main()

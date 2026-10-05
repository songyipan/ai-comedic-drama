"""生成一个工作流节点，并写入包导入。公共节点在 server/nodes，子图节点在 server/nodes/<子图>。"""

from scaffold import ask_name, ask_subgraph, create_module, kind_parent, load_template


def main():
    """询问子图与节点名，生成接收状态并返回部分更新的函数。"""
    subgraph = ask_subgraph()
    module_name = ask_name("节点名: ", "receive_idea")
    content = load_template("node.py.tmpl").replace("{{name}}", module_name)
    create_module(kind_parent("nodes", subgraph), module_name, content)


if __name__ == "__main__":
    main()

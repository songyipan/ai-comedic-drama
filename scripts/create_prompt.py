"""生成一个提示词常量，并写入包导入。公共提示词在 server/prompts，子图提示词在 server/prompts/<子图>。"""

from scaffold import (
    ask_name,
    ask_subgraph,
    create_module,
    kind_parent,
    load_template,
    sanitize_text,
)


def main():
    """先询问子图与模块名，再询问提示词内容。"""
    subgraph = ask_subgraph()
    module_name = ask_name("提示词模块名: ", "sys_prompt").lower()
    constant_name = module_name.upper()
    literal = python_literal(ask_prompt_text())
    content = load_template("prompt.py.tmpl").replace("{{constant}}", constant_name)
    content = content.replace("{{literal}}", literal, 1)
    create_module(kind_parent("prompts", subgraph), module_name, content, constant_name)


def ask_prompt_text():
    """逐行读取提示词，遇到空行结束。"""
    print("提示词内容，空行结束:")
    lines = []
    while True:
        try:
            line = input()
        except EOFError as error:
            if lines:
                break
            raise SystemExit("\n已取消") from error
        if line == "":
            break
        lines.append(line)
    if not lines:
        raise SystemExit("已取消")
    return sanitize_text("\n".join(lines))


def python_literal(text):
    """把提示词写成 Python 字面量，保留换行和引号。"""
    escaped = text.replace("\\", "\\\\")
    if '"""' not in escaped and not escaped.endswith('"'):
        return f'"""{escaped}"""'
    if "'''" not in escaped and not escaped.endswith("'"):
        return f"'''{escaped}'''"
    return repr(text)


if __name__ == "__main__":
    main()

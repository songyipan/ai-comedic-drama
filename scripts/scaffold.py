"""生成模块并登记到所在包的 __init__.py。"""

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEMPLATES = Path(__file__).resolve().parent / "templates"
IDENTIFIER = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


def create_module(parent, module_name, content, export_name=None):
    """写入模块文件，并在包的 __init__.py 中导出指定名字。"""
    module_path = parent / f"{module_name}.py"
    if module_path.exists():
        raise SystemExit(f"已存在，未覆盖: {display_path(module_path)}")

    parent.mkdir(parents=True, exist_ok=True)
    module_path.write_text(content, encoding="utf-8")

    init_path = parent / "__init__.py"
    created_init = not init_path.exists()
    exported = export_name or module_name
    init_path.write_text(render_init(init_path, module_name, exported), encoding="utf-8")

    print(f"已创建 {display_path(module_path)}")
    action = "已创建" if created_init else "已更新"
    print(f"{action} {display_path(init_path)}")


def load_template(name):
    """读取 scripts/templates 下的模板。"""
    return (TEMPLATES / name).read_text(encoding="utf-8")


def ask_parent():
    """读取父目录。输入文件时，模块创建在该文件所在目录。"""
    while True:
        raw_value = prompt("在哪个目录或文件下创建模块（例如 server/schema）: ")
        if not raw_value:
            raise SystemExit("已取消")
        try:
            return resolve_parent(raw_value)
        except ValueError as error:
            print(error)


def ask_name(message="模块名: ", example="plan_outline"):
    """读取合法的模块名。"""
    while True:
        raw_value = prompt(message)
        if not raw_value:
            raise SystemExit("已取消")
        module_name = raw_value.removesuffix(".py").strip()
        if IDENTIFIER.fullmatch(module_name):
            return module_name
        print(f"模块名需要是合法的 Python 标识符，例如 {example}")


def pascal_case(module_name):
    """把 snake_case 模块名转成类名。"""
    return "".join(part.capitalize() for part in module_name.split("_") if part)


def resolve_parent(raw_value):
    """把用户输入解析成仓库内的目录。"""
    candidate = Path(raw_value).expanduser()
    if not candidate.is_absolute():
        candidate = ROOT / candidate
    candidate = candidate.resolve()

    try:
        candidate.relative_to(ROOT)
    except ValueError as error:
        raise ValueError("路径必须在项目目录内") from error

    if candidate == ROOT:
        raise ValueError("请指定项目里的子目录，例如 server/schema")

    if candidate.exists() and candidate.is_file():
        parent = candidate.parent
    elif candidate.suffix == ".py":
        parent = candidate.parent
    else:
        parent = candidate

    try:
        parent.relative_to(ROOT)
    except ValueError as error:
        raise ValueError("路径必须在项目目录内") from error

    if parent == ROOT:
        raise ValueError("请指定项目里的子目录，例如 server/schema")
    if parent.exists() and not parent.is_dir():
        raise ValueError(f"不是目录: {display_path(parent)}")
    return parent


def render_init(init_path, module_name, export_name):
    """生成或更新包的 __init__.py。"""
    import_line = f"from .{module_name} import {export_name}"
    if not init_path.exists():
        directory_name = init_path.parent.name
        return (
            f'"""{directory_name}。"""\n\n'
            f"{import_line}\n\n"
            f'__all__ = ["{export_name}"]\n'
        )

    text = insert_import(init_path.read_text(encoding="utf-8"), import_line)
    return upsert_all(text, export_name)


def insert_import(text, import_line):
    """把相对导入插到现有导入块末尾。"""
    if import_line in text:
        return text

    lines = text.splitlines()
    last_import = None
    for index, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith("from .") or stripped.startswith("import "):
            last_import = index

    if last_import is None:
        insert_at = docstring_end(lines)
        addition = [import_line]
        if insert_at > 0 and lines[insert_at - 1] != "":
            addition.insert(0, "")
        lines[insert_at:insert_at] = addition
    else:
        lines.insert(last_import + 1, import_line)

    return "\n".join(lines) + "\n"


def docstring_end(lines):
    """返回模块文档字符串之后的行号。没有文档字符串时返回 0。"""
    if not lines:
        return 0

    stripped = lines[0].lstrip()
    if stripped.startswith('"""'):
        quote = '"""'
    elif stripped.startswith("'''"):
        quote = "'''"
    else:
        return 0

    if stripped.count(quote) >= 2 and len(stripped) > 3:
        return 1

    for index in range(1, len(lines)):
        if quote in lines[index]:
            return index + 1
    return 0


def upsert_all(text, export_name):
    """把导出名字加入 __all__。没有 __all__ 时补上一行。"""
    match = re.search(r"^__all__\s*=\s*\[([^\]]*)\]", text, re.M)
    if match is None:
        suffix = "" if text.endswith("\n") else "\n"
        separator = "\n" if text.endswith("\n\n") else "\n"
        return f'{text}{suffix}{separator}__all__ = ["{export_name}"]\n'

    existing = re.findall(r"""['"]([^'"]+)['"]""", match.group(1))
    if export_name in existing:
        return text

    existing.append(export_name)
    rendered = ", ".join(f'"{name}"' for name in existing)
    return f"{text[:match.start()]}__all__ = [{rendered}]{text[match.end():]}"


def prompt(message):
    """读取一行输入。遇到文件结束时取消。"""
    try:
        return sanitize_text(input(message).strip())
    except EOFError as error:
        raise SystemExit("\n已取消") from error


def sanitize_text(text):
    """还原输入里的孤立代理字符，避免写文件时报 surrogates not allowed。

    终端送来的非法 UTF-8 字节会被 stdin 按 surrogateescape 记成代理字符。这里先
    还原出原始字节，再按常见损坏来源尝试恢复：被拆成 CESU-8 的增补平面字符（通常
    是 emoji），以及 GBK 编码的中文；都失败时用替换符号占位并提示。
    """
    if not any("\ud800" <= char <= "\udfff" for char in text):
        return text
    raw = text.encode("utf-8", "surrogateescape")
    attempts = (
        ("CESU-8", decode_cesu8),
        ("GBK", lambda data: data.decode("gbk")),
    )
    for label, decode in attempts:
        try:
            recovered = decode(raw)
        except UnicodeDecodeError:
            continue
        print(f"输入里有编码损坏的字符，已按 {label} 恢复")
        return recovered
    print("输入里有无法恢复的字符，已用替换符号代替，请检查生成的内容")
    return raw.decode("utf-8", "replace")


def decode_cesu8(data):
    """把 CESU-8 字节里被拆开的代理对拼回单个字符。"""
    return (
        data.decode("utf-8", "surrogatepass")
        .encode("utf-16-le", "surrogatepass")
        .decode("utf-16-le")
    )


def display_path(path):
    """用相对项目根目录的路径显示文件。"""
    return path.resolve().relative_to(ROOT).as_posix()

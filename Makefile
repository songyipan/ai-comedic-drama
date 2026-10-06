.PHONY: dev debug client package node model schema prompt

# 启动 LangGraph 开发服务，默认 http://127.0.0.1:2024
dev:
	uv run langgraph dev

# 断点调试服务：先 make debug，再到 VS Code F5 附加（LangGraph: 附加调试），断点才会放行
debug:
	uv run langgraph dev --debug-port 5678 --wait-for-client --no-reload --no-browser

# 连接本地服务，跑一次漫画剧图
client:
	uv run python /Users/xiaosong/code/ai-comedic-drama/client/server_client.py

# 按提示在指定目录下生成一个模块，并写入包导入
package:
	uv run python scripts/create_package.py

# 按提示生成一个节点并写入包导入，指定子图或留空为公共节点
node:
	uv run python scripts/create_node.py

# 按提示在 server/model 下生成一个文本模型，并写入包导入
model:
	uv run python scripts/create_model.py

# 按提示生成一个数据模型并写入包导入，指定子图或留空为公共
schema:
	uv run python scripts/create_schema.py

# 按提示生成一个提示词并写入包导入，指定子图或留空为公共
prompt:
	uv run python scripts/create_prompt.py

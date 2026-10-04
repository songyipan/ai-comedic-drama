.PHONY: server client package node model schema prompt

# 启动 LangGraph 开发服务，默认 http://127.0.0.1:2024
server:
	uv run langgraph dev

# 连接本地服务，跑一次漫画剧图
client:
	uv run python /Users/xiaosong/code/ai-comedic-drama/client/server_client.py

# 按提示在指定目录下生成一个模块，并写入包导入
package:
	uv run python scripts/create_package.py

# 按提示在 server/nodes 下生成一个节点，并写入包导入
node:
	uv run python scripts/create_node.py

# 按提示在 server/model 下生成一个文本模型，并写入包导入
model:
	uv run python scripts/create_model.py

# 按提示在 server/schema 下生成一个数据模型，并写入包导入
schema:
	uv run python scripts/create_schema.py

# 按提示在 server/prompts 下生成一个提示词，并写入包导入
prompt:
	uv run python scripts/create_prompt.py

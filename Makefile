.PHONY: server client

# 启动 LangGraph 开发服务，默认 http://127.0.0.1:2024
server:
	uv run langgraph dev

# 连接本地服务，跑一次漫画剧图
client:
	uv run python /Users/xiaosong/code/ai-comedic-drama/client/server_client.py

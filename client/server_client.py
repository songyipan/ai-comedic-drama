"""连接本地 LangGraph 服务，跑一次漫画剧图。"""

from langgraph_sdk import get_sync_client

SERVER_URL = "http://127.0.0.1:2024"
GRAPH_ID = "comic_drama"
SAMPLE_IDEA = (
    "深夜的办公室里，程序员小林正在修改一款漫画应用。"
    "零点到来时，他设计的漫画角色阿沐突然从屏幕中走了出来。"
)


def main():
    """创建线程并等待 comic_drama 跑完，返回最终状态。"""
    client = get_sync_client(url=SERVER_URL, api_key=None)
    try:
        thread = client.threads.create()
        return client.runs.wait(
            thread["thread_id"],
            GRAPH_ID,
            input={"raw_requirement": SAMPLE_IDEA},
        )
    finally:
        client.close()


if __name__ == "__main__":
    print(main())

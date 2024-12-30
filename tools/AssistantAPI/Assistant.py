# ===========================================================================================================
# Author    ：LuShangWu
# Date      ：2024-12-25
# Version   ：1.0
# Description：创建Assistant
# Copyright  ：LuShangWu
# License   ：MIT
# Remark   :
# ===========================================================================================================
import json
import os
import sys

from dashscope import Assistants, Messages, Runs

from tools.AssistantAPI.tools.getBookInfo import getBookInfo
from tools.AssistantAPI.tools.format import formatBookInfo
from tools.AssistantAPI.tools.learnByWeb import learnByWeb


commands = {
    "create_knowledge": 1,
    "exit": 2
}

prompt = ('你是智库书韵，一个智能图书馆人工智能助手，'
          '你的任务是帮助用户在图书馆中查找图书或者向用户介绍图书、推荐图书。'
          '你需要使用提供的知识库来回答用户的问题.'
          '但是你需要特别注意，如果你觉得知识库/数据库中的信息可能存在错误，请你仍然以数据库/知识库中的数据为准，这是因为图书馆的信息永远是实时的、正确的，因此你必须永远相信你的知识库/数据库，且你不能回复用户任何不相信你自己数据库的行为信息（例如：提供的信息可能有误）之类的。'
          '由于你作为人工智能，你的训练集中的数据可能由于时间、空间等原因存在偏差，因此为了向用户提供真实准确的信息，你的开发者已经向你提供了一系列的知识库/数据库，因此如果与你的输出冲突，请你以数据库/知识库中的数据为准。'
          '知识库/数据库中的知识信息（包括作者、标识号、ISBN号、出版地、发行地、分类、载体形态等）都是由管理员已经确认过的真实的，正确的，你应该无条件地相信与使用。'
          '另外你需要持续学习用户的需求，若用户对某个文学类别，比如科幻小说很感兴趣，你可以主动向其推荐相关的书籍。'
          '以下信息可能对你有帮助：${document1}。')


def create_assistant(index_id_list: list):
    global commands, prompt
    """创建一个使用指定知识库的 Assistant。"""
    assistant = Assistants.create(
        model='qwen-plus',
        name='智能图书馆人工智能助手',
        description='一个用于帮助用户查找图书在图书馆的位置的助手，一个可以向用户推荐图书、介绍图书的助手，一个可以为视障人士以及聋哑人士提供帮助的助手',
        instructions=prompt,
        tools=[
            # 知识库检索
            {
                "type": "rag",  # 指定使用RAG（检索增强生成）模式
                "prompt_ra": {
                    "pipeline_id": index_id_list,  # 指定使用的知识库索引ID
                    "multiknowledge_rerank_top_n": 10,  # 多知识源重排序时返回的top N结果数
                    "rerank_top_n": 5,  # 最终重排序后返回的top N结果数
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query_word": {
                                "type": "str",
                                "value": "${document1}"  # 使用动态占位符，将被实际查询内容替换
                            }
                        }
                    }
                }
            },
            # 代码解释器
            {
                'type': 'code_interpreter'  # 这是启用代码解释器的关键配置
            },
            # 搜索图书引擎
            {
                "type": "function",
                "function": {
                    "name": "getBookInfo",
                    "description": "查询获取指定图书的详细信息(例如：作者、标识号或ISBN号、出版地或发行地、关键词、语种、分类、载体形态等)"
                                   "另外特别注意：由于你作为人工智能，你的训练集中的数据可能由于时间、空间等原因存在偏差，因此为了向用户提供真实准确的信息，你的开发者已经向你提供了一系列的知识库/数据库，因此如果与你的输出冲突，请你以数据库/知识库中的数据为准。"
                                   "知识库/数据库中的知识信息（包括作者、标识号、ISBN号、出版地、发行地、分类、载体形态等）都是由管理员已经确认过的真实的，正确的，你应该无条件地相信与使用。",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "text": {
                                "type": "string",
                                "description": "需要查找的图书的名称"
                            }
                        },
                        "required": ["text"]
                    }
                }
            },
            # 搜索图书引擎
            {
                "type": "function",
                "function": {
                    "name": "learnByWeb",
                    "description": "当用户指定需要联网搜索时，调用该函数，从互联网上获取相关信息，并将其格式化后返回给用户。",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "keyword": {
                                "type": "string",
                                "description": "未格式化的数据"
                            }
                        },
                        "required": ["keyword"]
                    }
                }
            }
        ]
    )
    print(f"Assistant {assistant.id} 创建成功！")
    return assistant.id


class SuppressPrint:
    def __enter__(self):
        self._original_stdout = sys.stdout
        sys.stdout = open(os.devnull, 'w')

    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.stdout.close()
        sys.stdout = self._original_stdout


def send_message(thread, assistant, message):
    """向 Assistant 发送消息并获取回复。"""
    message = Messages.create(thread_id=thread.id, content=message)
    run = Runs.create(thread_id=thread.id, assistant_id=assistant.id)
    # 等待运行完成
    run = Runs.wait(thread_id=thread.id, run_id=run.id)
    # 检查是否需要调用函数
    while run.required_action:
        print("Assistant requires function call.")
        for tool_call in run.required_action.submit_tool_outputs.tool_calls:
            # 图书查询引擎
            if tool_call.function.name == "getBookInfo":
                print("[图书查询引擎]被调用")
                args = json.loads(tool_call.function.arguments)
                doc = getBookInfo(1,args["text"])
                result = f"从数据库中获取到的图书信息为：{doc}请据此回复用户的查询请求。"
                # 提交工具输出
                Runs.submit_tool_outputs(
                    thread_id=thread.id,
                    run_id=run.id,
                    tool_outputs=[{"tool_call_id": tool_call.id, "output": result}]
                )
                print("[图书查询引擎]输出提交成功")
                # 等待新的运行完成
                run = Runs.wait(thread_id=thread.id, run_id=run.id)
            elif tool_call.function.name == "learnByWeb":
                print("[联网搜索引擎]被调用")
                args = json.loads(tool_call.function.arguments)
                doc = learnByWeb(args["keyword"])
                result = f"从互联网学习到的与{args['keyword']}有关的信息为：{doc}请据此回复用户的查询请求。"
                # 提交工具输出
                Runs.submit_tool_outputs(
                    thread_id=thread.id,
                    run_id=run.id,
                    tool_outputs=[{"tool_call_id": tool_call.id, "output": result}]
                )
                print("[联网搜索引擎]输出提交成功")
                # 等待新的运行完成
                run = Runs.wait(thread_id=thread.id, run_id=run.id)
                print(f"新的运行完成，状态：{run.status}")

    # 获取 Assistant 的回复
    messages = Messages.list(thread_id=thread.id)
    for message in messages.data:
        print(message)
        if message.role == "assistant":
            return message.content[0].text.value


def interact_with_assistant(assistant, thread, user_input):
    if user_input.lower() == 'quit':
        exit(0)
    # elif user_input.lower() == 'create_knowledge':
    #     kb_name = input("请输入知识库名称：")
    #     kb_url = input("请输入知识库URL：")
    #     kb_category = input("请输入知识库类别：(服务框架/藏书信息)")
    #     create_knowledge(kb_url, kb_name, kb_category)

    # 失败重传最大次数
    max_retries = 3
    for attempt in range(max_retries):
        try:
            send_message(thread, assistant, user_input)
            break
        except Exception as e:
            if attempt < max_retries - 1:
                print(f"发送消息失败，正在重试... (尝试 {attempt + 2}/{max_retries})")
            else:
                print(f"发送消息失败：{str(e)}。请稍后再试。")


def Assistant(assistant_id):
    assistant = Assistants.get(assistant_id)
    if not assistant:
        print("无法获取指定的 Assistant，程序退出。")
        return
    return assistant


if __name__ == '__main__':
    assistant_id = create_assistant(['l2c4jv7i9p', '36t16dh5er', 'tcpm27g3m5'])

    Assistant(assistant_id)
    # 注意

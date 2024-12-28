# ===========================================================================================================
# Author    ：LuShangWu
# Date      ：2024-12-25
# Version   ：1.0
# Description：用于上传本地文件到知识库
# Copyright  ：LuShangWu
# License   ：MIT
# Remark   :
# 仅支持非结构化文件(如doc、docx、ppt、pptx、pdf、txt等)上传到知识库
# 注意上传文件时需要携带其文件后缀(.doc)
# 【当前非流式回复】
# ===========================================================================================================
import os
from dashscope import Assistants, Messages, Runs, Threads
import sys

commands ={
    "create_knowledge":1,
    "exit":2
}

prompt = ('你是智库书韵，一个智能图书馆人工智能助手，'
          '你的任务是帮助用户在图书馆中查找图书或者向用户介绍图书、推荐图书。'
          '你需要使用提供的知识库来回答用户的问题.'
          '另外你需要持续学习用户的需求，若用户对某个文学类别，比如科幻小说很感兴趣，你可以主动向其推荐相关的书籍。'
          '以下信息可能对你有帮助：${document1}。')

def create_assistant(index_id_list:list):
    global commands, prompt
    """创建一个使用指定知识库的 Assistant。"""
    assistant = Assistants.create(
        model='qwen-plus',
        name='智能图书馆人工智能助手',
        description='一个用于帮助用户查找图书在图书馆的位置的助手，一个可以向用户推荐图书、介绍图书的助手，一个可以为视障人士以及聋哑人士提供帮助的助手',
        instructions= prompt,
        tools=[
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
            # {
            #     "type": "function",
            #     "function":{
            #         "name":'',
            #         'description':'',
            #         'parameters':{
            #     }
            # }
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
    responses = Runs.create(thread_id=thread.id, assistant_id=assistant.id,stream =True)
    returnValue =''
    for event, message_run in responses:
        try:
            print(message_run['delta']['content']['text']['value'],end='')
            returnValue += message_run['delta']['content']['text']['value']
        except:
            pass
    return returnValue

def interact_with_assistant(assistant,thread,user_input):
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
   assistant_id = create_assistant(['l2c4jv7i9p','36t16dh5er','tcpm27g3m5'])

   Assistant(assistant_id)
   # 注意
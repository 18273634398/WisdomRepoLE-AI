import json
import sys
from http import HTTPStatus

from dashscope import Assistants, Messages, Runs, Threads
prompt ='你是一个智能图书管的人工助手，需要帮助用户在图书馆查找图书所在的位置以及为他们介绍相关的图书。'

def create_assistant():
    global prompt
    # 创建助手
    assistant = Assistants.create(
        model='qwen-max',
        name='Library Assistant',
        description='A tool helper.',
        instructions=prompt,
    )

    return assistant  # 返回创建的助手

def verify_status_code(res):
    # 验证返回的状态码是否为200
    if res.status_code != HTTPStatus.OK:
        print('Failed: ')
        print(res)
        sys.exit(res.status_code)

def create_and_run_assistant():
    # 创建并运行助手
    assistant = create_assistant()
    print(assistant)
    verify_status_code(assistant)

    # 创建线程
    thread = Threads.create(
        messages=[{
            'role': 'user',
            'content': '刘慈欣的三体怎么样？'
        }])
    print(thread)
    verify_status_code(thread)

    # 创建运行任务
    run = Runs.create(thread.id, assistant_id=assistant.id)
    print(run)
    verify_status_code(run)
    # 等待运行完成或需要进一步操作
    run_status = Runs.wait(run.id, thread_id=thread.id)
    print(run_status)

    # 获取线程消息
    msgs = Messages.list(thread.id)
    print(msgs)
    print(json.dumps(msgs, ensure_ascii=False, default=lambda o: o.__dict__, sort_keys=True, indent=4))

if __name__ == '__main__':
    create_and_run_assistant()  # 运行助手创建及执行流程

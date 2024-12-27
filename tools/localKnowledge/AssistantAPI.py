import sys
from dashscope import Assistants, Messages, Runs, Threads
from llama_index.indices.managed.dashscope import DashScopeCloudIndex, DashScopeCloudRetriever
from typing import cast
import json
from http import HTTPStatus

def retrieve_nodes(rag_query: str):
    """
    环境变量 INDEX_NAME为管控台知识库索引名称。
    :param rag_query: 知识库查询
    :return:
    """
    index = DashScopeCloudIndex("上海AI峰会-百炼文档助手")
    retriever = index.as_retriever()
    retriever = cast(DashScopeCloudRetriever, retriever)
    print(f"Pipeline id {retriever.pipeline_id}", flush=True)
    nodes = retriever.retrieve(rag_query)
    return "\n\n".join([node.get_content() for node in nodes])


def get_train_info(user_id):
    """
    MOCK接口，进行代码测试；
    :param user_id: 用户ID信息
    :return:
    """
    answer = f"{user_id}"
    model_list = ['qwen-max-sft-v1']
    for model in model_list:
        answer += '\nmodel_name: ' + model + '\ntrain_acc ' + str(86.44) + ' \n training time' + '21 hours 40 mintues'

    return str(answer)


function_mapper = {
    "retrieve_nodes": retrieve_nodes,
    "get_train_info": get_train_info
}


def create_assistant():
    # create assistant with information
    assistant = Assistants.create(
        model="qwen-max",
        name='smart helper',
        description='A tool helper.',
        instructions='You are a helpful assistant. When asked a question, use tools wherever possible.',
        tools=[
            {
                'type': 'quark_search'
            },
            {
                'type': 'function',
                'function': {
                    'name': 'retrieve_nodes',
                    'description': '用于获取与百炼平台相关的信息，包括模型训练、部署，应用搭建、API-KEY等',
                    'parameters': {
                        'type': 'object',
                        'properties': {
                            'rag_query': {
                                'type': 'str',
                                'description': '百炼相关问题'
                            },
                        },
                        'required': ['rag_query']
                    }
                }
            },
            {
                'type': 'function',
                'function': {
                    'name': 'get_train_info',
                    'description': '用于获取用户部署在百炼平台上用数据额外训练的模型情况。包含SFT模型的具体情况',
                    'parameters': {
                        'type': 'object',
                        'properties': {
                            'user_id': {
                                'type': 'str',
                                'description': '用户id'
                            },
                        },
                        'required': ['user_id']
                    }
                }
            }
        ],
    )

    if assistant.status_code != HTTPStatus.OK:
        print('Create Assistant failed, status code: %s, code: %s, message: %s' % (
            assistant.status_code, assistant.code, assistant.message))
        sys.exit()
    else:
        print('Create Assistant success, id: %s' % assistant.id)

    return assistant


def create_message(thread_id, content):
    message = Messages.create(thread_id, content=content)
    if message.status_code != HTTPStatus.OK:
        print('Create Message failed, status code: %s, code: %s, message: %s' % (
            message.status_code, message.code, message.message))
        sys.exit()
    else:
        print('Create Message success, id: %s' % message.id)
    return message


def create_thread():
    thread = Threads.create()
    # check result is success.
    if thread.status_code != HTTPStatus.OK:
        print('Create Thread failed, status code: %s, code: %s, message: %s' % (
            thread.status_code, thread.code, thread.message))
        sys.exit()
    else:
        print('Create Thread success, id: %s' % thread.id)
    return thread


def create_run(thread_id, assistant_id):
    run = Runs.create(thread_id, assistant_id=assistant_id)
    if run.status_code != HTTPStatus.OK:
        print('Create Assistant failed, status code: %s, code: %s, message: %s' % (
            run.status_code, run.code, run.message))
    else:
        print('Create Assistant success, id: %s' % run.id)
    return run

def send_message(assistant, message=''):
    # create a thread.
    thread = create_thread()

    # create a message.
    create_message(thread_id=thread.id, content=message)

    # create run
    response = Runs.create(thread.id, assistant_id=assistant.id, stream=True)
    content_str = ""
    for event, run in response:
        if event == "thread.message.delta":
            content_str += run.delta.content.text.value
            print(content_str, flush=True)
    print(run)

    # wait for run completed or requires_action
    run_status = Runs.wait(run.id, thread_id=thread.id)
    print('插件调用前：')

    if run_status.status == 'failed':
        print('run failed:')
        print(run_status.last_error)

    # if prompt input tool result, submit tool result.
    if run_status.required_action:
        f = run_status.required_action.submit_tool_outputs.tool_calls[0].function
        func_name = f['name']
        param = json.loads(f['arguments'])
        print(f"Function name {func_name}, parameters {param}")
        if func_name in function_mapper:
            output = function_mapper[func_name](**param)
        else:
            output = ""

        tool_outputs = [{
            'tool_call_id': run_status.required_action.submit_tool_outputs.tool_calls[0].id,
            'output': output
        }]

        responses = Runs.submit_tool_outputs(run.id,
                                             thread_id=thread.id,
                                             tool_outputs=tool_outputs,
                                             stream=True)
        content_str = ""
        for event, run in responses:
            if event == "thread.message.delta":
                content_str += run.delta.content.text.value
                print(content_str, flush=True)

        # should wait for run completed
        run_status = Runs.wait(run.id, thread_id=thread.id)

    run_status = Runs.get(run.id, thread_id=thread.id)
    # print(run_status)
    # verify_status_code(run_status)

    # get the thread messages.
    msgs = Messages.list(thread.id)
    # print(msgs)
    # print(json.dumps(msgs, default=lambda o: o.__dict__, sort_keys=True, indent=4))

    print("运行结果:")
    for message in msgs['data'][::-1]:
        print("content: ", message['content'][0]['text']['value'])
    print("\n")

demo_assistant = create_assistant()
send_message(assistant=demo_assistant, message="请一句话概括爱因斯坦的成就？")
send_message(assistant=demo_assistant, message="请问如何获取API KEY？")
send_message(assistant=demo_assistant, message="请问用户ID 114578的用户，模型训练结果如何？")

import json
import sys
from http import HTTPStatus

import dashscope
from dashscope import Assistants, Messages, Runs, Steps, Threads


def create_assistant_call_function():
    # create assistant with information
    assistant = Assistants.create(
        model='qwen-max',
        name='smart helper',
        description='A tool helper.',
        instructions='You are a helpful assistant. When asked a question, use tools wherever possible.',  # noqa E501
        tools=[{
            'type': 'function',
            'function': {
                'name': 'big_add',
                'description': 'Add to number',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'left': {
                            'type': 'integer',
                            'description': 'The left operator'
                        },
                        'right': {
                            'type': 'integer',
                            'description': 'The right operator.'
                        }
                    },
                    'required': ['left', 'right']
                }
            }
        }],
    )

    return assistant



def verify_status_code(res):
    if res.status_code != HTTPStatus.OK:
        print('Failed: ')
        print(res)
        sys.exit(res.status_code)

def create_and_run_assistant_call_function():
    # create assistant
    assistant = create_assistant_call_function()
    print(assistant)
    verify_status_code(assistant)

    # create run
    run_iterator = Runs.create_thread_and_run(thread={'messages': [{
        'role': 'user',
        'content': 'What is transformer? Explain it in simple terms.'
    }]}, assistant_id=assistant.id, stream=True)
    thread = None
    for event, run in run_iterator:
        print(event)
        print(run)
        if event == 'thread.created':
            thread = run
    verify_status_code(run)

    run_status = Runs.get(run.id, thread_id=thread.id)
    print(run_status)
    verify_status_code(run_status)

    # list run steps
    run_steps = Steps.list(run.id, thread_id=thread.id)
    print(run_steps)
    verify_status_code(run_steps)

    # create a message.
    message = Messages.create(thread.id, content='Add 87787 to 788988737.')
    print(message)
    verify_status_code(message)

    # create a new run to run message
    responses = Runs.create(thread.id, assistant_id=assistant.id, stream=True)
    for event, message_run in responses:
        print(event)
        print(message_run)
    verify_status_code(message_run)

    # get run statue
    run_status = Runs.get(message_run.id, thread_id=thread.id)
    print(run_status)
    verify_status_code(run_status)

    # if prompt input tool result, submit tool result.
    # should call big_add
    if run_status.required_action:
        tool_outputs = [{
            'output':
                '789076524'
        }]
        # submit output with stream.
        responses = Runs.submit_tool_outputs(message_run.id,
                                             thread_id=thread.id,
                                             tool_outputs=tool_outputs,
                                             stream=True)
        for event, run in responses:
            print(event)
            print(run)
        verify_status_code(run)

    run_status = Runs.get(run.id, thread_id=thread.id)
    print(run_status)
    verify_status_code(run_status)

    run_steps = Steps.list(run.id,  thread_id=thread.id)

    print(run_steps)
    verify_status_code(run_steps)

    # get the thread messages.
    msgs = Messages.list(thread.id)
    print(msgs)
    print(json.dumps(msgs, ensure_ascii=False, default=lambda o: o.__dict__, sort_keys=True, indent=4))

if __name__ == '__main__':
    create_and_run_assistant_call_function()
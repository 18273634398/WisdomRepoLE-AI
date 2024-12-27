# ===========================================================================================================
# Author    ：LuShangWu
# Date      ：2024-12-25
# Version   ：1.0
# Description：使用应用ID进行流式多轮对话
# Copyright  ：LuShangWu
# License   ：MIT
# Remark   :注意使用session_id标记多轮对话，其保存在云端仅1小时，且最长对话轮次为50次。
# Support: :https://bailian.console.aliyun.com/?bestPractices=1#/best-practices/call_model
# ===========================================================================================================
from System import settings
from http import HTTPStatus
from dashscope import Application

# 流式多轮对话
def call(text,session_id=None):
    if session_id:
        responses = Application.call(app_id=settings.appID,
                                    prompt=text,
                                    session_id=session_id,
                                    stream=True,
                                    incremental_output=True
                                    )
        for response in responses:
            if response.status_code != HTTPStatus.OK:
                print('Error:%s\n' % (response.message))
            else:
                print(response.output.text, end='')
    else:
        responses = Application.call(app_id=settings.appID,
                                    prompt=text,
                                    stream=True,
                                    incremental_output=True
                                    )
        for response in responses:
            if response.status_code != HTTPStatus.OK:
                print('Error:%s\n' % (response.message))
            else:
                print(response.output.text, end='')
                session_id = response.output.session_id
    return session_id



if __name__ == '__main__':
    session_id = None
    while True:
        text = input('\n请输入：')
        if text == 'exit':
            break
        session_id = call(text,session_id)
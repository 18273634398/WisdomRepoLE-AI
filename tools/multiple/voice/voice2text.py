# ===========================================================================================================
# Author    ：LuShangWu
# Date      ：2024-12-25
# Version   ：1.0
# Description：用于语音转文本
# Copyright  ：LuShangWu
# License   ：MIT
# Remark   :
# Support   ：https://bailian.console.aliyun.com/#/model-market/detail/paraformer-mtl-v1?tabKey=sdk
# ===========================================================================================================


from http import HTTPStatus
import dashscope
import json
from System import settings


def voice2text(file_urls):
    task_response = dashscope.audio.asr.Transcription.async_call(
        model= settings.video2textModel,
        file_urls= file_urls
    )
    transcribe_response = dashscope.audio.asr.Transcription.wait(task=task_response.output.task_id)
    if transcribe_response.status_code == HTTPStatus.OK:
        print(json.dumps(transcribe_response.output, indent=4, ensure_ascii=False))
        print('Convert Success!')


if __name__ == '__main__':
    voice2text(['https://dashscope.oss-cn-beijing.aliyuncs.com/samples/audio/paraformer/hello_world_female2.wav',
                'https://dashscope.oss-cn-beijing.aliyuncs.com/samples/audio/paraformer/hello_world_male2.wav'],
               )
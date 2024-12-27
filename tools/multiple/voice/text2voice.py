# ===========================================================================================================
# Author    ：LuShangWu
# Date      ：2024-12-25
# Version   ：1.0
# Description：用于流式文字转化为语音
# Copyright  ：LuShangWu
# License   ：MIT
# Remark   :
#
# ===========================================================================================================


import sys
from dashscope.api_entities.dashscope_response import SpeechSynthesisResponse
from dashscope.audio.tts import ResultCallback, SpeechSynthesizer, SpeechSynthesisResult
from System import settings
import pyaudio

class Callback(ResultCallback):
    _player = None
    _stream = None

    def on_open(self):
        print('Speech synthesizer is opened.')
        self._player = pyaudio.PyAudio()
        self._stream = self._player.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=48000,
            output=True)

    def on_complete(self):
        print('Speech synthesizer is completed.')

    def on_error(self, response: SpeechSynthesisResponse):
        print('Speech synthesizer failed, response is %s' % (str(response)))

    def on_close(self):
        print('Speech synthesizer is closed.')
        self._stream.stop_stream()
        self._stream.close()
        self._player.terminate()

    def on_event(self, result: SpeechSynthesisResult):
        if result.get_audio_frame() is not None:
            # print('audio result length:', sys.getsizeof(result.get_audio_frame()))
            self._stream.write(result.get_audio_frame())

        # if result.get_timestamp() is not None:
        #     print('timestamp result:', str(result.get_timestamp()))




# 语音转文字函数
# text: 待合成的文本
# format: 音频格式
# volume: 音量(1-100)
# sample_rate: 采样率
# rate: 语速(0.5-2.0)
# pitch: 音调(0.5-2.0)
def text2voice(text,format='wav',volume=50,sample_rate=48000,rate=1,pitch=1):
    callback = Callback()
    SpeechSynthesizer.call(model=settings.text2videoModel,
                           text=text,
                           format = format,
                           volume = volume,
                           sample_rate= sample_rate,
                           rate = rate,
                           pitch = pitch,
                           callback=callback,
                           word_timestamp_enabled=True,
                           phoneme_timestamp_enabled=True)

if __name__ == '__main__':
    text2voice('')
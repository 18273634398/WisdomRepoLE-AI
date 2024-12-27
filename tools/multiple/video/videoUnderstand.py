# ===========================================================================================================
# Author    ：LuShangWu
# Date      ：2024-12-25
# Version   ：1.0
# Description：用于视觉（视频）识别
# Copyright  ：LuShangWu
# License   ：MIT
# Remark   :
# 需要使用线程运行该函数，否则程序会长时间卡在此处，调用示例：
# Thread(target=videoUnderstand.videoUnderstand).start()
# 返回格式：
# {推理过程:xxx}
# {用户意图:xxx}
# Support   ：https://bailian.console.aliyun.com/#/model-market/detail/paraformer-mtl-v1?tabKey=sdk
# ===========================================================================================================
from http import HTTPStatus
from tools.multiple.voice import text2voice
import cv2
import os
import time
from threading import Thread
import dashscope


prompt = \
    ('下面你作为一名图书馆的智能人工客服，需要接待视频中的客户，注意客户可能是残障人士，'
     '因此需要你对他的行为进行分析，并给出客户可能的意图:'
     '比如'
     '1.他如果拿起来了一本书，那么他可能是想要询问这本书的相关信息，因此你需要首先识别他拿着的那本书的，返回以{用户意图：查询书籍---{书名}}的形式，返回这本书的书名'
     '2.他可能会向你比手势，可能是想表达自己的心情，因此你需要识别他的手势，返回以{用户意图：表达心情---{情绪}}的形式，返回这段情绪的文字描述'
     '3.他如果没有看向你，那么你只需回复{用户意图：无意图}即可'
     '在这个识别的过程中，可能由于角度、以及图片清晰度等其他问题，使得你无法准确识别出用户的书本、手势等，此时你需要额外给出一个返回信息{错误信息:识别异常}'
     '最后，请你根据用户的行为，以{\'推理过程\':xxx}\n{\'用户意图\':xxx}\n{\'异常信息\':xxx}的形式返回'
     )
urls = []  # 用于保存图像的URL列表
fps = 0  # 视频采样帧率
importantFpsRatio = 1.5 # 采样率



# 摄像头捕获视频流的函数
def capture_video():
    global fps, urls,importantFpsRatio
    cap = cv2.VideoCapture(0)  # 0是默认的摄像头ID
    frame_count = 0  # 用于编号图片
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        _, buffer = cv2.imencode('.jpg', frame)  # 将帧编码为JPEG格式
        if fps <= 0:
            fps = cap.get(cv2.CAP_PROP_FPS)
        frame_bytes = buffer.tobytes()

        # 将图片保存到指定路径并进行编号命名
        frame_count += 1
        img_filename = f"{frame_count}.jpg"
        img_path = os.path.join("D:/Desktop/video", img_filename)
        with open(img_path, 'wb') as f:
            f.write(frame_bytes)

        # 将文件保存的位置URL添加在全局变量urls中
        urls.append(img_path)
        if urls.__len__() >= fps*importantFpsRatio:
            # 启动一个单独的线程来发送帧
            Thread(target=send_frame, args=(urls,)).start()
            urls = []
            image_counter = 1
            fps = 0
            print("视频发送完成")
            cap.release()  # 释放摄像头资源







# 发送视频帧到服务器的函数
def send_frame(urls):
    global prompt
    print("开始发送视频帧\n")
    # 开始计时
    start_time = time.time()
    messages = [{"role": "user",
                 "content": [
                     {"video": urls},
                     {"text": prompt}]}]
    response = dashscope.MultiModalConversation.call(
        api_key=os.getenv("DASHSCOPE_API_KEY"),
        model='qwen-vl-max-latest',
        messages=messages
    )
    if response.status_code == HTTPStatus.OK:
        # 结束计时
        end_time = time.time()
        print("视频识别成功，耗时：", end_time - start_time, "秒")
        result = response['output']['choices'][0]['message']['content'][0]['text']
        print(result)
        text2voice.text2voice(result)
    else:
        print(response.code)
        print(response.message)
        text2voice.text2voice("出现异常，原因："+response.message)



def videoUnderstand():
    capture_video()


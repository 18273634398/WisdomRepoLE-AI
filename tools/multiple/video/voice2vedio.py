# ===========================================================================================================
# Author    ：LuShangWu
# Date      ：2024-12-25
# Version   ：1.0
# Description：基于人物视频和人声音频，生成人物讲话口型与输入音频相匹配的新视频
# Copyright  ：LuShangWu
# License   ：MIT
# Remark   :
# Support  : https://bailian.console.aliyun.com/#/model-market/detail/videoretalk?tabKey=sdk
# ===========================================================================================================

import requests
import time
import os
from System import settings
# Get local environment variables
API_KEY = os.environ.get("DASHSCOPE_API_KEY")

'''
VIDEO_URL = 'http://example.com/yourvideo.mp4'
AUDIO_URL = 'http://example.com/youraudio.wav'
REF_IMAGE_URL = 'http://example.com/yourimage.jpg'
'''
def voice2vedio(video_url, audio_url, ref_image_url):
    # 提交任务并获取任务ID
    task_id = submit_task(video_url, audio_url, ref_image_url)
    # 检查任务状态并获取生成的视频URL
    video_url = check_task_status(task_id)
    # 下载生成的视频
    download_video(video_url)

def submit_task(video_url, audio_url, ref_image_url):
    # 提交视频生成任务到DashScope API，并返回任务ID
    url = 'https://dashscope.aliyuncs.com/api/v1/services/aigc/image2video/video-synthesis/'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {API_KEY}',
        'X-DashScope-Async': 'enable'
    }
    data = {
        "model": settings.video2vedioModel,
        "input": {
            "video_url": video_url,
            "audio_url": audio_url,
            "ref_image_url": ref_image_url
        },
        "parameters": {
            "video_extension": False
        }
    }
    response = requests.post(url, headers=headers, json=data)
    response_data = response.json()
    return response_data['output']['task_id']

def check_task_status(task_id):
    # 检查指定任务ID的任务状态，如果成功则返回生成的视频URL
    url = f'https://dashscope.aliyuncs.com/api/v1/tasks/{task_id}'
    headers = {
        'Authorization': f'Bearer {API_KEY}'
    }
    while True:
        response = requests.get(url, headers=headers)
        response_data = response.json()
        status = response_data['output']['task_status']
        if status == 'SUCCEEDED':
            return response_data['output']['video_url']
        elif status == 'FAILED':
            raise Exception("Task failed")
        time.sleep(10)  # Wait for 10 seconds before checking again

def download_video(video_url, file_path='output.mp4'):
    # 下载指定URL的视频并保存到本地文件
    response = requests.get(video_url)
    with open(file_path, 'wb') as file:
        file.write(response.content)
    print(f"Video downloaded to {file_path}")


# ===========================================================================================================
# Author    ：LuShangWu
# Date      ：2024-12-25
# Version   ：1.0
# Description：多模态向量模型将文本、图像或视频转换成一组由浮点数组成的向量，适用于视频分类、图像分类、图文检索等。
# Copyright  ：LuShangWu
# License   ：MIT
# Remark   :
# 多模态类型支持text、image、video类型, 不同类型的参数值均为String类型，格式参考如下{"模态类型": "输入字符串或图像、视频url"}
# 图片使用BASE64数据：将编码后的BASE64数据传递给image_url参数，格式为data:image/{format};base64,{base64_image}，其中：
# image/{format}：本地图像的格式。请根据实际的图像格式，例如图片为jpg格式，则设置为image/jpeg
# base64_image：图像的BASE64数据
#
# 返回的结果是包含Embeddings的数组，每个Embedding是一个浮点数组。
# ===========================================================================================================

import dashscope
import json
from http import HTTPStatus

# GlobalSetting
from System import settings

# imageEmbedding
def imageEmbedding(image = "https://dashscope.oss-cn-beijing.aliyuncs.com/images/256_1.png"):
    input = [{'image': image}]
    resp = dashscope.MultiModalEmbedding.call(
        model=settings.embeddingModel,
        input=input
    )

    if resp.status_code == HTTPStatus.OK:
        return resp.output
    else:
        print(f'错误码：{resp.code}\n错误信息：{resp.message}')



# textEmbedding
def textEmbedding(text='智慧图书馆项目'):
    input = [{'text': text}]
    resp = dashscope.MultiModalEmbedding.call(
        model=settings.embeddingModel,
        input=input
    )

    if resp.status_code == HTTPStatus.OK:
        return resp.output
    else:
        print(f'错误码：{resp.code}\n错误信息：{resp.message}')



# videoEmbedding
def videoEmbedding(video):
    input = [{'video': video}]
    resp = dashscope.MultiModalEmbedding.call(
        model=settings.embeddingModel,
        input=input
    )

    if resp.status_code == HTTPStatus.OK:
        return resp.output
    else:
        print(f'错误码：{resp.code}\n错误信息：{resp.message}')


# Test
if __name__ == '__main__':
    print("None Test Usage")
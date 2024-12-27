# ===========================================================================================================
# Author    ：LuShangWu
# Date      ：2024-12-26
# Version   ：1.0
# Description：允许通过文件上传达成本地知识库的构建
# Copyright  ：LuShangWu
# License   ：MIT
# Remark   :注意使用session_id标记多轮对话，其保存在云端仅1小时，且最长对话轮次为50次。
# Support: :https://bailian.console.aliyun.com/?bestPractices=1&accounttraceid=efb90f69faf9406db7157d78b4ab4fcaqtqd#/best-practices/assistant_api_rag
# ===========================================================================================================
import os
from llama_index.readers.dashscope.base import DashScopeParse
from llama_index.readers.dashscope.utils import ResultType
from llama_index.indices.managed.dashscope import DashScopeCloudIndex, DashScopeCloudRetriever
from llama_index.core import SimpleDirectoryReader
from llama_index.llms.dashscope import DashScope, DashScopeGenerationModels
from typing import cast
from enum import Enum

# 该函数用于将本地数据文件夹中的文件上传并解析，然后构建知识索引
def ingest_data(file_folder: str, name: str, category_id="default"):
    # 本地文档上传，并完成文档解析，可以指定百炼数据中心的目录
    parse = DashScopeParse(result_type=ResultType.DASHSCOPE_DOCMIND, category_id=category_id)
    # 定义文件类型对应的解析器
    file_extractor = {".pdf": parse, '.doc': parse, '.docx': parse}
    # 解析本地文档，并返回解析结果
    documents = SimpleDirectoryReader(
        file_folder, file_extractor=file_extractor
    ).load_data(num_workers=4)

    # 构建知识索引，完成文档切分、向量化和入库操作
    _ = DashScopeCloudIndex.from_documents(documents, name, verbose=True)
    return documents

# 定义返回结果的类型，可以是字符串或者LlamaIndex的nodes
class ReturnType(str, Enum):
    STRING = "str"
    NODE = "node"

# 该函数用于从知识库中检索节点，支持返回字符串或LlamaIndex的nodes
def retrieve_nodes(query: str, name: str, return_type: ReturnType = ReturnType.STRING):
    """
    知识库检索函数
    :param query: 用户Query
    :param name: 百炼知识索引名称
    :param return_type: 支持返回str或者LlamaIndex nodes
    :return:
    """
    def _format(doc_name=None, title=None, content=None, chunk_index=1):
        return f"[{chunk_index}] 【文档名】{doc_name}\n 【标题】{title}\n 【正文】{content}"

    index = DashScopeCloudIndex(name)
    retriever = index.as_retriever(rerank_min_score=0.3)
    retriever = cast(DashScopeCloudRetriever, retriever)
    print(f"Pipeline id {retriever.pipeline_id}", flush=True)
    nodes = retriever.retrieve(query)
    if return_type == ReturnType.STRING:
        context_str = "\n\n".join([_format(
            doc_name=node.metadata["doc_name"],
            title=node.metadata["title"],
            content=node.get_content(),
            chunk_index=index + 1
        ) for index, node in enumerate(nodes)])
        return context_str
    else:
        return nodes

# 该函数结合LLM，构造Query Engine，完成RAG完整链路
def query_rag(query: str, name: str):
    """
    结合LLM，构造Query Engine，完成RAG完整链路
    :param query: 用户Query
    :param name: 百炼知识索引名称
    :return:
    """
    dashscope_llm = DashScope(
        model_name=DashScopeGenerationModels.QWEN_MAX, api_key=os.environ["DASHSCOPE_API_KEY"]
    )
    index = DashScopeCloudIndex(name)
    query_engine = index.as_query_engine(llm=dashscope_llm)
    response = query_engine.query(query)
    return response

index_name = "上海AI峰会-百炼文档助手"

"""Step 1: 百炼知识库数据导入"""
docs = ingest_data(
    "/Users/towardsun/Documents/Project/Bailian/Demo", index_name,
    category_id="cate_ce28ea58687d4db599d974fe5cd7852010001"
)

"""Step 2: 在线RA检索"""
question = "请问百炼平台如何部署模型"
resp = retrieve_nodes(question, name=index_name)
print(f"Retrieve result:\nQuestion: {question}\nResponse:\n{resp}")


"""Step 3: 在线RAG完整链路"""
resp = query_rag(question, name=index_name)
print(f"Query result:\nQuestion: {question}\nResponse:\n{resp}")

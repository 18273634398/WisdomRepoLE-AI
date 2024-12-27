# ===========================================================================================================
# Author    ：LuShangWu
# Date      ：2024-12-25
# Version   ：1.0
# Description：用于
# Copyright  ：LuShangWu
# License   ：MIT
# Remark   :
# 多语言文本统一排序模型,提供高水平的文本排序服务。
# 通常用于语义检索、RAG等场景，可以简单、有效地提升文本检索的效果。
# 模型会根据与查询的语义相关性从高到低对候选文本进行排序。
# ===========================================================================================================
from llama_index.core.data_structs import Node
from llama_index.core.schema import NodeWithScore
from llama_index.postprocessor.dashscope_rerank import DashScopeRerank

# 定义一个包含评分节点的列表
nodes = [
    NodeWithScore(node=Node(text="text1"), score=0.7),
    NodeWithScore(node=Node(text="text2"), score=0.8),
]

# 创建DashScopeRerank实例，设置返回结果的数量n==5

dashscope_rerank = DashScopeRerank(top_n=5)

# 对节点列表进行后处理，根据查询字符串重新排序节点
# 返回的节点是与查询相关性最高的前n个节点
results = dashscope_rerank.postprocess_nodes(nodes, query_str="<user query>")

# 遍历处理后的结果，打印每个节点的文本内容和评分
for res in results:
    print("Text: ", res.node.get_content(), "Score: ", res.score)

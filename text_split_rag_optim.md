# 文本分割、向量化与召回优化技术参考（对标 LangChain / Dify）

---

## 一、文本分割技术

| 技术 / 策略                        | 描述                     | 借鉴对象             | 效果                      |
| ------------------------------ | ---------------------- | ---------------- | ----------------------- |
| RecursiveCharacterTextSplitter | 先按段落/句子/标点分割，后处理定长分割   | LangChain        | 保持语义完整，减少信息断裂           |
| MarkdownHeaderTextSplitter     | 根据 Markdown 标题层级划分矩阵结构 | LangChain        | 构建 "主题+段落" 父子结构，有利上下文联系 |
| Parent-Child Chunking          | 子块分割同时保留父节点信息          | Dify v0.15+      | 提升抽取精度＋保持上下文结构          |
| Sliding Window                 | 块之间设置重叠区域（如 20%）       | LangChain 通用     | 减少边界信息丢失                |
| 语义聚类分段                         | 用 embedding 对整文段聚类，再划分 | DeepSeek/Voyager | 分块更自然，精准地选择分割点          |

### 策略类型建议

- 结构化文档：MarkdownHeader + Parent-Child
- 普通文档：Recursive 分割 + 滑窗 + 聚类

---

## 二、Embedding 向量化技术

| 技术 / 策略              | 描述                        | 借鉴对象              | 效果             |
| -------------------- | ------------------------- | ----------------- | -------------- |
| 多模型 Embedding 路由     | 长文本用 bge-m3，短问题用 OpenAI 等 | LangChain / Dify  | 降低成本＋提高短句准确性   |
| 父子联合 Embedding       | 将子块+父块 合并生成向量             | Dify Hybrid Chunk | 增强该块的背景识别能力    |
| Embedding + Metadata | 向量排序配合元数据筛选               | LangChain         | 提升准确性，可控给定矩阵   |
| 优选向量模型               | bge-m3 / GTE / MiniLM 等   | Dify、Github示例     | 降低向量碎片化，提升抽取效果 |

---

## 三、抽取引擎提升

| 技术                    | 描述                        | 借鉴对象                  | 效果               |
| --------------------- | ------------------------- | --------------------- | ---------------- |
| Hybrid Retrieval      | 向量 + 关键词双通道               | LangChain RetrievalQA | 提高 recall，防止超过抽取 |
| Multi-query Expansion | 用 LLM 将查询扩展成3\~5 种全方体表达   | LangChain / Dify      | 防止表达不符时抽取失效      |
| Rerank 重排             | 用 cross-encoder 对抽取结果进行分序 | LangChain / Cohere    | 提升答案排序精度         |
| Metadata Filter       | 根据分类、知识库、时间等进行前筛          | Haystack / LangChain  | 控制抽取范围，避免乱扩      |

---

## 四、全系统环节优化推荐

1. 实现 **Parent-Child 分块器**：根据 Markdown / HTML 结构解析生成父子块并向量化
2. 插入 **Multi-query + Hybrid Retrieval** 抽取器
3. 线上合并 **Rerank 模型** (bge-reranker)
4. 优化分块长度：建议 256\~512 tokens，64 token 重叠

---

## 五、推荐 Pipeline 流程

```
文档输入 -> Markdown Header 分块 ->
  Recursive 分块 ->
    父子联合 Embedding ->
      向量库入库 + Metadata ->
        查询 Multi-query ->
          Hybrid Retrieval ->
            Reranker ->
              Top-k Answer
```

---

## 如需其他接入

- 可加入: 查询扩展器（LLM 生成多重表达）
- 可加入: 相关性分类器（根据题目、知识基结构进行分组查询）
- 可加入: Feedback / Rating 机制（用户评价回复质量）

---

若需帮你实现上述流程或实例代码，可随时请求帮助。


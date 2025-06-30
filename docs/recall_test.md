# 召回测试功能说明

## 功能简介
召回测试用于评估知识库检索效果，支持批量用例、自动运行、指标统计与可视化。

## 主要功能
- 测试用例管理（手动/批量导入）
- 一键运行测试，实时进度
- 指标统计（准确率、召回率、F1、响应时间）
- 结果可视化与导出
- 支持A/B检索策略对比

## API接口
- GET/POST /kb/{kb_id}/recall-tests/
- GET/PUT/DELETE /kb/{kb_id}/recall-tests/{test_id}
- GET/POST /kb/{kb_id}/recall-tests/{test_id}/cases
- POST /kb/{kb_id}/recall-tests/{test_id}/run
- GET /kb/{kb_id}/recall-tests/{test_id}/report

## 权限
仅知识库拥有者/管理员可管理召回测试。

## 示例流程
1. 新建召回测试，配置参数
2. 添加/导入测试用例
3. 一键运行测试，查看进度
4. 查看并导出测试报告 
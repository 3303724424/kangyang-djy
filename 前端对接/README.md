# 前端对接包

前端只需要调用：

```text
POST /api/v1/travel/plan
```

运行中的接口文档地址：

```text
http://服务器地址:8000/docs
```

建议前端直接渲染响应中的 `frontend_payload`，不要解析模型的原始文本。重点字段：

- `summary`：顶部温暖文案。
- `days[].timeline`：逐日时间线。
- `days[].meal_candidate`、`restaurant_candidates`：餐饮候选与地址。
- `wellness`：康养模式、候选或已选择后的排程候选。
- `student_guide`：学生导游候选和服务边界。
- `manual_confirmations`：必须展示的人工确认事项。

详细字段说明见 `FRONTEND_API.md`；可直接复制 `examples/travel-plan-request.json` 到 Swagger 的请求体进行测试。

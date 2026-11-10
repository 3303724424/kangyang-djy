# 都江堰银龄康养旅居 API（前端对接）

## 运行后可直接查看的文档

- Swagger UI：`http://127.0.0.1:8000/docs`
- OpenAPI JSON：`http://127.0.0.1:8000/openapi.json`
- 健康检查：`GET http://127.0.0.1:8000/health`
- 前端协议提示：`GET http://127.0.0.1:8000/api/v1/frontend-contract`

启动服务：

```powershell
cd D:\git\kangyang-djy\agent\backend
conda activate travel
python serve_api.py
```

模型会在启动阶段加载一次；看到 Uvicorn 的启动日志后，再由前端发起请求。停止服务按 `Ctrl + C`。

## 核心接口

`POST /api/v1/travel/plan`

请求 JSON 示例见 [examples/travel-plan-request.json](examples/travel-plan-request.json)。

```json
{
  "question": "两位七十多岁长者去都江堰三天，想慢游、泡温泉，需要学生导游陪同。",
  "name": "张阿姨",
  "days": 3,
  "travelers": 2,
  "mobility": "需要减少步行",
  "preferences": ["文化讲解", "轻松慢游", "温泉"],
  "needs_student_guide": true,
  "wellness_mode": "selected",
  "wellness_categories": ["温泉", "营养餐"]
}
```

响应 JSON 示例见 [examples/travel-plan-response.json](examples/travel-plan-response.json)。顶层结构如下：

```json
{
  "request_id": "uuid",
  "status": "success",
  "generated_at": "UTC ISO-8601 时间",
  "frontend_payload": { "version": "travel_frontend_payload_v1" }
}
```

## 前端渲染约定

- 只使用 `frontend_payload`，不要解析或展示模型的原始回答。
- `days[].timeline` 是时间轴卡片，使用 `time_range`、`title`、`icon`、`tone` 渲染。
- `days[].meal_candidate`、`restaurant_candidates` 均为候选信息，需同时展示地址、`note` 及“出发前确认”提示。
- `wellness_mode`：`not_needed` 不展示；`recommend_only` 只展示候选；只有 `selected` 且用户选定类别后，才可能在 `days[].wellness` 看到排程候选。
- `student_guide.requested=true` 表示用户希望陪伴服务；候选人仍需人工确认排班、集合点、授权及协议。
- 始终展示 `manual_confirmations` 与 `global_safety_copy`。酒店房态、价格、项目名额、开放状态均不是实时承诺。

## 浏览器调用示例

```js
const response = await fetch('http://127.0.0.1:8000/api/v1/travel/plan', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify(formValue),
});

if (!response.ok) throw new Error('行程生成失败');
const { frontend_payload } = await response.json();
// 使用 frontend_payload.days / restaurant_candidates / wellness 直接渲染
```

本地 Vite 前端（5173）与常用 React 前端（3000）已在默认 CORS 白名单中。其它域名请设置环境变量 `TRAVEL_ALLOWED_ORIGINS` 后重启服务，例如：

```powershell
$env:TRAVEL_ALLOWED_ORIGINS = 'https://your-frontend.example.com'
python serve_api.py
```

## 错误处理

- `422`：请求字段不合法，例如 `days` 不是 1-7。
- `503`：模型仍在启动。
- `500`：本地模型、LoRA 适配器或知识库加载/生成失败；前端应提示“系统暂时繁忙，请稍后再试”。

## 重新生成同步文档与样例

当数据字段有改动时执行：

```powershell
cd D:\git\kangyang-djy\agent\backend
python scripts\export_frontend_examples.py
```

它会自动更新 `docs/openapi.json`、请求样例和响应样例；运行中的 `/docs` 始终从当前接口代码自动生成。

# 伴旅 Git 上传目录

本目录只保留可上传 GitHub 的代码与交接资料，不包含 Qwen3 基座模型、LoRA 权重、训练数据集、检查点或 Python 缓存。

完整可运行项目（含模型）已迁移到：

```text
D:\project\travel1\3
```

## 目录

```text
backend/        FastAPI、规则规划、知识检索与运行时 JSON 数据
前端对接/      OpenAPI、前端接口文档、请求与响应 JSON 示例
部署配置/      Linux 部署说明、依赖、Nginx、systemd、环境变量样例
```

## 上传前

```powershell
git status
git add backend 前端对接 部署配置 README.md .gitignore
git status
```

确认待提交列表中没有以下内容再提交：

- `*.safetensors`
- `models/`
- `checkpoint-*`
- `__pycache__/`
- `.env`

## 本地开发

本 Git 目录不附带模型。需要运行时，请使用完整项目中的模型路径，或在环境变量中设置：

```powershell
$env:TRAVEL_MODEL_PATH = 'D:\project\travel1\3\后端部署\models\Qwen3-8B'
$env:TRAVEL_ADAPTER_PATH = 'D:\project\travel1\3\后端部署\models\qwen3-djy-lora-v2'
```

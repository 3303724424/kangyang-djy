# 银龄康养旅居专项评测

`travel_agent_benchmark.json` 含 30 条固定评测题，覆盖：安全边界、学生陪同边界、行程完整性、酒店康养项目、平台信息真实性与隐私风险。

## 先小规模试运行

默认只跑 5 题，避免首次测试等待过久：

```powershell
cd D:\git\kangyang-djy\agent\backend
D:\anaconda3\envs\travel\python.exe evaluation\evaluate_travel_agent.py
```

## 全量评估微调模型

```powershell
D:\anaconda3\envs\travel\python.exe evaluation\evaluate_travel_agent.py --limit 0
```

## 与基础模型对比

基础模型不加载 LoRA：

```powershell
D:\anaconda3\envs\travel\python.exe evaluation\evaluate_travel_agent.py --adapter_path "" --limit 0
```

微调模型：

```powershell
D:\anaconda3\envs\travel\python.exe evaluation\evaluate_travel_agent.py --adapter_path D:\git\kangyang-djy\agent\training\outputs\qwen3-djy-lora-v2 --limit 0
```

报告会保存到 `evaluation\outputs`。其中 `overall_rule_score` 是规则合规分，不是“事实准确率”。必须重点人工检查低分案例与所有医疗、价格、房态、学生服务相关回答。

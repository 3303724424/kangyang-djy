# 本地智能体 Demo

在 `backend` 目录运行，需使用已安装 torch、transformers、peft、bitsandbytes 的 `travel` 环境：

```cmd
cd D:\git\kangyang-djy\agent\backend
D:\anaconda3\envs\travel\python.exe run_agent_demo.py --question "带两位七十岁老人来都江堰三天，想了解放水节，怎么安排？"
```

执行顺序为：检索 `backend/data/knowledge_entries.json` 中已审核知识 -> 调用现有规划算法 -> 将知识和规划结果交给 Qwen3-8B 与 `qwen3-djy-lora-v2` 适配器。模型首次加载需要一些时间。

# 个性化用户画像输入

运行时可用以下参数控制方案，而不再使用写死的体验用户资料：

```powershell
cd D:\git\kangyang-djy\agent\backend
D:\anaconda3\envs\travel\python.exe run_agent_demo.py --question "两位七十多岁老人到都江堰三天，想轻松游览并住安静酒店" --name "张阿姨" --age_group "70-79岁" --travelers 2 --days 3 --budget 2600 --mobility "需要减少步行" --preferences "文化讲解,安静,温泉,停车" --needs_companion
```

## 参数

- `--age_group`：年龄段。
- `--travelers`：同行人数。
- `--days`：旅居天数。
- `--budget`：本次总预算（元）。
- `--mobility`：`可轻松步行`、`需要减少步行`、`需轮椅协助`。
- `--preferences`：使用英文或中文逗号分隔的偏好，例如 `安静,温泉,营养餐`。
- `--needs_companion`：加入学生陪同候选建议；不填写则不显示该模块。
- `--no_wellness`：不在晚间行程插入酒店康养项目。
- `--travel_date`：计划出行日期，仅作为画像记录；景区开放、天气、房态仍需实时核验。

所有酒店和康养项目演示数据仍需人工确认，学生陪同人员不能提供医疗、理疗或诊断服务。

# 酒店康养项目的三种使用方式

## 1. 默认：仅推荐，不排入行程

适合用户还没决定是否参加康养活动。系统展示合作酒店/演示酒店可提供的候选服务，但每日行程仍以休息为主。

```powershell
D:\anaconda3\envs\travel\python.exe run_agent_demo.py --question "两位老人到都江堰三天，想看看酒店有哪些康养活动" --wellness_mode recommend_only
```

## 2. 用户已选择：排入行程

仅在用户已经表达项目意愿后使用。`--wellness_categories` 可以填温泉、营养餐、轻运动、健康讲座、茶歇等关键词。

```powershell
D:\anaconda3\envs\travel\python.exe run_agent_demo.py --question "两位老人选择温泉和营养餐，帮我安排三天行程" --wellness_mode selected --wellness_categories "温泉,营养餐"
```

系统只将存在可衔接晚间时段的项目写入行程，并继续提示确认名额、费用、资质、身体适用性与预约规则。

## 3. 不需要康养服务

```powershell
D:\anaconda3\envs\travel\python.exe run_agent_demo.py --question "不需要酒店康养项目，只安排轻松游览" --wellness_mode not_needed
```

旧参数 `--no_wellness` 仍可使用，效果等同于 `--wellness_mode not_needed`。

## 学生导游联动

增加 `--needs_student_guide` 时，系统推送平台专属学生导游演示候选。服务确认后才进入每日陪同安排；学生导游不能提供医疗、理疗、按摩、诊断或给药服务。

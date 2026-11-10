# 合作酒店康养项目库（演示数据）

## 文件说明

- `hotels.json`：合作酒店（当前全部为虚拟演示酒店）。
- `wellness_programs.json`：由酒店提供的康养服务模块（当前全部为虚拟演示项目）。

程序会在每次生成行程时重新读取这两个 JSON 文件。因此修改并保存后，**下一次提问/运行就会同步采用新数据**，无需重新训练 LoRA 模型。

## 新增或修改酒店

在 `hotels.json` 中新增一个对象；`id` 必须唯一。康养项目的 `hotel_id` 必须完全等于该 `id`。

```json
{
  "id": "partner-hotel-001",
  "name": "某某康养酒店",
  "location": "青城山片区",
  "rating": null,
  "price_per_night": null,
  "accessible": true,
  "tags": ["康养", "营养餐", "停车"],
  "cooperation_status": "pending_confirmation",
  "note": "资料待酒店确认。"
}
```

## 新增康养项目

在 `wellness_programs.json` 中增加对象。仅录入酒店真实提供且已核验的项目；医疗、康复、理疗等高风险服务应保留人工确认与风险提示。

```json
{
  "id": "partner-program-001",
  "hotel_id": "partner-hotel-001",
  "name": "营养晚餐",
  "category": "餐饮",
  "duration_minutes": 60,
  "time_slots": ["17:30-19:00"],
  "suitable_mobility": ["可轻松步行", "需要减少步行", "需轮椅协助"],
  "tags": ["营养餐", "低强度"],
  "safety_note": "特殊饮食需求须提前确认。",
  "requires_manual_confirmation": true,
  "data_status": "partner_confirmed"
}
```

## 状态建议

- `demo_pending_partner_confirmation`：虚拟演示数据，不向用户承诺可预订。
- `pending_confirmation`：已收集资料，等待酒店确认。
- `partner_confirmed`：已完成合作/资料核验，仍应对房态、价格与名额做实时确认。

## 运行验证

```powershell
cd D:\git\kangyang-djy\agent\backend
D:\anaconda3\envs\travel\python.exe run_agent_demo.py --question "两位七十岁老人到都江堰三天，行动较慢，想安排轻松游览和酒店康养项目。"
```

在输出的 `plan` 中检查：

- `selected_wellness_hotel`
- `wellness_program_recommendations`
- `itinerary[*].wellness_program`


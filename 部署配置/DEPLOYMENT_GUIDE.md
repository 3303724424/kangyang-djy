# 服务器部署说明

## 1. 服务器建议

- Linux：Ubuntu 22.04 或 24.04。
- GPU：建议 NVIDIA 24GB 显存；24GB 可为模型加载、生成上下文和系统预留空间。
- 内存：建议 32GB 以上；磁盘：建议 100GB 以上。
- Python：当前本地可运行环境为 Python 3.10.22。

不要以普通 CPU 云服务器作为正式推理服务器。模型可以技术上运行，但生成速度和用户体验通常不适合在线服务。

## 2. 上传哪些文件

上传整个 `服务器部署包`，其中包含：

```text
服务器部署包/
├─ backend/                  # FastAPI、规划、知识检索和运行时 JSON 数据
├─ models/Qwen3-8B/          # 15GB 左右的基座模型
├─ models/qwen3-djy-lora-v2/ # 约 0.7GB 的 LoRA 适配器
├─ .env.example
├─ requirements-server.txt
├─ systemd/banlv-api.service
└─ nginx/banlv-api.conf
```

不要上传项目根目录的训练素材、训练缓存、`__pycache__` 和本机 Conda 环境。

## 3. 首次安装

在服务器安装 NVIDIA 驱动后，创建 Python 3.10 虚拟环境：

```bash
sudo mkdir -p /opt/banlv
sudo chown -R $USER:$USER /opt/banlv
cd /opt/banlv
python3.10 -m venv venv
source venv/bin/activate
python -m pip install --upgrade pip
```

先根据服务器驱动和 CUDA 兼容性，从 PyTorch 官方安装页安装**适合 Linux GPU 的 PyTorch**；再安装项目其余依赖：

```bash
pip install -r requirements-server.txt
```

验证 GPU：

```bash
python -c "import torch; print(torch.cuda.is_available(), torch.cuda.get_device_name(0))"
```

## 4. 设置配置并试运行

```bash
cp .env.example .env
nano .env
cd /opt/banlv/backend
source /opt/banlv/venv/bin/activate
set -a; source /opt/banlv/.env; set +a
python -m uvicorn app.api:app --host 127.0.0.1 --port 8000 --workers 1
```

服务启动后，在服务器执行：

```bash
curl http://127.0.0.1:8000/health
```

返回 `"status":"ready"` 即表示模型与接口已加载。

## 5. 正式常驻运行

复制 systemd 服务文件，并按实际 Linux 用户名、Python 路径修改 `User` 和 `ExecStart`：

```bash
sudo cp systemd/banlv-api.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now banlv-api
sudo systemctl status banlv-api
```

日志查看：

```bash
sudo journalctl -u banlv-api -f
```

此项目必须保持 `--workers 1`。每增加一个 worker 都会重复加载一份模型，额外占用显存。

## 6. 域名和 HTTPS

Nginx 配置模板在 `nginx/banlv-api.conf`。修改域名后复制至服务器的 Nginx 配置目录，配置 TLS 证书，并仅开放 80/443/SSH 必要端口。前端域名需同步填入 `.env` 中的 `TRAVEL_ALLOWED_ORIGINS`。

## 7. 上线前检查

- 调用 `/health` 返回 `ready`。
- 在 `/docs` 用请求样例成功调用 `/api/v1/travel/plan`。
- 确认跨域只允许正式前端域名。
- 确认酒店、康养、餐饮、学生导游数据已由真实合作方审核替换。
- 确认日志中不记录用户敏感健康信息和完整个人隐私。

# 行程管理主线项目

这是全栈学习库的第一版可运行示例。它把页面、真实 HTTP 请求、SQLite 数据和测试放在一起，作为后续登录、权限、部署和 AI 协作练习的基础。

## 当前范围

- 行程列表：加载、筛选、分页、空状态和错误状态；
- 新增行程：城市、天数、预算和状态校验；
- 删除行程：前端确认后调用真实 DELETE 接口；
- 健康检查：`GET /healthz`；
- 后端测试：列表、筛选、新增和删除主路径。

当前版本使用原生 HTML/CSS/JavaScript，降低第一次运行的环境成本。后续再把前端迁移到 React，把认证、权限、Docker 和 CI/CD 按主线步骤加入。

## 启动

在 `examples/trip-manager` 目录执行：

```powershell
python -m venv .venv
.\\.venv\\Scripts\\Activate.ps1
pip install -r requirements.txt
python -m uvicorn backend.app.main:app --reload
```

浏览器打开 <http://127.0.0.1:8000>。

## 测试

```powershell
pytest
```

## 目录约定

```text
backend/       FastAPI 应用、SQLite 初始化和接口测试
frontend/      页面、样式和浏览器端请求逻辑
data/          本地 SQLite 文件目录，运行后自动生成
```

## AI 协作练习

每次改动只完成一个小目标，并保留三份证据：

1. 修改前的需求和技术判断；
2. AI 修改的文件与差异；
3. 成功、空数据、错误输入和回归验证结果。

不要把数据库文件、密钥或包含私人数据的日志提交到仓库。

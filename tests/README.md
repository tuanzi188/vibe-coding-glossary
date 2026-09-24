# 页面导航回归

该检查只用于开发验证，学习库在浏览器运行时不依赖 Python 或 Playwright。

在仓库根目录运行：

```powershell
python -m pip install playwright
python -m playwright install chromium
python tests/reading_navigation.py
```

检查会启动仅监听本机的临时服务，结束后关闭服务和浏览器。覆盖双入口、连续章节顺序、目录滚动、刷新与后退、练习状态保留、参考区展开、旧项目链接、移动目录收起，以及 1440 / 768 / 375 像素亮暗布局。截图保存在已忽略的 `_shots/`。

# lens-km

模拟微软 LENS 的文档扫描 PWA，单文件应用，扫描生成 PDF。

在线体验：https://unplage.github.io/lens-km/

## 功能
- 扫描模式：白板 / 文档 / 照片 / 名片 / OCR
- 滤镜（11 个）：原图 / 白板 / 文档 / 灰度 / 黑白 / 自动增强 / 深度对比 / 提亮 / 反色 / 降噪 / 魔法
- 编辑：旋转、裁剪（拖拽四角）、透视校正（拖拽四角）、撤销（Ctrl+Z）
- 闪光灯、前后相机切换、数码变焦
- 相册：多选、拖拽排序、点击底部可修改文件名、按文件名排序导出
- 导出：PDF（可选 DPI 150-300）、TXT

## OCR（MiMo-V2.5，需配置 API Key）
- 引擎：小米 **MiMo-V2.5** 多模态 API（`mimo-v2.5`，OpenAI 兼容）
- 入口：相机顶栏 🔑 按钮配置 Key / Base URL（支持按量付费 `sk-` 与 Token Plan `tp-`）
- 识别分辨率可选 512/1024/1536/2048，识别前显示预估图片 Token（越小越省，小字选大）
- 支持单张（预览页 OCR）与批量（相册多选 → OCR识别，并发 3 张）
- 结构化输出：纯文本 / Markdown / JSON（含文本块、归一化 bbox、表格、键值对）
- 导出：TXT / Markdown / JSON / PDF，批量可一键全部导出

## 本地运行
```bash
python3 -m http.server 8080
# 浏览器打开 http://localhost:8080/lens-km/ （注意子路径）
```
需 HTTPS 或 localhost 才能访问相机；PWA 安装后支持离线。

# lens-km — 文档扫描 PWA

## 项目本质
单文件 PWA（`index.html` 内含全部 HTML+CSS+JS），模拟微软 Lens，扫描生成 PDF。**无构建工具、无包管理器、无测试**。

## 快速开始
```bash
python3 -m http.server 8080  # 在项目根目录运行
# 浏览器打开 http://localhost:8080/lens-km/ （注意子路径）
```

## 关键文件
- `index.html` — 唯一应用文件（~1600 行，`LensApp` 类架构）
- `manifest.json` — PWA 清单，`start_url: "/lens-km/"`（部署在 GitHub Pages 子路径）
- `sw.js` — Service Worker，**动态 BASE_PATH**（从自身路径推断缓存作用域）

## CDN 外部依赖（需联网）
- `cdn.tailwindcss.com` — Tailwind CSS（非必需，仅辅助样式）
- `cdnjs.cloudflare.com/ajax/libs/pdf-lib/1.17.1/pdf-lib.min.js` — PDF 生成
- `cdn.jsdelivr.net/npm/tesseract.js@4.0.2/dist/tesseract.min.js` — 客户端 OCR

## 架构要点
- **`LensApp` 类**：所有逻辑封装在一个类中，`_state` 集中管理状态，方法按 `_camera`/`_filters`/`_editor`/`_gallery`/`_ocr`/`_pdf`/`_persist` 分组
- **事件委托**：HTML 无 `onclick` 属性，全部通过 `data-cmd` 属性 + `_onClick` 统一分发
- **渲染管线**：`originalImage` → (透视校正) → (滤镜) → `currentImage`，无双重滤镜问题
- **持久化**：IndexedDB 存储 `capturedImages`，刷新不丢失
- **选中机制**：使用 `Set<id>` 而非数组索引，操作后不偏移
- **撤销栈**：维护 `_undoStack[]`，每次编辑前 push，`Ctrl+Z` 或按钮撤销（最多 20 步）
- **并发控制**：`_batchProcessUploads` 同时最多处理 3 张，用 `setTimeout(0)` 让出主线程
- **PDF 导出**：单张图片失败自动跳过，不影响其他页

## 功能清单
- 扫描模式：白板/文档/照片/名片/OCR
- 滤镜（11 个）：原图/白板/文档/灰度/黑白/自动增强/深度对比/提亮/反色/降噪/魔法
- 编辑：旋转/裁剪（预览确认模式）/透视校正（半自动，拖拽四角）/撤销
- OCR 引擎：**Tesseract.js**（浏览器本地）或 **GLM-4.6V-Flash**（智谱 API，需输入 Key）
- 导出：PDF（可选 DPI 150-300）、TXT、按文件名排序、进度条
- 其他：闪光灯、前后相机切换、数码变焦、相册拖拽排序、可编辑文件名

## OCR — GLM-4.6V-Flash
- 引擎选择器中切换到 `GLM-4.6V-Flash`，输入智谱 API Key
- Key 可勾选"记住"（存入 `localStorage`），默认仅存 `sessionStorage`
- API 地址：`https://open.bigmodel.cn/api/paas/v4/chat/completions`
- 模型：`glm-4.6v-flash`，支持中文/英文等多语言文字识别
- 显示识别耗时、Token 消耗

## 透视校正（自动校正）
- 默认开启，使用扫描框区域为初始四角
- 四个彩色手柄可拖拽调整文档范围
- 基于 homography 矩阵 + 双线性插值重采样
- 校正 + 滤镜按 **原始→校正→滤镜** 顺序流水线处理

## 快捷键
- `Space` — 拍照（相机就绪时）
- `Enter` — 在预览页确认添加
- `Ctrl+Z` — 撤销

## 本地测试注意事项
- `start_url` 是 `/lens-km/`，若根目录启动需访问 `/lens-km/` 或修改 `manifest.json` 为 `/`
- Service Worker 注册路径 `./sw.js`，相对路径自动适配子目录
- 需 HTTPS 或 localhost 才能访问相机

## 部署
- GitHub Pages：`https://unplage.github.io/lens-km/`
- Service Worker 的 `BASE_PATH` 自动从 `self.location.pathname` 推断

## Service Worker 更新规则
- **每次修改 `index.html` 后必须更新 `sw.js`** — 至少将缓存版本号 `vX` 递增（如 `v1` → `v2`），否则浏览器不会拉取新内容
- 版本号位于 `CACHE_NAME` 中，格式：`pwa-cache-<BASE_PATH>-v<数字>`

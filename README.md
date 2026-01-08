# ☁️ TTanG-CF-Bridge (Cloudflare AI 桥接工具)

这是一个专为 ComfyUI 设计的插件，通过对接 Cloudflare Workers AI，实现**零显存消耗**的语言特效处理与高质量图像生成。

## ✨ 主要功能
- **☁️ TTanG-语言特效**：支持最新的 DeepSeek, Llama 4, Gemma 3 等模型。具备“翻译并增强提示词”、“图片视觉反推”等预设功能。
- **🎨 TTanG-图片生成**：支持 Flux.1 [schnell]、SDXL Lightning 等云端生成模型。
- **🔒 安全持久化**：API Token 和 Account ID 仅保存在本地 `credentials.json`，无需反复输入。

## 🛠️ 安装方法
1. 进入 ComfyUI 的插件目录：`ComfyUI/custom_nodes/`。
2. 将本项目文件夹整个放入该目录。
3. 如果你发现节点无法工作，请确保安装了依赖：
pip install requests

🚀 Cloudflare 设置指引
为了使用本节点，你需要准备两样东西：
Account ID：
登录 Cloudflare 控制台，在网址中 dash.cloudflare.com/ 后面那一串 32 位字符即为 ID。
API Token：
点击右上角头像 -> “我的个人资料” -> “API 令牌” -> “创建令牌”。
使用“Workers AI (编辑)”模板创建，并获取生成的 Token。</p>
⚠️ 注意事项
免费额度：Cloudflare 每天提供 10,000 个“神经元”免费额度。生成一张图片或多次反推后额度会消耗，每天早上 8:00 (北京时间) 刷新。
模型授权：首次使用 Llama 系列模型，请先在 Cloudflare 网页端的 AI Playground 运行一次，并点击“接受协议”。
安全：请勿将 credentials.json 文件分享给他人，这包含你的个人密钥。</p>
📂 推荐模型
反推/视觉：@cf/meta/gemma-3-12b-it
绘图：@cf/black-forest-labs/flux-1-schnell (步数建议设置为 4)
对话/增强：@cf/deepseek-ai/deepseek-r1-distill-qwen-32b
<div align="center">
  <p><i>如图所示</i></p>
<img width="1919" height="821" alt="01" src="https://github.com/user-attachments/assets/053ae642-ea5f-4ce9-81ef-039704fd0117" />
</div>

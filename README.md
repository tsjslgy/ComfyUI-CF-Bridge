# ☁️ TTanG-CF-Bridge (Cloudflare AI 桥接工具)

这是一个专为 ComfyUI 设计的插件，通过对接 Cloudflare Workers AI，实现**零显存消耗**的语言特效处理与高质量图像生成。</p>
</p>
## ✨ 主要功能</p>
- **☁️ TTanG-语言特效**：支持最新的 DeepSeek, Llama 4, Gemma 3 等模型。具备“翻译并增强提示词”、“图片视觉反推”等预设功能。</p>
- **🎨 TTanG-图片生成**：支持 Flux.1 [schnell]、SDXL Lightning 等云端生成模型。</p>
- **🔒 安全持久化**：API Token 和 Account ID 仅保存在本地 `credentials.json`，无需反复输入。</p>
</p>
## 🛠️ 安装方法</p>
1. 进入 ComfyUI 的插件目录：`ComfyUI/custom_nodes/`。</p>
2. 将本项目文件夹整个放入该目录。</p>
3. 如果你发现节点无法工作，请确保安装了依赖：</p>
pip install requests</p>
</p>
🚀 Cloudflare 设置指引</p>
为了使用本节点，你需要在<a href=https://dash.cloudflare.com>cloudflare</a>准备两样东西：</p>
Account ID：</p>
登录 Cloudflare 控制台，在网址中 dash.cloudflare.com/ 后面那一串 32 位字符即为 ID。</p>
<img width="873" height="43" alt="image" src="https://github.com/user-attachments/assets/ad906727-2837-4df2-aec0-ce5401fbc8aa" />
API Token：</p>
点击右上角头像 -> “配置文件” -> “API 令牌” -> “创建令牌”。</p>
<img width="399" height="332" alt="image" src="https://github.com/user-attachments/assets/9b094107-1203-4cbe-9c0d-b47dcdfad2b8" />
使用“Workers AI (编辑)”模板创建，并获取生成的 Token。</p>
</p>
⚠️ 注意事项</p>
免费额度：Cloudflare 每天提供 10,000 个“神经元”免费额度。每天早上 8:00 (北京时间) 刷新。</p>
安全：请勿将 credentials.json 文件分享给他人，这包含你的个人密钥。</p>
📂 推荐模型（使用LLAMA模型须在CF模型列表里点击授权许可）</p>
反推/视觉：@cf/meta/gemma-3-12b-it</p>
绘图：@cf/black-forest-labs/flux-1-schnell (步数建议设置为 4)</p>
对话/增强：@cf/deepseek-ai/deepseek-r1-distill-qwen-32b</p>
自定义模型</p>
点击works ai后金瑞model复制模型名字，如图</p>
<img width="1851" height="773" alt="image" src="https://github.com/user-attachments/assets/af786627-745f-4982-aba5-bfabc284656f" />
</p>
😀使用方法</p>
1、加载文字特效节点-搜索TTANG，输入您的API和ID，支持图片反推，聊天模式（聊天模式可以定制功能和人设）。</p>
<img width="1491" height="728" alt="image" src="https://github.com/user-attachments/assets/0f2047b7-780a-44e5-a819-a5f89a15be6c" />
</p>
2、加载图片特效节点-搜索TTANG，输入您的API和ID，需要CF上开通图片推理模型，例如SDX,FLUX等。</p>
<img width="1853" height="672" alt="image" src="https://github.com/user-attachments/assets/68944290-c672-4822-bacc-0fc813d76964" />


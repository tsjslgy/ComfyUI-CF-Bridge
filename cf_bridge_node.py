import requests, base64, json, os, io
import numpy as np
from PIL import Image
import torch

# 文件路径定义
current_path = os.path.dirname(os.path.abspath(__file__))
config_path = os.path.join(current_path, "presets.json")
creds_path = os.path.join(current_path, "credentials.json")

class CF_Language_Node:
    def __init__(self):
        self.saved_token = ""
        self.saved_id = ""
        self.load_creds()
    
    def load_creds(self):
        if os.path.exists(creds_path):
            try:
                with open(creds_path, 'r') as f:
                    creds = json.load(f)
                    self.saved_token = creds.get("token", "").strip()
                    self.saved_id = creds.get("id", "").strip()
            except: pass

    @classmethod
    def INPUT_TYPES(s):
        preset_display = ["默认聊天"]
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    presets = json.load(f)
                    preset_display = [v["name"] for v in presets.values()]
            except: pass

        return {
            "required": {
                "cf_api_token": ("STRING", {"default": ""}),
                "cf_account_id": ("STRING", {"default": ""}),
                "预设功能": (preset_display,),
                "model": ([
                    "@cf/meta/llama-3.2-11b-vision-instruct",
                    "@cf/google/gemma-3-12b-it",
                    "@cf/meta/llama-4-scout-17b-16e-instruct",
                    "@cf/openai/gpt-oss-20b",
                    "@cf/deepseek-ai/deepseek-r1-distill-qwen-32b",
                    "[使用下方自定义模型ID]",
                ],),
                "自定义模型ID": ("STRING", {"default": ""}),
                "用户输入": ("STRING", {"multiline": True, "default": "Describe this image"}),
            },
            "optional": {
                "image": ("IMAGE",),
                "自定义人设": ("STRING", {"multiline": True, "default": "", "placeholder": "在此输入额外的人设或风格约束"}),
            }
        }

    RETURN_TYPES = ("STRING",)
    FUNCTION = "call_cf_ai"
    CATEGORY = "Cloudflare_AI"

    def call_cf_ai(self, cf_api_token, cf_account_id, 预设功能, model, 自定义模型ID, 用户输入, image=None, 自定义人设=""):
        # 1. 凭据处理
        self.load_creds()
        final_token = cf_api_token.strip() if cf_api_token.strip() else self.saved_token
        final_id = cf_account_id.strip() if cf_account_id.strip() else self.saved_id
        
        if cf_api_token.strip() or cf_account_id.strip():
            with open(creds_path, 'w') as f:
                json.dump({"token": final_token, "id": final_id}, f)

        if not final_token or not final_id: return ("⚠️ 缺少 Token 或 Account ID",)
        actual_model = 自定义模型ID.strip() if model == "[使用下方自定义模型ID]" else model

        # 2. 核心逻辑：冲突处理与指令融合
        base_task = "You are a helpful assistant."
        is_pure_custom = False

        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                presets = json.load(f)
                for k, v in presets.items():
                    if v["name"] == 预设功能:
                        base_task = v["system"]
                        if k == "custom": is_pure_custom = True
                        break

        if is_pure_custom:
            system_instruction = 自定义人设 if 自定义人设.strip() else "Direct output only."
        else:
            if 自定义人设.strip():
                system_instruction = (
                    f"### CORE TASK (Primary Constraint):\n{base_task}\n\n"
                    f"### STYLE & IDENTITY (Secondary Adjustments):\n{自定义人设}\n\n"
                    f"NOTICE: If instructions conflict, maintain the output format of the CORE TASK "
                    f"but adopt the tone and vocabulary of the STYLE."
                )
            else:
                system_instruction = base_task

        # 3. 构造请求
        api_url = f"https://api.cloudflare.com/client/v4/accounts/{final_id}/ai/run/{actual_model}"
        headers = {"Authorization": f"Bearer {final_token}", "Content-Type": "application/json"}
        
        is_vision = any(x in actual_model.lower() for x in ["vision", "gemma-3", "llava"])
        
        if image is not None and is_vision:
            try:
                # 图像处理
                i = 255. * image[0].cpu().numpy()
                img = Image.fromarray(np.clip(i, 0, 255).astype(np.uint8))
                img.thumbnail((512, 512))
                buffered = io.BytesIO()
                img.save(buffered, format="JPEG", quality=75)
                # 修正变量名：使用 img_base64
                img_base64 = base64.b64encode(buffered.getvalue()).decode()
                
                payload = {
                    "messages": [
                        {"role": "system", "content": system_instruction},
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": 用户输入},
                                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_base64}"}}
                            ]
                        }
                    ]
                }
            except Exception as e:
                return (f"图片处理失败: {str(e)}")
        else:
            payload = {
                "messages": [
                    {"role": "system", "content": system_instruction},
                    {"role": "user", "content": 用户输入}
                ]
            }

        try:
            response = requests.post(api_url, headers=headers, json=payload, timeout=60)
            res_json = response.json()
            if res_json.get("success"):
                result = res_json.get("result", {})
                out = result.get("response") or result.get("description") or result.get("text")
                return (out.strip() if out else "无内容",)
            return (f"CF错误: {res_json.get('errors')}",)
        except Exception as e:
            return (f"网络故障: {str(e)}",)

NODE_CLASS_MAPPINGS = {"CF_Language_Node": CF_Language_Node}
NODE_DISPLAY_NAME_MAPPINGS = {"CF_Language_Node": "☁️ TTanG-语言特效"}
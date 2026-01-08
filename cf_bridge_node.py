import requests, base64, json, os, io
import numpy as np
from PIL import Image

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
                "自定义人设": ("STRING", {"multiline": True, "default": ""}),
            }
        }

    RETURN_TYPES = ("STRING",)
    FUNCTION = "call_cf_ai"
    CATEGORY = "Cloudflare_AI"

    def call_cf_ai(self, cf_api_token, cf_account_id, 预设功能, model, 自定义模型ID, 用户输入, image=None, 自定义人设=""):
        self.load_creds()
        final_token = cf_api_token.strip() if cf_api_token.strip() else self.saved_token
        final_id = cf_account_id.strip() if cf_account_id.strip() else self.saved_id
        
        if cf_api_token.strip() or cf_account_id.strip():
            with open(creds_path, 'w') as f:
                json.dump({"token": final_token, "id": final_id}, f)

        if not final_token or not final_id: return ("⚠️ 缺少 Token/ID",)
        actual_model = 自定义模型ID.strip() if model == "[使用下方自定义模型ID]" else model

        system_instruction = "Direct output only. No preamble."
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                presets = json.load(f)
                for k, v in presets.items():
                    if v["name"] == 预设功能:
                        system_instruction = 自定义人设 if k == "custom" and 自定义人设.strip() else v["system"]
                        break

        api_url = f"https://api.cloudflare.com/client/v4/accounts/{final_id}/ai/run/{actual_model}"
        headers = {"Authorization": f"Bearer {final_token}", "Content-Type": "application/json"}
        
        # 核心逻辑：针对 Llama 3.2 Vision 的 Payload 修正
        if image is not None and ("vision" in actual_model.lower() or "gemma-3" in actual_model.lower()):
            i = 255. * image[0].cpu().numpy()
            img = Image.fromarray(np.clip(i, 0, 255).astype(np.uint8))
            img.thumbnail((512, 512)) # 锁定 512px，极致速度
            buffered = io.BytesIO()
            img.save(buffered, format="JPEG", quality=70)
            img_base64 = base64.b64encode(buffered.getvalue()).decode()
            
            # 使用标准的 OpenAI-like Messages 格式，这能让 Llama 3.2 看见图片
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
                ],
                "max_tokens": 1024
            }
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
                final_text = result.get("response") or result.get("description") or result.get("text")
                if not final_text: return ("API成功但无文字")
                
                # 过滤常见的废话前缀
                clean_text = final_text.strip()
                noise = ["Here is a", "Okay,", "Certainly!", "Description:", "The image shows"]
                for n in noise:
                    if clean_text.startswith(n):
                        clean_text = clean_text.split("\n", 1)[-1] # 尝试切掉第一行
                
                return (clean_text.strip(),)
            else:
                return (f"CF错误: {res_json.get('errors')}")
        except Exception as e:
            return (f"网络请求失败: {str(e)}")

NODE_CLASS_MAPPINGS = {"CF_Language_Node": CF_Language_Node}
NODE_DISPLAY_NAME_MAPPINGS = {"CF_Language_Node": "☁️ TTanG-语言特效"}
import requests, json, os, io, torch, base64
import numpy as np
from PIL import Image

current_path = os.path.dirname(os.path.abspath(__file__))
creds_path = os.path.join(current_path, "credentials.json")

class CF_Image_Node:
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
        return {
            "required": {
                "cf_api_token": ("STRING", {"default": ""}),
                "cf_account_id": ("STRING", {"default": ""}),
                "model": ([
                    "@cf/black-forest-labs/flux-1-schnell",
                    "@cf/black-forest-labs/flux-1-dev",
                    "@cf/bytedance/stable-diffusion-xl-lightning",
                    "@cf/stabilityai/stable-diffusion-xl-base-1.0",
                    "[使用下方自定义模型ID]",
                ],),
                "自定义模型ID": ("STRING", {"default": ""}),
                "正面提示词": ("STRING", {"multiline": True, "default": "A cyberpunk girl, high quality"}),
                "负面提示词": ("STRING", {"multiline": True, "default": ""}),
                "宽度": ("INT", {"default": 1024, "min": 256, "max": 2048, "step": 64}),
                "高度": ("INT", {"default": 768, "min": 256, "max": 2048, "step": 64}),
                "推理步数": ("INT", {"default": 4, "min": 1, "max": 50, "step": 1}),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "generate_image"
    CATEGORY = "Cloudflare_AI"

    def generate_image(self, cf_api_token, cf_account_id, model, 自定义模型ID, 正面提示词, 负面提示词, 宽度, 高度, 推理步数):
        self.load_creds()
        final_token = cf_api_token.strip() if cf_api_token.strip() else self.saved_token
        final_id = cf_account_id.strip() if cf_account_id.strip() else self.saved_id
        
        if not final_token or not final_id: raise Exception("⚠️ 缺少凭据")

        actual_model = 自定义模型ID.strip() if model == "[使用下方自定义模型ID]" else model
        api_url = f"https://api.cloudflare.com/client/v4/accounts/{final_id}/ai/run/{actual_model}"
        
        headers = {
            "Authorization": f"Bearer {final_token}",
            "Content-Type": "application/json"
        }

        # 构造 Payload，针对 Flux 进行特殊字段清洗
        payload = {
            "prompt": 正面提示词,
            "width": 宽度,
            "height": 高度,
            "num_inference_steps": 推理步数
        }
        
        # 只有非 Flux 模型才发送 negative_prompt
        if "flux" not in actual_model.lower():
            if 负面提示词.strip():
                payload["negative_prompt"] = 负面提示词

        try:
            response = requests.post(api_url, headers=headers, json=payload, timeout=120)
            
            if response.status_code != 200:
                raise Exception(f"HTTP {response.status_code}: {response.text}")

            # --- 智能响应处理逻辑 ---
            content_type = response.headers.get("Content-Type", "").lower()
            
            # 情况 A: 返回的是 JSON (里面藏着 Base64)
            if "application/json" in content_type:
                res_json = response.json()
                if not res_json.get("success"):
                    raise Exception(f"API逻辑错误: {res_json.get('errors')}")
                
                img_b64 = res_json.get("result", {}).get("image")
                if not img_b64:
                    raise Exception("JSON 中未找到 image 字段")
                
                img_bytes = base64.b64decode(img_b64)
                image = Image.open(io.BytesIO(img_bytes)).convert("RGB")
            
            # 情况 B: 直接返回二进制图片流
            else:
                try:
                    image = Image.open(io.BytesIO(response.content)).convert("RGB")
                except:
                    # 如果 Image.open 失败，说明可能是报错信息被当成二进制了
                    raise Exception(f"无法识别返回内容，原始数据预览: {response.text[:200]}")

            image_np = np.array(image).astype(np.float32) / 255.0
            image_tensor = torch.from_numpy(image_np)[None,]
            return (image_tensor,)

        except Exception as e:
            raise Exception(f"生成失败: {str(e)}")
from .cf_bridge_node import CF_Language_Node
from .cf_image_node import CF_Image_Node

NODE_CLASS_MAPPINGS = {
    "CF_Language_Node": CF_Language_Node,
    "CF_Image_Node": CF_Image_Node
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "CF_Language_Node": "TT-CF-Bridge",
    "CF_Image_Node": "TT-CF-Image"
}

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']
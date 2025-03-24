import yaml
from pathlib import Path
from typing import Dict, Any


def read_yaml(file_path: str) -> Dict[str, Any]:
    """
    读取YAML文件

    Args:
        file_path: YAML文件路径

    Returns:
        Dict[str, Any]: YAML内容
    """
    with open(file_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def format_file_size(size_bytes: int) -> str:
    """
    格式化文件大小

    Args:
        size_bytes: 文件大小(字节)

    Returns:
        str: 格式化后的文件大小
    """
    for unit in ["B", "KB", "MB", "GB"]:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} TB"

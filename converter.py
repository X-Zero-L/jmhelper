import re
import time
from pathlib import Path
from typing import List, Optional
import logfire
from PIL import Image


def sort_image_files(image_files: List[Path]) -> List[Path]:
    """
    按数字顺序排序图片文件

    Args:
        image_files: 图片文件路径列表

    Returns:
        List[Path]: 排序后的图片文件路径列表
    """

    def extract_number(filename: Path) -> int:
        try:
            file_name = filename.name
            match = re.search(r"(\d+)\.jpg$", file_name, re.IGNORECASE)
            if match:
                return int(match.group(1))
            return 0
        except Exception as e:
            logfire.warning(f"提取文件名数字失败 {filename}: {str(e)}")
            return 0

    return sorted(image_files, key=extract_number)


def convert_to_pdf(
    input_folder: str, output_folder: str, pdf_name: str
) -> Optional[str]:
    """
    将文件夹内的JPG图片转换为PDF

    Args:
        input_folder: 输入文件夹路径
        output_folder: 输出文件夹路径
        pdf_name: PDF文件名(不含扩展名)

    Returns:
        Optional[str]: 成功时返回PDF文件路径，失败时返回None
    """
    start_time = time.time()

    try:
        input_path = Path(input_folder)
        pdf_path = Path(output_folder)

        # 确保输出目录存在
        pdf_path.mkdir(parents=True, exist_ok=True)

        # 搜集所有JPG图片
        image_files = list(input_path.glob("**/*.jpg"))
        image_files.extend(list(input_path.glob("**/*.JPG")))

        if not image_files:
            logfire.warning(f"在 {input_folder} 中没有找到jpg图片")
            return None

        # 排序图片
        image_files = sort_image_files(image_files)
        logfire.info(f"找到 {len(image_files)} 张图片", image_files=image_files)

        # 打开第一张图片作为基础
        output = Image.open(image_files[0])
        if output.mode != "RGB":
            output = output.convert("RGB")

        # 准备其他图片
        sources = []
        for file in image_files[1:]:
            try:
                img = Image.open(file)
                if img.mode != "RGB":
                    img = img.convert("RGB")
                sources.append(img)
            except Exception as e:
                logfire.error(f"处理图片 {file} 时出错: {str(e)}", _exc_info=True)

        # 保存PDF
        pdf_file = pdf_path / f"{pdf_name}.pdf"
        output.save(
            str(pdf_file),
            "pdf",
            save_all=True,
            append_images=sources,
            resolution=100.0,
            quality=85,
        )

        end_time = time.time()
        run_time = end_time - start_time
        logfire.info(f"PDF生成完成: {pdf_file}，处理时间: {run_time:.2f}秒")

        return str(pdf_file)

    except Exception as e:
        logfire.error(f"PDF转换失败: {str(e)}", _exc_info=True)
        raise Exception(f"PDF转换失败: {str(e)}") from e

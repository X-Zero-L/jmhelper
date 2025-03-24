from pathlib import Path
from typing import Optional, Tuple

import logfire
from nonebot import get_plugin_config, require
from nonebot.plugin import PluginMetadata

logfire.configure(send_to_logfire="if-token-present", scrubbing=False)

require("nonebot_plugin_alconna")

from nonebot_plugin_alconna import Alconna, Args, on_alconna, Match
from nonebot.adapters import Bot, Event

import jmcomic
import yaml
from functools import partial
import asyncio
import concurrent.futures
import os

from .config import Config
from .downloader import download_album
from .converter import convert_to_pdf

__plugin_meta__ = PluginMetadata(
    name="JM助手",
    description="下载并转换漫画资源为PDF格式",
    usage="/jm [漫画ID]",
    config=Config,
)

config = get_plugin_config(Config)

download_command = on_alconna(
    Alconna(
        "/jm",
        Args["jmid", str],
    ),
    use_cmd_start=True,
    priority=5,
    block=True,
    aliases={"下载漫画", "下载本子", "/JM", "/Jm", "/jM"},
)

thread_pool_executor = concurrent.futures.ThreadPoolExecutor()

PLUGIN_DIR = Path(__file__).parent
OPTION_FILE = PLUGIN_DIR / "option.yml"
option = jmcomic.create_option_by_file(str(OPTION_FILE))

with open(OPTION_FILE, "r", encoding="utf-8") as f:
    option_dict = yaml.safe_load(f)
    BASE_DIR = option_dict["dir_rule"]["base_dir"]


async def process_download(jmid: str) -> Tuple[Optional[str], Optional[str]]:
    """
    处理下载和转换任务

    Args:
        jmid: 漫画ID

    Returns:
        Tuple[Optional[str], Optional[str]]: (PDF文件路径, 漫画名称)或错误情况下的(None, None)
    """
    try:
        album_pdf = os.path.join(BASE_DIR, f"{jmid}.pdf")
        if os.path.exists(album_pdf):
            logfire.info(f"PDF已存在: {album_pdf}")
            return album_pdf, jmid

        album, _ = await asyncio.get_event_loop().run_in_executor(
            thread_pool_executor, partial(download_album, jmid, option)
        )

        album_name = album.name
        album_dir = os.path.join(BASE_DIR, album_name)

        pdf_path = await asyncio.get_event_loop().run_in_executor(
            thread_pool_executor,
            partial(convert_to_pdf, album_dir, BASE_DIR, f"{jmid}"),
        )

        return pdf_path, jmid
    except Exception as e:
        logfire.error(f"处理漫画 {jmid} 失败: {str(e)}", exc_info=True)
        return None, None


@download_command.handle()
async def handle_download(bot: Bot, event: Event, jmid: Match[str]):
    jmid_value = jmid.result
    await download_command.send(f"正在处理 {jmid_value}，请稍等...")

    try:
        album_pdf, album_name = await process_download(jmid_value)

        if album_pdf and album_name:
            await bot.upload_group_file(
                group_id=event.group_id, file=album_pdf, name=f"{album_name}.pdf"
            )
        else:
            await download_command.send(f"处理 {jmid_value} 失败，请检查日志")

    except Exception as e:
        error_message = f"处理 {jmid_value} 时出错: {str(e)}"
        logfire.error(error_message, exc_info=True)
        await download_command.send(error_message)

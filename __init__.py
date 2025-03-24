from pathlib import Path
from typing import Optional, Tuple

import logfire
from nonebot import get_plugin_config, require
from nonebot.plugin import PluginMetadata

logfire.configure(send_to_logfire="if-token-present", scrubbing=False)

require("nonebot_plugin_alconna")
require("nonebot_plugin_htmlrender")
from nonebot_plugin_alconna import Alconna, Args, on_alconna, Match, UniMessage
from nonebot.adapters import Bot, Event

import jmcomic
import yaml
from functools import partial
import asyncio
import concurrent.futures
import os

from .config import Config
from .downloader import download_album, get_album_detail, search_albums
from .converter import convert_to_pdf
from .utils import merge_forward

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

meta_command = on_alconna(
    Alconna(
        "/jm_meta",
        Args["jmid", str],
    ),
    use_cmd_start=True,
    priority=5,
    block=True,
    aliases={"获取漫画详情", "/JM_META", "/Jm_Meta", "/jM_meta", "/jmt"},
)

search_command = on_alconna(
    Alconna(
        "/jm_search",
        Args["keyword", str],
    ),
    use_cmd_start=True,
    priority=5,
    block=True,
    aliases={"搜索漫画", "/JM_SEARCH", "/Jm_Search", "/jM_search", "/jms"},
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

    album_pdf = os.path.join(BASE_DIR, f"{jmid}.pdf")
    if os.path.exists(album_pdf):
        logfire.info(f"PDF已存在: {album_pdf}")
        return album_pdf, jmid

    album, _ = await asyncio.get_event_loop().run_in_executor(
        thread_pool_executor, partial(download_album, jmid, option)
    )

    album_name = album.name
    # 使用自带的插件，不再手动转换
    """
    album_dir = os.path.join(BASE_DIR, album_name)
    pdf_path = await asyncio.get_event_loop().run_in_executor(
        thread_pool_executor,
        partial(convert_to_pdf, album_dir, BASE_DIR, f"{jmid}"),
    )
    """
    # 检查文件大小，判断是否转换成功
    if os.path.exists(album_pdf):
        file_size = os.path.getsize(album_pdf)
        if file_size < 1024 * 1024:
            logfire.error(f"PDF文件过小: {file_size}")
            os.remove(album_pdf)
            raise Exception("下载失败，请重试")
    else:
        logfire.error(f"PDF文件不存在: {album_pdf}")
        raise Exception("下载失败，请重试")
    return album_pdf, album_name


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
        logfire.error(error_message, _exc_info=True)
        await download_command.send(error_message)


@meta_command.handle()
async def handle_meta(bot: Bot, event: Event, jmid: Match[str]):
    jmid_value = jmid.result
    await meta_command.send(f"正在获取 {jmid_value} 详情，请稍等...")

    try:
        album_info = await asyncio.get_event_loop().run_in_executor(
            thread_pool_executor, partial(get_album_detail, jmid_value, option)
        )

        if album_info:
            await meta_command.send(
                await merge_forward(
                    [await album_info.meta_img],
                    uid=event.user_id,
                    name=f"{jmid_value}详情",
                )
            )
        else:
            await meta_command.send(f"获取 {jmid_value} 详情失败，请检查日志")

    except Exception as e:
        error_message = f"获取 {jmid_value} 详情时出错: {str(e)}"
        logfire.error(error_message, _exc_info=True)
        await meta_command.send(error_message)


@search_command.handle()
async def handle_search(bot: Bot, event: Event, keyword: Match[str]):
    keyword_value = keyword.result
    await search_command.send(f"正在搜索 {keyword_value}，请稍等...")

    try:
        search_result = await asyncio.get_event_loop().run_in_executor(
            thread_pool_executor, partial(search_albums, keyword_value, option)
        )

        if search_result:
            await search_command.send(
                await merge_forward(
                    [search_result.str],
                    uid=event.user_id,
                    name=f"{keyword_value}搜索结果",
                )
            )
        else:
            await search_command.send(f"搜索 {keyword_value} 失败，请检查日志")

    except Exception as e:
        error_message = f"搜索 {keyword_value} 时出错: {str(e)}"
        logfire.error(error_message, _exc_info=True)
        await search_command.send(error_message)

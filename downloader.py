import jmcomic
import logfire
from typing import Tuple, Any


def download_album(jmid: str, option: Any) -> Tuple[Any, Any]:
    """
    下载漫画

    Args:
        jmid: 漫画ID
        option: jmcomic选项

    Returns:
        Tuple[Any, Any]: (album, downloader)对象
    """
    try:
        logfire.info(f"开始下载漫画 {jmid}")
        album, dler = jmcomic.download_album(jmid, option)
        logfire.info(f"漫画 {jmid} 下载完成，名称: {album.name}")
        return album, dler
    except Exception as e:
        logfire.error(f"下载漫画 {jmid} 失败: {str(e)}", exc_info=True)
        raise Exception(f"下载失败: {str(e)}") from e

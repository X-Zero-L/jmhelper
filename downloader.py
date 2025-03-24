import jmcomic
from jmcomic import JmOption
import logfire
from typing import Optional, Tuple, Any
from .model import AlbumInfo


def download_album(jmid: str, option: JmOption) -> Tuple[Any, Any]:
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
        logfire.error(f"下载漫画 {jmid} 失败: {str(e)}", _exc_info=True)
        raise Exception(f"下载失败: {str(e)}") from e


def get_album_detail(jmid: str, option: JmOption) -> Optional[AlbumInfo]:
    """
    获取漫画详情

    Args:
        jmid: 漫画ID
        option: jmcomic选项

    Returns:
        Optional[AlbumInfo]: 漫画详情对象，Pydantic模型
    """
    try:
        logfire.info(f"开始获取漫画 {jmid} 详情")
        client = option.build_jm_client()
        album = client.get_album_detail(jmid)
        album_info = AlbumInfo.from_jm_album(album)

        logfire.info(
            f"漫画 {jmid} 详情获取成功",
            album_id=album_info.album_id,
            name=album_info.name,
            authors=album_info.authors,
            tags=album_info.tags,
        )
        return album_info
    except Exception as e:
        logfire.error(f"获取漫画 {jmid} 详情失败: {str(e)}", _exc_info=True)
        return None

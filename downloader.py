import jmcomic
from jmcomic import JmOption
import logfire
from typing import Optional, Tuple, Any
from .model import AlbumInfo, SearchResult


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


def search_albums(
    keyword: str, option: JmOption, page: int = 1, limit: int | None = None
) -> SearchResult:
    """
    搜索漫画

    Args:
        keyword: 搜索关键词
        option: jmcomic选项
        page: 页码
        limit: 每页结果数量

    Returns:
        SearchResult: 搜索结果，Pydantic模型
    """
    try:
        logfire.info(f"搜索漫画: 关键词={keyword}, 页码={page}, 数量={limit}")
        client = option.build_jm_client()
        search_page = client.search_site(
            keyword,
            page=page,
        )

        albums_info = []
        total = 0

        # 如果是单个漫画的结果
        if search_page.is_single_album:
            album_detail = search_page.single_album
            albums_info.append(AlbumInfo.from_jm_album(album_detail))
            total = 1
        # 正常搜索结果
        else:
            total = (
                search_page.page_size
                if hasattr(search_page, "page_size")
                else len(search_page)
            )

            # 直接使用搜索结果中的基本信息
            for album_id, album_data in search_page:
                try:
                    # 从搜索结果创建简化版的AlbumInfo对象
                    album_info = AlbumInfo(
                        album_id=album_id,
                        name=album_data,
                    )
                    albums_info.append(album_info)
                    count += 1
                except Exception as e:
                    logfire.warning(f"处理漫画 {album_id} 信息失败: {str(e)}")

        search_result = SearchResult(
            query=keyword,
            total=len(albums_info),
            albums=albums_info,
            page=page,
            limit=limit,
            keyword=keyword,
        )

        logfire.info(f"搜索完成: 关键词={keyword}, 找到{total}个结果")
        return search_result
    except Exception as e:
        logfire.error(f"搜索漫画失败: {str(e)}", exc_info=True)
        return SearchResult(keyword=keyword, page=page, limit=limit)

import os
from pydantic import BaseModel, Field
from typing import Tuple, Any, List, Optional, Union
from jmcomic import JmAlbumDetail, JmModuleConfig
from nonebot_plugin_alconna import Image as AlconnaImage
from nonebot_plugin_htmlrender import template_to_pic
from pathlib import Path
import logfire

TEMPLATE_DIR = Path(os.path.dirname(os.path.abspath(__file__))) / "templates"


class AlbumInfo(BaseModel):
    """漫画信息模型"""

    cover: str = Field("", description="封面图片链接")
    album_id: str = Field(..., description="漫画ID")
    name: str = Field(..., description="漫画名称")
    author: str = Field("", description="主要作者")
    authors: List[str] = Field(default_factory=list, description="所有作者")
    page_count: int = Field(0, description="总页数")
    pub_date: str = Field("", description="发布日期")
    update_date: str = Field("", description="更新日期")
    likes: str = Field("0", description="点赞数")
    views: str = Field("0", description="浏览数")
    comment_count: int = Field(0, description="评论数")
    tags: List[str] = Field(default_factory=list, description="标签")
    episode_count: int = Field(0, description="章节数")
    works: List[str] = Field(default_factory=list, description="相关作品")

    @classmethod
    def from_jm_album(cls, album: JmAlbumDetail) -> "AlbumInfo":
        """从JmAlbumDetail对象创建AlbumInfo模型"""
        return cls(
            cover=f"https://{JmModuleConfig.DOMAIN_IMAGE_LIST[0]}/media/albums/{album.album_id}.jpg",
            album_id=album.album_id,
            name=album.name,
            author=album.author,
            authors=album.authors,
            page_count=album.page_count,
            pub_date=album.pub_date,
            update_date=album.update_date,
            likes=album.likes,
            views=album.views,
            comment_count=album.comment_count,
            tags=album.tags,
            episode_count=len(album.episode_list),
            works=album.works or [],
        )

    @property
    def meta(self) -> str:
        authors_str = "、".join(self.authors) if self.authors else "未知"
        display_tags = self.tags[:8]
        tags_str = "、".join(display_tags) if display_tags else "无标签"
        if len(self.tags) > 8:
            tags_str += f"...等{len(self.tags)}个标签"
        info_lines = [
            f"📚 {self.name} [{self.album_id}]",
            f"👤 作者: {authors_str}",
            f"📅 发布: {self.pub_date}",
            f"🔄 更新: {self.update_date}",
            f"📊 统计: {self.views}浏览 | {self.likes}喜欢 | {self.comment_count}评论",
            f"📖 页数: {self.page_count}页 (共{self.episode_count}章)",
            f"🏷️ 标签: {tags_str}",
        ]

        if self.works:
            works_str = "、".join(self.works) if self.works else "无关联作品"

            info_lines.append(f"🔗 系列: {works_str}")

        info_lines.append(f"\n💾 发送 /jm {self.album_id} 下载此漫画")

        return "\n".join(info_lines)

    @property
    async def meta_img(self) -> Union[AlconnaImage, str]:
        """
        生成漫画信息的图片版本

        Returns:
            Union[AlconnaImage, str]: 成功时返回AlconnaImage对象，失败时返回文本版本
        """
        try:
            pic_bytes = await template_to_pic(
                template_path=str(TEMPLATE_DIR),
                template_name="album_meta.html",
                templates={"album": self.model_dump()},
                pages={
                    "viewport": {"width": 1100, "height": 500},
                },
            )

            return AlconnaImage(raw=pic_bytes)
        except Exception as e:
            logfire.error(f"生成漫画信息图片失败: {str(e)}", _exc_info=True)
            return self.meta

    @property
    def brief_meta(self) -> str:
        authors_str = "、".join(self.authors[:2]) if self.authors else "未知"
        if len(self.authors) > 2:
            authors_str += f"...等{len(self.authors)}位作者"

        tags_preview = "、".join(self.tags[:3]) if self.tags else "无标签"
        if len(self.tags) > 3:
            tags_preview += "..."

        return f"📚 {self.name} [{self.album_id}]\n👤 {authors_str} | 📖 {self.page_count}页 | 🏷️ {tags_preview}"

    # id:name
    @property
    def id_name(self) -> str:
        return f"{self.album_id}:{self.name}"


class SearchResult(BaseModel):
    """搜索结果模型"""

    query: str = Field("", description="搜索关键词")
    total: int = Field(0, description="总结果数")
    albums: List[AlbumInfo] = Field(
        default_factory=list, description="搜索到的漫画列表"
    )
    page: int = Field(1, description="当前页码")
    limit: int | None = Field(None, description="每页结果数")
    keyword: str = Field("", description="搜索关键词")

    def format_search_results(self) -> str:
        detail_lines = []

        detail_lines.extend(
            f"{i}. {album.id_name}" for i, album in enumerate(self.albums, start=1)
        )
        footer = f"\n💡 发送 /jm [ID] 下载指定漫画"
        footer += f"\n🔍 发送 /jms {self.query} {self.page+1} 搜索下一页"

        return "\n\n".join(detail_lines) + footer

    @property
    def str(self) -> str:
        return self.format_search_results()

    @property
    async def meta_img(self) -> Union[AlconnaImage, str]:
        """
        生成搜索结果的图片版本

        Returns:
            Union[AlconnaImage, str]: 成功时返回AlconnaImage对象，失败时返回文本版本
        """
        try:
            pic_bytes = await template_to_pic(
                template_path=str(TEMPLATE_DIR),
                template_name="search_result.html",
                templates={"search": self.model_dump()},
                pages={"viewport": {"width": 720, "height": 1}},
            )

            return AlconnaImage(raw=pic_bytes)
        except Exception as e:
            logfire.error(f"生成搜索结果图片失败: {str(e)}", _exc_info=True)
            return self.format_search_results()

"""
Bilibili API 封装模块
处理视频信息获取、字幕下载等操作
"""
import re
import asyncio
from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from bilibili_api import video, favorite_list, cheese, user, Credential
from bilibili_api.exceptions import ResponseCodeException


@dataclass
class VideoInfo:
    """视频信息数据类"""
    bvid: str
    avid: int
    title: str
    description: str
    duration: int  # 秒
    upload_time: str
    up_name: str
    up_id: int
    tags: List[str]
    cover_url: str
    view_count: int
    like_count: int
    coin_count: int


def aid_to_bvid(aid: int) -> str:
    """
    AID转BV号
    算法来自：https://www.zhihu.com/question/381784377/answer/1099438784
    """
    table = 'fZodR9XQDSUm21yCkr6zBqiveYah8bt4xsWpHnJE7jL5VG3guMTKNPAwcF'
    tr = {c: i for i, c in enumerate(table)}
    s = [11, 10, 3, 8, 4, 6]
    xor = 177451812
    add = 8728348608

    aid = (aid ^ xor) + add
    r = list('BV1  4 1 7  ')
    for i in range(6):
        r[s[i]] = table[aid // (58 ** i) % 58]
    return ''.join(r)


@dataclass
class SubtitleItem:
    """字幕条目"""
    from_time: float  # 开始时间（秒）
    to_time: float    # 结束时间（秒）
    content: str      # 内容


@dataclass
class SubtitleInfo:
    """字幕信息"""
    lang: str                 # 语言代码
    lang_name: str           # 语言名称
    subtitle_type: str       # 字幕类型：ai | upload | cc
    items: List[SubtitleItem] # 字幕内容列表


class BilibiliClient:
    """Bilibili API 客户端"""

    def __init__(self, credential: Optional[Credential] = None):
        """
        初始化客户端

        Args:
            credential: 凭证（可选，用于需要登录的接口）
        """
        self.credential = credential

    @staticmethod
    def _extract_title_entities(title: str) -> List[str]:
        """从视频标题中提取实体标签

        规则：
        1. 提取英文单词（含连字符，如ChatGPT、AI-Agent），去重取前2个
        2. 英文单词需>=2字符，排除常见停用词
        """
        if not title:
            return []

        stopwords = {'the', 'of', 'in', 'on', 'at', 'to', 'for', 'and', 'or',
                      'is', 'it', 'no', 'by', 'vs', 'up', 'an', 'a', 'my'}

        # 提取英文单词/短语（含连字符的复合词如GPT-4、TypeScript）
        words = re.findall(r'[A-Za-z][A-Za-z0-9\-]*[A-Za-z0-9]|[A-Za-z]', title)

        seen = set()
        entities = []
        for w in words:
            w_lower = w.lower()
            if len(w) >= 2 and w_lower not in stopwords and w_lower not in seen:
                seen.add(w_lower)
                entities.append(w)

        return entities[:2]

    @staticmethod
    def extract_bvid(url: str) -> Optional[str]:
        """
        从URL中提取BV号

        Args:
            url: B站视频URL

        Returns:
            BV号或None
        """
        # 匹配BV号 (BV + 10位字母数字)
        pattern = r'BV[a-zA-Z0-9]{10}'
        match = re.search(pattern, url)
        if match:
            return match.group(0)

        # 匹配短链接 b23.tv
        if 'b23.tv' in url:
            # 需要额外处理短链接
            return None

        return None

    @staticmethod
    def extract_favorite_id(url: str) -> Optional[int]:
        """
        从收藏夹URL中提取media_id

        Args:
            url: B站收藏夹URL或直接输入的ID

        Returns:
            收藏夹ID或None
        """
        # 如果是纯数字，直接返回
        if url.isdigit():
            return int(url)

        # 从URL中提取fid参数
        patterns = [
            r'fid=(\d+)',  # 匹配 ?fid=123456 格式
            r'favlist\?(\d+)',  # 匹配 favlist?123456 格式
            r'media_id=(\d+)',  # 匹配 media_id=123456 格式
        ]

        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return int(match.group(1))

        return None

    @staticmethod
    def extract_course_id(url: str) -> Optional[tuple]:
        """
        从课程URL中提取ID

        Args:
            url: B站课程URL或直接输入的SS/EP号

        Returns:
            (type, id) 元组，type为'ss'或'ep'，或None
        """
        # 如果是纯数字，当作SS号
        if url.isdigit():
            return ('ss', int(url))

        # 匹配ss开头的ID格式
        ss_match = re.search(r'ss(\d+)', url, re.IGNORECASE)
        if ss_match:
            return ('ss', int(ss_match.group(1)))

        # 从cheese链接中提取
        patterns = [
            (r'cheese/play/ss(\d+)', 'ss'),
            (r'cheese/play/ep(\d+)', 'ep'),
            (r'cheese/ep(\d+)', 'ep'),
        ]

        for pattern, id_type in patterns:
            match = re.search(pattern, url)
            if match:
                return (id_type, int(match.group(1)))

        return None

    async def resolve_season_id(self, course_url_or_id: str) -> Optional[int]:
        """
        从课程URL或ID中解析出SS号（赛季/课程ID）

        Args:
            course_url_or_id: 课程URL、SS号或EP号

        Returns:
            SS号或None
        """
        result = self.extract_course_id(course_url_or_id)
        if not result:
            return None

        id_type, id_value = result
        if id_type == 'ss':
            return id_value

        # EP号需要通过API获取对应的SS号
        try:
            ep = cheese.CheeseVideo(epid=id_value, credential=self.credential)
            course_list = await ep.get_cheese()
            season_id = await course_list.get_season_id()
            if season_id:
                print(f"EP{id_value} 属于课程 SS{season_id}")
                return season_id
            else:
                print(f"警告: 无法从EP{id_value}获取课程ID，尝试直接使用EP号")
                return id_value
        except Exception as e:
            print(f"解析EP号失败: {e}，尝试直接使用EP号作为课程ID")
            return id_value

    async def get_course_videos(self, ss_id: int) -> List[Dict[str, Any]]:
        """
        获取付费课程下的所有视频列表

        Args:
            ss_id: 课程SS号

        Returns:
            视频列表，每个元素包含epid, title, up_name等字段
        """
        try:
            course = cheese.CheeseList(season_id=ss_id, credential=self.credential)
            all_videos = []

            # 获取课程信息
            course_info = await course.get_meta()
            title = course_info.get('title', '未知课程')
            # 尝试不同的字段获取UP主信息
            up_info = course_info.get('up_info', {}) or course_info.get('upper', {})
            up_name = up_info.get('name', '') or course_info.get('author', '')
            up_id = up_info.get('mid', 0) or course_info.get('uid', 0)

            # 如果up_name为空但有up_id，通过用户API获取名称
            if not up_name and up_id > 0:
                try:
                    u = user.User(uid=up_id, credential=self.credential)
                    user_info = await u.get_user_info()
                    up_name = user_info.get('name', '')
                except Exception as e:
                    print(f"获取UP主信息失败: {e}")

            print(f"正在获取课程: {title}，UP主: {up_name}")

            # 获取所有视频列表
            episodes = await course.get_list()
            for idx, episode in enumerate(episodes, 1):
                ep_meta = await episode.get_meta()
                title = ep_meta.get('title', '未知标题')
                epid = ep_meta.get('id', 0)
                aid = ep_meta.get('aid', 0)
                bvid = aid_to_bvid(aid) if aid else ''
                cover = ep_meta.get('cover', '')
                duration = ep_meta.get('duration', 0)
                play_count = ep_meta.get('play', 0)
                index = ep_meta.get('index', str(idx))

                print(f"正在解析第{idx}/{len(episodes)}集: {title} (EP{epid})")

                if epid:
                    all_videos.append({
                        'epid': epid,
                        'bvid': bvid,
                        'title': title,
                        'up_name': up_name,
                        'up_id': up_id,
                        'cover_url': cover,
                        'duration': duration,
                        'play_count': play_count,
                        'index': index
                    })

                await asyncio.sleep(0.5)  # 请求间隔

            print(f"共获取到{len(all_videos)}个课程视频")
            return all_videos

        except Exception as e:
            print(f"获取课程视频失败: {e}")
            import traceback
            traceback.print_exc()
            return []

    async def get_course_video_info(self, epid: int) -> VideoInfo:
        """
        获取课程视频的详细信息

        Args:
            epid: 课程视频EP号

        Returns:
            VideoInfo对象
        """
        ep = cheese.CheeseVideo(epid=epid, credential=self.credential)
        ep_meta = await ep.get_meta()

        # 获取CID
        cid = await ep.get_cid()

        # 获取统计信息（课程视频没有点赞投币等数据，留空）
        stat = {
            'view': ep_meta.get('play', 0),
            'like': 0,
            'coin': 0
        }

        # 构造VideoInfo
        return VideoInfo(
            bvid=ep_meta.get('bvid', aid_to_bvid(ep_meta.get('aid', 0))),
            avid=ep_meta.get('aid', 0),
            title=ep_meta.get('title', ''),
            description='',  # 课程视频没有简介
            duration=ep_meta.get('duration', 0),
            upload_time=str(ep_meta.get('release_date', '')),
            up_name='',  # 已经在课程层面获取，这里不需要重复
            up_id=0,
            tags=[],
            cover_url=ep_meta.get('cover', ''),
            view_count=stat.get('view', 0),
            like_count=stat.get('like', 0),
            coin_count=stat.get('coin', 0)
        )

    async def get_course_subtitle_list(self, epid: int) -> List[Dict[str, Any]]:
        """
        获取课程视频的字幕列表

        Args:
            epid: 课程视频EP号

        Returns:
            字幕列表
        """
        try:
            ep = cheese.CheeseVideo(epid=epid, credential=self.credential)
            # 获取aid转换为bvid，使用普通视频的方式获取字幕
            aid = await ep.get_aid()
            bvid = aid_to_bvid(aid)
            v = video.Video(bvid=bvid, credential=self.credential)
            pages = await v.get_pages()
            if not pages:
                return []

            cid = pages[0].get('cid')
            if not cid:
                return []

            player_info = await v.get_player_info(cid=cid)
            subtitle_info = player_info.get('subtitle', {})
            subtitles = subtitle_info.get('subtitles', [])
            return subtitles
        except Exception as e:
            print(f"获取课程字幕列表失败: {e}")
            return []

    async def get_video_info(self, bvid: str) -> VideoInfo:
        """
        获取视频详细信息

        Args:
            bvid: BV号

        Returns:
            VideoInfo对象

        Raises:
            ResponseCodeException: API请求失败
        """
        v = video.Video(bvid=bvid, credential=self.credential)
        info = await v.get_info()

        # 获取UP主信息
        up_name = info.get('owner', {}).get('name', '')
        up_id = info.get('owner', {}).get('mid', 0)

        # 获取标签：API取3个 + 标题提炼2个实体，去重合并
        api_tags = []
        try:
            tag_list = await v.get_tags()
            api_tags = [t.get('tag_name', '') for t in tag_list if t.get('tag_name')][:3]
        except:
            api_tags = info.get('dynamic', '').split('#') if info.get('dynamic') else []
            api_tags = [t.strip() for t in api_tags if t.strip()][:3]

        title_tags = self._extract_title_entities(info.get('title', ''))

        # 合并去重（不区分大小写）：标题实体优先
        seen_lower = set()
        tags = []
        for t in title_tags + api_tags:
            if t.lower() not in seen_lower:
                seen_lower.add(t.lower())
                tags.append(t)

        # 获取统计数据
        stat = info.get('stat', {})

        return VideoInfo(
            bvid=bvid,
            avid=info.get('aid', 0),
            title=info.get('title', ''),
            description=info.get('desc', ''),
            duration=info.get('duration', 0),
            upload_time=info.get('pubdate', ''),
            up_name=up_name,
            up_id=up_id,
            tags=tags,
            cover_url=info.get('pic', '').replace('http://', 'https://'),
            view_count=stat.get('view', 0),
            like_count=stat.get('like', 0),
            coin_count=stat.get('coin', 0)
        )

    async def get_subtitle_list(self, bvid: str) -> List[Dict[str, Any]]:
        """
        获取视频的字幕列表

        Args:
            bvid: BV号

        Returns:
            字幕列表
        """
        v = video.Video(bvid=bvid, credential=self.credential)

        try:
            # 首先获取CID列表
            pages = await v.get_pages()
            if not pages:
                print("无法获取视频分页信息")
                return []

            # 使用第一个CID
            cid = pages[0].get('cid')
            if not cid:
                print("无法获取视频CID")
                return []

            # 获取播放器信息（包含字幕URL）
            player_info = await v.get_player_info(cid=cid)
            subtitle_info = player_info.get('subtitle', {})
            subtitles = subtitle_info.get('subtitles', [])

            return subtitles
        except Exception as e:
            print(f"获取字幕列表失败: {e}")
            return []

    async def get_subtitle_content(self, subtitle_url: str) -> List[SubtitleItem]:
        """
        获取字幕内容

        Args:
            subtitle_url: 字幕JSON URL

        Returns:
            字幕条目列表
        """
        import aiohttp

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(subtitle_url) as response:
                    data = await response.json()

                    items = []
                    for body in data.get('body', []):
                        item = SubtitleItem(
                            from_time=body.get('from', 0),
                            to_time=body.get('to', 0),
                            content=body.get('content', '').strip()
                        )
                        if item.content:  # 过滤空内容
                            items.append(item)

                    return items
        except Exception as e:
            print(f"获取字幕内容失败: {e}")
            return []

    async def get_best_subtitle(self, bvid: str, preferred_type: str = "ai") -> Optional[SubtitleInfo]:
        """
        获取最佳字幕

        优先级: upload > ai > cc
        中文(zh/ai-zh)优先于其他语言

        Args:
            bvid: BV号
            preferred_type: 首选类型

        Returns:
            字幕信息或None
        """
        subtitles = await self.get_subtitle_list(bvid)

        if not subtitles:
            return None

        # 语言优先级：中文优先
        def lang_priority(lan):
            if lan == 'zh': return 0      # 人工中文
            if lan == 'ai-zh': return 1   # AI中文
            if lan.startswith('zh'): return 2  # 其他中文
            if lan == 'en': return 3      # 英文
            return 4

        # 类型优先级：upload > ai > cc
        def type_priority(sub):
            if sub.get('is_user_upload', False): return 0
            if sub.get('is_ai', False): return 1
            return 2

        best_subtitle = None
        best_score = float('inf')

        for sub in subtitles:
            lan = sub.get('lan', '')
            lp = lang_priority(lan)
            tp = type_priority(sub)

            # 综合评分：语言权重更高
            score = lp * 10 + tp

            # 如果指定了类型且匹配，加权
            sub_type_code = "cc"
            if sub.get('is_ai', False):
                sub_type_code = "ai"
            elif sub.get('is_user_upload', False):
                sub_type_code = "upload"

            if sub_type_code == preferred_type:
                score -= 5  # 匹配首选类型加分

            if score < best_score:
                best_score = score
                best_subtitle = sub

        if not best_subtitle:
            return None

        # 获取字幕内容
        subtitle_url = best_subtitle.get('subtitle_url', '')
        if not subtitle_url:
            return None

        # 拼接URL
        if not subtitle_url.startswith('http'):
            subtitle_url = f"https:{subtitle_url}"

        items = await self.get_subtitle_content(subtitle_url)

        if not items:
            return None

        # 确定字幕类型（根据 is_ai/is_user_upload 标志，或从语言代码推断）
        lan = best_subtitle.get('lan', '')
        sub_type = "cc"
        if best_subtitle.get('is_ai', False) or lan.startswith('ai-'):
            sub_type = "ai"
        elif best_subtitle.get('is_user_upload', False) or lan == 'zh':
            sub_type = "upload"

        return SubtitleInfo(
            lang=lan,
            lang_name=best_subtitle.get('lan_doc', ''),
            subtitle_type=sub_type,
            items=items
        )

    async def get_favorite_videos(self, media_id: int) -> List[Dict[str, Any]]:
        """
        获取收藏夹下的所有视频列表

        Args:
            media_id: 收藏夹ID

        Returns:
            视频列表，每个元素包含bvid, title, up_name等字段
        """
        try:
            fav = favorite_list.FavoriteList(media_id=media_id, credential=self.credential)
            all_videos = []
            pn = 1
            ps = 50  # 最大每页50条，减少请求次数

            while True:
                print(f"正在获取收藏夹第{pn}页视频...")
                # 传入页码参数
                result = await fav.get_content(page=pn)
                videos = result.get('medias', [])

                if not videos:
                    break

                # 格式化视频信息，只保留需要的字段
                for video in videos:
                    # 只处理视频类型（type=2），忽略收藏夹里的其他内容
                    if video.get('type') == 2:
                        all_videos.append({
                            'bvid': video.get('bvid', ''),
                            'title': video.get('title', ''),
                            'up_name': video.get('upper', {}).get('name', ''),
                            'up_id': video.get('upper', {}).get('mid', 0),
                            'cover_url': video.get('cover', ''),
                            'duration': video.get('duration', 0),
                            'play_count': video.get('cnt_info', {}).get('play', 0),
                            'fav_time': video.get('fav_time', 0)
                        })

                # 检查是否还有下一页
                if not result.get('has_more', False):
                    break

                pn += 1
                await asyncio.sleep(2)  # 增加请求间隔到2秒，避免触发反爬

            print(f"共获取到{len(all_videos)}个视频")
            return all_videos

        except Exception as e:
            print(f"获取收藏夹视频失败: {e}")
            return []

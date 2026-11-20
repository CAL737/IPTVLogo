# IPTVLogo · iptv.m3u

个人维护的 IPTV 直播源播放列表，频道带台标与 EPG 节目单信息，尽量保持「打开即用」。

> 账号被 Gitee 封了…… 来 GitHub 避难。

## 订阅地址

| 用途 | 地址 |
| --- | --- |
| GitHub 原始地址（推荐） | `https://raw.githubusercontent.com/CAL737/IPTVLogo/main/iptv.m3u` |
| 国内加速（gh-proxy） | `https://gh-proxy.com/raw.githubusercontent.com/CAL737/IPTVLogo/main/iptv.m3u` |
| jsDelivr CDN | `https://cdn.jsdelivr.net/gh/CAL737/IPTVLogo@main/iptv.m3u` |

把上面任意一条作为「远程播放列表 / M3U 订阅」导入播放器即可，每次打开都会拉取最新版本。

## 频道分组

| 分组 | 条数 | 内容 |
| --- | --- | --- |
| 凤凰卫视 | 3 | 凤凰卫视中文台、资讯台、香港台 |
| 4K频道 | 1 | 翡翠台（4K） |
| 香港频道 | 15 | 翡翠台、明珠台、TVB Plus、无线新闻、HOY 76/77/78、ViuTV/ViuTVsix、华丽翡翠台、功夫台、TVB 星河、娱乐新闻台等 |
| TVBUSA | 3 | TVB Drama、TVB 1、TVB J1 |
| 广东广播电视台 | 2 | 广东卫视、广东珠江 |
| 测试频道 | 1 | 4K / HEVC / EAC3 测试信号 |
| WebVTT | 3 | 翡翠台、TVB Plus、明珠台（外挂 WebVTT 字幕版） |

## 文件格式

标准 M3U 扩展格式，兼容绝大多数播放器：

```m3u
#EXTM3U url-tvg="https://epg.cdn.loc.cc/xml"

#香港频道
#EXTINF:-1 tvg-id="189" tvg-name="翡翠台" tvg-logo="台标地址" group-title="香港频道",翡翠台 81（1080i）
https://example.com/live/jade.m3u8
```

- `group-title`：分组名，与文件中的 `#分组名` 注释一一对应
- `tvg-name`：频道标准名，供 EPG 匹配节目单
- `tvg-logo`：台标图片，图床为本仓库配套的 [CAL737/TVlogo](https://github.com/CAL737/TVlogo)
- 显示名后缀标注清晰度（`1080i` / `720P` / `4K`）；失效但仍保留的会标 `（无法播放）`

## EPG 节目单

播放列表中已内置：

```text
url-tvg="https://epg.cdn.loc.cc/xml"
```

播放器（TiviMate、Kodi、DIYP 等）会自动读取；手动配置时填入同一地址即可。

## 播放器推荐

| 平台 | 播放器 |
| --- | --- |
| Windows / macOS / Linux | VLC、PotPlayer、mpv |
| Android / Android TV | TiviMate、DIYP、Televizo |
| iOS / tvOS | iPlayTV、Aptv |
| Kodi | PVR IPTV Simple Client |

## 分支说明

- `main`：稳定列表，只收录经过人工确认的频道
- `test`：实验分支，用于批量导入、探测与验证新源，内容可能随时变动

## 失效反馈

直播源失效是常态，欢迎提交 [Issue](https://github.com/CAL737/IPTVLogo/issues)，说明「分组 + 频道名 + 现象（黑屏 / 无法连接 / 无声音）」，我会尽快替换或下架。

## 免责声明

本项目仅收集互联网上公开可访问的直播流地址，不存储、不转码、不分发任何音视频内容，版权归各电视台及内容提供方所有。所有地址仅供个人学习与测试使用，请于下载后 24 小时内删除；因使用本列表产生的任何后果由使用者自行承担。如权利人认为内容侵权，请提交 Issue，将立即移除相关条目。

## 许可证

[GPL-2.0](./LICENSE)

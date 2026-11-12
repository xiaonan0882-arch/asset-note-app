#!/usr/bin/env python3
"""Public RSS market headlines; only verified recent items enter today's feed."""
import datetime as dt, email.utils, json, pathlib, urllib.request, xml.etree.ElementTree as ET
from urllib.parse import quote
NOW=dt.datetime.now(dt.timezone.utc)
QUERIES=[("中国消费","中国","消费 零售 食品饮料 茶饮"),("科技","全球","AI 半导体 NVIDIA"),("宏观","中国","中国 央行 经济 数据"),("全球","全球","美联储 美国 经济"),("大宗商品","全球","黄金 原油")]
items=[]
for theme,region,q in QUERIES:
    url="https://news.google.com/rss/search?q="+quote(q+" when:1d")+"&hl=zh-CN&gl=CN&ceid=CN:zh-Hans"
    try:
        req=urllib.request.Request(url,headers={"User-Agent":"Mozilla/5.0 AssetNoteResearch/1.0"})
        with urllib.request.urlopen(req,timeout=18) as response: xml=response.read()
        root=ET.fromstring(xml)
        for it in root.findall("./channel/item")[:8]:
            title=(it.findtext("title") or "").strip()
            link=(it.findtext("link") or "").strip()
            published=it.findtext("pubDate") or ""
            try: date=email.utils.parsedate_to_datetime(published).astimezone(dt.timezone.utc)
            except (ValueError,TypeError): continue
            age=(NOW-date).total_seconds()
            if not (0<=age<=36*3600) or not title or not link: continue
            source=it.findtext("source") or "Google News"
            items.append(dict(theme=theme,region=region,title=title,summary="",why="",source=source,url=link,publishedAt=date.isoformat(),freshness="recent"))
    except Exception as e:
        print("RSS fetch failed for",theme,str(e))
seen=set();out=[]
for it in sorted(items,key=lambda v:v["publishedAt"],reverse=True):
    key=it["title"].lower()
    if key in seen: continue
    seen.add(key);out.append(it)
path=pathlib.Path("data/daily-brief.json")
old={}
if path.exists():
    try:old=json.loads(path.read_text(encoding="utf-8"))
    except Exception:pass
data={"asOf":NOW.isoformat(),"title":"每日市场研究","freshnessRule":"仅展示最近36小时的新闻；来源及发布时间以原文为准。","items":out[:35],"latestData":old.get("latestData",[]),"status":"ok" if out else "no_recent_items"}
path.parent.mkdir(parents=True,exist_ok=True)
path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print("Saved",len(out),"recent headlines")

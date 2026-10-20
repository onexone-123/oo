"""Global discovery: X third-party snapshots; English reporting signals elsewhere.

Reporting signals are never described as official rankings or platform-wide popularity.
"""
import concurrent.futures
import datetime as dt
import email.utils
import html.parser
import http.client
import re
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

UTC = dt.timezone.utc
GLOBAL_KEYS = ('instagram', 'facebook', 'x', 'tiktok')
SOURCES = {
    'instagram': 'https://www.instagram.com/explore/',
    'facebook': 'https://www.facebook.com/',
    'x': 'https://trends24.in/',
    'tiktok': 'https://ads.tiktok.com/creative/creativeCenter/trends?LanguageId=1',
}
TRUSTED = ('bbc.com','bbc.co.uk','reuters.com','apnews.com','theguardian.com',
           'cnn.com','nbcnews.com','cbsnews.com','abcnews.go.com','abc.net.au',
           'theverge.com','techcrunch.com','wired.com','people.com',
           'today.com','usatoday.com','independent.co.uk','businessinsider.com',
           'socialmediatoday.com','marketingdive.com','adweek.com','adage.com',
           'eonline.com','rollingstone.com','billboard.com','variety.com',
           'elle.com','vogue.com','cosmopolitan.com','glamour.com',
           'about.fb.com','newsroom.tiktok.com','hollywoodreporter.com',
           'nytimes.com','socialmediaexaminer.com')

def fetch(url):
    req=urllib.request.Request(url, headers={'User-Agent':'Mozilla/5.0 (compatible; OperaRadar/1.0)', 'Accept-Encoding':'identity'})
    with urllib.request.urlopen(req, timeout=20) as response:
        try: raw=response.read(3_000_000)
        except http.client.IncompleteRead as error: raw=error.partial
    return raw.decode('utf-8', errors='replace')

def trusted(url):
    try:
        host=urllib.parse.urlparse(url).hostname or ''
        return any(host==d or host.endswith('.'+d) for d in TRUSTED)
    except ValueError: return False

def parse_feed(text, key, now):
    root=ET.fromstring(text)
    channel=root.find('channel')
    if channel is None: raise ValueError('Invalid news feed')
    rows=[]
    for item in channel.findall('item'):
        title=(item.findtext('title') or '').strip()
        source=item.find('source')
        publisher=source.text if source is not None else ''
        source_url=source.get('url','') if source is not None else ''
        link=(item.findtext('link') or '').strip()
        if not trusted(source_url) or not link.startswith('https://'): continue
        if publisher and title.endswith(' - '+publisher): title=title[:-len(publisher)-3]
        if not re.search(r'\b'+key+r'\b',title,re.I): continue
        try: published=email.utils.parsedate_to_datetime(item.findtext('pubDate')).astimezone(UTC)
        except (ValueError,TypeError,AttributeError): continue
        if not now-dt.timedelta(hours=72)<=published<=now+dt.timedelta(hours=1): continue
        rows.append({'title':title[:240], 'url':link, 'heat':'', 'publisher':publisher,
                     'feed_time':published.isoformat(), 'source_url':source_url})
    return rows

class XParser(html.parser.HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.snapshots=[]; self.timestamp=None; self.listing=False
        self.link=False; self.title=[]; self.row=None
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if 'data-timestamp' in a:
            try: self.timestamp=float(a['data-timestamp'])
            except ValueError: self.timestamp=None
        if tag=='ol' and 'trend-card__list' in a.get('class','').split():
            self.listing=True; self.snapshots.append({'timestamp':self.timestamp,'items':[],'complete':False})
        if self.listing and tag=='li': self.row={'heat':''}
        if self.listing and tag=='a' and 'trend-link' in a.get('class','').split():
            self.link=True; self.title=[]
        if self.listing and tag=='span' and 'data-count' in a and self.row is not None:
            self.row['heat']=a['data-count']
    def handle_data(self,text):
        if self.link:self.title.append(text)
    def handle_endtag(self,tag):
        if tag=='a' and self.link:
            self.link=False
            if self.row is not None:self.row['title']=''.join(self.title).strip()
        if tag=='li' and self.listing and self.row:
            if self.row.get('title'):self.snapshots[-1]['items'].append(self.row)
            self.row=None
        if tag=='ol' and self.listing:
            self.snapshots[-1]['complete']=True
            self.listing=False

def parse_x(text,now):
    parser=XParser();parser.feed(text)
    usable=[s for s in parser.snapshots if s['complete'] and s['timestamp'] and s['items'] and
            (now-dt.timedelta(hours=36)).timestamp()<=s['timestamp']<=(now+dt.timedelta(hours=1)).timestamp()]
    if not usable:raise ValueError('No recent timestamped X snapshot')
    snapshot=max(usable,key=lambda s:s['timestamp'])
    rows=[];seen=set()
    for original_rank,item in enumerate(snapshot['items'],1):
        if item['title'] in seen:continue
        seen.add(item['title'])
        rows.append({**item,'rank':original_rank,'url':'https://x.com/search?'+urllib.parse.urlencode({'q':item['title'],'src':'trend_click'})})
    return {'status':'ok','items':rows[:30], 'collected_at':now.isoformat(),
            'upstream_time':dt.datetime.fromtimestamp(snapshot['timestamp'],UTC).isoformat(),
            'kind':'third_party_trends','region':'全球 · 保留榜单原语言',
            'source_name':'Trends24','source_url':SOURCES['x'],
            'note':'第三方记录的 X 全球趋势快照，非 X 官方接口；条目按来源顺序，热度按来源口径。'}

def get_global_platform(key, now=None, request=fetch):
    now=now or dt.datetime.now(UTC)
    if key=='x':return parse_x(request(SOURCES[key]),now)
    if key not in GLOBAL_KEYS:raise ValueError('Unsupported platform')
    query=f'{key} when:3d'
    def edition(country):
        url='https://news.google.com/rss/search?'+urllib.parse.urlencode({'q':query,'hl':'en-'+country,'gl':country,'ceid':country+':en'})
        return parse_feed(request(url),key,now)
    rows=[];errors=[];success=0
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
        for future in concurrent.futures.as_completed([pool.submit(edition,c) for c in ('US','GB')]):
            try:rows.extend(future.result());success+=1
            except Exception as error:errors.append(type(error).__name__)
    if not success:raise RuntimeError('News feeds unavailable: '+', '.join(errors))
    unique={re.sub(r'\W+','',x['title']).lower():x for x in rows}
    rows=sorted(unique.values(),key=lambda x:x['feed_time'],reverse=True)[:20]
    for i,row in enumerate(rows,1):row['rank']=i
    return {'status':'ok','items':rows,'collected_at':now.isoformat(),
            'kind':'reported_signals','region':'全球报道 · 英文优先','source_name':'英文媒体报道',
            'source_url':SOURCES[key],'partial':bool(errors),
            'note':'近 72 小时订阅收录的英文平台动态，可能包含旧文重新收录；按订阅时间排序，不是官方热榜。',
            'empty_reason':'近 72 小时暂未发现符合来源筛选条件的报道。' if not rows else ''}

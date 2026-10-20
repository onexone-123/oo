"""Daily public Brandstar discovery. No login, full-text republication or invented analysis."""
import datetime as dt
import html.parser
import json
import pathlib
import re
import sys
import urllib.parse
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUTPUT = ROOT / 'docs/brandstar.json'
ORIGIN = 'https://www.brandstar.com.cn'
TZ = dt.timezone(dt.timedelta(hours=8))
RULES = {
    'IP 合作': ['联名', '授权', 'IP 合作', 'IP合作', '携手', '合作伙伴', '音乐人', '艺术家'],
    '社群经营': ['社群', '跑者', '会员', '社区', '用户关系'],
    '内容传播': ['叙事', '内容', '传播', '营销', '短片'],
    '零售体验': ['门店', '零售', '旗舰店', '体验', '快闪'],
}

def fetch(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'OperaRadar/1.0 (+public editorial discovery)', 'Accept-Encoding': 'identity'})
    with urllib.request.urlopen(req, timeout=25) as response:
        raw = response.read(3_000_000)
    # Large hydration scripts can exceed the size cap; only the completed public main content is used.
    text = raw.decode('utf-8', errors='replace')
    end = text.lower().find('</main>')
    if end < 0 or '\ufffd' in text[:end]:
        raise ValueError('Incomplete or invalid public main content')
    return text

class Page(html.parser.HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.meta, self.links, self.dates, self.body = {}, [], [], []
        self.in_main = False
        self.content_depth = 0
        self.script = False
        self.script_text = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == 'main': self.in_main = True
        if tag == 'meta': self.meta[a.get('property', a.get('name', ''))] = a.get('content', '')
        if tag == 'a' and self.in_main:
            url = urllib.parse.urljoin(ORIGIN, a.get('href', ''))
            if re.fullmatch(re.escape(ORIGIN) + r'/(in-depth|news)/\d+/?', url) and url not in self.links:
                self.links.append(url.rstrip('/'))
        if tag == 'div':
            if self.content_depth: self.content_depth += 1
            elif 'html-content' in a.get('class', '').split(): self.content_depth = 1
        if tag == 'script':
            self.script = a.get('type') == 'application/ld+json'
            self.script_text = []

    def handle_endtag(self, tag):
        if tag == 'main': self.in_main = False
        if tag == 'div' and self.content_depth: self.content_depth -= 1
        if tag == 'script' and self.script:
            try:
                def walk(value):
                    if isinstance(value, dict):
                        if value.get('datePublished'): self.dates.append(value['datePublished'])
                        for v in value.values(): walk(v)
                    elif isinstance(value, list):
                        for v in value: walk(v)
                walk(json.loads(''.join(self.script_text)))
            except (ValueError, TypeError): pass
            self.script = False

    def handle_data(self, data):
        if self.script: self.script_text.append(data)
        elif self.content_depth: self.body.append(data)

def parse(text):
    page = Page()
    page.feed(text)
    return page

def select_article(url, page, now):
    title = page.meta.get('og:title', '').split(' | 品牌星球')[0].strip()
    description = re.sub(r'\s+', ' ', page.meta.get('description', '')).strip()
    body = re.sub(r'\s+', ' ', ' '.join(page.body))
    if not title or not page.dates or len(body) < 120: return None
    published = dt.datetime.fromisoformat(page.dates[0].replace('Z', '+00:00'))
    if published.tzinfo is None: published = published.replace(tzinfo=TZ)
    age = (now - published).total_seconds() / 86400
    if age < -1 or age > 90: return None
    topics = [name for name, terms in RULES.items() if any(term in title + ' ' + description + ' ' + body for term in terms)]
    if not topics: return None
    deep = '/in-depth/' in url
    score = (3 if deep else 0) + len(topics) + (1 if len(body) > 1200 else 0)
    if score < 3: return None
    # Classify collaboration from title/description; incidental body mentions do not make a project an IP case.
    is_ip = any(term in title + ' ' + description for term in RULES['IP 合作'])
    return {
        'id': 'brandstar-' + url.rsplit('/', 1)[-1],
        'title': title, 'url': url, 'published_at': published.isoformat(),
        'date': published.astimezone(TZ).strftime('%Y-%m-%d'),
        'collected_at': now.isoformat(), 'source': '品牌星球',
        'kind': '深度报道' if deep else '品牌动态', 'topics': topics,
        'is_case': deep, 'is_ip': is_ip,
        'source_excerpt': description if len(description) <= 60 else description[:59] + '…',
        'selection_reason': ('深度报道，含具体品牌实践' if deep else '近期品牌动作') + '；涉及' + '、'.join(topics[:3]) + '。',
        'score': score,
    }

def sync(old, now, request=fetch):
    rows = {x['id']: x for x in old.get('items', [])}
    known = {x['url'] for x in rows.values()}
    errors, links, discoveries = [], [], 0
    for route in ['/', '/in-depth/']:
        try:
            found = parse(request(ORIGIN + route)).links
            if not found: raise ValueError('No article links found')
            discoveries += 1
            links.extend(url for url in found if url not in links)
        except Exception as error: errors.append(route + ': ' + type(error).__name__)
    examined = added = 0
    # Existing articles retain their first collection date; only new URLs are fetched.
    candidates = [url for url in links if url not in known]
    for url in candidates[:18]:
        try:
            article = select_article(url, parse(request(url)), now)
            examined += 1
            if article:
                rows[article['id']] = article
                added += 1
        except Exception as error: errors.append(url + ': ' + type(error).__name__)
    success = discoveries > 0 and (not candidates or examined > 0)
    items = sorted(rows.values(), key=lambda x: (x['date'], x.get('score', 0)), reverse=True)[:80]
    return {
        'checked_at': now.isoformat(),
        'last_success_at': now.isoformat() if success else old.get('last_success_at'),
        'last_content_update_at': now.isoformat() if added else old.get('last_content_update_at'),
        'status': ('partial' if errors else 'ok') if success else 'error',
        'added': added, 'examined': examined,
        'errors': errors, 'items': items,
        'policy': '每日北京时间 08:00 云端检查；筛选近 90 天的品牌实践与合作报道。自动导读不冒充深度分析。'
    }

def main():
    old = json.loads(OUTPUT.read_text(encoding='utf-8-sig')) if OUTPUT.exists() else {'items': []}
    result = sync(old, dt.datetime.now(TZ))
    temp = OUTPUT.with_suffix('.tmp')
    temp.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    temp.replace(OUTPUT)
    print(f"Brandstar: {result['status']}; added={result['added']}; retained={len(result['items'])}")
    return 1 if result['status'] == 'error' else 0

if __name__ == '__main__': sys.exit(main())


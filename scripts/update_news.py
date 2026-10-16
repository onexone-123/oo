"""Daily RSS discovery; no paid API or credentials required."""
import concurrent.futures, datetime as dt, email.utils, hashlib, json, pathlib, re, sys, urllib.parse, urllib.request, xml.etree.ElementTree as ET
ROOT = pathlib.Path(__file__).resolve().parents[1]
OUTPUT = ROOT / 'docs' / 'news.json'
QUERIES = [
    ('全球品牌营销', 'brand marketing campaign launch when:7d', '品牌运营', 'US', 'en-US'),
    ('全球平台动态', 'TikTok Instagram creator ecommerce launch when:7d', '内容运营', 'US', 'en-US'),
    ('中国运营动态', '品牌 营销 活动 电商 when:7d', '电商运营', 'CN', 'zh-CN'),
    ('IP合作动态', '联名 IP 合作 品牌 when:7d', '品牌运营', 'CN', 'zh-CN'),
]
def read_feed(spec):
    topic, query, tag, country, lang = spec
    url = 'https://news.google.com/rss/search?' + urllib.parse.urlencode({'q':query,'hl':lang,'gl':country,'ceid':country+':'+lang.split('-')[0]})
    req = urllib.request.Request(url, headers={'User-Agent':'OperaRadar/1.0 RSS Reader'})
    with urllib.request.urlopen(req, timeout=30) as response:
        root = ET.fromstring(response.read(2_000_000))
    result=[]
    for n in root.findall('./channel/item')[:12]:
        title = (n.findtext('title') or '').strip()
        publisher = (n.findtext('source') or '').strip()
        if publisher and title.endswith(' - '+publisher): title=title[:-len(publisher)-3]
        link=(n.findtext('link') or '').strip()
        if not title or not link.startswith('https://'): continue
        try: published=email.utils.parsedate_to_datetime(n.findtext('pubDate')).astimezone(dt.timezone.utc)
        except (TypeError, ValueError, AttributeError): continue
        now=dt.datetime.now(dt.timezone.utc)
        if published > now+dt.timedelta(hours=1) or published < now-dt.timedelta(days=14): continue
        key=hashlib.sha256(re.sub(r'\s+','',title).casefold().encode()).hexdigest()[:20]
        result.append({'id':'auto-'+key,'kind':'hot','tag':tag,'region':'中国' if country=='CN' else '全球','date':published.strftime('%Y.%m.%d'),'art':'meta' if country=='US' else 'lego','word':'DAILY SIGNAL','title':title[:240],'body':'每日资讯 · '+topic+'。点击展开查看收录说明。','extra':'这是一条自动收录的新闻标题，保留原标题语言；不代表已验证的营销成效或合作授权可用性。','published_at':published.isoformat(),'source_url':link,'publisher':publisher})
    return result

def main():
    old=json.loads(OUTPUT.read_text(encoding='utf-8-sig')) if OUTPUT.exists() else {'items':[]}
    found=[]; successes=0;errors=[]
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        futures={pool.submit(read_feed,q):q[0] for q in QUERIES}
        for future in concurrent.futures.as_completed(futures):
            try:
                rows=future.result()
                if rows: successes+=1
                found.extend(rows)
            except Exception as error: errors.append(futures[future]+': '+str(error))
    if not successes:
        print('No usable feeds; preserving existing content. '+ '; '.join(errors),file=sys.stderr)
        return 1
    combined={x['id']:x for x in old.get('items',[])}
    combined.update({x['id']:x for x in found})
    rows=sorted(combined.values(),key=lambda x:x.get('published_at',''),reverse=True)[:120]
    output={'checked_at':dt.datetime.now(dt.timezone.utc).isoformat(),'feeds_ok':successes,'items':rows}
    temp=OUTPUT.with_suffix('.tmp');temp.write_text(json.dumps(output,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');temp.replace(OUTPUT)
    print(f'Recorded {len(found)} candidates; retained {len(rows)} unique headlines; {successes}/{len(QUERIES)} feeds usable.')
    if errors: print('; '.join(errors),file=sys.stderr)
    return 0
if __name__=='__main__': sys.exit(main())

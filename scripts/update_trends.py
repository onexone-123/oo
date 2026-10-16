"""Fetch independently; preserve last successful snapshots per platform."""
import concurrent.futures,datetime as dt,json,pathlib,urllib.request,urllib.parse,sys
ROOT=pathlib.Path(__file__).resolve().parents[1];OUT=ROOT/'docs/trends.json'
UA='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/130.0.0.0 Safari/537.36'
def request(url,referer=''):
 req=urllib.request.Request(url,headers={'User-Agent':UA,**({'Referer':referer} if referer else {})})
 with urllib.request.urlopen(req,timeout=18) as r:return json.loads(r.read(3000000))
def get_platform(key):
 errors=[]
 urls={
 'bilibili':['https://api.bilibili.com/x/web-interface/search/square?limit=30','https://60s.crystelf.top/v2/bili'],
 'douyin':['https://aweme-lq.snssdk.com/aweme/v1/hot/search/list/?aid=1128&version_code=880','https://aweme.snssdk.com/aweme/v1/hot/search/list/?aid=1128&version_code=880'],
 'weibo':['https://weibo.com/ajax/side/hotSearch','https://60s.7se.cn/v2/weibo','https://60s.crystelf.top/v2/weibo'],
 'rednote':['https://edith.xiaohongshu.com/api/sns/v1/search/hot_list','https://60s.okbaike.com/v2/rednote','https://60s.crystelf.top/v2/rednote'],
 }[key]
 for url in urls:
  try:
   j=request(url,'https://weibo.com/' if key=='weibo' else 'https://app.xhs.cn/' if key=='rednote' else '')
   d=j.get('data',{});rows=[]
   if key=='bilibili' and isinstance(d,dict):raw=d.get('trending',{}).get('list',[])
   elif key=='douyin' and isinstance(d,dict):raw=d.get('word_list',[])
   elif key=='weibo' and isinstance(d,dict):raw=d.get('realtime',[])
   elif key=='rednote' and isinstance(d,dict):raw=d.get('items',[])
   else:raw=d if isinstance(d,list) else []
   seen=set()
   for x in raw:
    if x.get('is_ad')==1:continue
    title=str(x.get('show_name') or x.get('title') or x.get('word') or x.get('keyword') or '').strip()
    if not title or title in seen:continue
    seen.add(title);query=urllib.parse.quote(title)
    dest={'bilibili':f'https://search.bilibili.com/all?keyword={query}','douyin':f'https://www.douyin.com/search/{query}','weibo':f'https://s.weibo.com/weibo?q={query}','rednote':f'https://www.xiaohongshu.com/search_result?keyword={query}'}[key]
    rows.append({'rank':len(rows)+1,'title':title[:200],'heat':x.get('hot_value') or x.get('heat_score') or x.get('score') or x.get('hot') or x.get('num') or '', 'url':dest})
   if not rows:raise ValueError('No usable topics')
   return {'status':'ok','collected_at':dt.datetime.now(dt.timezone.utc).isoformat(),'items':rows[:30],'endpoint':url,'upstream_time':j.get('update_time')}
  except Exception as e:errors.append(str(e))
 raise RuntimeError('; '.join(errors))
def main():
 old=json.loads(OUT.read_text(encoding='utf-8-sig')) if OUT.exists() else {'platforms':{}}
 now=dt.datetime.now(dt.timezone.utc);platforms={};ok=0
 with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
  fs={pool.submit(get_platform,k):k for k in ['bilibili','douyin','rednote','weibo']}
  for f in concurrent.futures.as_completed(fs):
   k=fs[f]
   try:platforms[k]=f.result();ok+=1
   except Exception as e:
    prev=old.get('platforms',{}).get(k,{})
    platforms[k]={**prev,'status':'stale' if prev.get('items') else 'unavailable','checked_at':now.isoformat(),'error':str(e),'items':prev.get('items',[])}
    print(k+': unavailable this attempt',file=sys.stderr)
 result={'checked_at':now.isoformat(),'date':now.astimezone(dt.timezone(dt.timedelta(hours=8))).date().isoformat(),'platforms':platforms}
 OUT.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
 archive=ROOT/'docs/history';archive.mkdir(exist_ok=True)
 (archive/(result['date']+'.json')).write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
 files=sorted(archive.glob('????-??-??.json'))
 for f in files[:-30]:f.unlink()
 (ROOT/'docs/history.json').write_text(json.dumps([f.stem for f in sorted(archive.glob('????-??-??.json'),reverse=True)]),encoding='utf8')
 print(f'Trending snapshots: {ok}/4 platforms available; failed platforms explicitly marked.')
 return 0 if ok else 1
if __name__=='__main__':sys.exit(main())

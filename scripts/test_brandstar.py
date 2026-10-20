import datetime as dt
import unittest
from update_brandstar import parse, select_article, sync, ORIGIN, TZ

NOW = dt.datetime(2026,10,20,8,tzinfo=TZ)
URL = ORIGIN+'/in-depth/8348'
ARTICLE = '''<html><head><meta property="og:title" content="品牌联名与跑者社群 | 品牌星球Brandstar"><meta name="description" content="品牌联名活动记录"><script type="application/ld+json">{"datePublished":"2026-10-14T10:00:00+08:00"}</script></head><body><div class="html-content"><p>'''+('门店的社群体验与品牌营销。'*100)+'''</p></div></body></html>'''
HOME = '<html><main><a href="/in-depth/8348">A</a><a href="/in-depth/8348">B</a><a href="https://evil.example/in-depth/1">X</a></main><a href="/news/9">footer</a></html>'

class Tests(unittest.TestCase):
    def test_discovery(self):
        self.assertEqual(parse(HOME).links,[URL])
    def test_article(self):
        a=select_article(URL,parse(ARTICLE),NOW)
        self.assertTrue(a['is_ip']); self.assertTrue(a['is_case'])
        self.assertLessEqual(len(a['source_excerpt']),60)
        self.assertNotIn('body',a)
        self.assertIsNone(select_article(URL,parse(ARTICLE.replace('2026-10-14','2025-10-14')),NOW))
    def test_preserve_on_failure(self):
        old={'items':[select_article(URL,parse(ARTICLE),NOW)],'last_success_at':'previous'}
        def failed(url): raise OSError('offline')
        result=sync(old,NOW,failed)
        self.assertEqual(result['items'],old['items']); self.assertEqual(result['status'],'error')
        self.assertEqual(result['last_success_at'],'previous')
    def test_deduplicate(self):
        request=lambda url: ARTICLE if url==URL else HOME
        first=sync({'items':[]},NOW,request)
        second=sync(first,NOW,request)
        self.assertEqual(first['added'],1);self.assertEqual(second['added'],0)
        self.assertEqual(len(second['items']),1)

if __name__=='__main__': unittest.main()

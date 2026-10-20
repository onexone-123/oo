import unittest
from translate_trends import enrich

class TranslationTests(unittest.TestCase):
    def test_original_rank_and_duplicates(self):
        data={'platforms':{'instagram':{'items':[{'title':'Hello','rank':3},{'title':'Hello','rank':7}]}}}
        calls=[]
        def translator(title):
            calls.append(title)
            return '你好'
        enrich(data,translator)
        self.assertEqual(calls,['Hello'])
        self.assertEqual(data['platforms']['instagram']['items'][1], {'title':'Hello','rank':7,'title_zh':'你好','translation_status':'machine'})

    def test_failure_preserves_original(self):
        def broken(_):raise OSError()
        row={'title':'Original','rank':1}
        enrich({'platforms':{'x':{'items':[row]}}},broken)
        self.assertEqual(row['translation_status'],'unavailable')
        self.assertNotIn('title_zh',row)
        self.assertEqual(row['title'],'Original')

if __name__=='__main__':unittest.main()

import importlib.util,json,tempfile,pathlib,unittest
from unittest.mock import patch
spec=importlib.util.spec_from_file_location('trends',pathlib.Path(__file__).with_name('update_trends.py'));m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class SnapshotTests(unittest.TestCase):
 def test_failed_source_keeps_original_timestamp_and_items(self):
  with tempfile.TemporaryDirectory(dir=pathlib.Path(__file__).resolve().parent) as directory:
   root=pathlib.Path(directory);(root/'docs').mkdir();out=root/'docs/trends.json'
   old={'platforms':{'rednote':{'status':'ok','collected_at':'2026-10-01T00:00:00+00:00','items':[{'rank':1,'title':'previous'}]}}};out.write_text(json.dumps(old))
   def get(k):
    if k=='rednote':raise RuntimeError('offline')
    return {'status':'ok','collected_at':'2026-10-16T00:00:00+00:00','items':[{'rank':1,'title':k}]}
   with patch.object(m,'ROOT',root),patch.object(m,'OUT',out),patch.object(m,'get_platform',side_effect=get):self.assertEqual(m.main(),0)
   d=json.loads(out.read_text());self.assertEqual(d['platforms']['rednote']['status'],'stale');self.assertEqual(d['platforms']['rednote']['collected_at'],'2026-10-01T00:00:00+00:00');self.assertEqual(d['platforms']['rednote']['items'][0]['title'],'previous')
 def test_no_data_is_unavailable_not_fake_success(self):
  with tempfile.TemporaryDirectory(dir=pathlib.Path(__file__).resolve().parent) as directory:
   root=pathlib.Path(directory);(root/'docs').mkdir();out=root/'docs/trends.json'
   with patch.object(m,'ROOT',root),patch.object(m,'OUT',out),patch.object(m,'get_platform',side_effect=RuntimeError('offline')):self.assertEqual(m.main(),1)
   self.assertTrue(all(x['status']=='unavailable' and not x['items'] for x in json.loads(out.read_text())['platforms'].values()))
if __name__=='__main__':unittest.main()


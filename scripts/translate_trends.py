"""Translate public global topic titles; retain original text and honest failures."""
import concurrent.futures
import json
import pathlib
import urllib.parse
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[1]
KEYS = ('instagram', 'facebook', 'x', 'tiktok')

def translate(title):
    url = 'https://translate.googleapis.com/translate_a/single?' + urllib.parse.urlencode(
        {'client': 'gtx', 'sl': 'auto', 'tl': 'zh-CN', 'dt': 't', 'q': title})
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=15) as response:
        payload = json.loads(response.read(100000))
    result = ''.join(part[0] for part in payload[0] if part and isinstance(part[0], str)).strip()
    if not result:
        raise ValueError('Empty translation')
    return result

def enrich(data, translator=translate):
    rows = [row for key in KEYS for row in data.get('platforms', {}).get(key, {}).get('items', [])]
    pending = {}
    for row in rows:
        if not row.get('title_zh'):
            pending.setdefault(row['title'], []).append(row)
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        futures = {pool.submit(translator, title): title for title in pending}
        for future in concurrent.futures.as_completed(futures):
            title = futures[future]
            try:
                translated = future.result()
                for row in pending[title]:
                    row.update(title_zh=translated, translation_status='machine')
            except Exception:
                for row in pending[title]:
                    row['translation_status'] = 'unavailable'
    return data

def main():
    path = ROOT / 'docs/trends.json'
    data = enrich(json.loads(path.read_text(encoding='utf-8-sig')))
    content = json.dumps(data, ensure_ascii=False, indent=2) + '\n'
    path.write_text(content, encoding='utf-8')
    (ROOT / 'docs/history' / (data['date'] + '.json')).write_text(content, encoding='utf-8')
    rows = [x for k in KEYS for x in data.get('platforms', {}).get(k, {}).get('items', [])]
    print(f"Translated {sum(bool(x.get('title_zh')) for x in rows)}/{len(rows)} global titles")

if __name__ == '__main__':
    main()

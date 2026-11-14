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
            except Exception as exc:
                print(f"Translation failure: {type(exc).__name__}, HTTP {getattr(exc, 'code', 'n/a')}")
                for row in pending[title]:
                    row['translation_status'] = 'unavailable'
    return data


def reuse_translations(data, snapshots):
    """Reuse exact original-title matches from successful historical rows."""
    cache = {}
    for snapshot in snapshots:
        for key in KEYS:
            for row in snapshot.get('platforms', {}).get(key, {}).get('items', []):
                if (isinstance(row.get('title'), str)
                        and isinstance(row.get('title_zh'), str)
                        and row['title_zh'].strip()
                        and row.get('translation_status') == 'machine'):
                    cache[row['title']] = row['title_zh']
    for key in KEYS:
        for row in data.get('platforms', {}).get(key, {}).get('items', []):
            if not row.get('title_zh') and row.get('title') in cache:
                row.update(title_zh=cache[row['title']], translation_status='machine')
    return data

def main():
    path = ROOT / 'docs/trends.json'
    data = json.loads(path.read_text(encoding='utf-8-sig'))
    snapshots = []
    for previous in sorted((ROOT / 'docs/history').glob('????-??-??.json'))[-30:]:
        try:
            snapshot = json.loads(previous.read_text(encoding='utf-8-sig'))
            if isinstance(snapshot, dict):
                snapshots.append(snapshot)
        except (OSError, ValueError):
            print('Skipped unreadable translation history')
    data = enrich(reuse_translations(data, snapshots))
    content = json.dumps(data, ensure_ascii=False, indent=2) + '\n'
    path.write_text(content, encoding='utf-8')
    (ROOT / 'docs/history' / (data['date'] + '.json')).write_text(content, encoding='utf-8')
    rows = [x for k in KEYS for x in data.get('platforms', {}).get(k, {}).get('items', [])]
    print(f"Translated {sum(bool(x.get('title_zh')) for x in rows)}/{len(rows)} global titles")

if __name__ == '__main__':
    main()

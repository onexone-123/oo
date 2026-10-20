import datetime as dt
import unittest
from global_trends import parse_feed, parse_x, get_global_platform, UTC

NOW=dt.datetime(2026,10,20,14,tzinfo=UTC)
def feed(title='Instagram viral challenge',date='Tue, 20 Oct 2026 12:00:00 GMT',source='https://www.bbc.com'):
    return f'<rss><channel><item><title>{title} - BBC</title><link>https://news.google.com/articles/example</link><pubDate>{date}</pubDate><source url="{source}">BBC</source></item></channel></rss>'
def x_html(when):
    return f'<h3 data-timestamp="{when.timestamp()}"></h3><ol class="trend-card__list"><li><span class="trend-name"><a class="trend-link">#RealTrend</a><span data-count="24000"></span></span></li></ol>'

class Tests(unittest.TestCase):
    def test_feed_relevance_age_trust(self):
        self.assertEqual(len(parse_feed(feed(),'instagram',NOW)),1)
        self.assertFalse(parse_feed(feed(title='Facebook updates'),'instagram',NOW))
        self.assertFalse(parse_feed(feed(date='Tue, 13 Oct 2026 12:00:00 GMT'),'instagram',NOW))
        self.assertFalse(parse_feed(feed(source='https://bbc.com.spam.invalid'),'instagram',NOW))
    def test_dedupe_and_label(self):
        result=get_global_platform('instagram',NOW,lambda _:feed())
        self.assertEqual(len(result['items']),1)
        self.assertEqual(result['kind'],'reported_signals')
        self.assertEqual(result['items'][0]['heat'],'')
    def test_empty_success_is_not_failure(self):
        result=get_global_platform('facebook',NOW,lambda _: '<rss><channel/></rss>')
        self.assertEqual(result['status'],'ok');self.assertEqual(result['items'],[])
    def test_x_timestamp_and_source(self):
        result=parse_x(x_html(NOW),NOW)
        self.assertEqual(result['items'][0]['title'],'#RealTrend')
        self.assertEqual(result['items'][0]['heat'],'24000')
        self.assertEqual(result['kind'],'third_party_trends')
        for time in [NOW-dt.timedelta(days=2),NOW+dt.timedelta(days=1)]:
            with self.assertRaises(ValueError):parse_x(x_html(time),NOW)
    def test_feed_failures_raise(self):
        def broken(_):raise OSError('offline')
        with self.assertRaises(RuntimeError):get_global_platform('tiktok',NOW,broken)

if __name__=='__main__':unittest.main()

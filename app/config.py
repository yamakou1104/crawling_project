import os

# Celery設定
CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL', 'redis://redis:6379/0')
CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND', 'redis://redis:6379/0')

# スクレイピング設定
DEFAULT_URLS = [
    'https://news.yahoo.co.jp/pickup/domestic',
    'https://news.yahoo.co.jp/pickup/world',
    # 他のURLを追加
]

# スケジュール設定（秒単位）
SCHEDULE_INTERVALS = {
    'hourly': 60 * 60,
    'daily': 60 * 60 * 24,
    'weekly': 60 * 60 * 24 * 7,
}

# デフォルトのスケジュール設定
DEFAULT_SCHEDULE = {
    'task': 'tasks.scrape_scheduled_urls',
    'schedule': SCHEDULE_INTERVALS['hourly'],  # 1時間ごとに実行
    'args': (DEFAULT_URLS,),
    'kwargs': {
        'output_dir': 'data',
        'min_text_length': 50,
        'delay': 1,
        'keyword': None,
        'summarize': False,
    }
}

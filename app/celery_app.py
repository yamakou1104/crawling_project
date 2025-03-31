from celery import Celery
from config import CELERY_BROKER_URL, CELERY_RESULT_BACKEND, DEFAULT_SCHEDULE

app = Celery('crawler',
             broker=CELERY_BROKER_URL,
             backend=CELERY_RESULT_BACKEND,
             include=['tasks'])

# スケジュール設定
app.conf.beat_schedule = {
    'hourly-scraping': DEFAULT_SCHEDULE
}

app.conf.timezone = 'Asia/Tokyo'

if __name__ == '__main__':
    app.start()

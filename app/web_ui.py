from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import os
import json
from config import DEFAULT_URLS, SCHEDULE_INTERVALS, DEFAULT_SCHEDULE
from celery_app import app as celery_app
from tasks import scrape_url, scrape_scheduled_urls

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'dev_key_for_crawler')

# 設定ファイルのパス
CONFIG_FILE = 'scheduler_config.json'

def load_config():
    """設定ファイルを読み込む"""
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    return {
        'urls': DEFAULT_URLS,
        'schedule': DEFAULT_SCHEDULE['schedule'],
        'output_dir': 'data',
        'min_text_length': 50,
        'delay': 1,
        'keyword': None,
        'summarize': False
    }

def save_config(config):
    """設定ファイルを保存する"""
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)

@app.route('/')
def index():
    """ダッシュボードページ"""
    config = load_config()
    
    # スケジュール間隔の名前を取得
    schedule_name = 'カスタム'
    for name, seconds in SCHEDULE_INTERVALS.items():
        if seconds == config['schedule']:
            schedule_name = name
    
    return render_template('index.html', 
                          config=config, 
                          schedule_intervals=SCHEDULE_INTERVALS,
                          schedule_name=schedule_name)

@app.route('/update_config', methods=['POST'])
def update_config():
    """設定を更新する"""
    config = load_config()
    
    # フォームからデータを取得
    urls = request.form.get('urls', '').strip().split('\n')
    urls = [url.strip() for url in urls if url.strip()]
    
    schedule_type = request.form.get('schedule_type')
    if schedule_type in SCHEDULE_INTERVALS:
        schedule = SCHEDULE_INTERVALS[schedule_type]
    else:
        try:
            schedule = int(request.form.get('custom_schedule', 3600))
        except ValueError:
            schedule = 3600
    
    config.update({
        'urls': urls,
        'schedule': schedule,
        'output_dir': request.form.get('output_dir', 'data'),
        'min_text_length': int(request.form.get('min_text_length', 50)),
        'delay': float(request.form.get('delay', 1)),
        'keyword': request.form.get('keyword') or None,
        'summarize': 'summarize' in request.form
    })
    
    save_config(config)
    
    # Celeryのスケジュールを更新
    celery_app.conf.beat_schedule = {
        'scraping-task': {
            'task': 'tasks.scrape_scheduled_urls',
            'schedule': config['schedule'],
            'args': (config['urls'],),
            'kwargs': {
                'output_dir': config['output_dir'],
                'min_text_length': config['min_text_length'],
                'delay': config['delay'],
                'keyword': config['keyword'],
                'summarize': config['summarize'],
            }
        }
    }
    
    flash('設定が更新されました', 'success')
    return redirect(url_for('index'))

@app.route('/run_now', methods=['POST'])
def run_now():
    """今すぐスクレイピングを実行する"""
    config = load_config()
    
    task = scrape_scheduled_urls.delay(
        config['urls'],
        output_dir=config['output_dir'],
        min_text_length=config['min_text_length'],
        delay=config['delay'],
        keyword=config['keyword'],
        summarize=config['summarize']
    )
    
    flash(f'スクレイピングタスクが開始されました (タスクID: {task.id})', 'success')
    return redirect(url_for('index'))

@app.route('/task_status/<task_id>')
def task_status(task_id):
    """タスクのステータスを取得する"""
    task = celery_app.AsyncResult(task_id)
    response = {
        'state': task.state,
        'info': str(task.info) if task.info else None
    }
    return jsonify(response)

if __name__ == '__main__':
    # テンプレートディレクトリが存在しない場合は作成
    os.makedirs('templates', exist_ok=True)
    
    # 設定ファイルが存在しない場合は作成
    if not os.path.exists(CONFIG_FILE):
        save_config(load_config())
    
    app.run(host='0.0.0.0', port=5000, debug=True)

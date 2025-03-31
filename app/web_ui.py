from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import os
import json
import threading
import time
from config import DEFAULT_URLS, SCHEDULE_INTERVALS, DEFAULT_SCHEDULE
from celery_app import app as celery_app
from tasks import scrape_url, scrape_scheduled_urls
from pyngrok import ngrok

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'dev_key_for_crawler')

# ngrokの公開URL
public_url = None

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
    
    # ngrok URLを取得
    ngrok_url = app.config.get('NGROK_URL', None)
    
    return render_template('index.html', 
                          config=config, 
                          schedule_intervals=SCHEDULE_INTERVALS,
                          schedule_name=schedule_name,
                          active_tasks=[],
                          ngrok_url=ngrok_url)

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
    
    # JSONレスポンスを返す場合
    if request.headers.get('Accept') == 'application/json':
        return jsonify({'task_id': task.id, 'status': 'PENDING'})
    
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

@app.route('/stop_task/<task_id>', methods=['POST', 'GET'])
def stop_task(task_id):
    """実行中のタスクを停止する"""
    try:
        # タスクを取り消し（強制終了）
        celery_app.control.revoke(task_id, terminate=True)
        
        # JSONレスポンスを返す場合
        if request.headers.get('Accept') == 'application/json':
            return jsonify({'success': True, 'message': f'タスク {task_id} の停止を要求しました'})
            
        flash(f'タスク {task_id} の停止を要求しました', 'success')
    except Exception as e:
        if request.headers.get('Accept') == 'application/json':
            return jsonify({'success': False, 'error': str(e)}), 500
            
        flash(f'タスクの停止に失敗しました: {str(e)}', 'danger')
    
    return redirect(url_for('index'))

def start_ngrok():
    """ngrokトンネルを開始し、公開URLを取得する"""
    global public_url
    try:
        # 環境変数からngrokのauthトークンを取得（設定されていない場合はデモモードで動作）
        auth_token = os.environ.get('NGROK_AUTH_TOKEN')
        
        if auth_token:
            # 認証トークンが設定されている場合は使用
            ngrok.set_auth_token(auth_token)
            print(f"✅ ngrok認証トークンを設定しました")
            
            # ngrokトンネルを開始
            http_tunnel = ngrok.connect(5000)
            public_url = http_tunnel.public_url
            print(f"✅ ngrok公開URL: {public_url}")
            
            # 起動情報をテンプレートに渡すためにグローバル変数に保存
            app.config['NGROK_URL'] = public_url
            
            # ngrokトンネル情報をログに記録
            tunnels = ngrok.get_tunnels()
            for tunnel in tunnels:
                print(f"🔗 ngrokトンネル: {tunnel.public_url} -> {tunnel.config['addr']}")
                
            return public_url
        else:
            # 認証トークンが設定されていない場合はデモモードで動作
            print("⚠️ NGROK_AUTH_TOKENが設定されていません。公開URLは生成されません。")
            print("⚠️ ngrokを使用するには、https://dashboard.ngrok.com/signup でアカウント登録し、")
            print("⚠️ 認証トークンを取得して環境変数NGROK_AUTH_TOKENに設定してください。")
            
            # ローカルURLをテンプレートに渡す
            local_url = "http://localhost:5000"
            app.config['NGROK_URL'] = local_url
            app.config['IS_DEMO_MODE'] = True
            return local_url
    except Exception as e:
        print(f"❌ ngrok起動エラー: {str(e)}")
        app.config['IS_DEMO_MODE'] = True
        return None

@app.route('/ngrok_url')
def get_ngrok_url():
    """現在のngrok URLを返す"""
    global public_url
    if public_url:
        # デモモードかどうかの情報も含める
        is_demo_mode = app.config.get('IS_DEMO_MODE', False)
        return jsonify({
            'url': public_url,
            'is_demo_mode': is_demo_mode
        })
    return jsonify({'error': 'ngrok URLが利用できません'})

if __name__ == '__main__':
    # テンプレートディレクトリが存在しない場合は作成
    os.makedirs('templates', exist_ok=True)
    
    # 設定ファイルが存在しない場合は作成
    if not os.path.exists(CONFIG_FILE):
        save_config(load_config())
    
    # ngrokを別スレッドで起動
    threading.Thread(target=start_ngrok).start()
    
    # Flaskアプリを起動
    app.run(host='0.0.0.0', port=5000, debug=True)

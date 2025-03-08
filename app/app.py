import sys
import argparse
import logging
import requests
from bs4 import BeautifulSoup
import json
import csv
import os
import time
from datetime import datetime
from urllib.parse import urlparse, urljoin
from urllib.robotparser import RobotFileParser
<<<<<<< HEAD

# ロギングの初期設定（後でverboseで変更可能）
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
=======
# No longer importing from generic_scraper.py

# ロギングの設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
>>>>>>> 4804a5634bfd6d7799d786cb093562d525b225ba
)

# デフォルトのユーザーエージェント
HEADERS = {
<<<<<<< HEAD
    'User-Agent': (
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
        'AppleWebKit/537.36 (KHTML, like Gecko) '
        'Chrome/91.0.4472.124 Safari/537.36'
    )
=======
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
>>>>>>> 4804a5634bfd6d7799d786cb093562d525b225ba
}

# リクエスト間の待機時間（秒）
REQUEST_DELAY = 1

def check_robots_txt(url):
<<<<<<< HEAD
    """robots.txtをチェックしてURLへのアクセスが許可されているか確認"""
=======
    """robots.txtをチェックして、URLへのアクセスが許可されているかを確認する"""
>>>>>>> 4804a5634bfd6d7799d786cb093562d525b225ba
    try:
        parsed_url = urlparse(url)
        robots_url = f"{parsed_url.scheme}://{parsed_url.netloc}/robots.txt"
        
        rp = RobotFileParser()
        rp.set_url(robots_url)
        rp.read()
        
        can_fetch = rp.can_fetch(HEADERS['User-Agent'], url)
        if not can_fetch:
            logging.warning(f"robots.txtによりアクセスが制限されています: {url}")
        return can_fetch
    except Exception as e:
<<<<<<< HEAD
        logging.warning(f"robots.txtの確認中にエラー: {e}")
        return True  # 失敗した場合は許可する

def get_absolute_url(base_url, relative_url):
    """相対URLを絶対URLに変換"""
=======
        logging.warning(f"robots.txtの確認中にエラーが発生しました: {e}")
        # エラーが発生した場合はアクセスを許可する（寛容なアプローチ）
        return True

def get_absolute_url(base_url, relative_url):
    """相対URLを絶対URLに変換する"""
>>>>>>> 4804a5634bfd6d7799d786cb093562d525b225ba
    if not relative_url:
        return None
    if relative_url.startswith(('http://', 'https://')):
        return relative_url
    return urljoin(base_url, relative_url)

def save_to_json(data, filename):
<<<<<<< HEAD
    """データをJSON形式で保存"""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    logging.info(f"✅ JSONファイルを保存: {filename}")

def save_to_csv(data, filename):
    """データをCSV形式で保存"""
    fieldnames = list(data.keys())
    with open(filename, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
=======
    """データをJSON形式で保存する"""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    logging.info(f"✅ JSONファイルを保存しました: {filename}")

def save_to_csv(data, filename):
    """データをCSV形式で保存する"""
    # CSVのヘッダー
    fieldnames = list(data.keys())
    
    with open(filename, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        
        # リスト型のデータをカンマ区切りの文字列に変換
>>>>>>> 4804a5634bfd6d7799d786cb093562d525b225ba
        csv_data = {}
        for key, value in data.items():
            if isinstance(value, list):
                csv_data[key] = ','.join(value)
            else:
                csv_data[key] = value
<<<<<<< HEAD
        writer.writerow(csv_data)
    logging.info(f"✅ CSVファイルを保存: {filename}")
=======
        
        writer.writerow(csv_data)
    logging.info(f"✅ CSVファイルを保存しました: {filename}")
>>>>>>> 4804a5634bfd6d7799d786cb093562d525b225ba

def extract_content(soup, url, min_text_length=50):
    """Webページからコンテンツを抽出する汎用関数"""
    data = {}
<<<<<<< HEAD
    data['url'] = url
    
    # タイトル
    data['title'] = soup.title.text.strip() if soup.title else "No Title"
    logging.info(f"ページタイトル: {data['title']}")
    
    # og:title
=======
    
    # URLを追加
    data['url'] = url
    
    # タイトルの取得
    data['title'] = soup.title.text.strip() if soup.title else "No Title"
    logging.info(f"ページのタイトル: {data['title']}")
    
    # Open Graph タグからのタイトル取得（代替手段）
>>>>>>> 4804a5634bfd6d7799d786cb093562d525b225ba
    if data['title'] == "No Title":
        og_title = soup.find('meta', property='og:title')
        if og_title:
            data['title'] = og_title.get('content', 'No Title')
            logging.info(f"Open Graph タイトル: {data['title']}")
    
<<<<<<< HEAD
    # 説明
    meta_description = soup.find('meta', attrs={'name': 'description'})
    if meta_description:
        data['description'] = meta_description.get('content', '')
        logging.info(f"メタ説明: {data['description'][:100]}...")
    else:
        og_description = soup.find('meta', property='og:description')
        if og_description:
            data['description'] = og_description.get('content', '')
            logging.info(f"OG説明: {data['description'][:100]}...")
        else:
            data['description'] = ""
    
    # 本文
    logging.info("本文を抽出中...")
    content_candidates = []
    
    # 記事っぽい要素
    for selector in [
        'article', '.article', '#article', '.content', '#content',
        '.main', '#main', 'main', 'section', '.section', '#section'
    ]:
=======
    # メタデータの取得
    # 通常のメタ説明
    meta_description = soup.find('meta', attrs={'name': 'description'})
    if meta_description:
        data['description'] = meta_description.get('content', '')
        logging.info(f"ページの説明: {data['description'][:100]}...")
    else:
        # Open Graph 説明
        og_description = soup.find('meta', property='og:description')
        if og_description:
            data['description'] = og_description.get('content', '')
            logging.info(f"Open Graph 説明: {data['description'][:100]}...")
        else:
            data['description'] = ""
    
    # 本文の取得
    logging.info("ページ本文を抽出中...")
    
    # 様々なコンテンツ抽出方法を試す
    content_candidates = []
    
    # 方法1: 記事/コンテンツらしき要素を探す
    for selector in ['article', '.article', '#article', '.content', '#content', '.main', '#main', 'main', 'section', '.section', '#section']:
>>>>>>> 4804a5634bfd6d7799d786cb093562d525b225ba
        elements = soup.select(selector)
        if elements:
            for element in elements:
                content_candidates.append(element.get_text(strip=True))
    
<<<<<<< HEAD
    # pタグまとめ
=======
    # 方法2: 段落を取得
>>>>>>> 4804a5634bfd6d7799d786cb093562d525b225ba
    paragraphs = []
    for p in soup.find_all('p'):
        text = p.text.strip()
        if len(text) > min_text_length:
            paragraphs.append(text)
<<<<<<< HEAD
    if paragraphs:
        content_candidates.append("\n\n".join(paragraphs))
    
    # 最長の候補を本文とみなす
    if content_candidates:
        data['content'] = max(content_candidates, key=len)
        logging.info(f"本文を抽出（{len(data['content'])}文字）")
=======
    
    if paragraphs:
        content_candidates.append("\n\n".join(paragraphs))
    
    # 方法3: divで囲まれた大きなテキストブロックを探す
    for div in soup.find_all('div'):
        text = div.get_text(strip=True)
        if len(text) > min_text_length * 5:  # より大きなテキストブロック
            content_candidates.append(text)
    
    # 方法4: schema.org構造化データを探す
    schema_elements = soup.find_all('script', type='application/ld+json')
    for element in schema_elements:
        try:
            schema_data = json.loads(element.string)
            if isinstance(schema_data, dict):
                # 記事コンテンツを探す
                article_body = schema_data.get('articleBody')
                if article_body:
                    content_candidates.append(article_body)
        except Exception as e:
            logging.warning(f"schema.orgデータの解析中にエラーが発生しました: {e}")
    
    # 最も長いコンテンツ候補を選択
    if content_candidates:
        data['content'] = max(content_candidates, key=len)
        logging.info(f"本文を抽出しました（{len(data['content'])}文字）")
>>>>>>> 4804a5634bfd6d7799d786cb093562d525b225ba
        logging.info(f"プレビュー: {data['content'][:150]}...")
    else:
        data['content'] = ""
        logging.warning("本文が見つかりませんでした")
    
<<<<<<< HEAD
    # 画像
    logging.info("画像を抽出中...")
    images = []
=======
    # 画像URLの取得
    logging.info("画像を抽出中...")
    
    images = []
    
    # Open Graph 画像を探す
>>>>>>> 4804a5634bfd6d7799d786cb093562d525b225ba
    og_image = soup.find('meta', property='og:image')
    if og_image:
        img_url = og_image.get('content', '')
        if img_url:
<<<<<<< HEAD
            images.append({'url': img_url, 'alt': 'OpenGraph Image'})
    
    for img in soup.find_all('img'):
        src = img.get('src', '')
        if src:
            abs_src = get_absolute_url(url, src)
            if abs_src:
                alt = img.get('alt', '')
                images.append({'url': abs_src, 'alt': alt})
    data['images'] = [img['url'] for img in images]
    if images:
        logging.info(f"画像を{len(images)}枚見つけました")
    else:
        logging.warning("画像が見つかりませんでした")
    
    # リンク
    logging.info("リンクを抽出中...")
    links = []
    for a in soup.find_all('a', href=True):
        href = a.get('href', '')
        if href and not href.startswith(('javascript:', 'mailto:', '#')):
            abs_href = get_absolute_url(url, href)
            if abs_href:
                links.append({'url': abs_href})
    data['links'] = [link['url'] for link in links]
    if links:
        logging.info(f"リンクを{len(links)}個見つけました")
=======
            images.append({
                'url': img_url,
                'alt': 'Open Graph Image'
            })
    
    # 通常の画像を探す
    for img in soup.find_all('img'):
        src = img.get('src', '')
        if src:
            # 相対URLを絶対URLに変換
            abs_src = get_absolute_url(url, src)
            if abs_src:
                # 画像の代替テキストを取得
                alt = img.get('alt', '')
                
                images.append({
                    'url': abs_src,
                    'alt': alt
                })
    
    # 画像URLのリストを作成
    data['images'] = [img['url'] for img in images]
    
    if images:
        logging.info(f"画像を{len(images)}枚見つけました")
        for i, img in enumerate(images[:5]):  # 最初の5枚だけ表示
            logging.info(f"画像 {i+1}: {img['url']}")
        if len(images) > 5:
            logging.info(f"...他 {len(images) - 5} 枚")
    else:
        logging.warning("画像が見つかりませんでした")
    
    # リンクの取得
    logging.info("リンクを抽出中...")
    
    links = []
    for a in soup.find_all('a', href=True):
        href = a.get('href', '')
        if href and not href.startswith(('#', 'javascript:', 'mailto:')):
            # 相対URLを絶対URLに変換
            abs_href = get_absolute_url(url, href)
            if abs_href:
                link_text = a.get_text(strip=True)
                links.append({
                    'url': abs_href,
                    'text': link_text
                })
    
    # リンクURLのリストを作成
    data['links'] = [link['url'] for link in links]
    
    if links:
        logging.info(f"リンクを{len(links)}個見つけました")
        for i, link in enumerate(links[:5]):  # 最初の5個だけ表示
            logging.info(f"リンク {i+1}: {link['text']} - {link['url']}")
        if len(links) > 5:
            logging.info(f"...他 {len(links) - 5} 個")
>>>>>>> 4804a5634bfd6d7799d786cb093562d525b225ba
    else:
        logging.warning("リンクが見つかりませんでした")
    
    return data

<<<<<<< HEAD
def scrape_website(url, output_dir='data', min_text_length=50,
                   delay=REQUEST_DELAY, user_agent=None):
    """指定したURLをスクレイピングする"""
    
    logging.info(f"{url} のスクレイピングを開始！")
    
=======
def scrape_website(url, output_dir='data', min_text_length=50, delay=REQUEST_DELAY, user_agent=None):
    """指定されたURLのWebサイトをスクレイピングする"""
    logging.info(f"{url} のスクレイピングを開始しました！")
    
    # ユーザーエージェントの設定
>>>>>>> 4804a5634bfd6d7799d786cb093562d525b225ba
    headers = HEADERS.copy()
    if user_agent:
        headers['User-Agent'] = user_agent
    
<<<<<<< HEAD
    # robots.txt
    if not check_robots_txt(url):
        logging.error(f"robots.txt によりアクセス禁止: {url}")
        return None
    
    # レート制限
    if delay > 0:
        logging.info(f"{delay}秒待機...")
        time.sleep(delay)
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(response.text, "html.parser")
        
        data = extract_content(soup, url, min_text_length)
        
        os.makedirs(output_dir, exist_ok=True)
        
        domain = urlparse(url).netloc.replace('.', '_')
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        json_filename = f"{output_dir}/{domain}_{timestamp}.json"
        csv_filename = f"{output_dir}/{domain}_{timestamp}.csv"
        
        save_to_json(data, json_filename)
        save_to_csv(data, csv_filename)
        
        return data
    except requests.exceptions.HTTPError as e:
        logging.error(f"HTTPエラー: {e.response.status_code}")
        return None
    except requests.exceptions.ConnectionError:
        logging.error("接続エラー")
        return None
    except requests.exceptions.Timeout:
        logging.error("タイムアウトエラー")
=======
    try:
        # robots.txtをチェック
        if not check_robots_txt(url):
            logging.error(f"robots.txtによりアクセスが制限されています: {url}")
            return None
        
        logging.info("Webページを取得中...")
        
        # リクエスト前に待機（レート制限）
        if delay > 0:
            logging.info(f"{delay}秒間待機中...")
            time.sleep(delay)
        
        response = requests.get(url, headers=headers, timeout=30)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            
            # データを抽出
            data = extract_content(soup, url, min_text_length)
            
            # 保存用のディレクトリを作成
            os.makedirs(output_dir, exist_ok=True)
            
            # ドメイン名を取得してファイル名に使用
            domain = urlparse(url).netloc.replace('.', '_')
            
            # タイムスタンプを含むファイル名を生成
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            json_filename = f"{output_dir}/{domain}_{timestamp}.json"
            csv_filename = f"{output_dir}/{domain}_{timestamp}.csv"
            
            # JSONとCSVに保存
            save_to_json(data, json_filename)
            save_to_csv(data, csv_filename)
            
            return data
            
        else:
            logging.error(f"HTTPエラー: {response.status_code}")
            if response.status_code == 403:
                logging.error("アクセスが拒否されました。ユーザーエージェントを変更するか、後でもう一度試してください。")
            elif response.status_code == 404:
                logging.error("ページが見つかりませんでした。URLを確認してください。")
            elif response.status_code == 429:
                logging.error("リクエストが多すぎます。しばらく待ってから再試行してください。")
            elif response.status_code >= 500:
                logging.error("サーバーエラーが発生しました。後でもう一度試してください。")
            return None

    except requests.exceptions.Timeout:
        logging.error(f"タイムアウトエラー: {url}")
        return None
    except requests.exceptions.ConnectionError:
        logging.error(f"接続エラー: {url}")
>>>>>>> 4804a5634bfd6d7799d786cb093562d525b225ba
        return None
    except requests.exceptions.RequestException as e:
        logging.error(f"リクエストエラー: {e}")
        return None
    except Exception as e:
<<<<<<< HEAD
        logging.error(f"予期しないエラー: {e}")
        return None
    finally:
        logging.info("スクレイピング完了。")

def normalize_japanese_text(text):
    """日本語テキストを正規化"""
    if not text:
        return text
    import jaconv
    # 全角英数字→半角、カタカナ→ひらがな
    normalized_text = jaconv.z2h(text, kana=False, digit=True, ascii=True)
    normalized_text = jaconv.kata2hira(normalized_text)
    return normalized_text

def filter_content_by_keyword(data, keyword):
    """キーワードでフィルタリング"""
=======
        logging.error(f"例外発生: {e}")
        return None
    finally:
        logging.info("スクレイピング完了！")

def normalize_japanese_text(text):
    """日本語テキストを正規化する
    
    ひらがな、カタカナ、漢字などの異なる文字種を統一的に扱うための正規化を行います。
    現在の実装では、すべてのカタカナをひらがなに変換します。
    """
    if not text:
        return text
    
    import jaconv
    # カタカナをひらがなに変換
    normalized_text = jaconv.z2h(text, kana=False, digit=True, ascii=True)  # 全角英数字を半角に変換
    normalized_text = jaconv.kata2hira(normalized_text)  # カタカナをひらがなに変換
    
    return normalized_text


def filter_content_by_keyword(data, keyword):
    """キーワードに基づいてコンテンツをフィルタリングする"""
>>>>>>> 4804a5634bfd6d7799d786cb093562d525b225ba
    if not keyword:
        logging.warning("キーワードが指定されていません。すべてのコンテンツを返します。")
        return data
    
<<<<<<< HEAD
    keyword_lower = keyword.lower()
    normalized_keyword = normalize_japanese_text(keyword_lower)
    
    # 本文
    if 'content' in data and data['content']:
        content_lower = data['content'].lower()
        normalized_content = normalize_japanese_text(content_lower)
        if (keyword_lower in content_lower) or (normalized_keyword in normalized_content):
            logging.info(f"キーワード '{keyword}' が本文に含まれます。")
            return data
    
    # タイトル
    if 'title' in data and data['title']:
        title_lower = data['title'].lower()
        normalized_title = normalize_japanese_text(title_lower)
        if (keyword_lower in title_lower) or (normalized_keyword in normalized_title):
            logging.info(f"キーワード '{keyword}' がタイトルに含まれます。")
            return data
    
    # 説明
    if 'description' in data and data['description']:
        desc_lower = data['description'].lower()
        normalized_desc = normalize_japanese_text(desc_lower)
        if (keyword_lower in desc_lower) or (normalized_keyword in normalized_desc):
            logging.info(f"キーワード '{keyword}' が説明に含まれます。")
            return data
    
    logging.info(f"キーワード '{keyword}' は見つかりませんでした。")
=======
    # キーワードを小文字に変換（大文字小文字を区別しない検索のため）
    keyword_lower = keyword.lower()
    # 日本語キーワードを正規化
    normalized_keyword = normalize_japanese_text(keyword_lower)
    
    # コンテンツにキーワードが含まれているかチェック
    if 'content' in data and data['content']:
        content_lower = data['content'].lower()
        normalized_content = normalize_japanese_text(content_lower)
        if keyword_lower in content_lower or (normalized_keyword and normalized_keyword in normalized_content):
            logging.info(f"キーワード '{keyword}' が本文に見つかりました。")
            return data
    
    # タイトルにキーワードが含まれているかチェック
    if 'title' in data and data['title']:
        title_lower = data['title'].lower()
        normalized_title = normalize_japanese_text(title_lower)
        if keyword_lower in title_lower or (normalized_keyword and normalized_keyword in normalized_title):
            logging.info(f"キーワード '{keyword}' がタイトルに見つかりました。")
            return data
    
    # 説明にキーワードが含まれているかチェック
    if 'description' in data and data['description']:
        description_lower = data['description'].lower()
        normalized_description = normalize_japanese_text(description_lower)
        if keyword_lower in description_lower or (normalized_keyword and normalized_keyword in normalized_description):
            logging.info(f"キーワード '{keyword}' が説明に見つかりました。")
            return data
    
    logging.info(f"キーワード '{keyword}' が見つかりませんでした。")
>>>>>>> 4804a5634bfd6d7799d786cb093562d525b225ba
    return None

def main():
    parser = argparse.ArgumentParser(description='キーワードフィルタリング付きWebスクレイパー')
<<<<<<< HEAD
    
    parser.add_argument('url', help='スクレイピング先URL')
    parser.add_argument('--output-dir', '-o', default='data', help='出力先ディレクトリ（デフォルト: data）')
    parser.add_argument('--min-text-length', '-m', type=int, default=50,
                        help='本文として扱う最小文字数（デフォルト: 50）')
    parser.add_argument('--delay', '-d', type=float, default=1,
                        help='リクエスト間の待機秒（デフォルト: 1）')
    parser.add_argument('--user-agent', '-u',
                        help='カスタムUser-Agent文字列')
    parser.add_argument('--keyword', '-k',
                        help='フィルタリングするキーワード')
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='詳細なログ出力を有効にする（DEBUGレベル）')
    
    args = parser.parse_args()
    
    # --verbose が指定されたらログレベルをDEBUGに
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    logging.info(f"{args.url} のスクレイピング開始...")
    scraped_data = scrape_website(
=======
    parser.add_argument('url', help='スクレイピングするWebサイトのURL')
    parser.add_argument('--output-dir', '-o', default='data', help='出力ディレクトリ（デフォルト: data）')
    parser.add_argument('--min-text-length', '-m', type=int, default=50, help='本文として扱う最小テキスト長（デフォルト: 50）')
    parser.add_argument('--delay', '-d', type=float, default=1, help='リクエスト間の待機時間（秒）（デフォルト: 1）')
    parser.add_argument('--user-agent', '-u', help='カスタムユーザーエージェント')
    parser.add_argument('--keyword', '-k', help='フィルタリングするキーワード')
    
    args = parser.parse_args()
    
    # スクレイピングの実行
    logging.info(f"{args.url} のスクレイピングを開始します...")
    result = scrape_website(
>>>>>>> 4804a5634bfd6d7799d786cb093562d525b225ba
        url=args.url,
        output_dir=args.output_dir,
        min_text_length=args.min_text_length,
        delay=args.delay,
        user_agent=args.user_agent
    )
    
<<<<<<< HEAD
    if not scraped_data:
        logging.error("スクレイピングに失敗しました。")
        return
    
    # キーワード指定がない場合は、実行時に聞く
=======
    if not result:
        logging.error("スクレイピングに失敗しました。")
        return
    
    # キーワードの入力を促す（コマンドライン引数で指定されていない場合）
>>>>>>> 4804a5634bfd6d7799d786cb093562d525b225ba
    keyword = args.keyword
    if not keyword:
        keyword = input("フィルタリングするキーワードを入力してください: ")
    
<<<<<<< HEAD
    filtered_data = filter_content_by_keyword(scraped_data, keyword)
    
    if filtered_data:
        logging.info(f"キーワード '{keyword}' を含むコンテンツが見つかりました！")
        
        # 保存先ディレクトリを作成
        os.makedirs(args.output_dir, exist_ok=True)
        
        domain = urlparse(args.url).netloc.replace('.', '_')
=======
    # キーワードでフィルタリング
    filtered_result = filter_content_by_keyword(result, keyword)
    
    if filtered_result:
        logging.info(f"キーワード '{keyword}' を含むコンテンツが見つかりました。")
        
        # 保存用のディレクトリを作成
        os.makedirs(args.output_dir, exist_ok=True)
        
        # ドメイン名を取得してファイル名に使用
        domain = urlparse(args.url).netloc.replace('.', '_')
        
        # タイムスタンプを含むファイル名を生成
>>>>>>> 4804a5634bfd6d7799d786cb093562d525b225ba
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        json_filename = f"{args.output_dir}/{domain}_{timestamp}_filtered.json"
        csv_filename = f"{args.output_dir}/{domain}_{timestamp}_filtered.csv"
        
<<<<<<< HEAD
        save_to_json(filtered_data, json_filename)
        save_to_csv(filtered_data, csv_filename)
        
        logging.info("フィルタリング結果を保存しました。")
    else:
        logging.warning(f"キーワード '{keyword}' を含むコンテンツはありませんでした。")
=======
        # JSONとCSVに保存
        save_to_json(filtered_result, json_filename)
        save_to_csv(filtered_result, csv_filename)
        
        logging.info(f"フィルタリングされたデータを保存しました。")
    else:
        logging.warning(f"キーワード '{keyword}' を含むコンテンツは見つかりませんでした。")
>>>>>>> 4804a5634bfd6d7799d786cb093562d525b225ba

if __name__ == "__main__":
    main()

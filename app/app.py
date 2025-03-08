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

# ロギングの初期設定（後でverboseで変更可能）
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)

# デフォルトのユーザーエージェント
HEADERS = {
    'User-Agent': (
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
        'AppleWebKit/537.36 (KHTML, like Gecko) '
        'Chrome/91.0.4472.124 Safari/537.36'
    )
}

# リクエスト間の待機時間（秒）
REQUEST_DELAY = 1

def check_robots_txt(url):
    """robots.txtをチェックしてURLへのアクセスが許可されているか確認"""
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
        logging.warning(f"robots.txtの確認中にエラー: {e}")
        return True  # 失敗した場合は許可する

def get_absolute_url(base_url, relative_url):
    """相対URLを絶対URLに変換"""
    if not relative_url:
        return None
    if relative_url.startswith(('http://', 'https://')):
        return relative_url
    return urljoin(base_url, relative_url)

def save_to_json(data, filename):
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
        csv_data = {}
        for key, value in data.items():
            if isinstance(value, list):
                csv_data[key] = ','.join(value)
            else:
                csv_data[key] = value
        writer.writerow(csv_data)
    logging.info(f"✅ CSVファイルを保存: {filename}")

def extract_content(soup, url, min_text_length=50):
    """Webページからコンテンツを抽出する汎用関数"""
    data = {}
    data['url'] = url
    
    # タイトル
    data['title'] = soup.title.text.strip() if soup.title else "No Title"
    logging.info(f"ページタイトル: {data['title']}")
    
    # og:title
    if data['title'] == "No Title":
        og_title = soup.find('meta', property='og:title')
        if og_title:
            data['title'] = og_title.get('content', 'No Title')
            logging.info(f"Open Graph タイトル: {data['title']}")
    
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
        elements = soup.select(selector)
        if elements:
            for element in elements:
                content_candidates.append(element.get_text(strip=True))
    
    # pタグまとめ
    paragraphs = []
    for p in soup.find_all('p'):
        text = p.text.strip()
        if len(text) > min_text_length:
            paragraphs.append(text)
    if paragraphs:
        content_candidates.append("\n\n".join(paragraphs))
    
    # 最長の候補を本文とみなす
    if content_candidates:
        data['content'] = max(content_candidates, key=len)
        logging.info(f"本文を抽出（{len(data['content'])}文字）")
        logging.info(f"プレビュー: {data['content'][:150]}...")
    else:
        data['content'] = ""
        logging.warning("本文が見つかりませんでした")
    
    # 画像
    logging.info("画像を抽出中...")
    images = []
    og_image = soup.find('meta', property='og:image')
    if og_image:
        img_url = og_image.get('content', '')
        if img_url:
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
    else:
        logging.warning("リンクが見つかりませんでした")
    
    return data

def scrape_website(url, output_dir='data', min_text_length=50,
                   delay=REQUEST_DELAY, user_agent=None):
    """指定したURLをスクレイピングする"""
    
    logging.info(f"{url} のスクレイピングを開始！")
    
    headers = HEADERS.copy()
    if user_agent:
        headers['User-Agent'] = user_agent
    
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
        return None
    except requests.exceptions.RequestException as e:
        logging.error(f"リクエストエラー: {e}")
        return None
    except Exception as e:
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
    if not keyword:
        logging.warning("キーワードが指定されていません。すべてのコンテンツを返します。")
        return data
    
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
    return None

def main():
    parser = argparse.ArgumentParser(description='キーワードフィルタリング付きWebスクレイパー')
    
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
        url=args.url,
        output_dir=args.output_dir,
        min_text_length=args.min_text_length,
        delay=args.delay,
        user_agent=args.user_agent
    )
    
    if not scraped_data:
        logging.error("スクレイピングに失敗しました。")
        return
    
    # キーワード指定がない場合は、実行時に聞く
    keyword = args.keyword
    if not keyword:
        keyword = input("フィルタリングするキーワードを入力してください: ")
    
    filtered_data = filter_content_by_keyword(scraped_data, keyword)
    
    if filtered_data:
        logging.info(f"キーワード '{keyword}' を含むコンテンツが見つかりました！")
        
        # 保存先ディレクトリを作成
        os.makedirs(args.output_dir, exist_ok=True)
        
        domain = urlparse(args.url).netloc.replace('.', '_')
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        json_filename = f"{args.output_dir}/{domain}_{timestamp}_filtered.json"
        csv_filename = f"{args.output_dir}/{domain}_{timestamp}_filtered.csv"
        
        save_to_json(filtered_data, json_filename)
        save_to_csv(filtered_data, csv_filename)
        
        logging.info("フィルタリング結果を保存しました。")
    else:
        logging.warning(f"キーワード '{keyword}' を含むコンテンツはありませんでした。")

if __name__ == "__main__":
    main()

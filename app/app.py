import sys
import argparse
import logging
from generic_scraper import scrape_website, save_to_json, save_to_csv
import os
from datetime import datetime
from urllib.parse import urlparse

# ロギングの設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

def filter_content_by_keyword(data, keyword):
    """キーワードに基づいてコンテンツをフィルタリングする"""
    if not keyword:
        logging.warning("キーワードが指定されていません。すべてのコンテンツを返します。")
        return data
    
    # キーワードを小文字に変換（大文字小文字を区別しない検索のため）
    keyword_lower = keyword.lower()
    
    # コンテンツにキーワードが含まれているかチェック
    if 'content' in data and data['content']:
        if keyword_lower in data['content'].lower():
            logging.info(f"キーワード '{keyword}' が本文に見つかりました。")
            return data
    
    # タイトルにキーワードが含まれているかチェック
    if 'title' in data and data['title']:
        if keyword_lower in data['title'].lower():
            logging.info(f"キーワード '{keyword}' がタイトルに見つかりました。")
            return data
    
    # 説明にキーワードが含まれているかチェック
    if 'description' in data and data['description']:
        if keyword_lower in data['description'].lower():
            logging.info(f"キーワード '{keyword}' が説明に見つかりました。")
            return data
    
    logging.info(f"キーワード '{keyword}' が見つかりませんでした。")
    return None

def main():
    parser = argparse.ArgumentParser(description='キーワードフィルタリング付きWebスクレイパー')
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
        url=args.url,
        output_dir=args.output_dir,
        min_text_length=args.min_text_length,
        delay=args.delay,
        user_agent=args.user_agent
    )
    
    if not result:
        logging.error("スクレイピングに失敗しました。")
        return
    
    # キーワードの入力を促す（コマンドライン引数で指定されていない場合）
    keyword = args.keyword
    if not keyword:
        keyword = input("フィルタリングするキーワードを入力してください: ")
    
    # キーワードでフィルタリング
    filtered_result = filter_content_by_keyword(result, keyword)
    
    if filtered_result:
        logging.info(f"キーワード '{keyword}' を含むコンテンツが見つかりました。")
        
        # 保存用のディレクトリを作成
        os.makedirs(args.output_dir, exist_ok=True)
        
        # ドメイン名を取得してファイル名に使用
        domain = urlparse(args.url).netloc.replace('.', '_')
        
        # タイムスタンプを含むファイル名を生成
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        json_filename = f"{args.output_dir}/{domain}_{timestamp}_filtered.json"
        csv_filename = f"{args.output_dir}/{domain}_{timestamp}_filtered.csv"
        
        # JSONとCSVに保存
        save_to_json(filtered_result, json_filename)
        save_to_csv(filtered_result, csv_filename)
        
        logging.info(f"フィルタリングされたデータを保存しました。")
    else:
        logging.warning(f"キーワード '{keyword}' を含むコンテンツは見つかりませんでした。")

if __name__ == "__main__":
    main()

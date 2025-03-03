import sys
import requests
from bs4 import BeautifulSoup

sys.stdout.reconfigure(line_buffering=True)  # ログをリアルタイムで表示

URL = "https://news.yahoo.co.jp/expert/articles/31a65afbecc42b3780a6761a39f0c511a0f20948"
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

print("🟢 クローラーを開始しました！")

try:
    print("🔍 Webページを取得中...")

    response = requests.get(URL, headers=HEADERS)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        
        # タイトルの取得
        title = soup.title.text if soup.title else "No Title"
        print(f"✅ ページのタイトル: {title}")
        
        # 記事本文の取得
        print("🔍 記事本文を抽出中...")
        
        # 記事の段落を取得
        paragraphs = soup.find_all('p')
        article_paragraphs = []
        
        # 記事の本文を含む可能性のある段落を抽出（短すぎる段落は除外）
        for p in paragraphs:
            text = p.text.strip()
            # 50文字以上の段落を記事本文として扱う
            if len(text) > 50:
                article_paragraphs.append(text)
        
        if article_paragraphs:
            print("✅ 記事本文:")
            for i, paragraph in enumerate(article_paragraphs):
                print(f"  段落 {i+1}: {paragraph}")
        else:
            print("❌ 記事本文が見つかりませんでした")
            
        # 記事全体を一つの文字列として結合
        article_body = "\n\n".join(article_paragraphs)
        
        # 画像URLの取得
        print("\n🔍 画像URLを抽出中...")
        
        # 画像要素を取得
        images = soup.find_all('img')
        article_images = []
        
        # 記事の画像を抽出（ニュース記事の画像に特徴的なURLパターンを持つものを選択）
        for img in images:
            src = img.get('src', '')
            if src and ('newsatcl-pctr' in src or 'news-pctr' in src):
                article_images.append(src)
        
        # 図（figure）要素内の画像も取得
        figures = soup.find_all('figure')
        for fig in figures:
            img = fig.find('img')
            if img and img.get('src'):
                src = img.get('src')
                if src not in article_images:  # 重複を避ける
                    article_images.append(src)
        
        if article_images:
            print("✅ 画像URL:")
            for i, img_url in enumerate(article_images):
                print(f"  画像 {i+1}: {img_url}")
        else:
            print("❌ 画像が見つかりませんでした")
    else:
        print(f"❌ HTTPエラー: {response.status_code}")

except Exception as e:
    print(f"⚠️ 例外発生: {e}")

print("✅ クローリング完了！")

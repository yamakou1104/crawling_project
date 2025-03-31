import logging
from celery_app import app
from app import scrape_website, filter_content_by_keyword

@app.task
def scrape_url(url, output_dir='data', min_text_length=50, delay=1, user_agent=None, keyword=None, summarize=False):
    """単一URLのスクレイピングを行うタスク"""
    logging.info(f"スケジュールされたタスク: {url} のスクレイピングを開始します...")
    
    # スクレイピングの実行
    result = scrape_website(
        url=url,
        output_dir=output_dir,
        min_text_length=min_text_length,
        delay=delay,
        user_agent=user_agent
    )
    
    if not result:
        logging.error(f"{url} のスクレイピングに失敗しました。")
        return None
    
    # キーワードフィルタリング（指定されている場合）
    if keyword:
        logging.info(f"キーワード '{keyword}' でフィルタリングします...")
        filtered_result = filter_content_by_keyword(result, keyword)
        if filtered_result:
            logging.info(f"キーワード '{keyword}' を含むコンテンツが見つかりました。")
            return filtered_result
        else:
            logging.info(f"キーワード '{keyword}' を含むコンテンツは見つかりませんでした。")
            return None
    
    return result

@app.task
def scrape_scheduled_urls(urls, **kwargs):
    """複数URLのスクレイピングを行うタスク"""
    results = []
    for url in urls:
        result = scrape_url.delay(url, **kwargs)
        results.append(result.id)
    
    return results

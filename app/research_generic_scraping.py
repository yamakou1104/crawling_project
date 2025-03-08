import requests
from bs4 import BeautifulSoup
import json
from urllib.parse import urlparse

# Test URLs for different types of websites
urls = [
    'https://news.yahoo.co.jp/expert/articles/31a65afbecc42b3780a6761a39f0c511a0f20948',  # Yahoo News
    'https://en.wikipedia.org/wiki/Web_scraping',  # Wikipedia
    'https://github.com/about',  # GitHub
]

# Common selectors for different types of content
title_selectors = ['title', 'h1', '.title', '#title', '.headline', '.post-title']
content_selectors = ['article', '.article', '#article', '.content', '#content', '.post-content', '.entry-content', 'main', '.main', '#main']
image_selectors = ['img', '.image', '.img', '.featured-image', '.post-image']
link_selectors = ['a', '.link', '.url']

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

print('Investigating common patterns for generic website scraping...')
print('-' * 80)

for url in urls:
    try:
        print(f'Testing URL: {url}')
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            domain = urlparse(url).netloc
            
            print(f'\nAnalyzing website: {domain}')
            
            # Test title selectors
            print('\nTitle selectors:')
            for selector in title_selectors:
                elements = soup.select(selector)
                if elements:
                    print(f'  {selector}: {len(elements)} elements found')
                    print(f'  First element text: {elements[0].text.strip()[:50]}...')
            
            # Test content selectors
            print('\nContent selectors:')
            for selector in content_selectors:
                elements = soup.select(selector)
                if elements:
                    print(f'  {selector}: {len(elements)} elements found')
                    print(f'  First element text length: {len(elements[0].text.strip())} characters')
            
            # Test image selectors
            print('\nImage selectors:')
            for selector in image_selectors:
                elements = soup.select(selector)
                if elements:
                    print(f'  {selector}: {len(elements)} elements found')
                    if 'src' in elements[0].attrs:
                        print(f'  First element src: {elements[0]["src"][:50]}...')
            
            # Test link selectors
            print('\nLink selectors:')
            for selector in link_selectors:
                elements = soup.select(selector)
                if elements:
                    print(f'  {selector}: {len(elements)} elements found')
                    if 'href' in elements[0].attrs:
                        print(f'  First element href: {elements[0]["href"][:50]}...')
            
            # Test meta tags
            print('\nMeta tags:')
            meta_description = soup.find('meta', attrs={'name': 'description'})
            if meta_description:
                print(f'  Description: {meta_description.get("content", "")[:50]}...')
            
            meta_keywords = soup.find('meta', attrs={'name': 'keywords'})
            if meta_keywords:
                print(f'  Keywords: {meta_keywords.get("content", "")[:50]}...')
            
            # Test text density
            print('\nText density:')
            paragraphs = soup.find_all('p')
            if paragraphs:
                print(f'  Found {len(paragraphs)} paragraphs')
                long_paragraphs = [p for p in paragraphs if len(p.text.strip()) > 100]
                print(f'  Found {len(long_paragraphs)} paragraphs with >100 characters')
            
            divs = soup.find_all('div')
            if divs:
                print(f'  Found {len(divs)} divs')
                text_rich_divs = [d for d in divs if len(d.text.strip()) > 500]
                print(f'  Found {len(text_rich_divs)} divs with >500 characters')
            
            # Test schema.org structured data
            print('\nStructured data:')
            schema_elements = soup.find_all('script', type='application/ld+json')
            if schema_elements:
                print(f'  Found {len(schema_elements)} schema.org elements')
            
            # Test Open Graph tags
            print('\nOpen Graph tags:')
            og_title = soup.find('meta', property='og:title')
            if og_title:
                print(f'  og:title: {og_title.get("content", "")[:50]}...')
            
            og_description = soup.find('meta', property='og:description')
            if og_description:
                print(f'  og:description: {og_description.get("content", "")[:50]}...')
            
            og_image = soup.find('meta', property='og:image')
            if og_image:
                print(f'  og:image: {og_image.get("content", "")[:50]}...')
            
            # Test relative URLs
            print('\nRelative URLs:')
            relative_links = [a for a in soup.find_all('a', href=True) if not a['href'].startswith(('http://', 'https://', 'javascript:', 'mailto:'))]
            if relative_links:
                print(f'  Found {len(relative_links)} relative links')
                print(f'  Examples: {[link["href"] for link in relative_links[:3]]}')
            
            relative_images = [img for img in soup.find_all('img', src=True) if not img['src'].startswith(('http://', 'https://'))]
            if relative_images:
                print(f'  Found {len(relative_images)} relative image URLs')
                print(f'  Examples: {[img["src"] for img in relative_images[:3]]}')
            
            print('-' * 80)
        else:
            print(f'Error: HTTP status code {response.status_code}')
    
    except Exception as e:
        print(f'Error: {e}')
    
    print('\n' + '=' * 80 + '\n')

print('\nResearch findings:')
print('''
Based on the analysis, here are some effective methods for generic website scraping:

1. Title extraction:
   - The <title> tag is the most reliable source for page titles
   - Fallback to h1 or other heading elements if title is not available

2. Content extraction:
   - Look for semantic elements like <article>, <main>, or <section>
   - Use common class/id patterns like .content, #content, .article, etc.
   - Measure text density to identify content-rich areas
   - Collect all paragraphs (p tags) with substantial text

3. Image extraction:
   - Collect all <img> elements
   - Handle relative URLs by converting to absolute URLs
   - Filter out small icons and decorative images based on size attributes
   - Look for images in content-rich areas

4. Link extraction:
   - Collect all <a> elements with href attributes
   - Handle relative URLs by converting to absolute URLs
   - Filter out javascript: and mailto: links
   - Collect both URL and link text for context

5. Metadata extraction:
   - Check for meta description and keywords
   - Look for Open Graph tags (og:title, og:description, og:image)
   - Check for schema.org structured data in JSON-LD format

6. Handling different website structures:
   - Use multiple extraction methods and select the best result
   - Implement fallback mechanisms for each content type
   - Use text density as a heuristic for finding main content
   - Consider the DOM structure and nesting levels

7. Challenges and solutions:
   - JavaScript-rendered content: Consider using a headless browser
   - Rate limiting: Implement delays between requests
   - Robots.txt: Check and respect robots.txt rules
   - Different languages: Use encoding detection and handle Unicode
   - Dynamic content: Implement retry mechanisms
''')

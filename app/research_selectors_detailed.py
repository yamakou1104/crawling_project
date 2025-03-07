import requests
from bs4 import BeautifulSoup
import re

URL = 'https://news.yahoo.co.jp/expert/articles/31a65afbecc42b3780a6761a39f0c511a0f20948'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

response = requests.get(URL, headers=headers)
soup = BeautifulSoup(response.text, 'html.parser')

print('TITLE:')
print(soup.title.text if soup.title else 'No Title')
print('\n' + '-'*80 + '\n')

# Try to find the article content using various common selectors
print('ARTICLE CONTENT SEARCH:')

# Method 1: Look for common article content containers
selectors_to_try = [
    'article', '.article', '#article', 
    '.articleBody', '#articleBody',
    '.article-body', '#article-body',
    '.article-content', '#article-content',
    '.article_text', '#article_text',
    '.article-detail', '#article-detail',
    '.news-detail', '#news-detail',
    '.news-content', '#news-content',
    '.news-body', '#news-body',
    '.main-content', '#main-content',
    '.main', '#main',
    '.content', '#content'
]

for selector in selectors_to_try:
    elements = soup.select(selector)
    if elements:
        print(f'Found {len(elements)} elements with selector "{selector}"')
        print(f'First element text preview: {elements[0].text[:150].strip()}...\n')

# Method 2: Look for paragraphs that might contain article text
paragraphs = soup.find_all('p')
print(f'Found {len(paragraphs)} paragraph elements')
if paragraphs:
    for i, p in enumerate(paragraphs[:5]):  # Show first 5 paragraphs
        text = p.text.strip()
        if text and len(text) > 50:  # Only show substantial paragraphs
            print(f'Paragraph {i+1}: {text[:150]}...')
    print('...\n')

# Method 3: Look for div elements with substantial text
divs = soup.find_all('div')
print(f'Found {len(divs)} div elements')
substantial_divs = []
for div in divs:
    text = div.text.strip()
    if text and len(text) > 200:  # Only consider divs with substantial text
        substantial_divs.append((div, text))

print(f'Found {len(substantial_divs)} divs with substantial text')
for i, (div, text) in enumerate(substantial_divs[:3]):  # Show first 3 substantial divs
    print(f'Div {i+1} classes: {div.get("class")}')
    print(f'Div {i+1} id: {div.get("id")}')
    print(f'Div {i+1} text preview: {text[:150]}...\n')

# Method 4: Look for specific Yahoo News selectors
print('\n' + '-'*80 + '\n')
print('YAHOO NEWS SPECIFIC SELECTORS:')

yahoo_selectors = [
    '.yjDirectSLinkTarget', '.ExpertArticle', '.ExpertArticle_body',
    '.ExpertArticle_content', '.ExpertArticle_text', '.expert-article',
    '.expert-article-body', '.expert-article-content', '.expert-article-text',
    '.news-detail-body', '.news-detail-content', '.news-detail-text'
]

for selector in yahoo_selectors:
    elements = soup.select(selector)
    if elements:
        print(f'Found {len(elements)} elements with selector "{selector}"')
        print(f'First element text preview: {elements[0].text[:150].strip()}...\n')

# Method 5: Look for image elements
print('\n' + '-'*80 + '\n')
print('IMAGE SEARCH:')

# Find all images
all_images = soup.find_all('img')
print(f'Found {len(all_images)} image elements')

# Filter for likely article images (exclude icons, logos, etc.)
article_images = []
for img in all_images:
    src = img.get('src', '')
    if src and ('news' in src.lower() or 'article' in src.lower() or 'pctr' in src.lower()):
        article_images.append(img)

print(f'Found {len(article_images)} likely article images')
for i, img in enumerate(article_images[:5]):  # Show first 5 article images
    print(f'Image {i+1}: {img.get("src")}')
    print(f'Image {i+1} alt: {img.get("alt")}')
    print(f'Image {i+1} class: {img.get("class")}\n')

# Method 6: Look for figure elements that might contain images
figures = soup.find_all('figure')
print(f'Found {len(figures)} figure elements')
for i, fig in enumerate(figures[:3]):  # Show first 3 figures
    img = fig.find('img')
    if img:
        print(f'Figure {i+1} image: {img.get("src")}')
    figcaption = fig.find('figcaption')
    if figcaption:
        print(f'Figure {i+1} caption: {figcaption.text.strip()}')
    print()

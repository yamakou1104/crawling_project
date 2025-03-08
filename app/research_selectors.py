import requests
from bs4 import BeautifulSoup

URL = 'https://news.yahoo.co.jp/expert/articles/31a65afbecc42b3780a6761a39f0c511a0f20948'
response = requests.get(URL)
soup = BeautifulSoup(response.text, 'html.parser')

# Print the title for reference
print('TITLE:')
print(soup.title.text if soup.title else 'No Title')
print('\n' + '-'*80 + '\n')

# Examine potential article body selectors
print('POTENTIAL ARTICLE BODY SELECTORS:')
article_main = soup.select('.article_body')
print(f'Article body (.article_body): Found {len(article_main)} elements')
if article_main:
    print(f'First few characters: {article_main[0].text[:150]}...\n')

article_content = soup.select('.article_content')
print(f'Article content (.article_content): Found {len(article_content)} elements')
if article_content:
    print(f'First few characters: {article_content[0].text[:150]}...\n')

article_text = soup.select('.yjDirectSLinkTarget')
print(f'Article text (.yjDirectSLinkTarget): Found {len(article_text)} elements')
if article_text:
    print(f'First few characters: {article_text[0].text[:150]}...\n')

# Examine potential image selectors
print('\n' + '-'*80 + '\n')
print('POTENTIAL IMAGE SELECTORS:')
images = soup.select('img')
print(f'All images: Found {len(images)} elements')
if images:
    for i, img in enumerate(images[:5]):  # Show first 5 images
        print(f'Image {i+1}: {img.get("src")}')
    print('...\n')

article_images = soup.select('.article_body img')
print(f'Article body images (.article_body img): Found {len(article_images)} elements')
if article_images:
    for i, img in enumerate(article_images[:5]):
        print(f'Image {i+1}: {img.get("src")}')
    print('...\n')

main_images = soup.select('.article_main img')
print(f'Main article images (.article_main img): Found {len(main_images)} elements')
if main_images:
    for i, img in enumerate(main_images[:5]):
        print(f'Image {i+1}: {img.get("src")}')
    print('...\n')

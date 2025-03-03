# Generic Web Scraper

A flexible web scraper that can extract and save data from any website.

## Features
- Extract titles, content, images, and links from any website
- Save data in both JSON and CSV formats
- Handle different website structures and layouts
- Convert relative URLs to absolute URLs
- Respect robots.txt rules
- Rate limiting to avoid overloading websites
- Detailed error handling and logging
- Command-line interface for easy use

## Installation
```bash
pip install -r app/requirements.txt
```

## Usage
```bash
python app/generic_scraper.py https://example.com
```

### Options
- `--output-dir`, `-o`: Output directory (default: data)
- `--min-text-length`, `-m`: Minimum text length for content extraction (default: 50)
- `--delay`, `-d`: Request delay in seconds (default: 1)
- `--user-agent`, `-u`: Custom user agent
- `--no-robots`: Disable robots.txt checking (not recommended)
- `--verbose`, `-v`: Enable verbose logging

## Output
The scraper will create two files in the output directory:
- `domain_timestamp.json`: Data in JSON format
- `domain_timestamp.csv`: Data in CSV format

## Data Structure
The extracted data includes:
- `title`: Page title
- `url`: Page URL
- `description`: Meta description (if available)
- `content`: Main content
- `images`: List of image URLs
- `links`: List of link URLs

## Extraction Methods
The scraper uses multiple extraction methods to handle different website structures:

1. **Title extraction**:
   - Primary: `<title>` tag
   - Fallback: Open Graph `og:title` meta tag

2. **Content extraction**:
   - Method 1: Look for semantic elements like `<article>`, `<main>`, or `<section>`
   - Method 2: Collect all paragraphs (`<p>` tags) with substantial text
   - Method 3: Look for large text blocks in `<div>` elements
   - Method 4: Extract content from schema.org structured data

3. **Image extraction**:
   - Collect all `<img>` elements
   - Look for Open Graph `og:image` meta tag
   - Handle relative URLs by converting to absolute URLs

4. **Link extraction**:
   - Collect all `<a>` elements with href attributes
   - Handle relative URLs by converting to absolute URLs
   - Filter out javascript: and mailto: links

## Examples
```bash
# Basic usage
python app/generic_scraper.py https://example.com

# Specify output directory
python app/generic_scraper.py https://example.com --output-dir output

# Set minimum text length for content extraction
python app/generic_scraper.py https://example.com --min-text-length 100

# Set request delay
python app/generic_scraper.py https://example.com --delay 2

# Use custom user agent
python app/generic_scraper.py https://example.com --user-agent "MyBot/1.0"

# Enable verbose logging
python app/generic_scraper.py https://example.com --verbose
```

## Notes
- The scraper respects robots.txt rules by default
- Rate limiting is implemented to avoid overloading websites
- Relative URLs are automatically converted to absolute URLs
- The scraper handles different website structures and layouts

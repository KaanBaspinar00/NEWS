import datetime
import requests
from bs4 import BeautifulSoup
import asyncio
import pandas as pd

"""

requirments:
pip install beautifulsoup4 asyncio pandas requests datetime

"""
#################################################################################################
                                    #getArticleContent#
###################################000000000000000000000#########################################

verifyMessages = [
    "you are human",
    "are you human",
    "i'm not a robot",
    "recaptcha"
]

def getArticleContent(articles, filterWords):
    processedArticles = []
    for article in articles:
        processedArticle = extractArticleContentAndFavicon(article, filterWords)
        processedArticles.append(processedArticle)
    return processedArticles

def extractArticleContentAndFavicon(article, filterWords):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'DNT': '1',
    }
    try:
        response = requests.get(article['url'], headers=headers, timeout=1)
        if response.status_code == 200:
            print("response success")
            content = response.text

            favicon = extractFavicon(content)

            soup = BeautifulSoup(content, 'html.parser')
            articleContent = soup.get_text(separator='\n')

            if not articleContent:
                return { **article, 'content': '', 'favicon': favicon }

            hasVerifyMessage = any(w in articleContent.lower() for w in verifyMessages)
            if hasVerifyMessage:
                return { **article, 'content': '', 'favicon': favicon }

            cleanedText = cleanText(articleContent, filterWords)

            if len(cleanedText.split(' ')) < 100:  # Example threshold: 100 words
                return { **article, 'content': '', 'favicon': favicon }

            return { **article, 'content': cleanedText, 'favicon': favicon }
        else:
            print("Response fail")
            return { **article, 'content': '', 'favicon': '' }
    except Exception as error:
        return { **article, 'content': '', 'favicon': '' }

def extractFavicon(content):
    soup = BeautifulSoup(content, 'html.parser')
    link = soup.find('link', rel=['icon', 'shortcut icon'])
    return link['href'] if link else ''

def cleanText(text, filterWords):
    unwantedKeywords = [
        "subscribe now",
        "sign up",
        "newsletter",
        "subscribe now",
        "sign up for our newsletter",
        "exclusive offer",
        "limited time offer",
        "free trial",
        "download now",
        "join now",
        "register today",
        "special promotion",
        "promotional offer",
        "discount code",
        "early access",
        "sneak peek",
        "save now",
        "don't miss out",
        "act now",
        "last chance",
        "expires soon",
        "giveaway",
        "free access",
        "premium access",
        "unlock full access",
        "buy now",
        "learn more",
        "click here",
        "follow us on",
        "share this article",
        "connect with us",
        "advertisement",
        "sponsored content",
        "partner content",
        "affiliate links",
        "click here",
        "for more information",
        "you may also like",
        "we think you'll like",
        "from our network",
        *filterWords
    ]
    return '\n'.join(
        line for line in map(str.strip, text.split('\n'))
        if len(line.split(' ')) > 4 and not any(keyword in line.lower() for keyword in unwantedKeywords)
    )

###################################000000000000000000000#########################################



#################################################################################################
                                    #buildQueryString#
###################################000000000000000000000#########################################

def buildQueryString(query):
    # Sanity check
    if not query or not isinstance(query, dict) or len(query) == 0:
        return ''
    # Build and return query string
    return '&'.join([f"{key}={query[key]}" for key in query])

###################################000000000000000000000#########################################






#################################################################################################
                                    #get_pretty_url#
###################################000000000000000000000#########################################

import re
import base64
import json

def get_pretty_url(url):
    base64_pattern = r"articles\/([A-Za-z0-9+_\-\/=]+)"
    match = re.search(base64_pattern, url)

    if match and match.group(1):
        base64_encoded_url = match.group(1).replace("-", "+").replace("_", "/")
        # Add padding to the base64_encoded_url
        base64_encoded_url += "=" * ((4 - len(base64_encoded_url) % 4) % 4)
        try:
            decoded_url = base64.urlsafe_b64decode(base64_encoded_url).decode("latin1")

            # Remove any trailing "R" if it's the last character
            decoded_url = decoded_url.rstrip("R")

            # Remove non-ASCII characters and split by potential delimiters
            parts = re.split(r"[^\x20-\x7E]+", decoded_url)

            # Regular expression to validate and extract URLs
            url_pattern = r"(https?:\/\/[^\s]+)"
            cleaned_url = ""

            # Iterate over parts to find the first valid URL
            for part in parts:
                url_match = re.search(url_pattern, part)
                if url_match and url_match.group(1):
                    cleaned_url = url_match.group(1)
                    break  # Stop at the first match

            if cleaned_url:
                # Log the cleaned URL in a well-formatted JSON
                output = {
                    "originalUrl": url,
                    "cleanedUrl": cleaned_url
                }

                # print(json.dumps(output, indent=2))
                return cleaned_url
            else:
                print("No valid URL found in the decoded string:", decoded_url)
                return url
        except UnicodeDecodeError as error:
            print("Error decoding Base64 string:", base64_encoded_url, "Original URL:", url, "Error:", str(error))
            return url
    else:
        print("No Base64 segment found in the URL. Original URL:", url)
        return url

###################################000000000000000000000#########################################




#################################################################################################
                                    #googleNewsScraper#
###################################000000000000000000000#########################################


# Set the number of rows and columns displayed in the console
pd.set_option('display.max_rows', None)  # None means show all rows
pd.set_option('display.max_columns', None)  # None means show all columns

# Set the width of the display in characters
pd.set_option('display.width', None)  # None will make pandas use the current terminal width

# Set column width to a large number to ensure columns aren't truncated if they have long strings
pd.set_option('display.max_colwidth', None)  # None means show full width of column content

def googleNewsScraper(userConfig):
    time_before = "7d"
    config = {
        "prettyURLs": True,
        "getArticleContent": False,
        "timeframe": time_before,
        "puppeteerArgs": [],
    }
    config.update(userConfig)

    queryString = buildQueryString(config["queryVars"]) if config["queryVars"] else ""
    url = f"https://news.google.com/search?{queryString}&q={config['searchTerm']} when:{config.get('timeframe', time_before)}"
    print(f"SCRAPING NEWS FROM: {url}")

    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3",
        "Accept-Encoding": "gzip",
        "Accept-Language": "en-US,en;q=0.9,es;q=0.8",
        "Upgrade-Insecure-Requests": "1",
        "Referer": "https://www.google.com/"
    }
    cookies = {
        "CONSENT": f"YES+cb.{datetime.datetime.now().isoformat().split('T')[0].replace('-', '')}-04-p0.en-GB+FX+667"
    }
    response = requests.get(url, headers=headers, cookies=cookies)
    content = response.content

    soup = BeautifulSoup(content, 'html.parser')
    articles = soup.find_all('article')
    results = []
    urlChecklist = []

    for article in articles:
        link_element = article.find('a', href=lambda href: href and href.startswith('./article'))
        link = link_element.get('href').replace('./', 'https://news.google.com/') if link_element else None
        if link:
            urlChecklist.append(link)
        figure_element = article.find('figure')
        srcset = figure_element.find('img').get('srcset').split(' ') if figure_element and figure_element.find(
            'img') else []
        image = srcset[-2] if srcset else figure_element.find('img').get(
            'src') if figure_element and figure_element.find('img') else None
        if image and image.startswith('/'):
            image = f"https://news.google.com{image}"
        title_element = \
        article.find_all('div', {"class": 'm5k28'})[0].find_all('div', {"class": 'B6pJDd'})[0].find_all('div')[
            0].find_all('a')
        title = title_element[0].text
        source_element = article.find('div', {'data-n-tid': True})
        source = source_element.text if source_element else None
        datetime_element = article.time['datetime']
        datetime_str = datetime.datetime.fromisoformat(datetime_element[:-1])
        datetime_val = datetime.datetime.strptime(str(datetime_str), "%Y-%m-%d %H:%M:%S") if datetime_str else None
        time = datetime_val
        mainArticle = {
            "title": title,
            "link": link,
            "image": image,
            "source": source,
            # "datetime": datetime_val,
            "time": time
        }
        results.append(mainArticle)

    if config["prettyURLs"]:
        for result in results:
            new_link = get_pretty_url(result["link"])
            result["link"] = new_link

    if config["getArticleContent"]:
        filterWords = config.get("filterWords", [])
        results = asyncio.run(getArticleContent(results, filterWords))

    return results


user_config_me = {
    "searchTerm": "Israel",
    "queryVars": {"region": "US"},
    "timeframe": "1y"
    # Change this according to what Google News supports; you may need to adjust your scraper to run multiple times for each year.
}

# Call the function with the configuration dictionary
result = googleNewsScraper(user_config_me)

df = pd.DataFrame(result)

print(df)


import requests
from bs4 import BeautifulSoup
from textblob import TextBlob
import pandas as pd
from langdetect import detect

# Function to get sentiment polarity
def get_sentiment(text):
    blob = TextBlob(text)
    return blob.sentiment.polarity

# Function to detect language
def detect_language(text):
    try:
        return detect(text)
    except:
        return "unknown"
import re
# Function to categorize headline
def categorize_headline(headline):
    sports_keywords = [
    'cricket', 'football', 'sports', 'match', 'tournament', 'olympics',
    'player', 'athlete', 'fifa', 'ipl', 'score', 'medal', 'championship',
    'series', 'world cup', 'goal', 'coach', 'team', 'league', 'wicket'
    ]

    politics_keywords = [
    'election', 'politics', 'government', 'parliament', 'minister',
    'prime minister', 'modi', 'bjp', 'congress', 'pm', 'president',
    'cabinet', 'assembly', 'policy', 'bill', 'campaign', 'senate',
    'democracy', 'political', 'vote', 'lok sabha', 'rajya sabha'
    ]

    technology_keywords = [
    'technology', 'tech', 'gadget', 'ai', 'robotics', 'software',
    'it', 'startup', 'google', 'apple', 'microsoft', 'iphone',
    'android', 'cybersecurity', 'blockchain', 'data', 'cloud',
    'innovation', 'machine learning', 'metaverse', 'digital'
   ]

    entertainment_keywords = [
    'movie', 'actor', 'actress', 'bollywood', 'hollywood', 'music',
    'trailer', 'film', 'song', 'album', 'celebrity', 'theatre',
    'award', 'series', 'web series', 'netflix', 'ott', 'dance',
    'drama', 'comedy', 'director'
    ]

    world_keywords = [
    'world', 'global', 'international', 'united states', 'war', 'uk',
    'pakistan', 'china', 'ukraine', 'america', 'trump', 'terrorist',
    'us', 'england', 'j&k', 'india', 'visa', 'country', 'nato',
    'united nations', 'foreign', 'diplomatic', 'border', 'geopolitics',
    'embassy', 'eu', 'russia', 'israel', 'palestine'
    ]

    crime_keywords = [
    'crime', 'murder', 'theft', 'robbery', 'assault', 'violence',
    'rape', 'kidnap', 'hijack', 'horrific-crimes', 'arrested',
    'fraud', 'scam', 'cybercrime', 'drug', 'smuggling', 'gang',
    'shooting', 'terrorism', 'criminal', 'illegal', 'underworld',
    'extortion', 'prison', 'custody', 'firing'
     ]  

    judiciary_keywords = [
    'court', 'trial', 'verdict', 'judge', 'judiciary', 'justice',
    'petition', 'sentence', 'bail', 'lawsuit', 'legal', 'acquitted',
    'convicted', 'supreme court', 'high court', 'tribunal',
    'judgement', 'appeal', 'litigation'
    ]

    educational_keywords = [
    'cbse', 'final', 'key', 'paper', 'ssc', 'exam', 'answer',
    'result', 'neet', 'jee', 'gate', 'question', 'hall ticket',
    'admission', 'scholarship', 'education', 'rank', 'marks',
    'degree', 'university', 'college'
    ]

    health_keywords = [
    'health', 'hospital', 'doctor', 'vaccine', 'covid', 'virus',
    'disease', 'medical', 'nurse', 'surgery', 'treatment', 'patient',
    'infection', 'outbreak', 'wellness', 'cancer', 'mental health',
    'cardiac', 'blood', 'diabetes', 'medicine'
    ]



   
    #headline_words = re.findall(r'\b\w+\b', headline.lower())
    headline_lower = headline.lower()
    #headline_words = re.findall(r'\b\w+\b', headline.lower())

    if any(keyword in headline_lower for keyword in sports_keywords):
        return 'Sports'
    elif any(keyword in headline_lower for keyword in politics_keywords):
        return 'Politics'
    elif any(keyword in headline_lower for keyword in technology_keywords):
        return 'Technology'
    elif any(keyword in headline_lower for keyword in entertainment_keywords):
        return 'Entertainment'
    elif any(keyword in headline_lower for keyword in world_keywords):
        return 'World'
    elif any(keyword in headline_lower for keyword in judiciary_keywords):
        return 'Judiciary'
    elif any(keyword in headline_lower for keyword in crime_keywords):
        return 'Crime'
    elif any(keyword in headline_lower for keyword in educational_keywords):
        return 'Education'
    elif any(keyword in headline_lower for keyword in health_keywords):
        return 'Health'
    else:
        return 'General'

# Scrape the Times of India homepage
def scrape_toi():
    url = "https://timesofindia.indiatimes.com/"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    headlines = []
    categories = []
    urls = []
    languages = []
    sentiments = []
    polarities = []

    # Scrape all <a> tags with headlines
    for a_tag in soup.find_all('a', href=True):
        headline_text = a_tag.get_text(strip=True)
        link = a_tag['href']

        if headline_text and "/articleshow/" in link:
            if not link.startswith('http'):
                link = 'https://timesofindia.indiatimes.com' + link

            # categorize, language, sentiment, polarity
            category = categorize_headline(headline_text)
            lang = detect_language(headline_text)
            sentiment_value = get_sentiment(headline_text)
            polarity = 'Positive' if sentiment_value > 0 else 'Negative' if sentiment_value < 0 else 'Neutral'

            headlines.append(headline_text)
            categories.append(category)
            urls.append(link)
            languages.append(lang)
            sentiments.append(sentiment_value)
            polarities.append(polarity)

    # Dataframe creation
    df = pd.DataFrame({
        'Headline': headlines,
        'Category': categories,
        'URL': urls,
        'Language': languages,
        'Sentiment': sentiments,
        'Polarity': polarities,
    })

    # Add Image URL based on category
    category_image_mapping = {
        "Sports": "https://mediabrief.com/wp-content/uploads/2024/10/Image-YAS-Ministry-seeks-inputs-on-draft-Sports-Governance-Bill-MediaBrief.png",
        "Politics": "https://www.samanyagyan.com/images/cat/indian-politics.jpg",
        "Technology": "https://timestech.in/wp-content/uploads/2022/12/education.jpg",
        "Entertainment": "https://www.shutterstock.com/image-illustration/entertainment-related-word-infotext-graphic-260nw-112744108.jpg",
        "World": "https://static.vecteezy.com/system/resources/thumbnails/012/131/279/small/worldwide-global-earth-planet-flag-country-community-international-business-blue-sky-outdoor-government-politic-travel-together-agreement-exhibition-meeting-group-culture-corporation-unity-teamwork-photo.jpg",
        "Crime": "https://images.hindustantimes.com/img/2024/08/20/550x309/So-far-nine-persons--including-two-juveniles--invo_1709065177678_1724139986130.jpg",
        "Judiciary": "https://www.shutterstock.com/image-photo/legal-scales-judge-gavel-justice-260nw-2293288299.jpg",
        "General": "https://deadline.com/wp-content/uploads/2022/10/foxn.jpg",
        "Education" : "https://img.freepik.com/free-photo/book-with-green-board-background_1150-3837.jpg?semt=ais_hybrid&w=740",
        "Health":"https://t4.ftcdn.net/jpg/02/99/77/47/360_F_299774742_bC5FdQRrohGqAUxrTvOLFvrPVWoYyXqQ.jpg"
       }

    df['Image URL'] = df['Category'].map(category_image_mapping)

    # Save to CSV
    #df.to_csv('toi_headlines_with_all_info.csv', index=False)

    df.to_csv('toi_headlines_with_all_info.csv', index=False, quoting=1)

    print("Scraping completed! Data saved to 'toi_headlines_with_all_info.csv'.")

def main():
    scrape_toi()

if __name__ == "__main__":
    main()

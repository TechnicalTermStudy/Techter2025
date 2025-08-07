import re
import spacy
import wikipediaapi
import wikipedia
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import langdetect
from langdetect import detect
import time

try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    import subprocess
    subprocess.run(["python", "-m", "spacy", "download", "en_core_web_sm"])
    nlp = spacy.load("en_core_web_sm")

wikipedia.set_lang("en")
    
def preprocess_term(term):
    # preprocessing contexts using spaCy
    doc = nlp(term)
    print(f"{term} tagging results: {[(token.text, token.pos_) for token in doc]}")
    # if only one word for term
    if len(doc) == 1:
        token = doc[0]
        if token.pos_ == "VERB":
            return token.text
        if not token.is_stop:
            return token.lemma_
        return ""

    # if the first word for term is VERB
    if doc and doc[0].pos_ == "VERB":
        tokens = [token for token in doc[1:]]
    else:
        tokens = [token for token in doc]
    
    filtered_words = [token.lemma_ for token in tokens if not token.is_stop]

    return ' '.join(filtered_words).strip()

def google_search_and_fetch(term):

    # undetected-chromedriver
    options = uc.ChromeOptions()
    # Mac Safari User-Agent
    options.add_argument(
        "user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.1 Safari/605.1.15"
    )
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--lang=en-US")
    options.add_argument("--accept-lang=en-US")

    driver = uc.Chrome(options=options)
    print("Driver Done!")
    results_texts = []
    try:
        driver.get("https://www.google.com")
        print("open google")
        time.sleep(2)
        
        search_box = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "q"))
        )
        time.sleep(2)
        
        query = term + " meaning"
        search_box.send_keys(query)
        search_box.submit()

        # 
        div_xpath = (
            "//*[contains(@class, 'VwiC3b') and contains(@class, 'yXK7lf') "
            "and contains(@class, 'p4wth') and contains(@class, 'r025kc') "
            "and contains(@class, 'hJNv6b') and contains(@class, 'Hdw6tb')]"
        )

        # 
        div_elements = WebDriverWait(driver, 20).until(
            EC.presence_of_all_elements_located((By.XPATH, div_xpath))
        )
        div_elements = div_elements[:20]

        date_pattern = re.compile(
            r'^(?:\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4}|'
            r'(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2},\s+\d{4})\s*[—-]\s*'
        )
        
        for div_elem in div_elements:
            text = div_elem.text
            text_clean = re.sub(date_pattern, "", text)
            results_texts.append(text_clean)
        
        term_lower = term.lower()
        matched_snippets = [
            txt for txt in results_texts
            if term_lower in txt.lower()
        ]

    except Exception as e:
        print("Got error", e)
        matched_snippets = []
        

    if matched_snippets:
        
        all_sentences = []
        for text in matched_snippets:
            sentences = re.split(r'[.!?]', text)
            for sentence in sentences:
                if term_lower in sentence.lower():
                    
                    sentence_end = text[text.find(sentence) + len(sentence):].strip()
                    sentence = sentence.strip()
                    
                    if detect(sentence) == 'en':
                        if sentence_end.startswith('.'):
                            all_sentences.append((sentence + '.', 1))  # 1 end with .
                        elif sentence_end.startswith('...') or sentence_end.startswith('…'):
                            all_sentences.append((sentence + '...', 2))  # 2 end with ...
                            
        if all_sentences:
            all_sentences.sort(key=lambda x: x[1])
            return all_sentences[0][0]
        
    driver.quit()
    return None

def get_term_explanation_knowledge(term):
    try:
        preprocessed_term = preprocess_term(term=term)
        print(f"preprocessed term: {preprocessed_term}")

        # Wikipedia searching
        try:
            explanation = wikipedia.summary(preprocessed_term)
            return explanation
        except wikipedia.exceptions.DisambiguationError as e:
            print("Disambiguation:", e.options)
        except wikipedia.exceptions.PageError:
            print("No Wiki page found")
        
        print("Try Google Search Now")
        explanation = google_search_and_fetch(preprocessed_term)

    except Exception as e:
        print(f"Searching Error: {e}")
        explanation = None
        
    return explanation
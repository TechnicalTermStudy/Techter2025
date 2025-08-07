import textstat
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from openai import OpenAI
from openai._exceptions import RateLimitError, OpenAIError
import time

system_role_content = "You are a privacy-focused assistant. You should have the capability to write clear, plain-language explanations for technical concepts appeared in Alexa skill privacy policies. The explanation should be logically consistent and easy to understand."

FRE_prompt_template = (
    "Here is your generated explanation: [{explanation}]. Please revise it to improve its readability for a general user. The Flesch Reading Ease score of it should larger than 60. Keep the original meaning and sentence structure as much as possible. Only replace difficult or technical words with simpler, easier-to-understand alternatives. Do not delete or significantly rewrite the sentences. Only return the final revised explanation content.")


def get_embedding(text, client):
    response = client.embeddings.create(
        input=text,
        model="text-embedding-3-small"
    )
    return response.data[0].embedding

def calculate_cosine_sim(sentence1, sentence2, client):
    embeddding_sentence1 = get_embedding(sentence1, client)
    embeddding_sentence2 = get_embedding(sentence2, client)
    embeddding_sentence1 = np.array(embeddding_sentence1).reshape(1, -1)
    embeddding_sentence2 = np.array(embeddding_sentence2).reshape(1, -1)
    
    similarity = cosine_similarity(embeddding_sentence1, embeddding_sentence2)
    return similarity[0][0]

def safe_term_FRE_chat_request(term, client, model_name, messages, max_retries=8):
    for attempt in range(max_retries):
        try:
            return client.chat.completions.create(
                model=model_name, 
                messages=messages, 
                temperature=0.3,
                top_p=0.8,            # 控制采样范围，进一步抑制发散
                frequency_penalty=0.2,  # 可保持句式多样性
                presence_penalty=0    # 不鼓励偏离主题
                )
        except RateLimitError:
            print(f"{term} Rate Limitation Error, please wait...")
            time.sleep(2 ** attempt)
        except OpenAIError as e:
            print(f"{term} OpenAI Error: ", e)
            break
    return None

def check_FRE_score(client, model_name, term, explanation):
    FRE_rounds = 0
    min_similarity = 0.9
    max_FRE_score = 60
    while True:
        similarity = 0
        FRE_score = textstat.flesch_reading_ease(explanation)
        if FRE_score >= max_FRE_score  or FRE_rounds > 3:
            break
        
        FRE_rounds += 1
        FRE_prompt = FRE_prompt_template.format(explanation=explanation)
        
        messages=[
        {"role": "system", "content": system_role_content}, 
        {"role": "user", "content": FRE_prompt}, 
        ]
        
        while similarity < min_similarity:
            term_FRE_chat = safe_term_FRE_chat_request(term=term, client=client, model_name=model_name, messages=messages)
            FRE_refined_explanation = term_FRE_chat.choices[0].message.content.strip()
            
            similarity = calculate_cosine_sim(sentence1=explanation, sentence2=FRE_refined_explanation, client=client)
            
        
        explanation = FRE_refined_explanation
            
    return explanation
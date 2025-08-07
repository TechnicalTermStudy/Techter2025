from openai import OpenAI
from openai._exceptions import RateLimitError, OpenAIError
import nltk
from nltk.tokenize import sent_tokenize
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from itertools import combinations
import torch
import torch.nn.functional as F
import time
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

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

def NLI_check(explanations, nli_tokenizer, nli_model):
    sentences = nltk.sent_tokenize(explanations)
    sentence_pairs = list(combinations(sentences, 2))

    contradictions = []
    for sent1, sent2 in sentence_pairs:
        inputs = nli_tokenizer(sent1, sent2, return_tensors="pt", truncation=True)
        with torch.no_grad():
            logits = nli_model(**inputs).logits
        probs = F.softmax(logits, dim=1)
        labels = ["contradiction", "neutral", "entailment"]
        pred = labels[torch.argmax(probs)]
        score = torch.max(probs).item()
        if pred == "contradiction":
            contradictions.append((sent1, sent2, score))

    return contradictions

def safe_contradiction_summary_chat_request(term, client, model_name, messages, max_retries=8):
    for attempt in range(max_retries):
        try:
            return client.chat.completions.create(
                model=model_name, 
                messages=messages, 
                temperature=0.2,
                top_p=0.9,            # 控制采样范围，进一步抑制发散
                frequency_penalty=0.2,  # 可保持句式多样性
                presence_penalty=0.4    # 不鼓励偏离主题
                )
        except RateLimitError:
            print(f"{term} Rate Limitation Error, please wait...")
            time.sleep(2 ** attempt)
        except OpenAIError as e:
            print(f"{term} OpenAI Error: ", e)
            break
    return None
  
    
def check_NLI(client, model_name, term, explanation):
    system_role_content = "You are a privacy-focused assistant. You should have the capability to write clear, plain-language explanations for technical concepts appeared in Alexa skill privacy policies. The explanation should be logically consistent and easy to understand."
    
    nli_tokenizer = AutoTokenizer.from_pretrained("roberta-large-mnli")
    nli_model = AutoModelForSequenceClassification.from_pretrained("roberta-large-mnli")
    
    contradiction_rounds = 0
    min_similarity = 0.6
    while True:
        similarity = 0
        contradictions = NLI_check(explanations=explanation, nli_tokenizer=nli_tokenizer, nli_model=nli_model)
        if not contradictions or contradiction_rounds > 3:
            break
        contradiction_rounds += 1
        contradiction_summary = "Your generated explanation has some contradictions:\n"
        for s1, s2, sc in contradictions:
            contradiction_summary += f"- \"{s1}\" contradicts with \"{s2}\".\n"
            
        contradiction_summary += "Please revise the explanation to eliminate these contradictions while preserving clarity and simplicity.\n"
        
        messages=[
        {"role": "system", "content": system_role_content}, 
        {"role": "user", "content": contradiction_summary}, 
        {"role": "assistant", "content": explanation}, 
        {"role": "user", "content": "Please regenerate the explanation, resolving the contradictions above. Keep it within 100 words, simple and accurate."}
        ]
        
        while similarity < min_similarity:
            contradiction_summary_chat = safe_contradiction_summary_chat_request(term=term, client=client, model_name=model_name, messages=messages)
            contradiction_refined_explanation = contradiction_summary_chat.choices[0].message.content.strip()
            
            
            similarity = calculate_cosine_sim(sentence1=explanation, sentence2=contradiction_refined_explanation, client=client)
            
        explanation = contradiction_refined_explanation
            
    return explanation
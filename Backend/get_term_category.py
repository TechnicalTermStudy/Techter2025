from openai import OpenAI
from openai._exceptions import RateLimitError, OpenAIError
import time

def get_term_category(term, client, model_name, max_retries=8):
    
    system_role_content = "You are a great tool to analyze technical terms appeared in the Alexa skill privacy policies. There are totally seven categories for terms about Alexa skills privacy policy, namely named data type, entity name, data usage, data sharing, user rights, data storage, legal and compliance. Data type describes that users should understand what types of data are being collected. Entity name describes that users should know who is responsible for collecting and processing their data. Data usage describes that users should be clearly informed about how their data will be used. Data sharing describes that users need to be aware of with whom their data will be shared and why. User rights describes that users should be informed of their rights regarding their data under GDPR and other regulations. Data storage describes that users should know how and where their data will be stored and for how long. Legal and compliance describes that users should be informed about how the service complies with relevant laws and what legal safeguards are in place. You should have the capability to first identify the terms' category and then explain the terms clearly and accurately."
    system_message = {"role": "system", "content": system_role_content}
    
    messages = [system_message]

    term_type_prompt_template = "Could you help me identify the term [{Term}] for Alexa skills privacy policy belonging to which category? You need to output the only one category's name from seven categories (data type, entity name, data usage, data sharing, user rights, data storage, legal and compliance)."
    term_type_prompt = term_type_prompt_template.format(Term = term)

    messages.append({"role": "user", "content": term_type_prompt})
    
    for attempt in range(max_retries):
        try:
            term_type_chat = client.chat.completions.create(
                model=model_name, 
                messages=messages, 
                temperature=0.3, 
                presence_penalty=0
                )
        except RateLimitError:
            print(f"{term} Rate Limitation Error, please wait...")
            time.sleep(2 ** attempt)
        except OpenAIError as e:
            print(f"{term} OpenAI Error: ", e)
            break
        
    term_type = term_type_chat.choices[0].message.content.lower()
    
    return term_type
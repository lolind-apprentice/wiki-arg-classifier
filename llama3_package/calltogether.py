#  single prediction
from together import Together
client = Together()
import re

# PARAMETERS OF LLAMA 3 - TOGETHER

TEMP         = 0.3            # model variability 
MODEL_NAME   ="meta-llama/Llama-3.3-70B-Instruct-Turbo-Free"

def predict_one(rational: str, system_prompt: str) -> str:
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[{"role": "system", "content": system_prompt},
                  {"role": "user",   "content": rational}],
        max_tokens=70,
        temperature=TEMP
    )
# return response
    raw = response.choices[0].message.content.strip()
    quoted = re.findall(r'"([^"]+)"', raw)
    if quoted:
        return quoted[-1]

    # 2. Fallback: last standalone lowercase token
    allowed = {"fact", "policy", "value", "other",
           "editorial/meta"}
    tokens = re.findall(r'\b[\w\s]+\b', raw.lower())
    for tok in reversed(tokens):
        if tok.strip() in allowed:
            return tok.strip()
    return "other"


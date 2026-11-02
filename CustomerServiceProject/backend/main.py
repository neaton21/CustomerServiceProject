from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from langchain_ollama import ChatOllama
import re

#Initialize FastAPI web framework
app = FastAPI(title="Customer Service Backend")

#Enable CORS (required for browser)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

#Load GYM Information

def load_sections():
    with open('info.txt', 'r') as f:
        content = f.read()

    sections = re.split(r'\[(.*?)\]', content) #Split the content into sections based on headers in square brackets
    return {sections[i]: sections[i+1].strip() for i in range(1, len(sections), 2)} #Create a dictionary with section headers as keys and content as values

INFO = load_sections() 

#Load Reviews from CSV file
def load_reviews():
    with open('reviews.csv', 'r') as f:
        content = f.read()
    lines = content.strip().split('\n')
    reviews = []
    for line in lines[1:]:  # Skip header
        parts = line.split(',') #Split each line into parts based on commas (name, rating, comment)
        reviews.append({ #Create a dictionary for each review with keys 'name', 'rating', and 'comment'
            'name': parts[0].strip(),
            'rating': parts[1].strip(),
            'comment': parts[2].strip()
        })
    return reviews

REVIEWS = load_reviews()

#Initialize Ollama LLM - Temperature 0 for precise answers from the text
llm = ChatOllama(model="llama3", temperature=0)

class ChatRequest(BaseModel):
    message: str

#Root

@app.get("/")
def root():
    return {"status": "Backend is running"}


#Chat API (uses info text and reviews only)

@app.post("/chat")
def chat(req: ChatRequest):
    all_context = "\n".join([f"{k}: {v}" for k, v in INFO.items()])
    reviews_context = "\n".join([f"{r['name']}: {r['comment']}: {r['rating']}" for r in REVIEWS])
    
    prompt = f"""
    SYSTEM INSTRUCTIONS:
    You are a literal-minded gym assistant. You have NO outside knowledge. 
    You MUST ONLY use the provided Gym Information to answer. 
    If the answer is not EXACTLY in the text, say "I don't have that information."
    Do not start the response with "Based on the information provided" or similar phrases: Act as if you are speaking to the user directly with the information you have.
    
    CRITICAL: Do not invent hours. Do not invent phone numbers. 
    If the text says '24/7', your answer MUST say '24/7'.
    
    If the provided context is brief, do not elaborate or add any additional details. Repeat the facts as they appear.

    If you are using information from the reviews, you MUST cite the reviewer's name. For example, "According to John Doe's 3 star review, ..."

    You may use information from both the general info and the reviews, but you MUST cite the source of any information from the reviews as stated above.
    Gym Information:
    {all_context}\n {reviews_context}
    
    User Question: {req.message}
    
    Helpful Answer:"""
    response = llm.invoke(prompt)

    reply_text = response.content
    return {"reply": reply_text} 


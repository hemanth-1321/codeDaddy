from langchain_google_genai import ChatGoogleGenerativeAI
from dataclasses import dataclass
import os



@dataclass
class LLMResponse:
    content:str
    
class LLMWrapper:
    def __init__(self) :
        self.client=ChatGoogleGenerativeAI(
             model="gemini-2.5-flash", 
             temperature=0.5,
        )
    def invoke(self,prompt)->LLMResponse:
        res = self.client.invoke(prompt).content
        return LLMResponse(content=str(res))
    
        
llm = LLMWrapper()
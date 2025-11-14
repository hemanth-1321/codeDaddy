from langchain_groq import ChatGroq
from dataclasses import dataclass
import os



@dataclass
class LLMResponse:
    content:str
    
class LLMWrapper:
    def __init__(self) :
        self.client=ChatGroq(
             model="openai/gpt-oss-20b", 
             temperature=0.5,
        )
    def invoke(self,prompt)->LLMResponse:
        res = self.client.invoke(prompt).content
        return LLMResponse(content=str(res))
    
        
llm = LLMWrapper()
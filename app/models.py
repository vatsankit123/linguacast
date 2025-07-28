from typing import Dict
from pydantic import BaseModel

class PromptObject(BaseModel):
    prompts: Dict[str, str]

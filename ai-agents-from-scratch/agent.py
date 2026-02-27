from typing import List

import requests


class Tool:
    def __init__(self, name: str, description: str, function: callable):
        self.name = name
        self.description = description
        self.function = function


class Memory:
    def __init__(self, size: int = 1000):
        self.size = size
        self.memory = []

    def add(self, item: dict):
        if len(self.memory) >= self.size:
            self.memory.pop(0)
        self.memory.append(item)


class Model:
    def __init__(self, name: str, base_url: str, params: dict = {}):
        self.name = name
        self.base_url = base_url
        self.params = params


class Agent:
    def __init__(
        self,
        name: str,
        description: str,
        task: str,
        model: Model,
        tools: List[Tool] = [],
        memory: Memory = Memory(),
    ):
        self.name = name
        self.description = description
        self.task = task  # system prompt
        self.model = model
        self.tools = tools
        self.memory = memory

        self.SYSTEM_PROMPT = f"""
        You are {self.name}, {self.description}.
        Your main task/role: {self.task}.
        You have access to the following tools:
        {", ".join([{tool.name: tool.description} for tool in self.tools])}
        """

    def chat_completion(self, prompt: str) -> str:
        self.SYSTEM_PROMPT += f"""
        You have a memory of previous conversations:
        {self.memory.memory}
        """

        print(f"[DEBUG] SYSTEM PROMPT: {self.SYSTEM_PROMPT}")
        # print(f"[DEBUG] Memory: {self.memory.memory}")
        headers = {
            "Content-Type": "application/json",
        }
        data = {
            "model": self.model.name,
            "messages": [
                {"role": "system", "content": self.SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            "max_tokens": self.model.params.get("max_tokens", 1000),
            "temperature": self.model.params.get("temperature", 0.3),
        }
        response = requests.post(self.model.base_url, headers=headers, json=data)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]

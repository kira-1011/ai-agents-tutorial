from dataclasses import dataclass, field
from typing import Callable, List

import keyboard
import requests


@dataclass
class Tool:
    name: str
    description: str
    function: Callable

    def execute(self, arguments: dict):
        return self.function(**arguments)


class Memory:
    def __init__(self, size: int = 1000):
        self.size = size
        self.memory = []

    def add(self, item: dict):
        if len(self.memory) >= self.size:
            self.memory.pop(0)
        self.memory.append(item)


@dataclass
class State:
    step: int = 0
    status: str = ""


@dataclass
class Model:
    name: str
    base_url: str
    params: dict = field(default_factory=dict)

    def generate(self, user_input: str) -> str:
        headers = {
            "Content-Type": "application/json",
        }
        data = {
            "model": self.name,
            "messages": [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": user_input},
            ],
            "max_tokens": self.params.get("max_tokens", 1000),
            "temperature": self.params.get("temparature", 0.5),
        }
        response = requests.post(self.base_url, headers=headers, json=data)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]


class Agent:
    def __init__(
        self,
        name: str,
        description: str,
        instruction: str,
        model: Model,
        tools: List[Tool] = [],
        max_steps: int = 10,
    ):
        self.name = name
        self.description = description
        self.instruction = instruction  # system prompt
        self.model = model
        self.tools = tools
        self.memory = Memory()
        self.state = State()
        self.max_steps = max_steps

        tool_descriptions = "\n".join(
            [f"- {tool.name}: {tool.description}" for tool in self.tools]
        )

        self.SYSTEM_PROMPT = f"""You are {self.name}, {self.description}.
Your main task/role: {self.instruction}.

Available tools:
{tool_descriptions}
"""

    def _tool_call(self, name: str, arguments: dict):
        print(f"Calling tool {name} with arguments {arguments}")
        for tool in self.tools:
            if tool.name == name:
                return tool.execute(arguments)
        return None

    def run(self):
        while not keyboard.is_pressed("esc"):
            user_input = input("User: ")
            response = self.run_agent_loop(user_input)
            print(f"Assistant: {response}")

    def run_agent_loop(self, input):
        """
        Run very basic ReAct agent loop.
        """
        pass

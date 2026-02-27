from typing import List

import keyboard
import requests

from utils import extract_json_from_response


class Tool:
    def __init__(self, name: str, description: str, function: callable):
        self.name = name
        self.description = description
        self.function = function

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
        max_steps: int = 10,
    ):
        self.name = name
        self.description = description
        self.task = task  # system prompt
        self.model = model
        self.tools = tools
        self.memory = memory
        self.max_steps = max_steps

        self.SYSTEM_PROMPT = f"""
        You are {self.name}, {self.description}.
        Your main task/role: {self.task}.
        You have access to the following tools:
        {", ".join([f"{tool.name}: {tool.description}" for tool in self.tools])}

        IMPORTANT:
        - When using a tool, always return the input as a JSON object. for example: {{"tool": "search", "arguments": {{"query": "query"}}}}
        """

    def chat_completion(self, prompt: str) -> str:
        self.SYSTEM_PROMPT += f"""
        Memory of previous conversations:
        {self.memory.memory}
        """
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

    def _tool_call(self, name: str, arguments: dict):
        print(f"Calling tool {name} with arguments {arguments}")
        for tool in self.tools:
            if tool.name == name:
                return tool.execute(arguments)

        return None

    def run(self):

        while not keyboard.is_pressed("esc"):
            user_input = input("User: ")
            output = self.chat_completion(user_input)
            output_json = extract_json_from_response(output)

            if output_json and "tool" in output_json:
                tool_name = output_json["tool"]
                tool_args = output_json["arguments"]
                tool_output = self._tool_call(tool_name, tool_args)
                self.memory.add({"role": "user", "content": user_input})
                self.memory.add(
                    {
                        "role": "tool_call_output",
                        "content": {
                            "tool_name": tool_name,
                            "tool_args": tool_args,
                            "tool_output": tool_output,
                        },
                    }
                )
                print(f"[DEBUG] Tool Output: {tool_output}")
                print(f"Assistant: {output}")
                continue

            print(f"Assistant: {output}")

            self.memory.add({"role": "user", "content": user_input})
            self.memory.add({"role": "assistant", "content": output})

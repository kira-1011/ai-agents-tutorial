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


class State:
    def __init__(self, step: int = 0, status: str = ""):
        self.step = step
        self.status = status


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
        state: State = State(),
        max_steps: int = 10,
    ):
        self.name = name
        self.description = description
        self.task = task  # system prompt
        self.model = model
        self.tools = tools
        self.memory = memory
        self.state = state
        self.max_steps = max_steps

        tool_descriptions = "\n".join(
            [f"- {tool.name}: {tool.description}" for tool in self.tools]
        )

        self.SYSTEM_PROMPT = f"""You are {self.name}, {self.description}.
Your main task/role: {self.task}.

Available tools:
{tool_descriptions}

CRITICAL INSTRUCTIONS:
1. Respond with ONLY valid JSON. No explanations, no markdown, no extra text.
2. Start your response with {{ and end with }}
3. Use a tool ONLY when the user asks to do something with files, directories, or the terminal.
4. For general questions or conversation, respond directly with: {{"final_output": "your answer"}}
5. To call a tool: {{"tool": "tool_name", "arguments": {{"param": "value"}}}}

Examples:
- User says "hi" → {{"final_output": "Hello! I can help you create, read, and manage files. What would you like to do?"}}
- User asks "what can you do" → {{"final_output": "I can create, read, update, rename, and list files using terminal commands."}}
- User asks "what directory am I in?" → {{"tool": "run_terminal", "arguments": {{"command": "cd"}}}}
- User asks "create test.txt" → {{"tool": "run_terminal", "arguments": {{"command": "echo. > test.txt"}}}}
- User asks "show me files" → {{"tool": "run_terminal", "arguments": {{"command": "dir"}}}}"""

    def chat_completion(self, prompt: str, temperature: float = None) -> str:
        system = self.SYSTEM_PROMPT
        if self.memory.memory:
            system += f"\n\nMemory of previous conversations:\n{self.memory.memory}"

        headers = {
            "Content-Type": "application/json",
        }
        data = {
            "model": self.model.name,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": prompt},
            ],
            "max_tokens": self.model.params.get("max_tokens", 1000),
            "temperature": temperature if temperature is not None else self.model.params.get("temperature", 0.3),
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
            # TODO: run agent loop here
            response = self.run_agent_loop(user_input)
            print(f"Assistant: {response}")

    def run_agent_loop(self, input):
        """
        Run very basic ReAct agent loop.
        """
        state = {"step": 0, "status": ""}

        agent_input = input
        final_output = ""

        while state["step"] < self.max_steps and state["status"] != "done":
            print(f"[DEBUG] Agent Input: {agent_input}")
            print(f"[DEBUG] Agent State: {state}")

            # retry up to 3 times to get valid JSON
            output_json = None
            output = ""
            for attempt in range(3):
                output = self.chat_completion(agent_input, temperature=0.0)
                output_json = extract_json_from_response(output)
                if output_json is not None:
                    break
                print(f"[DEBUG] Retry {attempt + 1}: failed to parse JSON from: {output}")

            # check if final answer
            if output_json and "final_output" in output_json:
                final_output = output_json["final_output"]
                self.memory.add({"role": "user", "content": agent_input})
                self.memory.add(
                    {
                        "role": "final_output",
                        "content": {
                            "final_output": final_output,
                        },
                    }
                )
                state["status"] = "done"

            # check tool call
            elif output_json and "tool" in output_json:
                tool_name = output_json["tool"]
                tool_args = output_json["arguments"]
                tool_output = self._tool_call(tool_name, tool_args)
                self.memory.add({"role": "user", "content": agent_input})
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
                result = tool_output if tool_output else "Command executed successfully (no output)."
                agent_input = f'Original request: {agent_input}\nTool "{tool_name}" with arguments {tool_args} returned: {result}\nNow summarize the result for the user in {{"final_output": "your summary"}}'
                state["step"] += 1
                continue

            # no JSON / unrecognized response — treat as final output
            else:
                final_output = output
                self.memory.add({"role": "user", "content": agent_input})
                self.memory.add({"role": "assistant", "content": output})
                state["status"] = "done"

        return final_output

from agent import Agent, Model

if __name__ == "__main__":
    # MODEL_NAME = "ai/smollm2"
    MODEL_NAME = "ai/llama3.2:latest"
    MODEL_BASE_URL = "http://localhost:12434/engines/llama.cpp/v1/chat/completions"

    model = Model(name=MODEL_NAME, base_url=MODEL_BASE_URL)
    tools = []
    my_agent = Agent(
        name="Assistant",
        description="A personal file assistant with terminal access.",
        instruction="Help users create, read, and update files using terminal commands. Use the run_terminal tool to execute commands like 'cat' to read files, 'echo > file' to create files, and 'type' or 'dir' to list and view files.",
        model=model,
        tools=tools,
    )

    my_agent.run()

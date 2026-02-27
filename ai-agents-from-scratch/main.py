from agent import Agent, Memory, Model, Tool


def add(x, y):
    return x + y


if __name__ == "__main__":
    MODEL_NAME = "ai/smollm2"
    MODEL_BASE_URL = "http://localhost:12434/engines/llama.cpp/v1/chat/completions"

    model = Model(name=MODEL_NAME, base_url=MODEL_BASE_URL)
    memory = Memory()
    tools = [
        Tool(
            name="add",
            description="Add two numbers. x:int y:int ex: add(x=2, y=3) => 5",
            function=add,
        )
    ]
    my_agent = Agent(
        name="Assistant",
        description="A helpful assistant.",
        task="You are a helpful assistant.",
        model=model,
        memory=memory,
        tools=tools,
    )

    my_agent.run()

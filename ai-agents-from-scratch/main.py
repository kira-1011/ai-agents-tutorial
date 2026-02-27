import keyboard

from agent import Agent, Memory, Model

if __name__ == "__main__":
    MODEL_NAME = "ai/smollm2"
    MODEL_BASE_URL = "http://localhost:12434/engines/llama.cpp/v1/chat/completions"

    model = Model(name=MODEL_NAME, base_url=MODEL_BASE_URL)
    memory = Memory()
    my_agent = Agent(
        name="Assistant",
        description="A helpful assistant.",
        task="You are a helpful assistant.",
        model=model,
        memory=memory,
    )
    while not keyboard.is_pressed("esc"):
        user_input = input("User: ")
        output = my_agent.chat_completion(user_input)
        print(f"Assistant: {output}")

        memory.add({"role": "user", "content": user_input})
        memory.add({"role": "assistant", "content": output})

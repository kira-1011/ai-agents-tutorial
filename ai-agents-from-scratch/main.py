import platform
import subprocess

from agent import Agent, Memory, Model, Tool

IS_WINDOWS = platform.system() == "Windows"


BLOCKED_COMMANDS = [
    "rm",
    "rmdir",
    "del",
    "format",
    "mkfs",
    "shutdown",
    "reboot",
    "halt",
    "poweroff",
    "dd",
    "fdisk",
    "diskpart",
    "reg",
    "regedit",
    "net user",
    "net localgroup",
    "passwd",
    "useradd",
    "userdel",
    "chmod",
    "chown",
    "icacls",
    "takeown",
    "kill",
    "taskkill",
    "pkill",
    "curl",
    "wget",
    "invoke-webrequest",
    "ssh",
    "scp",
    "ftp",
    "telnet",
    "nc",
    "ncat",
    "powershell",
    "cmd /c",
    "bash -c",
]


def run_terminal(command):
    cmd_lower = command.lower().strip()
    for blocked in BLOCKED_COMMANDS:
        if blocked in cmd_lower:
            return f"Blocked: '{blocked}' is not allowed for safety reasons."

    shell_cmd = ["cmd", "/c", command] if IS_WINDOWS else ["bash", "-c", command]
    result = subprocess.run(shell_cmd, capture_output=True, text=True)
    if result.returncode == 0:
        return result.stdout.strip()
    else:
        return f"Error: {result.stderr.strip()}"


if __name__ == "__main__":
    # MODEL_NAME = "ai/smollm2"
    MODEL_NAME = "ai/llama3.2:latest"
    MODEL_BASE_URL = "http://localhost:12434/engines/llama.cpp/v1/chat/completions"

    model = Model(name=MODEL_NAME, base_url=MODEL_BASE_URL)
    memory = Memory()
    tools = [
        Tool(
            name="run_terminal",
            description=(
                "Execute a terminal/shell command and return the output. command:str. "
                "Examples: "
                "run_terminal(command='dir') => list files. "
                "run_terminal(command='cd') => current directory. "
                "run_terminal(command='type test.txt') => read file contents. "
                "run_terminal(command='echo hello > test.txt') => create file with content. "
                "run_terminal(command='echo new line >> test.txt') => append to file. "
                "run_terminal(command='mkdir mydir') => create directory. "
                "run_terminal(command='move old.txt new.txt') => rename file. "
                "run_terminal(command='copy file.txt backup.txt') => copy file."
            ),
            function=run_terminal,
        ),
    ]
    my_agent = Agent(
        name="Assistant",
        description="A personal file assistant with terminal access.",
        task="Help users create, read, and update files using terminal commands. Use the run_terminal tool to execute commands like 'cat' to read files, 'echo > file' to create files, and 'type' or 'dir' to list and view files.",
        model=model,
        memory=memory,
        tools=tools,
    )

    my_agent.run()

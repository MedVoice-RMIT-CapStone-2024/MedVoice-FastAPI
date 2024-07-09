import subprocess
import platform

# Define a function to run a command and print its output
def run_command(command):
    process = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
    output, error = process.communicate()
    if error:
        print(f"Error: {error}")
    else:
        print(output.decode())

# Check if the current OS is Linux
if platform.system() != "Linux":
    raise SystemError("This script can only be run on a Linux system, refer to Ollama Documentation for your OS Installation.")

# Run the commands
run_command("curl -fsSL https://ollama.com/install.sh | sh")
run_command("ollama pull nomic-embed-text")
# run_command("ollama pull llama3")

print("The script has successfully run the commands.")

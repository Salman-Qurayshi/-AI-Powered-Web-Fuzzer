
# AI-Powered Web Fuzzer

An intelligent web fuzzer that uses the Google Gemini API to generate targeted wordlists for `ffuf`, iteratively discovering new and hidden file paths on a target website.

## Prerequisites

Before you begin, ensure you have the following installed on your system:
* **Python 3.x**
* **ffuf** - A fast web fuzzer. You can download it from ffuf's GitHub repository.
* **Git** (optional, but recommended for cloning this repository).

## Setup

### 1. **Clone the repository** (if you haven't already):

   git clone https://github.com/your-username/your-repository-name.git
   cd your-repository-name

### 2. **Get a Gemini API Key**:
  * Go to **Google AI Studio** and log in with your Google account.
  * Click "Get API key" in the left-hand navigation.
  * Click "Create API key in new project" and copy the key.

### 3. **Set the API Key as an Environment Variable**: 
The script reads your API key from the environment. **Do not hardcode it in the script.** Add the following line to your `~/.bashrc` or `~/.zshrc` file:

   export GOOGLE_API_KEY="your_gemini_api_key_here"

After adding the line, apply the changes by running:

   source ~/.bashrc

### 4. **Install Python Dependencies**: 
The script requires the `google-generativeai` and `requests` libraries. Install them using `pip`:

   pip install google-generativeai --break-system-packages
   pip install requests beautifulsoup4 colorama

### 5. **Review the Prompt File**: 
The fuzzer uses the prompt in the `prompts/files.txt` file to instruct the AI. This file contains placeholders like `{{initialLinks}}` and `{{serverHeaders}}` that the script replaces at runtime. You can modify this file to improve the AI's suggestions.

## Usage

Run the `fuzzer.py` script from your terminal, passing your `ffuf` command as a string argument. The script will automatically replace the `-u` and `-w` arguments as it runs.

   python3 fuzzer.py "ffuf -u http://example.com/FUZZ -w wordlist.txt"

## Optional Arguments

* `--cycles`: The number of times the fuzzer will run. The default is 50.
* `--model`: The Gemini model to use. The default is `gemini-1.5-flash`.
* `--prompt-file`: The path to a custom prompt file.
* `--status-codes`: A comma-separated list of HTTP status codes to consider a successful hit. The default is `200,301,302,303,307,308,403,401,500`.
* `--debug`: Enables debug logging, showing the full prompts and AI responses.

Example with all arguments:

   python3 fuzzer.py "ffuf -u http://example.com/FUZZ -w wordlist.txt -H 'User-Agent: my-fuzzer'" --cycles 10 --status-codes 200,403 --debug

## How It Works

1. **Initial Reconnaissance**: The script first scrapes the target URL to discover any public-facing links.
2. **AI Analysis**: It sends these initial links and the target server's HTTP headers to the Gemini API as a prompt.
3. **Intelligent Wordlist Generation**: The Gemini model analyzes the provided information and generates a list of new, logical, and contextual file and directory names that might exist on the server.
4. **Fuzzing**: The script takes the AI-generated list and uses it as a wordlist for `ffuf`, running the command to check for valid URLs.
5. **Iteration**: If `ffuf` discovers any new links, the process repeats, using the newly found links to inform the AI's next set of suggestions. This allows the fuzzer to "learn" about the target's structure over time, potentially uncovering deeper, harder-to-find paths.

## Disclaimer

This tool is intended for educational and ethical security research purposes only. Unauthorized access to computer systems is illegal and unethical. By using this tool, you acknowledge that you are responsible for your actions. Ensure you have explicit permission to test any system you use this tool on.

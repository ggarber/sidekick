# AI Review

A tool for AI-powered code review and labeling of GitLab merge requests.

## Features

- Review code changes using various LLM providers (OpenAI, Anthropic, Google, AWS Bedrock)
- Generate appropriate labels for merge requests
- Support for GitLab repositories
- Verbose mode for debugging and transparency

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/ai-review.git
cd ai-review
```

2. Create and activate a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file with your configuration:
```bash
cp .env.example .env
```

5. Edit `.env` with your settings:
```env
# Required for GitLab
GITLAB_TOKEN=your_gitlab_token
GITLAB_HOST=https://gitlab.com  # Optional, defaults to gitlab.com

# Required for LLM provider
PROVIDER=openai  # or anthropic, google, bedrock
OPENAI_API_KEY=your_openai_api_key  # if using OpenAI
ANTHROPIC_API_KEY=your_anthropic_api_key  # if using Anthropic
GOOGLE_API_KEY=your_google_api_key  # if using Google
AWS_ACCESS_KEY_ID=your_aws_access_key  # if using Bedrock
AWS_SECRET_ACCESS_KEY=your_aws_secret_key  # if using Bedrock
AWS_REGION=your_aws_region  # if using Bedrock
```

## Usage

### Review Code Changes

```bash
python main.py review <project_id> <merge_request_id>
```

### Generate Labels

```bash
python main.py label <project_id> <merge_request_id>
```

### Verbose Mode

Add `-v` or `--verbose` flag to see detailed output:
```bash
python main.py review <project_id> <merge_request_id> -v
```

## Available Actions

- `review`: Review code changes and provide feedback
- `label`: Generate appropriate labels for the merge request

## Available Providers

- `openai`: OpenAI's GPT models
- `anthropic`: Anthropic's Claude models
- `google`: Google's Gemini models
- `bedrock`: AWS Bedrock models

## Development

### Adding New Providers

1. Create a new provider class in `providers/` that implements the `LLMProvider` interface
2. Add the provider to the `providers` dictionary in `get_provider()`

### Adding New Actions

1. Create a new action class in `actions/` that implements the `Action` interface
2. Add the action to the `actions` dictionary in `get_action()`

## License

MIT 
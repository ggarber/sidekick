# Sidekick

The customizable tool for AI-powered code review of merge requests.

## Features

- Review code changes using various LLM providers (OpenAI, Anthropic, Google, AWS Bedrock)
- Support for GitLab repositories and GitHub ones (WIP)
- Configurable rules based on markdown files
- Verbose mode for debugging and transparency
- Multiple actions implemented:
   - Summarize: provides a summary of what the merge request does and how it does it
   - Label: label the merge request in different dimensions with default labels or with a custom list of labels provided
   - Review Format: provides reviews of some general rules about the format of the merge request to make sure it has the appropriate length, description, title, design, documentation... as defined by the owner of the repo.
   - Review Code: reviews specific changes in the code and provides comments about them using a list of defined rules about design, implementation, dependencies... that are configured by the owner of the repo. 

## Installation

### Run locally 

1. Clone the repository:
```bash
git clone https://github.com/ggarber/sidekick
cd sidekick
```

2. Create and activate a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install .
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

6. Run any action for any project id and merge request id:
```bash
python main.py -v review_code,review_format,summarize,label PROJECT_ID MERGE_REQUEST_IID -p
```

### Run on GitLab merge request jobs

```
review:
  stage: review
  image:
    name: ggarber10/sidekick:0.0.6
    entrypoint: [""]
  script:
    - python main.py -v -p -t review_format,review_code,summarize "$CI_PROJECT_ID" "$CI_MERGE_REQUEST_IID"
  rules:
    - if: $CI_PIPELINE_SOURCE == 'merge_request_event' AND
          $CI_MERGE_REQUEST_LABELS ~= 'sidekick'
```

### Run on GitHub pull request actions
(TBD)

## License

MIT 

import os
import json
import boto3
from .base import LLMProvider, CompletionResponse


class BedrockProvider(LLMProvider):
    def __init__(self):
        self.client = boto3.client(
            "bedrock-runtime",
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            region_name=os.getenv("AWS_REGION"),
        )
        if not all(
            [
                os.getenv("AWS_ACCESS_KEY_ID"),
                os.getenv("AWS_SECRET_ACCESS_KEY"),
                os.getenv("AWS_REGION"),
            ]
        ):
            raise ValueError("AWS credentials environment variables are not set")
        self.model = os.getenv(
            "BEDROCK_MODEL", "anthropic.claude-3-7-sonnet-20250219-v1:0"
        )

    def completion(self, prompt: str) -> CompletionResponse:
        response = self.client.invoke_model(
            modelId=self.model,
            body=json.dumps(
                {
                    "anthropic_version": "bedrock-2023-05-31",
                    "max_tokens": 120000,
                    "messages": [
                        {
                            "role": "user",
                            "content": [{"type": "text", "text": prompt}],
                        }
                    ],
                }
            ),
        )

        response_body = json.loads(response.get("body").read())

        return CompletionResponse(
            text=response_body["content"][0]["text"],
            tokens_used=response_body["usage"]["input_tokens"]
            + response_body["usage"]["output_tokens"],
        )

    @property
    def max_tokens(self) -> int:
        # Example: Maximum tokens for completion
        return 120000

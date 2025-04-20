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
            "BEDROCK_MODEL", "anthropic.claude-3-sonnet-20240229-v1:0"
        )

    def completion(self, prompt: str) -> CompletionResponse:
        response = self.client.invoke_model(
            modelId=self.model,
            body={
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 4096,
                "messages": [{"role": "user", "content": prompt}],
            },
        )

        response_body = json.loads(response.get("body").read())

        return CompletionResponse(
            text=response_body["content"][0]["text"],
            tokens_used=response_body["usage"]["input_tokens"]
            + response_body["usage"]["output_tokens"],
        )

    def get_context_window(self) -> int:
        context_windows = {
            "anthropic.claude-3-opus-20240229-v1:0": 200000,
            "anthropic.claude-3-sonnet-20240229-v1:0": 200000,
            "anthropic.claude-3-haiku-20240307-v1:0": 200000,
            "anthropic.claude-v2:1": 200000,
            "anthropic.claude-v2": 100000,
            "anthropic.claude-v1": 100000,
            "amazon.titan-text-express-v1": 8000,
            "meta.llama2-70b-chat-v1": 4096,
            "meta.llama2-13b-chat-v1": 4096,
        }
        return context_windows.get(self.model, 200000)

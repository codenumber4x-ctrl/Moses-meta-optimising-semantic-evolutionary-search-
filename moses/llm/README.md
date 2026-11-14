# moses/llm

## Summary
This package gives every model provider the same small interface: `client.complete(prompt, system=None) -> str`. The search code depends only on that interface, so a provider can be swapped without changing anything else.

## Providers
| Provider | Key variable | Default model | Notes |
|---|---|---|---|
| `openai` | `OPENAI_API_KEY` | `gpt-5-mini` | OpenAI Chat Completions |
| `anthropic` | `ANTHROPIC_API_KEY` | `claude-opus-5-5` | Anthropic Messages API; `temperature` is not sent |
| `groq` | `GROQ_API_KEY` | `openai/gpt-oss-120b` | OpenAI-compatible endpoint at `api.groq.com` |
| `openai-compatible` | `LLM_API_KEY` | none, set `model` | Any compatible server (vLLM, Ollama, LM Studio, ...); needs `base_url` or `LLM_BASE_URL` |

## Usage
```python
from moses.llm import GenerationConfig, create_client

client = create_client(
    "groq",                    # provider
    api_key=None,              # None: read the key from GROQ_API_KEY
    config=GenerationConfig(max_tokens=4096, reasoning_effort="low"),
    min_interval=10,           # seconds between calls, for low rate limits
)
print(client.complete("Say hello."))
```

## Behaviour
- **Retries:** both official SDKs retry rate limits (honouring `Retry-After`), timeouts and server errors, up to 5 times.
- **Errors:** anything that still fails raises `LLMError`. So do empty replies and refusals.
- **Adding a provider:** subclass `LLMClient`, implement `_complete`, and register the provider in `PROVIDERS` and `create_client` in `__init__.py`.

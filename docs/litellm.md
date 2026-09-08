# LiteLLM Gateway

## 目的 / Purpose

**繁體中文**  
LiteLLM 位於 RAG API 與 Model Runtime 之間，讓應用程式只依賴 OpenAI-compatible Interface，而不用直接綁定 Ollama、OpenAI、Azure OpenAI 或其他 Provider。

**English**  
LiteLLM sits between the RAG API and model runtimes, allowing the application to depend only on an OpenAI-compatible interface rather than a specific provider.

## Default Route / 預設路由

    enterprise-rag
        |
        v
    ollama/llama3.2:3b
        |
        v
    http://ollama:11434

設定檔 / Configuration:

    litellm_config.yaml

## API Route

FastAPI uses:

    LLM_BASE_URL=http://litellm:4000/v1
    LLM_MODEL=enterprise-rag

## 更換 Provider / Changing provider

**繁體中文**  
修改 litellm_config.yaml 的 model_list 即可將 enterprise-rag Route 到其他 Model，不需要修改 RAG Application Code。

**English**  
Change model_list in litellm_config.yaml to route enterprise-rag to another model without modifying RAG application code.

## Production Notes / 正式環境注意

- Replace LITELLM_MASTER_KEY.
- Use Secret Management rather than committed keys.
- Add rate limits, budgets, provider fallback, and model allowlists as needed.
- Consider LiteLLM spend/cost telemetry when using paid providers.

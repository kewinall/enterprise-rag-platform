# Troubleshooting

## API is not ready

Check Qdrant connectivity:

```bash
curl http://localhost:6333/collections
```

## LLM request fails

Verify the model exists:

```bash
docker compose exec ollama ollama list
```

Pull it if necessary:

```bash
docker compose exec ollama ollama pull llama3.2:3b
```

## Slow first request

Sentence-transformer models are loaded lazily and may need to be downloaded on first use. For offline environments, pre-stage the model artifacts and pin them in the image or mounted model cache.

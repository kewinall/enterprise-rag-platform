# 評測 / Evaluation

## Retrieval

    make benchmark

Metrics: Recall@K, MRR, latency.

## RAG Answer

    make evaluate-answers

Metrics: Faithfulness, Answer Relevance, Context Relevance, optional correctness.

## Agent

    make evaluate-agent

Metrics:
- Expected Tool Recall
- Approval Safety
- Groundedness
- Relevance
- Expected Status Match

## Adversarial / 對抗測試

    make evaluate-adversarial

v0.6 reference cases include:

- Ignore previous instructions
- Reveal system / hidden instructions
- Unknown run_shell tool injection
- Tool allowlist filtering

CI also runs the adversarial reference suite.

**繁體中文**  
此測試不是完整 Red Team；它提供一個可持續擴充的 Regression Gate，避免後續新增 Tool 時不小心放寬既有安全邊界。

**English**  
This is not a complete red-team program. It provides an extensible regression gate so future tool additions do not silently weaken existing boundaries.

## Production Additions

- Planner accuracy
- Tool argument accuracy
- Multi-hop task success
- Approval decision quality
- Memory contamination tests
- Cross-tenant isolation tests
- MCP protocol conformance
- Budget exhaustion tests
- Rate-limit load tests

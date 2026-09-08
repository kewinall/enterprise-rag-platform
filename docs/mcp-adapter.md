# MCP Tool Adapter

## Scope / 支援範圍

**繁體中文**  
v0.6 提供 MCP-compatible Tool Adapter，重點是將既有 Tool Registry 透過 MCP JSON-RPC Tool Contract 暴露給外部 Agent Client。此版本不是完整 MCP Server Implementation。

**English**  
v0.6 provides an MCP-compatible tool adapter that exposes the existing server-side tool registry through an MCP JSON-RPC tool contract. It is intentionally not a full MCP server implementation.

Endpoint:

    POST /mcp

## Supported

- modern server/discover
- legacy initialize
- tools/list
- tools/call

Protocol revisions advertised:

- 2026-07-28
- 2025-11-25

## Not Implemented

- Sampling
- Elicitation
- Resources
- Prompts
- Subscriptions
- Server-to-client requests
- Full Streamable HTTP session lifecycle

## Security

MCP 不會繞過既有 Tool Registry。  
MCP never bypasses the existing tool registry.

所有 tools/call 仍套用：

- OIDC / API Key Principal
- Tenant Scope
- Required Role
- Tool Allowlist
- Human Approval Policy

破壞性 delete_document 不會透過 MCP 直接執行，因為它仍需要 Approval Gate。  
Destructive delete_document calls are not directly executed through MCP because the approval gate still applies.

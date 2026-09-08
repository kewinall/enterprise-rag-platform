# Tool Permission Policy / Tool 權限政策

## Principle / 原則

**繁體中文**  
LLM 不等於 Authorization Engine。模型只能提出 Tool Call，Server 才是唯一能決定 Tool 是否允許執行的元件。

**English**  
An LLM is not an authorization engine. The model may propose a tool call, but only the server can authorize execution.

## Tool Catalog

| Tool | Role | Approval | Scope |
|---|---|---|---|
| search_knowledge | viewer | No | Current tenant |
| list_documents | viewer | No | Current tenant |
| get_document_metadata | viewer | No | Current tenant |
| delete_document | admin | Yes | Current tenant |

## Explicitly Not Exposed

- Shell
- Arbitrary HTTP Request
- Raw SQL
- Arbitrary File Write
- Python eval / exec
- Kubernetes Admin
- Cloud IAM Admin
- Secret Read API

**繁體中文**  
這些能力未來若需要加入，應建立專用、參數受限、Least-Privilege 的 Tool，而不是直接開放通用執行器。

**English**  
If these capabilities are needed later, expose narrow, parameter-constrained, least-privilege tools rather than generic execution primitives.

## Approval Workflow

    Planner proposes delete_document
              |
              v
       Server checks Admin
              |
              v
       Create pending action
              |
              v
          Redis + TTL
              |
          +---+---+
          |       |
        Reject  Approve
                  |
                  v
         Re-check Tenant/Role
                  |
                  v
             Execute once

## Approval Data

Stored:

- action_id
- tool_name
- arguments
- tenant_id
- requested_by
- required_role
- created_at
- status

**繁體中文**  
Approval 不保存 LLM Credential。Action 執行時仍由 Server Runtime 使用既有受控 Connection。

**English**  
Approval records do not store infrastructure credentials. Execution still uses controlled server-side connections.

## Tenant Protection

Approval Request 綁定 tenant_id。  
Approval requests are bound to tenant_id.

其他 Tenant 即使知道 action_id 也不能讀取、核准或拒絕。  
Another tenant cannot inspect, approve, or reject an action even if it knows the action ID.

## Recommended Production Extensions

- Dedicated approval audit table
- Two-person approval for high-impact tools
- Approval reason / ticket number
- Tool-specific rate limits
- Maximum affected-resource count
- Maintenance-window checks
- Signed approval event
- SIEM notification

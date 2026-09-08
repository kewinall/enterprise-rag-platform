from app.agent.tools import execute_tool, list_tool_policies
from app.core.security import Principal


def mcp_tools_list(principal: Principal) -> dict:
    tools = []
    for policy in list_tool_policies():
        if not principal.has_role(policy["required_role"]):
            continue
        tools.append(
            {
                "name": policy["name"],
                "description": policy["description"],
                "inputSchema": {
                    "type": "object",
                    "additionalProperties": True,
                },
                "annotations": {
                    "readOnlyHint": not policy["requires_approval"],
                    "destructiveHint": policy["requires_approval"],
                },
            }
        )
    return {"tools": tools}


async def mcp_tools_call(
    principal: Principal,
    name: str,
    arguments: dict,
) -> dict:
    result = await execute_tool(principal, name, arguments)
    return {
        "content": [
            {
                "type": "text",
                "text": str(result),
            }
        ],
        "structuredContent": result,
        "isError": False,
    }

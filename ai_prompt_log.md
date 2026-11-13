# Security Audit Log

This document records the initial implementation prompt, identified security risks, and the changes made before the final implementation.

## Initial Implementation Prompt

> Build an end-to-end Python 3.11+ system using the Model Context Protocol (MCP). The system should expose three tools: a read-only SQLite query tool, a live weather tool using Open-Meteo, and a deterministic mathematical evaluator. Use stdio transport, dynamic MCP tool discovery, a bounded multi-turn tool-calling loop, a Streamlit interface, and automated tests.

---

## 1. Unsafe Mathematical Execution

### Initial Risk

A direct implementation could evaluate expressions using:

```python
result = eval(expression)
```

This creates an arbitrary code execution vulnerability.

For example:

```python
__import__('os').listdir('.')
```

could attempt to interact with the host environment.

### Final Control

The math tool uses:

```python
ast.parse(expression, mode="eval")
```

Only explicitly approved AST nodes are accepted, including:

- numeric constants
- approved binary operators
- approved unary operators
- whitelisted mathematical functions

Imports, attribute access, arbitrary function calls, lambdas, comprehensions, and other executable Python constructs are rejected.

The implementation does not use `eval()` or `exec()`.

---

## 2. SQL Validation and Database Protection

### Initial Risk

Simple keyword filtering such as:

```python
if "drop" in query.lower():
    raise ValueError("Blocked")
```

is not a sufficient security boundary.

It can fail to account for:

- stacked statements
- alternate destructive operations
- SQL comments
- malformed queries
- unexpected write operations

### Final Control

The SQL tool uses multiple layers of protection:

1. SQL is parsed before execution.
2. Only one statement is allowed.
3. Only approved read operations are accepted.
4. DDL and DML operations are rejected.
5. Stacked statements are rejected.
6. SQLite is opened with `mode=ro`.
7. `PRAGMA query_only = ON` is enabled.
8. Query output is capped to a limited number of rows.

This provides defense in depth even if one validation layer fails.

---

## 3. MCP Tool Schema Translation

### Initial Risk

MCP tool definitions and LLM function definitions do not necessarily use the same object structure.

Passing MCP tool objects directly to the model provider can result in invalid tool definitions or failed function calls.

### Final Control

Discovered MCP tools are explicitly translated into the function schema expected by the model:

```python
{
    "type": "function",
    "function": {
        "name": tool["name"],
        "description": tool["description"],
        "parameters": tool["inputSchema"],
    },
}
```

This keeps MCP tool discovery separate from provider-specific formatting.

---

## 4. Unbounded Agent Loops

### Initial Risk

An unrestricted loop such as:

```python
while True:
    response = call_model(...)
```

could repeatedly invoke tools, consume resources, and continuously grow conversation state.

### Final Control

The orchestration layer enforces:

```python
max_turns = 5
```

Tool execution failures are converted into structured error responses instead of crashing the process.

If the maximum turn count is reached, the loop terminates safely.

---

## Additional Security Controls

The final implementation also includes:

- `.env` excluded from Git
- scoped application configuration
- HTTP request timeouts
- redirect restrictions for external API calls
- sanitized weather API output
- limited SQL result sizes
- structured tool errors without internal stack traces
- no database filesystem paths exposed to the user
- adversarial SQL injection testing
- arbitrary code execution testing
- bounded MCP tool execution
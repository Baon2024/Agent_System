# Agent System Overview

This repository contains a prototype agent runtime with a Python backend, a React frontend, and optional MCP tool integrations. The main agent is created from `agentVariant.py` and coordinated by a WebSocket loop in `loopVariant.py`.

The system is designed around long-lived agent instances. Each agent is stored by `agent_id` and can be toggled between running and idle with its `is_running` flag. When a new message arrives for an existing agent, the same instance is reused, preserving its configured tools, permissions, state, and prompt context instead of creating a fresh agent every time.

## Features

- Tool-using agent loop with structured JSON actions and final answers.
- Continuous agents backed by persistent in-memory `Agent` instances, controlled through a running/idle flag.
- Human-in-the-loop approvals for tools that require user permission before execution.
- Client-executed tools, including browser-side geolocation through `get_user_location`.
- WebSocket communication between frontend and backend for messages, tool calls, approvals, and task results.
- MCP tool discovery and execution, currently configured for a local Gmail MCP server.
- File and todo-list helper tools available to the agent.
- Skill loading from the local `SKILLS` directory so the agent can read task-specific instructions.
- Optional file upload and final-answer file handling through Gemini and Supabase helper paths.

## Tech Stack

- Backend: Python, `asyncio`, `websockets`, Pydantic, Google GenAI/Gemini, Firecrawl, Supabase, FastMCP/MCP.
- Frontend: React 18, Vite, Tailwind CSS, Supabase JS.
- Tooling and integrations: MCP over HTTP, browser geolocation APIs, Google Gmail API via a FastMCP server.

## Backend Overview

The backend runtime is centered on two files:

- `agentVariant.py` defines the `Agent` class, tool schemas, prompt construction, skill loading, MCP tool loading, and the `get_new_agent(...)` factory used to create a configured main agent instance.
- `loopVariant.py` runs the WebSocket server on `localhost:3077`, stores active agents in `agents_state`, routes user messages to the correct agent, and handles bidirectional events such as frontend tool results and human approval responses.

When a user message arrives, the backend checks whether an agent already exists for the provided `agent_id`. If it does, the existing instance is reused. If the agent is idle, it is marked as running and scheduled again. If it is already running, the message is appended to shared message memory so the active run can continue with the new input.

Human-in-the-loop requests are handled through `AgentBidirectionalController`. When a tool requires approval, the backend sends a `human_in_loop_request` message to the frontend and waits on an `asyncio.Future` until the user approves or rejects it.

Client-side tools use a similar future-based flow. The agent sends a `client_side_tool_call` event to the browser, the frontend executes the tool locally, then sends the result back to the backend.

## Frontend Overview

The frontend lives in `web-app/` and is a Vite React application. It connects to the backend WebSocket server, sends user messages with an `agent_id`, renders agent responses, and handles special backend events.

The frontend is responsible for:

- Sending user messages and uploaded file references to the backend.
- Receiving normal agent responses, task results, and task errors.
- Displaying human-in-the-loop approval requests and returning the user's decision.
- Executing client-side tools requested by the agent, including browser geolocation.

Client-executed tools are registered in `web-app/frontendTools/tools.js` and mapped in the React app. The current location tool uses the browser's `navigator.geolocation` API, allowing location access to remain client-side instead of running on the server.

## MCP Server Overview

The `mcpServer/` folder contains a FastMCP Gmail server. It exposes Gmail-related tools such as email search and email reading. The main agent discovers MCP tools from `mcp.json`, then adds the discovered tool definitions to its system prompt and dispatches selected MCP tool calls through `mcpClient.py`.

import websockets
import asyncio
from agent import get_agent
import json

# python -m venv agent

## home for core websockets outer loop
messages_memory = [] # for first version, store messages locally, and add new user messages on-top.

# need some kind of controller, to indicate whether a current agent is running - if it is, will automatically have new message aded
# if false, then need to actively create new agent run
agent_running = False
agents_state = {}

run_number = 0
current_ws = None


## need to ensure that agent_id is a key/value in messages_memory, and broken off later within each agent instance when called

async def run_agent(agent_id):
    global current_ws, agent_running
    try:
        agent = await get_agent()
        result = await agent.run(messages_memory, agent_id, current_ws)
        if current_ws:
            await current_ws.send(json.dumps({"agent_id": agent_id,"agent_response": result, "message_type": "task_result" }))
            agents_state[agent_id]["is_agent_running"] = False
            print(f"run_number so far: {run_number}")
    except Exception as e:
        if current_ws:
            await current_ws.send(json.dumps({"agent_id": agent_id,"agent_error": str(e), "message_type": "task_error" }))
            agents_state[agent_id]["is_agent_running"] = False
            print(f"run_number so far: {run_number}")



## i would like to move agent system from separate state that tracks which exist, and whcih are running
## to instantiating agent in this file, and then saving it in list, whcih can be triggered when neccesayr to run
## so that the class values can be accessed outisde of the agent

## add messages to supabase table, and add in agent_session_id

async def handler(ws):
    print("Client connected")

    global agent_running
    global run_number
    global current_ws
    current_ws = ws


    ## re-arrange everything to allow multiple agents
    ## add in mcp logic, and parent re-start loop for token memory issue. and giving new folder for each run.

    try:
        async for message in ws:
            print("Received:", message)

            # 🔥 your logic here
            if message == "ping":
                await ws.send("pong")

            parsed_message = json.loads(message)
            print(f"parsed_message is: {parsed_message}")

            user_message = parsed_message["user_message"]
            agent_id = parsed_message["agent_id"]
            message_id = parsed_message["message_id"]

            agent_exists = agents_state.get(agent_id, None)
            if agent_exists:
                if agent_exists["is_agent_running"] == True:
                    # if agent exists, and is running - add message to existing run
                    ## when re-starting existing finished agent, probably need a intermediate message explaining to LLM?
                    messages_memory.append({ "role": "user", "content": user_message, "agent_id": agent_id, "message_id": message_id })
                else:
                    # if agent exists, not running - restart it
                    messages_memory.append({ "role": "user", "content": user_message, "agent_id": agent_id, "message_id": message_id  })
                    agents_state[agent_id]["is_agent_running"] = True
                    asyncio.create_task(run_agent(agent_id)) # - don't think i need to actually instantiate agent before
            else:
                # if agent doesn't exist yet, create it, and mark it as running
                messages_memory.append({ "role": "user", "content": user_message, "agent_id": agent_id, "message_id": message_id  })
                agents_state[agent_id] = {}
                asyncio.create_task(run_agent(agent_id))
                agents_state[agent_id]["is_agent_running"] = True

    except websockets.exceptions.ConnectionClosed:
        print("Client disconnected")


async def main():                                                                                                                                                                                                                                                                                                                                                           
    async with websockets.serve(handler, "localhost", 3013):                                                                        
        print("websocket server listening on 3076")                                                                                 
        await asyncio.Future() 

asyncio.run(main())
import websockets
import asyncio
from agentVariant import get_new_agent
import json
from gemini_helper import save_to_gemini

# python -m venv agent

## home for core websockets outer loop
messages_memory = [] # for first version, store messages locally, and add new user messages on-top.

# need some kind of controller, to indicate whether a current agent is running - if it is, will automatically have new message aded
# if false, then need to actively create new agent run
agents_state = {}

frontend_tool_queue = {}
human_in_loop_queue = {}

run_number = 0
current_ws = None

import uuid
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

## create agentBidirectionalController class
class AgentBidirectionalController():
    ## this is agnostic to agent run - works for any agent, not agent specific
    
    def __init__(self, ws, human_in_loop_queue):
        self.ws = ws
        self.human_in_loop_queue = human_in_loop_queue
    
    async def request_user_approval(self, tool_call, agent_id, existing_permission_given):
        if existing_permission_given == True:
            return True ## if user has already given permission (saved to agent instance), then don't need to ask again
        request_id = str(uuid.uuid4())

        future = asyncio.Future() ## or asyncio.get_running_loop().create_future() - which is more mdoern version
        
        self.human_in_loop_queue[request_id] = future

        await self.ws.send(json.dumps({"agent_id": agent_id, "request_id": request_id, "tool_call_request": tool_call, "message_type": "human_in_loop_request" }))#

        response =  await future
        return response
    
    def resolve_user_request(self, request_id, result):
        
        future = self.human_in_loop_queue.pop(request_id, None) ## better to permantly rmeove it, once respponse recievd
        if future is None:
            return
        
        if not future.done():
            future.set_result(result) # user's response from frontend
        # or could check .done() first, to make certain it hasn't been marked as done yet





## need to ensure that agent_id is a key/value in messages_memory, and broken off later within each agent instance when called

async def run_agent(agent_id):
    global current_ws, agent_running
    try:
        agent = agents_state.get(agent_id)
        result = await agent.run(messages_memory, current_ws)
        if current_ws:
            await current_ws.send(json.dumps({"agent_id": agent_id,"agent_response": result, "message_type": "task_result" }))
            agent.is_running = False
            print(f"run_number so far: {run_number}")
    except Exception as e:
        if current_ws:
            await current_ws.send(json.dumps({"agent_id": agent_id,"agent_error": str(e), "message_type": "task_error" }))
            agent.is_running  = False
            print(f"run_number so far: {run_number}")



## i would like to move agent system from separate state that tracks which exist, and whcih are running
## to instantiating agent in this file, and then saving it in list, whcih can be triggered when neccesayr to run
## so that the class values can be accessed outisde of the agent

## add messages to supabase table, and add in agent_session_id


def does_agent_exist(agent_id):

    return agents_state.get(agent_id, None)

async def handler(ws):
    print("Client connected")

    global agent_running
    global run_number
    global current_ws
    current_ws = ws
    bidirectionalController = AgentBidirectionalController(current_ws, human_in_loop_queue)


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

            user_message = parsed_message.get("user_message", None)
            agent_id = parsed_message["agent_id"]
            message_id = parsed_message.get("message_id", None)
            frontend_tool_call = parsed_message.get("frontend_tool_call", None)
            human_in_loop_response = parsed_message.get("human_in_loop_response", None)

            ## check if human in loop response
            if human_in_loop_response:
                bidirectionalController.resolve_user_request(parsed_message["request_id"], parsed_message["result"])
                continue
            if frontend_tool_call:
                ## must be result for frontend tool call
                result = parsed_message["frontend_tool_call_result"]
                frontend_tool_call_id = parsed_message["frontend_tool_call_id"]
                frontend_tool_queue[frontend_tool_call_id].set_result(result) ## because existing value is intsance of asyncio.Future()
            else:   
                files = parsed_message.get('files', None)
                if files:
                    gemini_files_ids = save_to_gemini(files)
                    ## create a helper function to upload files to Gemini, and get ids back
                    new_formatted_message = { "role": "user", "content": user_message, "agent_id": agent_id, "message_id": message_id, "files": gemini_files_ids }
                else:
                    new_formatted_message = { "role": "user", "content": user_message, "agent_id": agent_id, "message_id": message_id }
            ## if supabase id/s exist in message, then retrieve the files here
            ## and then to the message when added to messages_memory below
            ## then format files for gemini llm api call within specific agent


                agent_exists = does_agent_exist(agent_id)
                if agent_exists:
                    current_agent = agents_state.get(agent_id) # agents are stored as dict, indexed by their agent_instance
                    if current_agent.is_running == True:
                    # if agent exists, and is running - add message to existing run
                    ## when re-starting existing finished agent, probably need a intermediate message explaining to LLM?
                        messages_memory.append(new_formatted_message)
                    else:
                    # if agent exists, not running - restart it
                        messages_memory.append(new_formatted_message)
                        current_agent.is_running = True
                        asyncio.create_task(run_agent(agent_id)) # - don't think i need to actually instantiate agent before
                else:
                # if agent doesn't exist yet, create it, and mark it as running
                    messages_memory.append(new_formatted_message)
                # create new agent
                    new_agent = await get_new_agent(agent_id, frontend_tool_queue, bidirectionalController)
                    new_agent.is_running = True
                    agents_state[agent_id] = new_agent
                    asyncio.create_task(run_agent(agent_id))
    except websockets.exceptions.ConnectionClosed:
        print("Client disconnected")


async def main():                                                                                                                                                                                                                                                                                                                                                           
    async with websockets.serve(handler, "localhost", 3077):                                                                        
        print("websocket server listening on 3077")                                                                                 
        await asyncio.Future() 

asyncio.run(main())
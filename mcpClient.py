## mcp client with https-sse transporrt



# pip install mcp httpx
import asyncio
from mcp import ClientSession
from mcp.client.sse import sse_client
from mcp.client.streamable_http import streamable_http_client
import traceback
from fastmcp import Client

from fastmcp.client.auth import OAuth

oauth = OAuth(scopes=["user"])

async def mcpClientListTools(mcp_server_url_list): # param needs to be an array of urls, not direct url

    tool_list = []
    known_mcp_tools_for_agent = {} # needs to be index on function name, with value as url

    

    for mcp_server_url in mcp_server_url_list:

        try:
            print(f"connecting to mcp server {mcp_server_url} ..")

            #client = Client(mcp_server_url) https://eager-coffee-toad.fastmcp.app/mcp

            async with Client(mcp_server_url) as client:
                await client.ping()

                tools = await client.list_tools()
                print(f"tools are: {tools}")

                

                for tool in tools:
                        print(f"tool name: {tool.name}")
                        print(f"tool description: {tool.description}")
                        print(f"tool input schema: {tool.inputSchema}")

                        tool_item = {
                            "tool_name": tool.name,
                            "tool_deescription": tool.description,
                            "tool_input_schema": tool.inputSchema ## not sure break into optional and required params makes sense
                        }
                        #in order for this tool_item with input_schema to work in inauvural version, would need to exempt it
                        # from the param checker functionality - as it would break it,
 
                        known_mcp_tools_for_agent[f"{tool.name}"] = mcp_server_url 
                        tool_list.append(tool_item)

            #async with streamable_http_client(url=mcp_server_url) as (read_stream, write_stream, _):
                #print("hhhh")

                #async with ClientSession(read_stream, write_stream) as session:
                   # print("inside session")
                   # await session.initialize()

                    #response = await session.list_tools()
                    #tools = response.tools

                    #for tool in tools:
                      #  print(f"tool name: {tool.name}")
                       # print(f"tool description: {tool.description}")
                       # print(f"tool input schema: {tool.inputSchema}")

                        #tool_item = {
                           # "tool_name": tool.name,
                           # "tool_deescription": tool.description,
                           # "tool_input_schema": tool.inputSchema ## not sure break into optional and required params makes sense
                        #}
                        #in order for this tool_item with input_schema to work in inauvural version, would need to exempt it
                        # from the param checker functionality - as it would break it,
 
                       # known_mcp_tools_for_agent[f"{tool.name}"] = mcp_server_url 
                        #tools.append(tool_item)
               
        except Exception as e:
            print(f"\nInner exceptions: {e}")
            #for i, exc in enumerate(e.exceptions, 1):
                #print(f"\n--- sub-exception {i} ---")
               # print(f"{type(exc).__name__}: {exc}")
                #traceback.print_exception(type(exc), exc, exc.__traceback__)
        
    return tool_list, known_mcp_tools_for_agent
            ## then can return tools for listing tools in correct format
            ## and separtely, call tools

            # i think save each tool with tool_name as index, and url as value
            # then, when fucntions returned by LLM,. check fio any tool_name matches - if so
            # if so, then use mcpClientCallTool (create this) and use server_url attached as value



async def mcpClientCallTool(url: str, tool_name, tool_args): # what params to call
    
    try: 
        async with Client(url) as client:
            await client.ping()
                    

            result = await client.call_tool(tool_name, arguments=tool_args)
            print(f"result is: {result}")

            return result.content
    
    except Exception as e:
        print(f"Exception occured: {e}")



async def main():
   # mcpClientListTools, mcpClient
    result = await mcpClientListTools(['http://127.0.0.1:9000/mcp'])
    print(f"result is: {result}")

    args =  { "a": 7, "b": 14 }
    args1 = {"genre": "English"}
            
    result1 = await mcpClientCallTool('http://127.0.0.1:9000/mcp', 'choose_genre', args1)
    print(f"tool call result is: {result1}")


#asyncio.run(main())
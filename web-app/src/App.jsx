import { useEffect, useRef, useState } from "react";
import { supabase } from "../supabase/supabase.js";
import { get_user_location } from "../frontendTools/tools.js";
import { HumanInLoopModal } from "../components/modal.jsx";

const functionUI = {
  read_todo: "📝",
  write_todo: "📝",
  edit_todo_list: "📝",
  }



export default function App() {
  const [agentIds, setAgentIds] = useState([]);
  const [agentMessages, setAgentMessages] = useState({}) // array of dicts of arrays
  const [draftMessages, setDraftMessages] = useState({});
  const [ agentTaskFiles, setAgentTaskFiles] = useState({})
  const clientSideTools = {"get_user_location": get_user_location } // add in each imported
  const wsRef = useRef(null);

  // create array of local tools, which have been imported form localTools.ts
  // need taskFiles, array of File objects index by agentId - or draftMessagesFile ? some way to save to supabase when request made

useEffect(() => {
  console.log("agentTaskFiles are: ", agentTaskFiles);


},[agentTaskFiles])
  // add supabase

  // Local hook, and sync with supabase.
  // After adding to supabase, setAgentIds((prev) => [...prev, newAgentId]).
  const webSocketUrl = "ws://localhost:3077";

  async function sendClientToolMessage(agentId, toolResult, frontendToolCallId, error, errorMessage ) {
    

    const socket = wsRef.current;

    if (!socket || socket.readyState !== WebSocket.OPEN) {
      console.log("websocket is not connected");
      return;
    }

    if (error) {
      socket.send(JSON.stringify({ agent_id: agentId, frontend_tool_call_result: null, frontend_tool_call_id: frontendToolCallId, error: true, error_message: errorMessage, frontend_tool_call: true   }));
    } else {
      socket.send(JSON.stringify({ agent_id: agentId, frontend_tool_call_result: toolResult, frontend_tool_call_id: frontendToolCallId, error: false, error_message: null, frontend_tool_call: true  }));
    
    }

    
  
    
  }

  useEffect(() => {
    const ws = new WebSocket(webSocketUrl);
    wsRef.current = ws;

    ws.onopen = () => {

    }

    ws.onmessage = async (event) => {
      console.log("event recieved by websocket frontend: ", event);
      const eventParsed = JSON.parse(event.data);
      // then figure out which agent it belongs to by agent_id.
      let agentId = eventParsed.agent_id;
      let agentResponse = eventParsed.agent_response;
      let messageType = eventParsed.message_type;
      let toolCallRequest = eventParsed?.tool_call_request
      let requestId = eventParsed?.request_id

      if (messageType === "client_side_tool_call") {
        console.log("frontend_tool_call recieved: ", eventParsed);
        const toolName = eventParsed.tool_name
        const args = eventParsed.args ?? {}
        const frontendToolCallId = eventParsed.frontend_tool_call_uuid 

        // then, use tool name to locate the function to call
        const chosenTool = clientSideTools[toolName];
        if (!chosenTool) {
          // need to handle tool not being found or existing
          sendClientToolMessage(agentId, null, frontendToolCallId, true, "chosen tool did not exist in frontend" )
        }
        try {
        const result = await chosenTool(args);
        console.log("result from frontend tool call is: ", result);
        
        sendClientToolMessage(agentId, result, frontendToolCallId, false, null)

        } catch(e) {
           sendClientToolMessage(agentId, null, frontendToolCallId, true, String(e) )
        }

        // then return outcome
      
      }
      // if messageType === 'human_in_loop_request'
      // need to send new message back for human in loop, with same human-in-loop uuid, but also mark original message as 'complete'
      // for filtering to find any for each agent
      if (messageType === "human_in_loop_request") {
        setAgentMessages((prev) => ({...prev, [agentId]: [...(prev[agentId] ?? []),  {"toolCallRequest": toolCallRequest , "type": messageType, "requestId": requestId, "requestCompleted": false, "agentId": agentId }]}))
      }

      if (messageType === "task_result") {
      setAgentMessages((prev) => ({...prev, [agentId]: [...(prev[agentId] ?? []), { "content": agentResponse, "type": messageType} ]}))
      } else if (messageType === "function_call") {
      setAgentMessages((prev) => ({...prev, [agentId]: [...(prev[agentId] ?? []), { "content": agentResponse, "type": messageType, "functionName": eventParsed.function_name } ]}))
      } else if (messageType === 'client_side_tool_call') {
        // need to look for client_side_tool name in 
        // find tool with tool name from clientSideTools array
        // then execute, then return output with new WS message, and same UUID as original message
      }




      // easier just to keep two states, one for agentIds, one for messages. 
    }


    // on reception of message, filter by agent_id, and save under agentMessages by id. dict index by agentId, values are array of messages

    return () => {
      ws.close();
      wsRef.current = null;
    };
  }, [webSocketUrl]);


  async function supabaseSaveFile(agentId, fileList) {

    const files = Array.from(fileList);

    const uploads = files.map(async (file) => {
    const safeName = file.name.replace(/[^\w.-]/g, "_");
    const path = `inputs/${crypto.randomUUID()}-${safeName}`;

    console.log("file on insert is: ", file);

    const { data, error } = await supabase.storage
      .from("agent_files")
      .upload(path, file, {
        cacheControl: "3600",
        upsert: false,
        contentType: file.type,
      })

    if (error) throw error;
    console.log("data is:", data);

    const { data: publicUrlData } = supabase.storage                                                                                    
    .from("agent_files")                                                                                                              
    .getPublicUrl(path); 
    
    return {
      ...data,
      publicUrl: publicUrlData.publicUrl,
      file_name: file.name,
      file_type: file.type,
      path
    }
  });

  const results = await Promise.all(uploads);
  console.log("results from saving files to supabase: ", results);
  return results
  }

  async function addAgentId() {
    const newAgentId = crypto.randomUUID();


    if (!supabase) {
      console.log("supabase client not available, adding agentId locally:", newAgentId);
      setAgentIds((prev) => [...prev, newAgentId]);
      return;
    }

    const { data, error } = await supabase
      .from("agent_id_table")
      .insert({ agent_id: newAgentId })
      .select();

    if (error) {
      console.log("there was an error saving new agentId in supabase:", error);
      return;
    }

    const savedAgentId = data?.[0]?.agent_id ?? newAgentId;

    console.log("agentId successfully saved to supabase:", data);

    setAgentIds((prev) => [...prev, savedAgentId ]);
    setAgentMessages((prev) => ({...prev, [savedAgentId]: []}))
  }
  

  async function sendUserMessage(agentId, message) {
    const trimmedMessage = message.trim();

    if (!trimmedMessage) {
      return;
    }

    const socket = wsRef.current;

    if (!socket || socket.readyState !== WebSocket.OPEN) {
      console.log("websocket is not connected");
      return;
    }

    // create unique message uuid, for more specificity than agent_id
    const messageId = crypto.randomUUID()

    // check if the current agentId has any files attached, ready to be uploaded to supabase
    if (agentTaskFiles[agentId]) {
      console.log("agentTaskFiles exist for current user task request about to be triggered - will save to supabase and retrieved public urls..");
      const files = await supabaseSaveFile(agentId, agentTaskFiles[agentId]);
      socket.send(JSON.stringify({ agent_id: agentId, user_message: trimmedMessage, message_id: messageId, files: files  }));
      setAgentMessages((prev) => ({...prev, [agentId]: [...(prev[agentId] ?? []), { agent_id: agentId, user_message: trimmedMessage, type: "user_question_task", message_id: messageId, files: files }]}))
      // then wipe existing files, so they don't get re-sbubmitted next time
      agentTaskFiles[agentId] = [];
      setDraftMessages((draftMessagesClone) => {
        let existing = draftMessagesClone
        existing.agentId = ""
        return existing
      })
    } else {

    socket.send(JSON.stringify({ agent_id: agentId, user_message: trimmedMessage, message_id: messageId }));
    setAgentMessages((prev) => ({...prev, [agentId]: [...(prev[agentId] ?? []), { agent_id: agentId, user_message: trimmedMessage, type: "user_question_task", message_id: messageId }]}))
    setDraftMessages((draftMessagesClone) => ({
      ...draftMessagesClone,
      [agentId]: ""
    })
  
  )
  }
    
  }

  function updateDraftMessage(agentId, value) {
    setDraftMessages((prev) => ({ ...prev, [agentId]: value }));
  }

  useEffect(() => {
    console.log("agentMessage are: ", agentMessages);
  },[agentMessages])


  async function downloadFile(fileUrl) {
    if (!fileUrl) {
      console.log("fileUrl inside of downloadFile does not actually exist - returning.. ");
      return;
    }

    const response = await fetch(fileUrl);
const blob = await response.blob();

const url = window.URL.createObjectURL(blob);

const a = document.createElement("a");
a.href = url;
a.download = fileUrl;
a.click();

window.URL.revokeObjectURL(url);
  }


  function addFiles(files, agentId) { // files will be a FileList object
    const filesArray = Array.from(files ?? []);
    if (filesArray.length === 0) return;

    setAgentTaskFiles((prev) => ({
      ...prev,
      [agentId]: [...(prev[agentId] ?? []), ...filesArray],
    }));
  }

  return (
    <main className="h-screen bg-slate-100 p-4 md:p-6">
      <section className="flex h-full w-full flex-col rounded-2xl bg-white p-6 shadow-sm ring-1 ring-slate-200 md:p-8">
        <div className="flex flex-col gap-5 border-b border-slate-200 pb-6 md:flex-row md:items-end md:justify-between">
          <div>
            <p className="text-sm font-medium uppercase tracking-[0.2em] text-slate-500">
              Web App
            </p>
            <h1 className="mt-4 text-3xl font-semibold text-slate-900">
              Agent Tasks
            </h1>
            <p className="mt-3 max-w-2xl text-base leading-7 text-slate-600">
              Create a task card for each agent ID, then send a message from that card.
            </p>
          </div>
          <button
            type="button"
            onClick={addAgentId}
            className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white transition hover:bg-blue-500"
          >
            Create New Task
          </button>
        </div>

        <div className="flex-1 overflow-auto pt-6">
          {Array.isArray(agentIds) && agentIds.length > 0 ? (
            <div className="grid grid-cols-[repeat(auto-fill,minmax(320px,1fr))] gap-4">
              {agentIds.map((agentId) => {

                const findCurrentAgentTask = agentMessages[agentId]
                  ? agentMessages[agentId].filter((message) => message.type === "user_question_task").at(-1)
                  : null;
                const latestAgentTaskQuestion = findCurrentAgentTask?.user_message ?? null;

                // use agentMessages, whcih will have files if they exist for user input, to show files sent from latestAgentTaskQuestion
             
                return (
                <article
                  key={agentId}
                  className="relative flex min-h-[18rem] flex-col overflow-hidden rounded-xl border border-slate-200 bg-slate-50 p-5"
                >
                  <div className="flex items-start justify-between gap-4">
                    <h2 className="text-lg font-semibold text-slate-900">
                      Task
                      {latestAgentTaskQuestion ? ` - ${latestAgentTaskQuestion}` : ""}
                    </h2>
                    <span className="max-w-[13rem] truncate rounded-full bg-white px-3 py-1 text-xs font-semibold text-slate-500 ring-1 ring-slate-200">
                      {agentId}
                    </span>
                  </div>

                  {agentMessages[agentId] && (() => {
                     
                     //console.log("message inside of agentMessage[agentId] is: ", message);

                     // need to retrieve the user's question sent - so it can be displayed as current question being answered
                     // find latest messgae for this agentId, that is 'user_question_task'

                     // see if any toolCallRequestExist and if requestCompleted is false
                     // after user responds, send ws to backend, but also filter agentMessages[agentId]
                     // to mark requestCompleted as true, so it no longer appears
                     let humanInLoopRequestslist = agentMessages[agentId].filter((message) => message["type"] === "human_in_loop_request" && message["requestCompleted"] === false)
                     // if multiple exist, get most last
                     let latestHumanInLoopRequest = null;
                     if (humanInLoopRequestslist.length > 0) {
                      latestHumanInLoopRequest = humanInLoopRequestslist.at(-1)
                     } else {
                      latestHumanInLoopRequest = null
                     }
                     console.log("humanInLoopRequestList is: ", humanInLoopRequestslist);
                     console.log("latestHumanInLoopRequest is: ", latestHumanInLoopRequest);
                     // need to add in time sent, on backend, so i can reliably sort for latest in the future
                     // latestHumanInLoopRequest["toolCalRequest"]

                     // if latestHumanInLoopRequest exists, conditionally render JSX
                     // and render toolCallRequest

                     // function to handle response by user
                     function handleHumanInLoopResponse(approval, request) {

                      // update react hook messages array
                      setAgentMessages((agentMessages) => ({
                        ...agentMessages,
                        [agentId]: (agentMessages[agentId] ?? []).map(message => message.requestId === request.requestId ? {...message, "requestCompleted": true } : message)
                      }))
                      // then send message back to backend, re-using requestId and agentId
                      // need "human_in_loop_response" True, and result with True or False
                      const socket = wsRef.current;

                      if (!socket || socket.readyState !== WebSocket.OPEN) {
                         console.log("websocket is not connected");
                         return;
                      }

                      socket.send(JSON.stringify({"human_in_loop_response": true, "agent_id": request["agentId"], "request_id": request["requestId"], "result": approval }))

                     }

                     

                     // get and show the most recent message - so, text, function or result
                     const latestAgentTaskAnswer = agentMessages[agentId] ? agentMessages[agentId].at(-1) : null;
                     console.log("latestAgentTaskAnswer is: ", latestAgentTaskAnswer);

                     let answer = null;
                     let files = null;
                     let functionUIVisual = null;

                     // then, make choice by type
                     if (latestAgentTaskAnswer && latestAgentTaskAnswer.type === "task_result") {

                      let convertedContent = JSON.parse(latestAgentTaskAnswer.content);
                      console.log("convertedContent is: ", convertedContent);

                      answer = convertedContent?.answer;
                  
                      if (convertedContent?.files) {
                        files = convertedContent.files;
                      }

                     } else if (latestAgentTaskAnswer && latestAgentTaskAnswer.type === "function_call") {
                      // then show function call
                      // import different icon, dependent on name - need to return function name from backend
                      // and have different conditional for skills, mcp calls
                      functionUIVisual = functionUI[latestAgentTaskAnswer.functionName];
                      console.log("functionUIVisual chosen is: ", functionUIVisual);
                     
                    } else {
                      answer = null;
                     files = null;
                     functionUIVisual = null;
                    }

                     /*const agentTaskAnswer = agentMessages[agentId].find((message) => message.type === "task_result");
                     console.log("result from agent task exists: ", agentTaskAnswer);

                     

                     if (agentTaskAnswer) {
                      let convertedContent = JSON.parse(agentTaskAnswer.content);
                      console.log("convertedContent is: ", convertedContent);

                      answer = convertedContent?.answer;
                  
                      if (convertedContent?.files) {
                        files = convertedContent.files;
                      }
                     }*/

                     // only return most recent message for display?
                     // and only if it's the final response.
                     return (
                      <>
                      {latestHumanInLoopRequest && !latestHumanInLoopRequest.requestCompleted && (
                        <HumanInLoopModal latestHumanInLoopRequest={latestHumanInLoopRequest} handleHumanInLoopResponse={handleHumanInLoopResponse} />
                      )}
    
                      {answer && (
                        <p>Answer: {answer}</p>
                      )}
                      { functionUIVisual && (
                        <>
                        <h3>{functionUIVisual} - {latestAgentTaskAnswer.functionName}</h3>
                        </>
                      )}
                      {files && files.map((file, idx) => (
                        <div key={idx}>
                        <p>{file?.file_name ?? `file`}</p>
                        <button onClick={()=> downloadFile(file?.file_path)}>download file</button>
                        </div>
                      ))}
                      </>
                     )
                     
                     
                     })()}

                  <textarea
                    value={draftMessages[agentId] ?? ""}
                    onChange={(event) => updateDraftMessage(agentId, event.target.value)}
                    placeholder="Enter a message for this agent"
                    className="mt-4 min-h-32 flex-1 resize-none rounded-lg border border-slate-300 bg-white px-4 py-3 text-sm text-slate-900 outline-none transition focus:border-slate-400 focus:ring-2 focus:ring-slate-200"
                  />

                  <div className="mt-4 flex items-center justify-between gap-3">
                    <div className="flex items-center gap-3">
                      <button
                        type="button"
                        onClick={() => sendUserMessage(agentId, draftMessages[agentId] ?? "")}
                        className="rounded-lg bg-slate-900 px-4 py-2 text-sm font-medium text-white transition hover:bg-slate-700"
                      >
                        Submit
                      </button>

                      <label
                        htmlFor={`file-upload-${agentId}`}
                        className="cursor-pointer rounded-lg border border-slate-300 bg-white px-4 py-2 text-sm font-medium text-slate-700 transition hover:border-slate-400 hover:bg-slate-100"
                      >
                        Add Files
                      </label>
                      <input
                        id={`file-upload-${agentId}`}
                        type="file"
                        multiple
                        onChange={(e) => addFiles(e.target.files, agentId)}
                        className="hidden"
                      />
                    </div>

                    {!!agentTaskFiles[agentId]?.length && (
                      <span className="text-xs font-medium text-slate-500">
                        {agentTaskFiles[agentId].length} file{agentTaskFiles[agentId].length === 1 ? "" : "s"} selected
                      </span>
                    )}
                  </div>
                </article>
                );
              })}
            </div>
          ) : (
            <div className="flex h-full min-h-[16rem] items-center justify-center rounded-2xl border border-dashed border-slate-300 bg-slate-50 px-6 text-center text-sm text-slate-500">
              No tasks yet. Create a new task to add the first agent card.
            </div>
          )}
        </div>
      </section>
    </main>
  );
}


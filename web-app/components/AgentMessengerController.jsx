import { useLayoutEffect, useRef } from "react";
import { HumanInLoopModal } from "./modal.jsx";
import AskFurtherInformation from "./AskFurtherInformation.jsx";

const functionUI = {
  read_todo: "📝",
  write_todo: "📝",
  edit_todo_list: "📝",
};

function displayContent(content) {
  return typeof content === "string" ? content : JSON.stringify(content, null, 2);
}

export default function AgentMessengerController({
  agentId,
  messages,
  websocket,
  handleHumanInLoopResponse,
  handleHumanInputResponse,
  downloadFile,
}) {
  const chatRef = useRef(null);

  // Scroll only this agent's chat after its messages change, including on mount.
  // Native DOM scrolling keeps the behavior visible and editable here.
  useLayoutEffect(() => {
    const chat = chatRef.current;
    if (chat) chat.scrollTop = chat.scrollHeight;
  }, [messages]);

  function renderFiles(files, uploadedByUser = false) {
    return files?.map((file, index) => (
      <button
        key={`${file.file_path ?? file.publicUrl ?? file.file_name}-${index}`}
        type="button"
        onClick={() => downloadFile(uploadedByUser ? file.publicUrl : file.file_path)}
        className="mt-3 block max-w-full break-all text-left text-sm font-medium text-blue-700 underline underline-offset-2 hover:text-blue-900 focus-visible:outline focus-visible:outline-2 focus-visible:outline-blue-600"
      >
        {file.file_name ?? "Download file"}
      </button>
    ));
  }

  function renderMessage(message, index) {
    switch (message.type) {
      case "user_question_task":
        return (
          <div className="ml-auto max-w-[90%] rounded-xl bg-blue-100 px-4 py-3 text-slate-900">
            <p className="mb-1 text-xs font-semibold text-blue-800">You</p>
            <p className="whitespace-pre-wrap break-words">{message.user_message}</p>
            {renderFiles(message.files, true)}
          </div>
        );

      case "task_result": {
        let result;
        try {
          result = typeof message.content === "string" ? JSON.parse(message.content) : message.content;
        } catch {
          return <p role="alert" className="text-sm text-red-700">The agent returned an unreadable response.</p>;
        }

        if (result?.type === "custom_ui") {
          return (
            <div className="min-w-0 overflow-hidden rounded-xl border border-slate-200 bg-white">
              <p className="border-b border-slate-200 px-4 py-2 text-xs font-semibold text-slate-600">Agent · Custom component</p>
              <iframe
                title={`Agent ${agentId} custom response ${index + 1}`}
                sandbox="allow-scripts"
                srcDoc={`<!DOCTYPE html>
<html>
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <style>${result.css ?? ""}</style>
  </head>
  <body>
    ${result.html ?? ""}
    <script>${result.js ?? ""}</script>
  </body>
</html>`}
                className="block h-[500px] w-full border-0"
              />
            </div>
          );
        }

        return (
          <div className="rounded-xl border border-slate-200 bg-white px-4 py-3">
            <p className="mb-1 text-xs font-semibold text-slate-600">Agent</p>
            <p className="whitespace-pre-wrap break-words">{result?.answer}</p>
            {renderFiles(result?.files)}
          </div>
        );
      }

      case "function_call":
      case "client_side_tool_call":
        return (
          <div className="rounded-lg border-l-2 border-slate-300 bg-slate-100 px-4 py-3 text-sm text-slate-700">
            <p className="font-medium">{functionUI[message.functionName]} {message.functionName ?? "Tool update"}</p>
            <p className="mt-1 whitespace-pre-wrap break-words">{displayContent(message.content)}</p>
          </div>
        );

      case "task_error":
        return <p role="alert" className="rounded-lg bg-red-50 px-4 py-3 text-sm text-red-700">Error: {message.content}</p>;

      case "human_in_loop_request":
        if (message.requestCompleted) {
          return (
            <p className="rounded-lg bg-slate-100 px-4 py-3 text-sm text-slate-600">
              Tool request {message.approved === false ? "declined" : "approved"}: {displayContent(message.toolCallRequest)}
            </p>
          );
        }
        return (
          <div className="relative min-h-[24rem] overflow-hidden rounded-xl">
            <HumanInLoopModal
              latestHumanInLoopRequest={message}
              handleHumanInLoopResponse={handleHumanInLoopResponse}
            />
          </div>
        );

      case "human_input_request":
        if (message.requestCompleted) {
          return (
            <div className="rounded-lg border border-slate-200 bg-white px-4 py-3">
              <p className="mb-1 text-xs font-semibold text-slate-600">Agent · Follow-up answered</p>
              <p className="whitespace-pre-wrap break-words">{message.humanInputRequest}</p>
            </div>
          );
        }
        return (
          <AskFurtherInformation
            websocket={websocket}
            agentId={agentId}
            requestCompleted={message.requestCompleted}
            question={message.humanInputRequest}
            onRequestCompletion={(answer, messageId) => handleHumanInputResponse(agentId, message.requestId, answer, messageId)}
          />
        );

      default:
        return <p className="whitespace-pre-wrap break-words text-sm text-slate-600">{displayContent(message.content)}</p>;
    }
  }

  return (
    <div
      ref={chatRef}
      role="region"
      aria-label={`Chat for agent ${agentId}`}
      tabIndex={0}
      className="min-h-0 flex-1 overflow-y-auto overscroll-contain rounded-xl border border-slate-200 bg-slate-50 p-3 focus-visible:outline focus-visible:outline-2 focus-visible:outline-blue-600 md:p-4"
      style={{ overflowWrap: "anywhere" }}
    >
      {messages.length === 0 ? (
        <p className="py-8 text-center text-sm text-slate-500">Send a message to start this conversation.</p>
      ) : (
        <div className="space-y-4">
          {messages.map((message, index) => (
            <div key={`${agentId}-${message.type}-${message.requestId ?? index}`}>
              {renderMessage(message, index)}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

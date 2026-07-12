export function HumanInLoopModal({ handleHumanInLoopResponse, latestHumanInLoopRequest }) {
  function requestApproved() {
    // close modal
    handleHumanInLoopResponse(true, latestHumanInLoopRequest);
  }

  function requestDeclined() {
    // close modal
    handleHumanInLoopResponse(false, latestHumanInLoopRequest);
  }

  const toolName =
    typeof latestHumanInLoopRequest.toolCallRequest === "string"
      ? latestHumanInLoopRequest.toolCallRequest
      : latestHumanInLoopRequest.toolCallRequest?.name ??
        latestHumanInLoopRequest.toolCallRequest?.tool_name ??
        latestHumanInLoopRequest.toolCallRequest?.functionName ??
        latestHumanInLoopRequest.toolCallRequest?.function_name ??
        "Tool request";

  return (
    <div className="absolute inset-0 z-30 flex flex-col justify-between rounded-xl bg-blue-500/95 p-6 text-white backdrop-blur-md">
      <div>
        <p className="text-xs font-semibold uppercase tracking-[0.22em] text-blue-50/80">
          Approval Required
        </p>
        <h2 className="mt-4 text-2xl font-semibold leading-tight text-white">
          Allow this tool call?
        </h2>

        <div className="mt-6 rounded-lg bg-blue-600/60 px-4 py-4 shadow-inner">
          <p className="text-xs font-semibold uppercase tracking-[0.18em] text-blue-50/80">
            Tool Name
          </p>
          <p className="mt-3 break-words font-mono text-lg font-semibold text-white">
            {toolName}
          </p>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-3 pt-6">
        <button
          type="button"
          onClick={requestDeclined}
          className="min-h-12 rounded-lg bg-blue-700 px-4 py-3 text-base font-semibold text-white shadow-sm transition hover:bg-blue-800 focus:outline-none focus:ring-2 focus:ring-white"
        >
          No
        </button>

        <button
          type="button"
          onClick={requestApproved}
          className="min-h-12 rounded-lg bg-white px-4 py-3 text-base font-semibold text-blue-700 shadow-sm transition hover:bg-blue-50 focus:outline-none focus:ring-2 focus:ring-white"
        >
          Yes
        </button>
      </div>
    </div>
  );
}

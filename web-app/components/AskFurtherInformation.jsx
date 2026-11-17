import {useState } from "react"







export default function AskFurtherInformation({ websocket, agentId, requestCompleted, onRequestCompletion,  question }) {
    const [ userAnswer, setUserAnswer ] = useState("")
    const [ showComponent, setShowComponent ] = useState(true);
    

    async function userResponse() {
        if (!userAnswer) return;

        let messageId = crypto.randomUUID()

        await websocket.send(JSON.stringify({ agent_id: agentId, user_message: userAnswer.trim(), message_id: messageId, message_type: "ask_further_information_response" }))
        setShowComponent(false);
        onRequestCompletion()
    }
 

    
    if (requestCompleted && userAnswer && !showComponent) return (
        <div className="flex flex-col gap-4 rounded-xl border border-slate-200 bg-white p-5">
            <div>
                <p className="text-sm font-medium text-slate-600">You were asked</p>
                <p className="mt-1 whitespace-pre-wrap break-words text-lg font-semibold text-slate-900">
                    {question}
                </p>
            </div>
            <div>
                <p className="text-sm font-medium text-slate-600">You answered</p>
                <p className="mt-1 whitespace-pre-wrap break-words text-base text-slate-900">
                    {userAnswer.trim()}
                </p>
            </div>
        </div>
    );

    return (
        <form
            onSubmit={(event) => {
                event.preventDefault();
                if (userAnswer.trim()) userResponse();
            }}
            className="flex flex-col gap-4 rounded-xl border border-slate-200 bg-white p-5"
        >
            <label className="flex flex-col gap-3">
                <span className="whitespace-pre-wrap break-words text-lg font-semibold text-slate-900">
                    {question}
                </span>
                <span className="text-sm font-medium text-slate-600">Your answer</span>
                <textarea
                    value={userAnswer}
                    onChange={(event) => setUserAnswer(event.target.value)}
                    placeholder="Type your answer..."
                    rows={4}
                    required
                    className="w-full resize-y rounded-lg border border-slate-300 bg-white px-3 py-3 text-base text-slate-900 placeholder:text-slate-500 focus:border-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-600"
                />
            </label>
            <button
                type="submit"
                disabled={!userAnswer.trim()}
                className="min-h-11 self-end rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white transition hover:bg-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-600 focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
            >
                Submit answer
            </button>
        </form>
    )

}

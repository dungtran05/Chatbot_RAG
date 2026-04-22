import { useState } from "react";

export default function ChatPanel({ conversation, onSend, loading }) {
  const [message, setMessage] = useState("");

  const submit = async (event) => {
    event.preventDefault();
    const trimmed = message.trim();
    if (!trimmed || loading) return;
    await onSend(trimmed);
    setMessage("");
  };

  return (
    <section className="chat-panel">
      <div className="chat-header">
        <p className="eyebrow">RAG Assistant</p>
        <h2>{conversation?.title || "Cuoc tro chuyen moi"}</h2>
      </div>

      <div className="messages">
        {(conversation?.messages || []).map((messageItem, index) => (
          <div key={`${messageItem.created_at}-${index}`} className={`message ${messageItem.role}`}>
            <span>{messageItem.role === "user" ? "Ban" : "Tro ly"}</span>
            <p>{messageItem.content}</p>
            {messageItem.role === "assistant" && messageItem.citations?.length > 0 && (
              <div className="message-meta">
                <strong>Nguon tham khao</strong>
                <ul className="citation-list">
                  {messageItem.citations.map((citation) => (
                    <li key={`${citation.index}-${citation.source || citation.header || "source"}`}>
                      [{citation.index}] {citation.source || "Unknown"}
                      {citation.header ? ` - ${citation.header}` : ""}
                      {citation.source_type ? ` (${citation.source_type})` : ""}
                    </li>
                  ))}
                </ul>
                <div className="retrieval-meta">
                  <span>Model: {messageItem.model}</span>
                  <span>Contexts: {messageItem.retrieval?.total_contexts ?? 0}</span>
                  <span>
                    Queries: {(messageItem.retrieval?.generated_queries || []).join(" | ")}
                  </span>
                </div>
              </div>
            )}
          </div>
        ))}
      </div>

      <form className="composer" onSubmit={submit}>
        <textarea
          placeholder="Nhap cau hoi..."
          rows={4}
          value={message}
          onChange={(event) => setMessage(event.target.value)}
        />
        <button type="submit">{loading ? "Dang xu ly..." : "Gui"}</button>
      </form>
    </section>
  );
}

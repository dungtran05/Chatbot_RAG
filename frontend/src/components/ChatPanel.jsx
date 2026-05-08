import { useEffect, useMemo, useRef, useState } from "react";

const labels = {
  assistant: "Tr\u1ee3 l\u00fd",
  citations: "Ngu\u1ed3n tham kh\u1ea3o",
  loading: "\u0110ang t\u00ecm c\u00e2u tr\u1ea3 l\u1eddi",
  newChat: "Cu\u1ed9c tr\u00f2 chuy\u1ec7n m\u1edbi",
  placeholder: "H\u1ecfi tr\u1ee3 l\u00fd...",
  send: "G\u1eedi c\u00e2u h\u1ecfi",
  upload: "Th\u00eam t\u00e0i li\u1ec7u",
  user: "B\u1ea1n",
};

function capitalizeFirstLetter(text) {
  const trimmed = (text || "").trim();
  if (!trimmed) return "";
  return trimmed.charAt(0).toLocaleUpperCase("vi-VN") + trimmed.slice(1);
}

function splitTokens(content) {
  return content.match(/\S+\s*/g) || [];
}

function cleanText(text) {
  return text.replace(/\*/g, "");
}

function shouldBold(text) {
  const cleaned = cleanText(text).trim();
  return cleaned.length > 0 && cleaned.length <= 70;
}

function InlineText({ text }) {
  const parts = text.split(/(\*\*[^*]+\*\*)/g).filter(Boolean);

  return parts.map((part, index) => {
    if (part.startsWith("**") && part.endsWith("**")) {
      const boldText = part.slice(2, -2);
      if (shouldBold(boldText)) {
        return <strong key={`${part}-${index}`}>{cleanText(boldText)}</strong>;
      }
      return cleanText(boldText);
    }
    return cleanText(part);
  });
}

function MessageText({ content }) {
  const blocks = content
    .split(/\n\s*\n/)
    .map((block) => block.trim())
    .filter(Boolean);

  return (
    <div className="message-content">
      {blocks.map((block, blockIndex) => {
        const lines = block.split("\n").filter(Boolean);
        const isList = lines.every((line) => /^(\*|-|\d+\.)\s+/.test(line.trim()));

        if (isList) {
          return (
            <ul key={`${block}-${blockIndex}`}>
              {lines.map((line, lineIndex) => (
                <li key={`${line}-${lineIndex}`}>
                  <InlineText text={line.replace(/^(\*|-|\d+\.)\s+/, "")} />
                </li>
              ))}
            </ul>
          );
        }

        return (
          <p key={`${block}-${blockIndex}`}>
            {lines.map((line, lineIndex) => (
              <span key={`${line}-${lineIndex}`}>
                <InlineText text={line} />
                {lineIndex < lines.length - 1 && <br />}
              </span>
            ))}
          </p>
        );
      })}
    </div>
  );
}

function LoadingBubble() {
  return (
    <div className="loading-bubble" aria-label={labels.loading}>
      <span />
      <span />
      <span />
    </div>
  );
}

function Citations({ citations }) {
  if (!citations?.length) return null;

  return (
    <div className="message-sources">
      <strong>{labels.citations}</strong>
      <ul className="citation-list">
        {citations.map((citation) => (
          <li key={`${citation.index}-${citation.source || citation.header || "source"}`}>
            [{citation.index}] "{citation.source || "Unknown"}"
            {citation.header ? ` - "${citation.header}"` : ""}
            {citation.source_type ? ` (${citation.source_type})` : ""}
          </li>
        ))}
      </ul>
    </div>
  );
}

function AssistantMessage({ messageItem, conversationId, onAnimationComplete }) {
  const tokens = useMemo(() => splitTokens(messageItem.content), [messageItem.content]);
  const [visibleTokenCount, setVisibleTokenCount] = useState(
    messageItem.animate ? 0 : tokens.length
  );
  const hasReportedComplete = useRef(false);

  useEffect(() => {
    if (!messageItem.animate) {
      setVisibleTokenCount(tokens.length);
      return undefined;
    }

    setVisibleTokenCount(0);
    const intervalId = window.setInterval(() => {
      setVisibleTokenCount((current) => {
        if (current >= tokens.length) {
          window.clearInterval(intervalId);
          return current;
        }
        return current + 1;
      });
    }, 45);

    return () => window.clearInterval(intervalId);
  }, [messageItem.animate, tokens.length]);

  const isComplete = visibleTokenCount >= tokens.length;
  const visibleContent = tokens.slice(0, visibleTokenCount).join("");

  useEffect(() => {
    if (!messageItem.animate || !isComplete || hasReportedComplete.current) return;
    hasReportedComplete.current = true;
    onAnimationComplete?.(conversationId, messageItem.created_at);
  }, [conversationId, isComplete, messageItem.animate, messageItem.created_at, onAnimationComplete]);

  return (
    <>
      <MessageText content={visibleContent} />
      {messageItem.animate && !isComplete && (
        <span className="typing-cursor">{labels.loading}...</span>
      )}
      {isComplete && <Citations citations={messageItem.citations} />}
    </>
  );
}

function MessageBubble({ messageItem, conversationId, onAnimationComplete }) {
  const isAssistant = messageItem.role === "assistant";

  return (
    <div className={`message-row ${messageItem.role}`}>
      <article className={`message ${messageItem.role} ${messageItem.loading ? "loading" : ""}`}>
        <span className="message-author">{isAssistant ? labels.assistant : labels.user}</span>
        {messageItem.loading ? (
          <LoadingBubble />
        ) : isAssistant ? (
          <AssistantMessage
            messageItem={messageItem}
            conversationId={conversationId}
            onAnimationComplete={onAnimationComplete}
          />
        ) : (
          <MessageText content={messageItem.content} />
        )}
      </article>
    </div>
  );
}

export default function ChatPanel({
  conversation,
  onSend,
  onAssistantAnimationComplete,
  loading,
}) {
  const [message, setMessage] = useState("");
  const messagesRef = useRef(null);
  const messages = conversation?.messages || [];

  useEffect(() => {
    const container = messagesRef.current;
    if (container) {
      container.scrollTo({ top: container.scrollHeight, behavior: "smooth" });
    }
  }, [messages.length, loading]);

  const submit = async (event) => {
    event.preventDefault();
    const trimmed = message.trim();
    if (!trimmed || loading) return;
    setMessage("");
    await onSend(trimmed);
  };

  const handleComposerKeyDown = (event) => {
    if (event.key !== "Enter" || event.shiftKey) return;
    event.preventDefault();
    event.currentTarget.form?.requestSubmit();
  };

  return (
    <section className="chat-panel">
      <header className="chat-header">
        <div>
          <p className="eyebrow">Trợ lý pháp luật</p>
          <h2>{capitalizeFirstLetter(conversation?.title || labels.newChat)}</h2>
        </div>
      </header>

      <main className="messages" ref={messagesRef}>
        {messages.length === 0 && (
          <div className="empty-state">
            <h1>Trợ Lý Pháp Luật</h1>
            <p>{"T\u1ea3i t\u00e0i li\u1ec7u v\u00e0 \u0111\u1eb7t c\u00e2u h\u1ecfi \u0111\u1ec3 nh\u1eadn c\u00e2u tr\u1ea3 l\u1eddi d\u1ef1a tr\u00ean ng\u1eef c\u1ea3nh c\u1ee7a b\u1ea1n."}</p>
          </div>
        )}

        {messages.map((messageItem, index) => (
          <MessageBubble
            key={messageItem.id || `${messageItem.created_at}-${index}`}
            messageItem={messageItem}
            conversationId={conversation?.id}
            onAnimationComplete={onAssistantAnimationComplete}
          />
        ))}
      </main>

      <form className="composer" onSubmit={submit}>
        <div className="composer-input">
          <textarea
            placeholder={labels.placeholder}
            rows={3}
            value={message}
            onChange={(event) => setMessage(event.target.value)}
            onKeyDown={handleComposerKeyDown}
          />
          <div className="composer-actions">
            <button
              type="submit"
              className="icon-button send-button"
              disabled={!message.trim() || loading}
              aria-label={labels.send}
              title={labels.send}
            >
              <span aria-hidden="true">&gt;</span>
            </button>
          </div>
        </div>
      </form>
    </section>
  );
}

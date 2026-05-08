function capitalizeFirstLetter(text) {
  const trimmed = (text || "").trim();
  if (!trimmed) return "";
  return trimmed.charAt(0).toLocaleUpperCase("vi-VN") + trimmed.slice(1);
}

export default function Sidebar({
  user,
  documents,
  conversations,
  activeConversationId,
  onNewConversation,
  onSelectConversation,
  onUpload,
  onDeleteDocument,
  onLogout,
}) {
  return (
    <aside className="sidebar">
      <div className="brand-block">
        <div className="brand-mark">R</div>
        <div>
          <p className="eyebrow">Trợ Lý Pháp Luật</p>
          <h2>{user.name}</h2>
        </div>
      </div>

      <div className="sidebar-section">
        <button className="new-chat-button" type="button" onClick={onNewConversation}>
          <svg viewBox="0 0 24 24" aria-hidden="true">
            <path d="M12 20h9" />
            <path d="M16.5 3.5a2.1 2.1 0 0 1 3 3L7 19l-4 1 1-4Z" />
          </svg>
          <span>{"Cu\u1ed9c tr\u00f2 chuy\u1ec7n m\u1edbi"}</span>
        </button>
        <button className="ghost account-button" type="button" onClick={onLogout}>
          <span>{user.email}</span>
          <strong>{"\u0110\u0103ng xu\u1ea5t"}</strong>
        </button>
      </div>

      <div className="sidebar-section">
        <label className="upload-sidebar-button">
          <input type="file" accept=".pdf,.txt,.md" hidden onChange={onUpload} />
          <span className="upload-sidebar-button__icon">+</span>
          <span className="upload-sidebar-button__text">
            <strong>{"Th\u00eam t\u00e0i li\u1ec7u"}</strong>
            <small>PDF, TXT, Markdown</small>
          </span>
        </label>

        <p className="section-title">{"T\u00e0i li\u1ec7u \u0111\u00e3 t\u1ea3i l\u00ean"}</p>
        <div className="list">
          {documents.map((doc) => (
            <div className="card-item document-card" key={doc.id}>
              <div className="document-card__body">
                <strong title={doc.filename}>{doc.filename}</strong>
                <span>{doc.chunk_count} chunks</span>
              </div>
              <button
                type="button"
                className="delete-doc-button"
                onClick={() => onDeleteDocument(doc.id)}
              >
                {"X\u00f3a"}
              </button>
            </div>
          ))}
          {documents.length === 0 && (
            <p className="empty-list">{"Ch\u01b0a c\u00f3 t\u00e0i li\u1ec7u."}</p>
          )}
        </div>
      </div>

      <div className="sidebar-section">
        <p className="section-title">{"L\u1ecbch s\u1eed tr\u00f2 chuy\u1ec7n"}</p>
        <div className="list">
          {conversations.map((item) => (
            <button
              key={item.id}
              className={`history-item ${activeConversationId === item.id ? "active" : ""}`}
              type="button"
              onClick={() => onSelectConversation(item)}
            >
              <strong>{capitalizeFirstLetter(item.title)}</strong>
              <span>{new Date(item.updated_at).toLocaleString()}</span>
            </button>
          ))}
          {conversations.length === 0 && (
            <p className="empty-list">{"Ch\u01b0a c\u00f3 l\u1ecbch s\u1eed."}</p>
          )}
        </div>
      </div>
    </aside>
  );
}

export default function Sidebar({
  user,
  documents,
  conversations,
  activeConversationId,
  onSelectConversation,
  onUpload,
  onDeleteDocument,
  onLogout,
}) {
  return (
    <aside className="sidebar">
      <div className="sidebar-section">
        <p className="eyebrow">Tai khoan</p>
        <h2>{user.name}</h2>
        <p className="muted">{user.email}</p>
        <button className="ghost" onClick={onLogout}>
          Dang xuat
        </button>
      </div>

      <div className="sidebar-section">
        <label className="upload-button upload-button--hero">
          <input type="file" accept=".pdf,.txt,.md" hidden onChange={onUpload} />
          <span className="upload-button__icon">+</span>
          <span className="upload-button__content">
            <strong>Them tai lieu</strong>
            <small>PDF, TXT, Markdown</small>
          </span>
        </label>

        <p className="section-title">Tai lieu da upload</p>
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
                Xoa
              </button>
            </div>
          ))}
        </div>
      </div>

      <div className="sidebar-section">
        <p className="section-title">Lich su tro chuyen</p>
        <div className="list">
          {conversations.map((item) => (
            <button
              key={item.id}
              className={`history-item ${activeConversationId === item.id ? "active" : ""}`}
              onClick={() => onSelectConversation(item)}
            >
              <strong>{item.title}</strong>
              <span>{new Date(item.updated_at).toLocaleString()}</span>
            </button>
          ))}
        </div>
      </div>
    </aside>
  );
}

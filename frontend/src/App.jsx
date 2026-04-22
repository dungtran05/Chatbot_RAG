import { useEffect, useState } from "react";
import api from "./api/client";
import AuthForm from "./components/AuthForm";
import ChatPanel from "./components/ChatPanel";
import Sidebar from "./components/Sidebar";
import { useAuth } from "./context/AuthContext";

export default function App() {
  const { user, logout } = useAuth();
  const [documents, setDocuments] = useState([]);
  const [conversations, setConversations] = useState([]);
  const [activeConversation, setActiveConversation] = useState(null);
  const [loading, setLoading] = useState(false);

  const loadData = async () => {
    const [docsResponse, historyResponse] = await Promise.all([
      api.get("/documents"),
      api.get("/history"),
    ]);
    setDocuments(docsResponse.data);
    setConversations(historyResponse.data);
    if (!activeConversation && historyResponse.data.length) {
      setActiveConversation(historyResponse.data[0]);
    }
  };

  useEffect(() => {
    if (user) {
      loadData().catch(console.error);
    }
  }, [user]);

  const handleUpload = async (event) => {
    const file = event.target.files?.[0];
    if (!file) return;
    const formData = new FormData();
    formData.append("file", file);
    await api.post("/documents/upload", formData, {
      headers: { "Content-Type": "multipart/form-data" },
    });
    await loadData();
    event.target.value = "";
  };

  const handleDeleteDocument = async (documentId) => {
    await api.delete(`/documents/${documentId}`);
    setDocuments((prev) => prev.filter((item) => item.id !== documentId));
  };

  const handleSend = async (message) => {
    setLoading(true);
    try {
      const { data } = await api.post("/chat", {
        message,
        conversation_id: activeConversation?.id || null,
      });

      let nextConversation = activeConversation;
      if (!nextConversation || nextConversation.id !== data.metadata.conversation_id) {
        nextConversation = {
          id: data.metadata.conversation_id,
          title: message.slice(0, 50),
          updated_at: new Date().toISOString(),
          messages: [],
        };
      }

      const updated = {
        ...nextConversation,
        updated_at: new Date().toISOString(),
        messages: [
          ...(nextConversation.messages || []),
          { role: "user", content: message, created_at: new Date().toISOString() },
          {
            role: "assistant",
            content: data.answer,
            citations: data.citations,
            retrieval: data.retrieval,
            model: data.metadata.model,
            created_at: new Date().toISOString(),
          },
        ],
      };

      setActiveConversation(updated);
      setConversations((prev) => {
        const filtered = prev.filter((item) => item.id !== updated.id);
        return [updated, ...filtered];
      });
    } finally {
      setLoading(false);
    }
  };

  if (!user) {
    return <AuthForm />;
  }

  return (
    <div className="app-shell">
      <Sidebar
        user={user}
        documents={documents}
        conversations={conversations}
        activeConversationId={activeConversation?.id}
        onSelectConversation={setActiveConversation}
        onUpload={handleUpload}
        onDeleteDocument={handleDeleteDocument}
        onLogout={logout}
      />
      <ChatPanel conversation={activeConversation} onSend={handleSend} loading={loading} />
    </div>
  );
}

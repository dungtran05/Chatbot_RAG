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

  // Tải danh sách tài liệu và lịch sử trò chuyện của user hiện tại.
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

  // Upload file tài liệu sang backend bằng FormData.
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

  // Xóa tài liệu khỏi backend và cập nhật lại danh sách trên giao diện.
  const handleDeleteDocument = async (documentId) => {
    await api.delete(`/documents/${documentId}`);
    setDocuments((prev) => prev.filter((item) => item.id !== documentId));
  };

  // Tạo cuộc trò chuyện mới bằng cách bỏ chọn conversation hiện tại.
  const handleNewConversation = () => {
    setActiveConversation(null);
  };

  // Tắt hiệu ứng gõ lại khi mở lịch sử trò chuyện cũ.
  const clearMessageAnimations = (conversation) => ({
    ...conversation,
    messages: (conversation.messages || []).map((message) => ({
      ...message,
      animate: false,
    })),
  });

  const handleSelectConversation = (conversation) => {
    setActiveConversation(clearMessageAnimations(conversation));
  };

  // Xóa một cuộc trò chuyện trong lịch sử.
  const handleDeleteConversation = async (conversationId) => {
    await api.delete(`/history/${conversationId}`);
    setConversations((prev) => prev.filter((item) => item.id !== conversationId));
    setActiveConversation((current) => (current?.id === conversationId ? null : current));
  };

  // Khi hiệu ứng trả lời chạy xong, lưu trạng thái để không animate lại.
  const handleAssistantAnimationComplete = (conversationId, createdAt) => {
    const clearAnimation = (conversation) => {
      if (!conversation || conversation.id !== conversationId) return conversation;
      return {
        ...conversation,
        messages: (conversation.messages || []).map((message) =>
          message.role === "assistant" && message.created_at === createdAt
            ? { ...message, animate: false }
            : message
        ),
      };
    };

    setActiveConversation((current) => clearAnimation(current));
    setConversations((prev) => prev.map((item) => clearAnimation(item)));
  };

  // Gửi câu hỏi đến backend, hiển thị loading trước rồi thay bằng câu trả lời thật.
  const handleSend = async (message) => {
    const now = new Date().toISOString();
    const pendingAssistantId = `pending-${now}`;
    const baseConversation =
      activeConversation || {
        id: null,
        title: message.slice(0, 50),
        updated_at: now,
        messages: [],
      };
    const optimisticConversation = {
      ...baseConversation,
      updated_at: now,
      messages: [
        ...(baseConversation.messages || []),
        { role: "user", content: message, created_at: now },
        {
          id: pendingAssistantId,
          role: "assistant",
          content: "",
          loading: true,
          created_at: now,
        },
      ],
    };

    setActiveConversation(optimisticConversation);
    setLoading(true);
    try {
      const { data } = await api.post("/chat", {
        message,
        conversation_id: activeConversation?.id || null,
      });

      // Nếu backend tạo conversation mới, frontend cập nhật lại id thật từ response.
      let nextConversation = optimisticConversation;
      if (!nextConversation || nextConversation.id !== data.metadata.conversation_id) {
        nextConversation = {
          id: data.metadata.conversation_id,
          title: message.slice(0, 50),
          updated_at: new Date().toISOString(),
          messages: optimisticConversation.messages,
        };
      }

      const updated = {
        ...nextConversation,
        updated_at: new Date().toISOString(),
        messages: (nextConversation.messages || []).map((item) =>
          item.id === pendingAssistantId
            ? {
                role: "assistant",
                content: data.answer,
                animate: true,
                citations: data.citations,
                retrieval: data.retrieval,
                model: data.metadata.model,
                created_at: new Date().toISOString(),
              }
            : item
        ),
      };

      setActiveConversation(updated);
      setConversations((prev) => {
        const filtered = prev.filter((item) => item.id !== updated.id);
        return [updated, ...filtered];
      });
    } catch (error) {
      setActiveConversation((current) => ({
        ...(current || optimisticConversation),
        messages: ((current || optimisticConversation).messages || []).map((item) =>
          item.id === pendingAssistantId
            ? {
                role: "assistant",
                content: "Không thể gửi câu hỏi. Vui lòng kiểm tra backend và thử lại.",
                created_at: new Date().toISOString(),
              }
            : item
        ),
      }));
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
        onNewConversation={handleNewConversation}
        onSelectConversation={handleSelectConversation}
        onDeleteConversation={handleDeleteConversation}
        onUpload={handleUpload}
        onDeleteDocument={handleDeleteDocument}
        onLogout={logout}
      />
      <ChatPanel
        conversation={activeConversation}
        onSend={handleSend}
        onAssistantAnimationComplete={handleAssistantAnimationComplete}
        loading={loading}
      />
    </div>
  );
}

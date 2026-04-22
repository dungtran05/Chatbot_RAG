import { useState } from "react";
import api from "../api/client";
import { useAuth } from "../context/AuthContext";

export default function AuthForm() {
  const { login } = useAuth();
  const [mode, setMode] = useState("login");
  const [form, setForm] = useState({ name: "", email: "", password: "" });
  const [error, setError] = useState("");

  const submit = async (event) => {
    event.preventDefault();
    setError("");
    try {
      const endpoint = mode === "login" ? "/auth/login" : "/auth/register";
      const payload =
        mode === "login"
          ? { email: form.email, password: form.password }
          : form;
      const { data } = await api.post(endpoint, payload);
      login(data);
    } catch (err) {
      setError(err.response?.data?.detail || "Authentication failed");
    }
  };

  return (
    <div className="auth-shell">
      <form className="auth-card" onSubmit={submit}>
        <p className="eyebrow">Chatbot RAG</p>
        <h1>{mode === "login" ? "Đăng nhập" : "Tạo tài khoản"}</h1>
        {mode === "register" && (
          <input
            placeholder="Họ tên"
            value={form.name}
            onChange={(event) => setForm({ ...form, name: event.target.value })}
          />
        )}
        <input
          placeholder="Email"
          type="email"
          value={form.email}
          onChange={(event) => setForm({ ...form, email: event.target.value })}
        />
        <input
          placeholder="Mật khẩu"
          type="password"
          value={form.password}
          onChange={(event) => setForm({ ...form, password: event.target.value })}
        />
        {error && <div className="error-text">{error}</div>}
        <button type="submit">{mode === "login" ? "Đăng nhập" : "Đăng ký"}</button>
        <button
          type="button"
          className="ghost"
          onClick={() => setMode(mode === "login" ? "register" : "login")}
        >
          {mode === "login" ? "Chuyển sang đăng ký" : "Chuyển sang đăng nhập"}
        </button>
      </form>
    </div>
  );
}


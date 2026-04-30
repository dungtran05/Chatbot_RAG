import { useState } from "react";
import api from "../api/client";
import { useAuth } from "../context/AuthContext";

const text = {
  email: "Email",
  failed: "\u0110\u0103ng nh\u1eadp kh\u00f4ng th\u00e0nh c\u00f4ng",
  login: "\u0110\u0103ng nh\u1eadp",
  name: "H\u1ecd t\u00ean",
  password: "M\u1eadt kh\u1ea9u",
  register: "\u0110\u0103ng k\u00fd",
  switchLogin: "Chuy\u1ec3n sang \u0111\u0103ng nh\u1eadp",
  switchRegister: "Chuy\u1ec3n sang \u0111\u0103ng k\u00fd",
  titleRegister: "T\u1ea1o t\u00e0i kho\u1ea3n",
};

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
      setError(err.response?.data?.detail || text.failed);
    }
  };

  return (
    <div className="auth-shell">
      <form className="auth-card" onSubmit={submit}>
        <p className="eyebrow">Chatbot RAG</p>
        <h1>{mode === "login" ? text.login : text.titleRegister}</h1>
        {mode === "register" && (
          <input
            placeholder={text.name}
            value={form.name}
            onChange={(event) => setForm({ ...form, name: event.target.value })}
          />
        )}
        <input
          placeholder={text.email}
          type="email"
          value={form.email}
          onChange={(event) => setForm({ ...form, email: event.target.value })}
        />
        <input
          placeholder={text.password}
          type="password"
          value={form.password}
          onChange={(event) => setForm({ ...form, password: event.target.value })}
        />
        {error && <div className="error-text">{error}</div>}
        <button type="submit">{mode === "login" ? text.login : text.register}</button>
        <button
          type="button"
          className="ghost"
          onClick={() => setMode(mode === "login" ? "register" : "login")}
        >
          {mode === "login" ? text.switchRegister : text.switchLogin}
        </button>
      </form>
    </div>
  );
}

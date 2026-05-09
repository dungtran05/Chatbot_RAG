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
  // mode quyet dinh form dang o man hinh dang nhap hay dang ky.
  const [mode, setMode] = useState("login");
  // Luu du lieu nguoi dung nhap tren form.
  const [form, setForm] = useState({ name: "", email: "", password: "" });
  // Luu thong bao loi neu API dang nhap/dang ky that bai.
  const [error, setError] = useState("");

  // Gui form dang nhap hoac dang ky, sau do luu token vao AuthContext.
  const submit = async (event) => {
    event.preventDefault();
    setError("");
    try {
      // Chon endpoint va payload tuy theo che do hien tai.
      const endpoint = mode === "login" ? "/auth/login" : "/auth/register";
      const payload =
        mode === "login"
          ? { email: form.email, password: form.password }
          : form;
      const { data } = await api.post(endpoint, payload);
      // API thanh cong thi luu token + user de vao man hinh chat.
      login(data);
    } catch (err) {
      // API that bai thi hien loi cho nguoi dung.
      setError(err.response?.data?.detail || text.failed);
    }
  };

  return (
    <div className="auth-shell">
      <form className="auth-card" onSubmit={submit}>
        <p className="eyebrow">Trợ lý pháp luật</p>
        <h1>{mode === "login" ? text.login : text.titleRegister}</h1>
        {/* Truong ho ten chi hien khi nguoi dung dang ky tai khoan moi. */}
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
        {/* Nut submit se doi chu theo dang nhap/dang ky. */}
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

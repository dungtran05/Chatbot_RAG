import { createContext, useContext, useState } from "react";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  // Khôi phục user từ localStorage để reload trang vẫn giữ đăng nhập.
  const [user, setUser] = useState(() => {
    const raw = localStorage.getItem("user");
    return raw ? JSON.parse(raw) : null;
  });

  // Lưu token và thông tin user sau khi đăng nhập/đăng ký thành công.
  const login = (payload) => {
    localStorage.setItem("token", payload.access_token);
    localStorage.setItem("user", JSON.stringify(payload.user));
    setUser(payload.user);
  };

  // Xóa dữ liệu đăng nhập khi người dùng đăng xuất.
  const logout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("user");
    setUser(null);
  };

  const value = { user, login, logout };
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  return useContext(AuthContext);
}

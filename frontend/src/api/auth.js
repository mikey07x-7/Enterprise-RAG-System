import api from "./axios";

// ==========================================================
// Login
// ==========================================================

export const loginUser = async (username, password) => {
  const response = await api.post("/auth/login", {
    username,
    password,
  });

  return response.data;
};

// ==========================================================
// Register
// ==========================================================

export const registerUser = async (
  username,
  email,
  password
) => {
  const response = await api.post("/auth/register", {
    username,
    email,
    password,
  });

  return response.data;
};
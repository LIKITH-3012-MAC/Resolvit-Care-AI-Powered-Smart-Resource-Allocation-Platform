import axios from "axios";
import { API_BASE } from "./constants";

const apiClient = axios.create({
  baseURL: API_BASE,
  headers: {
    "Content-Type": "application/json",
  },
});

// Add response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error("API Error:", error.response?.data || error.message);
    return Promise.reject(error);
  }
);

export default apiClient;

export const authApi = {
  login: (data: FormData) => apiClient.post("/auth/login", data, {
    headers: { "Content-Type": "application/x-www-form-urlencoded" }
  }),
  signup: (data: any) => apiClient.post("/auth/signup", data),
};

export const usersApi = {
  getMe: () => apiClient.get("/users/me"),
};

export const ngosApi = {
  getAll: () => apiClient.get("/ngos/"),
  create: (data: any) => apiClient.post("/ngos/", data),
};

export const reportsApi = {
  getAll: (params?: any) => apiClient.get("/reports/", { params }),
  getById: (id: string | number) => apiClient.get(`/reports/${id}/`),
  create: (data: any) => apiClient.post("/reports/", data),
};

export const volunteersApi = {
  getAll: (params?: any) => apiClient.get("/volunteers/", { params }),
};

export const tasksApi = {
  getAll: (params?: any) => apiClient.get("/tasks/", { params }),
};

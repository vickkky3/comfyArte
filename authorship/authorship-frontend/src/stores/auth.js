import { defineStore } from "pinia";
import axios from "axios";

const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";

export const useAuthStore = defineStore("auth", {
  state: () => ({
    token: null,
    user: null, 
  }),
  actions: {
    setToken(token) {
      this.token = token;
      localStorage.setItem("token", token);
    },
    async fetchUserProfile() {
      if (!this.token) {
        console.error("No hay token en el Store, no puedo pedir el perfil.");
        return;
      }

      try {
        const res = await axios.get(`${API_BASE}/api/users/me/`, {
          headers: { Authorization: `Token ${this.token}` }
        });
        this.user = res.data; 
      } catch (err) {
        console.error("Error en la petición a /me/:", err.response?.status, err.message);
      }
    },
    loadToken() {
      const savedToken = localStorage.getItem("token");
      if (savedToken) {
        this.token = savedToken;
      }
    },
    logout() {
      this.token = null;
      this.user = null;
      localStorage.removeItem("token");
    },
  },
});
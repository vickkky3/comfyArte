<template>
    <nav class="navbar">
        <div class="navbar-left">
            <img src="/logo.png" class="logo-img" alt="Logo comforART" />
            <span class="nav-title">
                <span class="text-comfor">Comfor</span><span class="text-art">ART</span>
            </span>
        </div>
    </nav>

    <transition name="popup-fade">
        <div v-if="notification.show" :class="['popup-notification', notification.type]">
            <div class="popup-icon">
                <i v-if="notification.type === 'error'" class="fa-solid fa-circle-exclamation"></i>
                <i v-else class="fa-solid fa-circle-check"></i>
            </div>
            <div class="popup-body">
                <span class="popup-title" v-if="notification.type === 'error'">Operación Denegada</span>
                <span class="popup-title" v-else>¡Acción Exitosa!</span>
                <p class="popup-message">{{ notification.message }}</p>
            </div>
            <button @click="notification.show = false" class="popup-close">
                <i class="fa-solid fa-xmark"></i>
            </button>
        </div>
    </transition>

    <div class="login-wrapper">
        <div class="login-card">
            <header class="login-header">
                <div class="icon-login">
                    <i class="fa-solid fa-address-card"></i>
                </div>

                <h1>Identificación</h1>
                <p>Accede a tu panel de protección de obras</p>

                <div class="divider-icon">
                    <span class="line"></span>
                    <div class="icon">
                        <i class="fa-solid fa-shield-halved"></i>
                    </div>
                    <span class="line"></span>
                </div>
            </header>

            <form @submit.prevent="handleLogin" class="login-form">
                <div class="form-group">
                    <label>Nombre de Usuario</label>
                    <div class="input-container">
                        <i class="fa-solid fa-circle-user"></i>
                        <input v-model="username" type="text" placeholder="Tu usuario..." required />
                    </div>
                </div>

                <div class="form-group">
                    <label>Contraseña</label>
                    <div class="input-container">
                        <i class="fa-solid fa-lock"></i>
                        <input v-model="password" type="password" placeholder="Tu contraseña..." required />
                    </div>
                </div>

                <button type="submit" class="btn-login" :disabled="loading">
                    <template v-if="!loading">
                        <i class="fa-solid fa-user-lock"></i> Iniciar Sesión
                    </template>
                    <template v-else>
                        <i class="fa-solid fa-spinner fa-spin"></i> Procesando...
                    </template>
                </button>
            </form>

            <div class="simple-divider"></div>

            <div class="login-footer">
                <p>¿No tienes cuenta?</p>
                <div class="back-link">
                    <i class="fa-solid fa-circle-arrow-left  "></i>
                    <router-link :to="{ path: '/' }">Regístrate como autor o consumidor</router-link>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref } from "vue";
import { useRouter } from "vue-router";
import axios from "axios";
import { useAuthStore } from "../stores/auth";

const router = useRouter();
const authStore = useAuthStore();

const username = ref("");
const password = ref("");
const error = ref("");
const loading = ref(false);

const notification = ref({
    show: false,
    message: "",
    type: "error"
});

const triggerNotification = (message, type = 'error') => {
    notification.value = { show: true, message, type };
};

const handleLogin = async () => {
    loading.value = true;
    error.value = "";

    try {
        const response = await axios.post("http://localhost:8000/api/users/login/", {
            username: username.value,
            password: password.value,
        });

        const token = response.data.token;

        authStore.setToken(token);
        localStorage.setItem("token", token);

        router.push("/dashboard");
    } catch (err) {
        if (err.response && err.response.data && err.response.data.detail) {
            triggerNotification(err.response.data.detail, "error");
        } else {
            triggerNotification("Credenciales incorrectas. Por favor, inténtalo de nuevo.", "error");
        }
    } finally {
        loading.value = false;
    }
};
</script>

<style scoped>
.icon-login {
    width: 60px;
    height: 60px;
    margin: 0 auto 20px;

    border: 1px solid var(--granate-principal);
    border-radius: 50%;

    display: flex;
    justify-content: center;
    align-items: center;

    background: var(--rosa-claro);
    color: #8B0029;
    font-size: 24px;
}

.login-wrapper {
    margin: 10px;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    padding: 20px;
}

.login-card {
    background: white;
    padding: 45px 35px;
    border-radius: 20px;
    box-shadow: 0 15px 35px rgba(0, 0, 0, 0.07);
    width: 100%;
    max-width: 420px;
    text-align: center;
}

h1 {
    color: var(--granate-principal);
    margin: 0 0 10px;
    font-size: 1.8rem;
    font-weight: 800;
}

.login-header p {
    color: #777;
    font-size: 0.95rem;
    margin-bottom: 35px;
}

.btn-login {
    width: 100%;
    background: var(--granate-principal);
    color: white;
    padding: 15px;
    border: none;
    border-radius: 10px;
    font-size: 1rem;
    font-weight: 700;
    cursor: pointer;
    transition: all 0.3s ease;
    margin-top: 10px;
}

.btn-login:hover:not(:disabled) {
    background: var(--rosa-fuerte);
    transform: translateY(-2px);
    box-shadow: 0 5px 15px rgba(128, 0, 32, 0.2);
}

.btn-login:disabled {
    background: #ccc;
    cursor: not-allowed;
}

.login-footer {
    padding-top: 5px;
}

.login-footer p {
    margin: 0;
    font-size: 0.9rem;
    color: #888;
}

.error-alert {
    background: #fff0f0;
    color: #c0392b;
    padding: 12px;
    border-radius: 8px;
    font-size: 0.85rem;
    margin-top: 20px;
    border: 1px solid #f8d7da;
}

.input-container {
    position: relative;
    width: 100%;
}

.input-container i {
    position: absolute;
    left: 12px;
    top: 50%;
    transform: translateY(-42%);
    color: #888888;
    font-size: 1.1em;
    transition: color 0.3s;
    pointer-events: none;
}

.input-container input[type="text"],
.input-container input[type="password"] {
    width: 100%;
    padding: 12px 12px 12px 40px;
    border: 1px solid #ddd;
    border-radius: 8px;
    box-sizing: border-box;
    transition: border-color 0.3s, background-color 0.3s;
}

.input-container input:focus {
    outline: none;
    border-color: var(--rosa-fuerte);
    background: var(--rosa-claro);
}

.input-container input:focus~i {
    color: var(--granate-principal);
}

.simple-divider {
    height: 1px;
    background: #e7c3cb;
    margin: 30px 0;
}
</style>

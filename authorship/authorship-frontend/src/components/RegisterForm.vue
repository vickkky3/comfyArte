<template>
  <nav class="navbar">
    <div class="navbar-left">
      <img src="/logo.png" class="logo-img" alt="Logo comforART" />
      <span class="nav-title">
        <span class="text-comfor">Comfy</span><span class="text-art">ARTE</span>
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

  <div class="page-split-container">
    <div class="welcome-section">
      <div class="icon">
        <i class="fa-solid fa-shield-halved"></i>
      </div>
      <div>
        <div v-if="currentRol == 'author'">
          <h1 class="title-welcome">Protege tu creatividad y muestra tu talento al mundo</h1>
          <div class="divider-icon">
            <span class="line"></span>
          </div>
          <p class="subtitle-welcome">Únete a una plataforma segura que te permite gestionar tus obras y difundirlas al
            resto de usuarios</p>
          <div class="features-list">

            <div class="feature-item">
              <div class="feature-icon">
                <i class="fa-solid fa-layer-group"></i>
              </div>
              <div class="feature-text">
                <h2>Gestión inteligente</h2>
                <p>Organiza tus obras y licencias fácilmente.</p>
              </div>
            </div>

            <div class="feature-item">
              <div class="feature-icon">
                <i class="fa-solid fa-chart-line"></i>
              </div>
              <div class="feature-text">
                <h2>Monetiza tu trabajo</h2>
                <p>Conecta con más personas y genera ingresos.</p>
              </div>
            </div>

            <div class="feature-item">
              <div class="feature-icon">
                <i class="fa-solid fa-award"></i>
              </div>
              <div class="feature-text">
                <h2>Certificado digital</h2>
                <p>Obtén pruebas de la autoría de tus obras.</p>
              </div>
            </div>
          </div>
        </div>

        <div v-if="currentRol == 'consumer'">
          <h1 class="title-welcome">Descubre talento único y accede a creaciones originales</h1>
          <div class="divider-icon">
            <span class="line"></span>
          </div>
          <p class="subtitle-welcome">Únete a la comunidad ideal para apoyar a creadores independientes y consumir
            contenido de forma segura.</p>
          <div class="features-list">

            <div class="feature-item">
              <div class="feature-icon">
                <i class="fa-solid fa-magnifying-glass"></i>
              </div>
              <div class="feature-text">
                <h2>Exploración exclusiva</h2>
                <p>Encuentra obras auténticas y filtradas por categorías profesionales.</p>
              </div>
            </div>

            <div class="feature-item">
              <div class="feature-icon">
                <i class="fa-solid fa-gem"></i>
              </div>
              <div class="feature-text">
                <h2>Suscripciones exclusivas</h2>
                <p>Accede a planes premium y disfruta del mejor contenido sin límites.</p>
              </div>
            </div>

            <div class="feature-item">
              <div class="feature-icon">
                <i class="fa-solid fa-heart"></i>
              </div>
              <div class="feature-text">
                <h2>Apoyo directo al creador</h2>
                <p>Fomenta el consumo responsable y valora el talento de tus artistas favoritos.</p>
              </div>
            </div>
          </div>
        </div>

      </div>
    </div>
    <div class="form-container">
      <div v-if="currentRol === 'author'" class="icon-circle author">
        <i class="fa-solid fa-pen-nib"></i>
      </div>
      <div v-else class="icon-circle consumer">
        <i class="fa-solid fa-book-open"></i>
      </div>
      <h1 class="register">{{ title }}</h1>
      <p class="subtitle">
        Crea tu cuenta de <strong class="role-highlight">{{ spanishRol }}</strong> para empezar.
      </p>

      <div class="divider-icon">
        <span class="line"></span>

        <div class="icon">
          <i class="fa-solid fa-shield-halved"></i>
        </div>

        <span class="line"></span>
      </div>

      <form @submit.prevent="handleRegister">
        <div class="form-row">
          <div class="form-group">
            <label for="first_name">Nombre</label>
            <div class="input-container">
              <i class="fa-solid fa-circle-user"></i>
              <input type="text" id="first_name" v-model="firstName" placeholder="Tu nombre">
            </div>
          </div>
          <div class="form-group">
            <label for="last_name">Apellidos</label>
            <div class="input-container">
              <i class="fa-solid fa-circle-user"></i>
              <input type="text" id="last_name" v-model="lastName" placeholder="Tus apellidos">
            </div>
          </div>
        </div>

        <div class="form-group">
          <label for="username">Nombre de usuario</label>
          <div class="input-container">
            <i class="fa-solid fa-circle-user"></i>
            <input type="text" id="username" v-model="username" placeholder="Tu nombre de usuario">
          </div>
        </div>

        <div class="form-group">
          <label for="email">Correo Electrónico</label>
          <div class="input-container">
            <i class="fa-solid fa-envelope"></i>
            <input type="email" id="email" v-model="email" placeholder="Tu correo electrónico">
          </div>
        </div>

        <div class="form-group">
          <label for="password">Contraseña</label>
          <div class="input-container">
            <i class="fa-solid fa-lock"></i>
            <input type="password" id="password" v-model="password" placeholder="Tu contraseña">
          </div>
        </div>

        <div v-if="currentRol === 'author'" class="form-group">
          <label for="biography">Biografía Profesional</label>
          <div class="input-container textarea-container">
            <i class="fa-regular fa-pen-to-square"></i>
            <textarea id="biography" v-model="biography" rows="3"
              placeholder="Cuéntanos sobre tu trayectoria artística..."></textarea>
          </div>
        </div>

        <div v-if="currentRol === 'consumer'" class="form-group">
          <label for="interests">Intereses / Preferencias</label>
          <div class="interests-grid">
            <div v-for="work in workTypes" :key="work.id" class="checkbox-item">
              <label class="checkbox-wrapper">
                <input type="checkbox" :value="work.id" v-model="interests" class="custom-check">
                <span class="check-label">{{ work.label }}</span>
              </label>
            </div>
          </div>
          <small class="info-help">Selecciona los tipos de contenido que deseas descubrir en tu catálogo.</small>
        </div>

        <button class="btn-register" type="submit" :disabled="loading">
          <template v-if="loading">
            <i class="fa-solid fa-spinner fa-spin"></i> Procesando...
          </template>

          <template v-else>
            Finalizar Registro
          </template>
        </button>

        <div class="back-link">
          <i class="fa-solid fa-circle-arrow-left  "></i>
          <router-link :to="{ path: '/' }">Volver a la pantalla de selección de tipo de usuario</router-link>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref } from "vue";
import { useRouter, useRoute } from "vue-router";
import axios from "axios";
import { useAuthStore } from "../stores/auth";

const router = useRouter();
const route = useRoute();
const authStore = useAuthStore();

const username = ref("");
const email = ref("");
const password = ref("");
const firstName = ref("");
const lastName = ref("");
const biography = ref("");
const interests = ref([]);
const currentRol = route.params.role;

const error = ref("");
const loading = ref(false);

const titles = {
  author: 'Registro de Autor',
  consumer: 'Registro de Consumidor'
};

const title = titles[currentRol]

const spanishRoles = {
  author: 'autor',
  consumer: 'consumidor'
};

const spanishRol = spanishRoles[currentRol]

const workTypes = [
  { id: 'book', label: 'Libros' },
  { id: 'music', label: 'Música' },
  { id: 'video', label: 'Vídeos' },
  { id: 'software', label: 'Software' },
  { id: 'paint', label: 'Pintura' },
  { id: 'sculpture', label: 'Escultura' }
];

const notification = ref({
  show: false,
  message: "",
  type: "error"
});

const triggerNotification = (message, type = 'error') => {
  notification.value = { show: true, message, type };
};

const handleRegister = async () => {
  loading.value = true;
  error.value = "";

  try {
    const payload = {
      first_name: firstName.value,
      last_name: lastName.value,
      username: username.value,
      email: email.value,
      password: password.value,
      role: currentRol,
    }

    if (currentRol === 'author') {
      payload.biography = biography.value;
    }
    else if (currentRol === 'consumer') {
      payload.interests = interests.value.join(',');
    }

    const response = await axios.post("http://localhost:8000/api/users/register/", payload);

    const token = response.data.token;
    if (token) {
      authStore.setToken(token);
      localStorage.setItem("token", token);
      router.push("/dashboard");
    } else {
      router.push("/login");
    }
  } catch (err) {
    if (err.response && err.response.data && err.response.data.detail) {
      triggerNotification(err.response.data.detail, "error");
    } else {
      triggerNotification("Error al crear la cuenta. Por favor, inténtalo de nuevo.", "error");
    }
  } finally {
    loading.value = false;
  }
};
</script>
<style scoped>
body {
  background-color: #fafafa;
  color: var(--texto-oscuro);
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  margin: 0;
}

.register {
  color: var(--granate-principal);
  font-size: 2.2em;
  font-weight: 800;
  line-height: 1.2;
  margin: 15px 0;
}

.title-welcome {
  color: var(--granate-principal);
  font-size: 1.2em;
  font-weight: 800;
  line-height: 1.2;
  margin: 15px 0;

  text-align: left;
}

.subtitle-welcome {
  text-align: left;
  color: #666;
  margin-bottom: 30px;
}

.form-container {
  width: 100%;
  background: white;
  padding: 50px;
  border-radius: 24px;
  box-shadow: 0 15px 35px rgba(0, 0, 0, 0.04);
  box-sizing: border-box;
}

h1 {
  color: var(--granate-principal);
  text-align: center;
  margin-bottom: 10px;
  font-size: 1.8em;
}

.subtitle {
  text-align: center;
  color: #666;
  margin-bottom: 30px;
}

.role-highlight {
  color: var(--granate-principal);
  font-weight: 700;
  text-transform: lowercase;
}

input:focus,
textarea:focus {
  outline: none;
  border-color: var(--rosa-fuerte);
  background-color: var(--rosa-claro);
  box-shadow: 0 0 5px rgba(219, 112, 147, 0.2);
}

.helptext {
  font-size: 0.8em;
  color: #888;
  display: block;
  margin-top: 5px;
}

.errorlist {
  color: #d9534f;
  font-size: 0.85em;
  list-style: none;
  padding: 0;
  margin: 5px 0;
}

.btn-register {
  width: 100%;
  background-color: var(--granate-principal);
  color: white;
  padding: 14px;
  border: none;
  border-radius: 8px;
  font-size: 1.1em;
  font-weight: bold;
  cursor: pointer;
  transition: background 0.3s, transform 0.2s;
  margin-top: 10px;
}

.btn-register:hover {
  background-color: var(--rosa-fuerte);
  transform: translateY(-2px);
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 15px;
}

textarea {
  width: 100%;
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 8px;
  resize: vertical;
}

.interests-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
  gap: 12px;
  background: #fdfdfd;
  padding: 20px;
  border-radius: 10px;
  border: 1px solid #eee;
  margin-bottom: 10px;
}

.checkbox-wrapper {
  display: flex;
  align-items: center;
  cursor: pointer;
  transition: 0.2s;
}

.checkbox-wrapper:hover .check-label {
  color: var(--granate-principal);
}

.custom-check {
  width: 18px;
  height: 18px;
  cursor: pointer;
  accent-color: var(--granate-principal);
  margin-right: 10px;
}

.check-label {
  font-size: 0.95rem;
  color: #555;
  font-weight: 500;
}

.info-help {
  color: #888;
  font-style: italic;
  display: block;
  margin-top: 5px;
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
.input-container input[type="email"],
.input-container input[type="password"],
.input-container textarea {
  width: 100%;
  padding: 12px 12px 12px 40px;
  border: 1px solid #ddd;
  border-radius: 8px;
  box-sizing: border-box;
  font-family: inherit;
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

.textarea-container i {
  top: 16px !important;
  transform: none !important;
}

.input-container textarea:focus {
  outline: none;
  border-color: var(--rosa-fuerte);
  background: var(--rosa-claro);
}

.input-container textarea:focus~i {
  color: var(--granate-principal);
}

.page-split-container {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: center;
  gap: 60px;
  max-width: 1350px;
  margin: 40px auto;
  padding: 0 40px;
  box-sizing: border-box;
}

.welcome-section {
  flex: 0 1 500px;
  text-align: left;

  color: var(--granate-principal);
  font-size: 1em;
  font-weight: bold;
  line-height: 1.3;
}

.features-list {
  display: flex;
  flex-direction: column;
  gap: 24px;
  margin-top: 30px;
  width: 100%;
}

.feature-item {
  display: flex;
  align-items: flex-start;
  gap: 16px;
}

.feature-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 42px;
  height: 42px;
  background-color: var(--rosa-claro);
  color: var(--granate-principal);
  border-radius: 12px;
  font-size: 1.1em;
  flex-shrink: 0;
}

.feature-text {
  display: flex;
  flex-direction: column;
  gap: 4px;
  text-align: left;
}

.feature-text h2 {
  margin: 0;
  color: var(--granate-principal);
  font-size: 1.15em;
  font-weight: bold;
}

.feature-text p {
  margin: 0;
  color: #666666;
  font-size: 0.95em;
  line-height: 1.4;
}
</style>
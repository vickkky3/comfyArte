<template>
  <div v-if="loading" class="loading">Cargando tus obras...</div>

  <div v-else>
    <nav class="navbar">
      <div class="navbar-left">
        <img src="/logo.png" class="logo-img" alt="Logo comforART" />
        <span class="nav-title">
          <span class="text-comfor">Comfor</span><span class="text-art">ART</span>
        </span>
        <span class="nav-separator">|</span>
        <span class="nav-user"><i class="fa-solid fa-circle-user"></i>{{ user.username }}</span>
      </div>
      <div class="navbar-right">
        <span class="points"><i class="fa-solid fa-wallet"></i>{{ userPoints }} Puntos</span>
        <button @click="handleLogout" class="btn-logout">Cerrar Sesión</button>
      </div>
    </nav>

    <div class="page-layout-grid">

      <div class="left-column-content">

        <div class="container-card" v-if="work">
          <div class="back-link2">
            <i class="fa-solid fa-circle-arrow-left"></i>
            <router-link :to="{ path: '/dashboard' }">Volver</router-link>
          </div>

          <div class="main-content-layout">
            <div class="icon-side" v-if="work && work.work_type">
              <div class="giant-icon-square">
                <i :class="workIcon"></i>
              </div>
            </div>

            <div class="info-side">
              <div class="paralel">
                <h1>{{ work.title }}</h1>
                <span class="circle-pink">{{ workType }}</span>
              </div>
              <div class="paralel-fields">
                <div class="info-block">
                  <span class="label"><i class="fa-solid fa-circle-user"></i>Autor/a</span>
                  <span class="value">{{ work.author_username || 'Desconocido' }}</span>
                </div>

                <div class="info-block">
                  <span class="label"><i class="fa-solid fa-calendar-days"></i>Fecha de registro</span>
                  <span class="value">{{ formatDate(work.created_at) }}</span>
                </div>

                <div class="info-block">
                  <span class="label"><i class="fa-solid fa-shield"></i>Estado</span>
                  <span class="value">Registrada</span>
                </div>
              </div>

              <div class="divider-icon2">
                <span class="line"></span>
              </div>

              <div class="info-block2">
                <span class="label">Descripción</span>
                <span class="value">{{ work.description || 'Sin descripción' }}</span>
              </div>

              <div class="divider-icon2">
                <span class="line"></span>
              </div>

              <div class="info-block2">
                <span class="label">Plan de suscripción requerido</span>
                <p>¿Qué plan deben tener los consumidores para acceder a esta obra?</p>

                <div v-if="work.plan_required" class="value-box">
                  <span class="plan-name">{{ work.plan_required.name }}</span>
                  <span class="circle-pink2 "> precio: {{ work.plan_required.points }} puntos</span>
                </div>

                <div v-else class="free-box">
                  <span class="circle-pink2"><i class="fa-solid fa-coins"></i>Esta obra es gratuita.</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="container-card" v-if="hasTechnicalData">
          <div class="technical-sheet">
            <h3 class="technical-title">Detalles adicionales</h3>

            <div class="divider-icon2">
              <span class="line"></span>
            </div>

            <template v-if="work.work_type === 'book'">
              <div class="technical-row">
                <div class="icon-circle"><i class="fa-solid fa-file-lines"></i></div>
                <span class="tech-label">Páginas</span>
                <span class="tech-value">{{ work.pages || '-' }}</span>
              </div>
              <div class="divider-icon2"><span class="line"></span></div>
              <div class="technical-row">
                <div class="icon-circle"><i class="fa-solid fa-barcode"></i></div>
                <span class="tech-label">ISBN</span>
                <span class="tech-value">{{ work.isbn || '-' }}</span>
              </div>
              <div class="divider-icon2"><span class="line"></span></div>
              <div class="technical-row">
                <div class="icon-circle"><i class="fa-solid fa-tags"></i></div>
                <span class="tech-label">Género</span>
                <span class="tech-value">{{ work.genre || '-' }}</span>
              </div>
              <div class="divider-icon2"><span class="line"></span></div>
              <div class="technical-row">
                <div class="icon-circle"><i class="fa-solid fa-language"></i></div>
                <span class="tech-label">Idioma</span>
                <span class="tech-value">{{ work.language || '-' }}</span>
              </div>
            </template>

            <template v-else-if="work.work_type === 'music'">
              <div class="technical-row">
                <div class="icon-circle"><i class="fa-solid fa-clock"></i></div>
                <span class="tech-label">Duración</span>
                <span class="tech-value">{{ work.duration }} minutos</span>
              </div>
              <div class="divider-icon2"><span class="line"></span></div>
              <div class="technical-row">
                <div class="icon-circle"><i class="fa-solid fa-tags"></i></div>
                <span class="tech-label">Género</span>
                <span class="tech-value">{{ work.genre }}</span>
              </div>
              <div class="divider-icon2"><span class="line"></span></div>
              <div class="technical-row">
                <div class="icon-circle"><i class="fa-solid fa-compact-disc"></i></div>
                <span class="tech-label">Álbum</span>
                <span class="tech-value">{{ work.album }}</span>
              </div>
            </template>

            <template v-else-if="work.work_type === 'video'">
              <div class="technical-row">
                <div class="icon-circle"><i class="fa-solid fa-clock"></i></div>
                <span class="tech-label">Duración</span>
                <span class="tech-value">{{ work.duration }} minutos</span>
              </div>
              <div class="divider-icon2"><span class="line"></span></div>
              <div class="technical-row">
                <div class="icon-circle"><i class="fa-solid fa-tags"></i></div>
                <span class="tech-label">Género</span>
                <span class="tech-value">{{ work.genre }}</span>
              </div>
            </template>

            <template v-else-if="work.work_type === 'software'">
              <div class="technical-row">
                <div class="icon-circle"><i class="fa-solid fa-code"></i></div>
                <span class="tech-label">Lenguaje</span>
                <span class="tech-value">{{ work.programming_language || '-' }}</span>
              </div>
              <div class="divider-icon2"><span class="line"></span></div>
              <div class="technical-row">
                <div class="icon-circle"><i class="fa-solid fa-folder-open"></i></div>
                <span class="tech-label">Repositorio de código</span>
                <span class="tech-value">
                  <a v-if="work.repository_url" :href="work.repository_url" target="_blank">{{ work.repository_url
                    }}</a>
                  <span v-else>-</span>
                </span>
              </div>
              <div class="divider-icon2"><span class="line"></span></div>
              <div class="technical-row">
                <div class="icon-circle"><i class="fa-solid fa-book"></i></div>
                <span class="tech-label">Repositorio de documentación</span>
                <span class="tech-value">
                  <a v-if="work.repository_url" :href="work.repository_url" target="_blank">{{ work.documentation_url
                    }}</a>
                  <span v-else>-</span>
                </span>
              </div>
            </template>

            <template v-else-if="work.work_type === 'paint' || work.work_type === 'sculpture'">
              <div class="technical-row">
                <div class="icon-circle"><i class="fa-solid fa-arrows-up-down"></i></div>
                <span class="tech-label">Altura</span>
                <span class="tech-value">{{ work.height }} cm</span>
              </div>
              <div class="divider-icon2"><span class="line"></span></div>
              <div class="technical-row">
                <div class="icon-circle"><i class="fa-solid fa-weight-hanging"></i></div>
                <span class="tech-label">Peso</span>
                <span class="tech-value">{{ work.weight }} kg</span>
              </div>
              <div class="divider-icon2"><span class="line"></span></div>
              <div class="technical-row">
                <div class="icon-circle"><i class="fa-solid fa-palette"></i></div>
                <span class="tech-label">Material / Técnica</span>
                <span class="tech-value">{{ work.type_detail || '-' }}</span>
              </div>
            </template>
          </div>
        </div>
      </div>

      <div class="right-column-sidebar">
        <div class="container-card sidebar-card-info" v-if="work">

          <div v-if="work.file_name" class="file-box-section">
            <span class="label-sidebar-title">
              <i class="fa-solid fa-box-archive"></i> Obra Completa
            </span>

            <div v-if="canSeeProtectedContent" class="unlocked-zone">
              <p class="sidebar-help-text">Tienes acceso total. Puedes descargar el archivo original firmado:</p>
              <a :href="`http://localhost:8000/api/works/${work.id}/serve/`" class="btn-action btn-download"
                target="_blank">
                <i class="fa-solid fa-circle-down"></i> Descargar Original
              </a>
              <span class="file-real-name-tag">{{ work.file_name }}</span>
            </div>

            <div v-else class="locked-zone">
              <p class="sidebar-help-text" style="color: #999;">Este archivo está protegido por derechos de autor.</p>
              <button @click="handleSubscribe" class="btn-action btn-subscribe-now">
                <i class="fa-solid fa-lock"></i> Suscribirse para acceder
              </button>

              <div v-if="work.resume_name && work.file_name" class="divider-icon2" style="margin: 20px 0;">
                <span class="line"></span>
              </div>

              <div v-if="work?.resume_name" class="file-box-section" style="margin-bottom: 25px;">
                <span class="label-sidebar-title">
                  <i class="fa-solid fa-eye"></i> Muestra Gratuita
                </span>
                <p class="sidebar-help-text">Revisa un fragmento libre antes de adquirir la obra completa:</p>

                <div class="media-preview-container">
                  <a :href="`http://localhost:8000/api/works/${work?.id}/serve-resume/`" target="_blank"
                    class="btn-sidebar-secondary">
                    <i class="fa-solid fa-arrow-up-right-from-square"></i> Abrir preview ({{ work?.resume_name }})
                  </a>

                </div>
              </div>
            </div>

          </div>

        </div>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from "vue";
import { useRoute, useRouter } from "vue-router";
import axios from "axios";
import { useAuthStore } from "../stores/auth";

const router = useRouter();
const route = useRoute();
const authStore = useAuthStore();
const loading = ref(true);
const works = ref([]);

const user = ref({
  id: null,
  username: "",
  email: "",
  role: "",
  biography: "",
  interests: "",
  first_name: "",
  last_name: "",
  es_autor: false,
  es_consumidor: false
});
const userPoints = ref(0);
const work = ref(null);
const subscriptionTypes = ref([]);
const activeSubscription = ref(null);

const workTypes = {
  book: 'LIBRO',
  music: 'MÚSICA',
  video: 'VIDEO',
  software: 'SOFTWARE',
  paint: 'PINTURA',
  sculpture: 'ESCULTURA'
};

const workType = computed(() => {
  if (!work.value || !work.value.work_type) return 'Obra';
  return workTypes[work.value.work_type] || 'Obra';
});

const workIcons = {
  book: 'fa-solid fa-book-open',
  music: 'fa-solid fa-music',
  video: 'fa-solid fa-video',
  software: 'fa-solid fa-code',
  paint: 'fa-solid fa-palette',
  sculpture: 'fa-solid fa-hammer'
};

const workIcon = computed(() => {
  if (!work.value || !work.value.work_type) return 'fa-solid fa-file-image';
  return workIcons[work.value.work_type] || 'fa-solid fa-file-image';
});

const hasTechnicalData = computed(() => {
  return work.value && work.value.work_type;
});

const getUserData = async () => {
  try {
    const response = await axios.get("http://localhost:8000/api/users/me/", {
      headers: { Authorization: `Token ${authStore.token || localStorage.getItem("token")}` },
    });

    user.value = response.data;
    user.value.es_autor = user.value.role === 'author';
    user.value.es_consumidor = user.value.role === 'consumer';

    if (user.value.es_consumidor) {
      const worksResponse = await axios.get("http://localhost:8000/api/works/", {
        headers: { Authorization: `Token ${authStore.token || localStorage.getItem("token")}` },
      });
      works.value = worksResponse.data;
    }
  } catch (err) {
    console.error("Error en la petición de usuario:", err);
    router.push("/login");
  }
};

const getUserPoints = async () => {
  try {
    const token = authStore.token || localStorage.getItem("token");
    const response = await axios.get("http://localhost:8000/api/subscriptions/points/", {
      headers: { Authorization: `Token ${token}` },
    });
    userPoints.value = response.data.points;
  } catch (err) {
    console.error("Error en los puntos:", err);
  }
};

const fetchWorkDetails = async () => {
  try {
    const id = route.params.id;
    const response = await axios.get(`http://localhost:8000/api/works/${id}/`, {
      headers: { Authorization: `Token ${authStore.token || localStorage.getItem('token')}` }
    });
    work.value = response.data;
  } catch (err) {
    console.error("Error al cargar la obra:", err);
    router.push("/works");
  }
};

const fetchMySubscription = async () => {
  try {
    const id = route.params.id;
    const response = await axios.get(`http://localhost:8000/api/subscriptions/me/`, {
      headers: { Authorization: `Token ${authStore.token || localStorage.getItem('token')}` }
    });
    activeSubscription.value = response.data;

  } catch (err) {
    if (err.response && err.response.status === 404) {
      activeSubscription.value = null;
    } else {
      console.error("Error al cargar tu suscripción:", err);
    }
  }
};

const fetchSubscriptionPlan = async () => {
  try {
    const response = await axios.get(`http://localhost:8000/api/subscriptions/plans/`, {
      headers: { Authorization: `Token ${authStore.token || localStorage.getItem('token')}` }
    });
    subscriptionTypes.value = response.data;

  } catch (err) {
    console.error("Error al cargar los planes de suscripción:", err);
  } finally {
    loading.value = false;
  }
};

const formatDate = (dateString) => {
  if (!dateString) return '';
  return new Date(dateString).toLocaleDateString('es-ES', {
    day: '2-digit', month: 'long', year: 'numeric'
  });
};

const isAuthor = computed(() => {
  if (!authStore.user || !work.value) return false;

  const userId = authStore.user.id || authStore.user.pk;
  const authorId = work.value.author;

  return Number(userId) === Number(authorId);
});

const canSeeProtectedContent = computed(() => {
  if (!work.value) return false;

  if (!authStore.user) return false;

  const isAdmin = authStore.user.role === 'admin';
  const isAuthor = Number(authStore.user.id) === Number(work.value.author);

  const isFreeWork = !work.value.plan_required;

  let isSubscribed = false;

  if (activeSubscription.value && work.value.plan_required) {
    const planUserId = activeSubscription.value.plan;
    const planRequiredId = work.value.plan_required.id;

    if (planUserId === planRequiredId) {
      isSubscribed = true;
    }
    else if (activeSubscription.value.plan_points >= work.value.plan_required.points) {
      isSubscribed = true;
    }
  }

  return isAdmin || isAuthor || isFreeWork || isSubscribed;
});

const handleSubscribe = () => {
  router.push("/subscription/plans");
};

const handleLogout = async () => {
  try {
    await axios.post("http://localhost:8000/api/users/", {}, {
      headers: { Authorization: `Token ${authStore.token || localStorage.getItem("token")}` },
    });
  } catch (err) {
    console.error("Error al cerrar sesión:", err);
  } finally {
    authStore.setToken(null);
    localStorage.removeItem("token");
    router.push("/login");
  }
};

onMounted(async () => {
  loading.value = true;

  authStore.loadToken();

  if (authStore.token) {
    try {
      await authStore.fetchUserProfile();
    } catch (profileErr) {
      console.error("Error al cargar perfil en el almacén global:", profileErr);
    }
  } else {
    console.warn("No hay token, el usuario debe iniciar sesión.");
    router.push("/login");
    return;
  }

  getUserData(),
    getUserPoints(),
    fetchWorkDetails(),
    fetchSubscriptionPlan(),
    fetchMySubscription()
});
</script>

<style scoped>
.page-layout-grid {
  display: flex;
  align-items: flex-start;
  justify-content: center;
  gap: 30px;
  max-width: 1400px;
  margin: 30px auto;
  padding: 0 25px;
  box-sizing: border-box;
}

.left-column-content {
  flex: 2;
  display: flex;
  flex-direction: column;
  gap: 25px;
}

.right-column-sidebar {
  flex: 1;
  min-width: 320px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.container-card {
  background: white;
  padding: 35px;
  border-radius: 15px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.06);
  width: 100%;
  box-sizing: border-box;
}

.main-content-layout {
  display: flex;
  align-items: flex-start;
  justify-content: flex-start;
  gap: 40px;
}

.icon-side {
  flex-shrink: 0;
  display: flex;
  align-items: flex-start;
}

.giant-icon-square {
  width: 160px;
  height: 230px;
  background-color: var(--rosa-claro, #FFF0F3);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.08);
  border: 1px solid rgba(219, 112, 147, 0.15);
}

.giant-icon-square i {
  font-size: 4rem;
  color: var(--granate-principal);
}

.info-side {
  flex: 1;
}

.circle-pink {
  background: var(--rosa-claro);
  color: var(--granate-principal);
  padding: 4px 10px;
  border-radius: 15px;
  font-size: 0.75em;
  font-weight: bold;
}

.paralel {
  display: flex;
  align-items: center;
  gap: 30px;
  margin-bottom: 25px;
}

.paralel h1 {
  margin: 0;
  font-size: 2em;
  color: #111;
}

.paralel-fields {
  display: flex;
  margin-top: 20px;
  padding-bottom: 0;
  margin-bottom: 0;
}

.info-block {
  display: flex;
  flex-direction: column;
  gap: 6px;
  flex: 1;
  padding: 0 20px;
}

.info-block .label {
  font-size: 0.8em;
  color: #888;
  font-weight: bold;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  display: flex;
  align-items: center;
}

.info-block .label i {
  color: var(--rosa-fuerte);
  margin-right: 6px;
  font-size: 1.1em;
}

.info-block .value {
  font-size: 1.05em;
  color: #333;
  font-weight: 500;
}

.info-block2 {
  display: flex;
  flex-direction: column;
  gap: 6px;
  padding-bottom: 0;
  margin-bottom: 0;
}

.info-block2 .label {
  font-size: 0.8em;
  color: var(--granate-principal);
  font-weight: bold;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.info-block2 p {
  margin: 0 0 4px 0;
  font-size: 0.95em;
  color: #666;
}

.info-block2 .value {
  font-size: 1.05em;
  color: #333;
  font-weight: 400;
  line-height: 1.5;
}

.info-block:not(:last-child) {
  border-right: 1px solid var(--rosa-fuerte);
}

.value-box {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-top: 4px;
}

.free-box {
  margin-top: 4px;
}

.plan-name {
  font-weight: 700;
  color: #333;
  font-size: 1.05em;
}

.circle-pink2 {
  display: inline-block;
  background: var(--rosa-claro);
  color: #111;
  padding: 4px 12px;
  border-radius: 15px;
  font-size: 1.05em;
  font-weight: bold;
  white-space: nowrap;
  margin: 0;
}

.divider-icon2 {
  display: flex;
  align-items: center;
  width: 100%;
  margin: 20px 0;
}

.divider-icon2 .line {
  flex: 1;
  height: 1.5px;
  background-color: var(--rosa-fuerte);
}

.back-link2 {
  display: block;
  text-align: left;
  margin-bottom: 20px;
  font-size: 1.1em;
  color: var(--granate-principal);
}

.back-link2 i {
  margin-right: 8px;
}

.back-link2 a {
  color: inherit;
  text-decoration: none;
  font-weight: bold;
}

.technical-sheet {
  text-align: left;
  width: 100%;
}

.technical-title {
  color: var(--granate-principal);
  font-size: 1.05em;
  font-weight: 700;
  margin-top: 0;
  margin-bottom: 10px;
}

.technical-row {
  display: grid;
  grid-template-columns: 38px 130px 1fr;
  align-items: center;
  padding: 5px 0;
  border-bottom: 1px solid #f5f5f5;
}

.technical-row:last-child {
  border-bottom: none;
}

.icon-circle {
  width: 24px;
  height: 24px;
  background-color: var(--rosa-claro);
  border-radius: 50%;

  display: inline-flex;
  align-items: center;
  justify-content: center;

  margin: 0 auto 0 0;
}

.icon-circle i {
  color: var(--granate-principal);
  font-size: 0.75rem;
  line-height: 1;
  display: inline-block;
}

.tech-label {
  color: #555555;
  font-size: 0.85rem;
  font-weight: 600;
  height: auto;
  line-height: normal;
}

.tech-value {
  color: #222222;
  font-size: 0.85rem;
  font-weight: 400;
  height: auto;
  line-height: normal;
}

.tech-value a {
  color: var(--rosa-fuerte);
  text-decoration: none;
  font-weight: 500;
}

.tech-value a:hover {
  text-decoration: underline;
}

.btn-action {
  display: block;
  width: 100%;
  padding: 12px;
  border: none;
  border-radius: 8px;
  text-align: center;
  font-weight: bold;
  cursor: pointer;
  transition: 0.3s;
  text-decoration: none;
  margin-top: 15px;
}

.btn-download {
  background: var(--rosa-fuerte);
  color: #333;
}

.btn-download:hover {
  background: var(--granate-principal);
  color: white;
}

.label-sidebar-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.95rem;
  font-weight: 700;
  color: var(--granate-principal);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.sidebar-help-text {
  font-size: 0.82rem !important;
  color: #666;
  margin: 6px 0 12px 0 !important;
  line-height: 1.4;
}

.media-preview-container {
  width: 100%;
  margin-top: 5px;
}

.sidebar-player {
  width: 100%;
  height: 32px;
  outline: none;
}

.btn-sidebar-secondary {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  width: 100%;
  padding: 10px;
  background-color: #f7fafc;
  border: 1px solid #e2e8f0;
  color: #4a5568;
  text-decoration: none;
  border-radius: 6px;
  font-size: 0.82rem;
  font-weight: bold;
  transition: background 0.2s;
  box-sizing: border-box;
}

.btn-sidebar-secondary:hover {
  background-color: #edf2f7;
}

.file-real-name-tag {
  display: block;
  text-align: center;
  font-size: 0.75rem;
  color: #888;
  margin-top: 6px;
  word-break: break-all;
}

.btn-subscribe-now {
  background: #edf2f7 !important;
  color: var(--granate-principal) !important;
  border: 1px solid rgba(139, 0, 41, 0.2) !important;
}

.btn-subscribe-now:hover {
  background: var(--rosa-claro) !important;
}
</style>
<template>
  <div v-if="loading" class="loading-screen">
    <div class="spinner-wrapper">
      <div class="brand-spinner"></div>
      <div class="spinner-inner-dot"></div>
    </div>
    <p class="loading-label">Cargando detalles de la obra...</p>
  </div>

  <div v-else>
    <nav class="navbar">
      <div class="navbar-left">
        <img src="/logo.png" class="logo-img" alt="Logo comforART" />
        <span class="nav-title">
          <span class="text-comfor">Comfy</span><span class="text-art">ARTE</span>
        </span>
        <span class="nav-separator">|</span>
        <span class="nav-user"><i class="fa-solid fa-circle-user"></i>{{ user.username }}</span>
      </div>
      <div class="navbar-right">
        <span class="points"><i class="fa-solid fa-wallet"></i>{{ userPoints }} Puntos</span>

        <div class="notifications-wrapper">
          <button @click="toggleNotifications" class="btn-icon-bell" title="Notificaciones">
            <i class="fa-solid fa-bell"></i>
          </button>

          <div v-if="isNotificationsOpen" class="notifications-dropdown">

            <div class="notif-header">
              <h3>Notificaciones</h3>
            </div>

            <div class="notif-body">
              <div v-if="notifications.length > 0">
                <div v-for="notif in notifications" :key="notif.id" class="notif-item">
                  <div class="notif-icon-circle">
                    <i class="fa-solid fa-book-open"></i>
                  </div>

                  <div class="notif-content">
                    <div class="notif-title-row">
                      <span class="notif-title">Nueva obra disponible</span>
                      <span v-if="!notif.is_read" class="unread-dot"></span>
                    </div>
                    <p class="notif-text">
                      El autor <strong>{{ notif.author_username }}</strong> ha subido una nueva obra: <em>"{{
                        notif.work_title }}"</em>.
                    </p>
                    <span class="notif-time">{{ formatDate(notif.created_at) }}</span>
                  </div>
                </div>
              </div>

              <div v-else class="notif-empty">
                <p>No tienes notificaciones por ahora.</p>
              </div>
            </div>

          </div>
        </div>

        <button @click="handleLogout" class="btn-logout">Cerrar Sesión</button>
      </div>
    </nav>

    <transition name="popup-fade">
      <div v-if="information.show" :class="['popup-notification', information.type]">
        <div class="popup-icon">
          <i v-if="information.type === 'error'" class="fa-solid fa-circle-exclamation"></i>
          <i v-else class="fa-solid fa-circle-check"></i>
        </div>
        <div class="popup-body">
          <span class="popup-title" v-if="information.type === 'error'">Operación Denegada</span>
          <span class="popup-title" v-else>¡Acción Exitosa!</span>
          <p class="popup-message">{{ information.message }}</p>
        </div>
        <button @click="information.show = false" class="popup-close">
          <i class="fa-solid fa-xmark"></i>
        </button>
      </div>
    </transition>

    <div class="container">

      <div>

        <div class="content-header">
          <i class="fas fa-book"></i>
          <div class="header-text">
            <h1>Mis obras favoritas</h1>
          </div>
        </div>

        <div class="filters-container">
          <div class="filter-field" style="flex: 1;">
            <label class="filter-label">Buscar obra por nombre:</label>
            <input v-model="workSearchQuery" type="text" placeholder="Escribe el nombre o usuario del autor..."
              class="filter-input" />
          </div>
        </div>

        <div v-if="filteredWorks.length > 0" class="works-cards-grid">
          <div v-for="workItem in filteredWorks" :key="workItem.id" class="work-custom-card">

            <div class="work-card-left">
              <div class="work-icon-box">
                <i :class="getWorkIcon(workItem.work_type)"></i>
              </div>
              <div class="work-text-info">
                <h3 class="work-card-title">{{ workItem.title }}</h3>
                <p class="work-card-author">Autor @{{ workItem.author_username || 'Autor' }}</p>
              </div>
            </div>

            <div class="work-card-right">
              <span class="pill-type-tag">{{ getWorkTypeName(workItem.work_type) }}</span>

              <div class="work-card-buttons">
                <button v-if="user.es_consumidor" type="button" @click="saveWork(workItem.work_id || workItem.id)"
                  class="btn-bookmark-action"
                  :title="isSaved(workItem.work_id || workItem.id) ? 'Quitar de favoritos' : 'Guardar en favoritos'">
                  <i
                    :class="isSaved(workItem.work_id || workItem.id) ? 'fa-solid fa-bookmark' : 'fa-regular fa-bookmark'"></i>
                </button>

                <router-link :to="`/works/${workItem.work_id || workItem.id}`" class="btn-card-details">
                  Ver detalles &rarr;
                </router-link>
              </div>
            </div>

          </div>
        </div>

        <div v-else class="empty-msg">
          <p>No se han encontrado obras que coincidan con la búsqueda.</p>
        </div>
      </div>

      <router-link to="/dashboard" class="btn-back-link" style="margin-top: 30px;">
        &larr; Volver al Panel Principal
      </router-link>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from "vue";
import { useRouter, useRoute } from "vue-router";
import axios from "axios";
import { useAuthStore } from "../stores/auth";

const authStore = useAuthStore();
const router = useRouter();

const loading = ref(true);
const user = ref({ interests: "" });

const userPoints = ref(0);

const savedWorks = ref([]);
const workSearchQuery = ref("");
const savedWorkIds = ref(new Set());

const information = ref({
    show: false,
    message: "",
    type: "error"
});

const triggerInformation = (message, type = 'error') => {
    information.value = { show: true, message, type };
};

const workTypeNames = {
  libro: 'Libro', book: 'Libro',
  music: 'Música', video: 'Video',
  software: 'Software', paint: 'Pintura',
  sculpture: 'Escultura'
};

const workIconMap = {
  book: 'fa-solid fa-book-open',
  libro: 'fa-solid fa-book-open',
  music: 'fa-solid fa-music',
  video: 'fa-solid fa-video',
  software: 'fa-solid fa-code',
  paint: 'fa-solid fa-palette',
  sculpture: 'fa-solid fa-hammer'
};

const getWorkTypeName = (type) => workTypeNames[type] || 'Obra';
const getWorkIcon = (type) => workIconMap[type] || 'fa-solid fa-file-image';

const getUserData = async () => {
  try {
    const response = await axios.get("http://localhost:8000/api/users/me/", {
      headers: {
        Authorization: `Token ${authStore.token || localStorage.getItem("token")}`,
      },
    });

    user.value = response.data;
    user.value.es_autor = user.value.role === 'author';
    user.value.es_consumidor = user.value.role === 'consumer';

  } catch (err) {
    console.error("Error en la petición:", err);
    triggerInformation("Sesión inválida o expirada", "error");
    router.push("/login");
  }
};

const getSavedWorks = async () => {
  try {
    const token = authStore.token || localStorage.getItem("token");

    const response = await axios.get("http://localhost:8000/api/subscriptions/works/subscribe/", {
      headers: {
        Authorization: `Token ${token}`,
      },
    });

    savedWorks.value = response.data;
    savedWorkIds.value = new Set(response.data.map(item => item.work_id || item.id));
    console.log("Obras guardadas cargadas");

  } catch (err) {
    console.error("Error en la petición:", err);
  }
};

const filteredWorks = computed(() => {
  if (!workSearchQuery.value) return savedWorks.value;
  const query = workSearchQuery.value.toLowerCase();

  return savedWorks.value.filter(w =>
    w.title?.toLowerCase().includes(query)
  );
});

const formatDate = (dateString) => {
  if (!dateString) return "";

  const date = new Date(dateString);

  return date.toLocaleDateString("es-ES");
};

const getUserPoints = async () => {
  try {
    const token = authStore.token || localStorage.getItem("token");

    const response = await axios.get("http://localhost:8000/api/subscriptions/points/", {
      headers: {
        Authorization: `Token ${token}`,
      },
    });

    userPoints.value = response.data.points;
    console.log("Puntos del usuario cargados:", userPoints.value);

  } catch (err) {
    console.error("Error en la petición:", err);
  }
};

const isNotificationsOpen = ref(false);

const notifications = ref([
]);

const unreadCount = computed(() => {
  return notifications.value.filter(n => !n.is_read).length;
});

const toggleNotifications = () => {
  isNotificationsOpen.value = !isNotificationsOpen.value;

  if (isNotificationsOpen.value) {
    fetchNotifications();
  }
};

const fetchNotifications = async () => {
  try {
    const token = authStore.token || localStorage.getItem("token");
    const response = await axios.get("http://localhost:8000/api/users/notifications/", {
      headers: { Authorization: `Token ${token}` }
    });

    notifications.value = response.data;
  } catch (error) {
    console.error("Error al cargar notificaciones:", error);
  }
};

const isSaved = (workId) => {
  return savedWorkIds.value.has(workId);
};

const saveWork = async (workId) => {
  const token = authStore.token || localStorage.getItem("token");
  const config = {
    headers: { Authorization: `Token ${token}` },
    data: { work_id: workId }
  };

  try {
    if (isSaved(workId)) {

      await axios.delete(`http://localhost:8000/api/subscriptions/works/subscribe/`, config);
      savedWorkIds.value.delete(workId);

      savedWorks.value = savedWorks.value.filter(item => (item.work_id || item.id) !== workId);

      triggerInformation("¡Obra eliminada de tus favoritos!", "success");
    } else {

      await axios.post(`http://localhost:8000/api/subscriptions/works/subscribe/`, { work_id: workId }, {
        headers: { Authorization: `Token ${token}` }
      });

      savedWorkIds.value.add(workId);

      triggerInformation("¡Obra guardada en favoritos!", "success");
    }

  } catch (error) {
    triggerInformation("No se pudo eliminar la obra de favoritos. Por favor, inténtalo de nuevo.", "error");
    console.error("Error al actualizar guardados:", error);
  }
};

const handleLogout = () => {
  authStore.logout();
  router.push("/login");
};

onMounted(async () => {
  loading.value = true;

  await Promise.all([
    getUserData(),
    getUserPoints(),
    getSavedWorks()
  ]);

  loading.value = false;
});
</script>

<style scoped>
.loading {
  text-align: center;
  margin-top: 100px;
  color: var(--granate-principal);
  font-weight: bold;
}

.navbar {
  background: var(--granate-principal);
  color: white;
  padding: 15px 30px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-radius: 0 0 15px 15px;
  margin-bottom: 30px;
}

.container {
  background: white;
  padding: 40px;
  border-radius: 15px;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
  max-width: 900px;
  margin: auto;
}

.content-header {
  display: flex;
  align-items: center;
  gap: 20px;
  margin-bottom: 25px;
}

.content-header i {
  width: 70px;
  height: 70px;
  flex-shrink: 0;
  background: var(--rosa-claro);
  color: var(--granate-principal);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.8em;
  font-weight: bold;
  margin: 0;
  border: 2px solid var(--rosa-claro);
}

.header-text h1 {
  margin: 0 0 5px 0;
  color: #000;
}

.filters-container {
  display: flex;
  gap: 15px;
  margin-bottom: 25px;
  background-color: #fffafc;
  padding: 15px 20px;
  border-radius: 10px;
  border: 1px solid var(--rosa-claro);
  align-items: flex-start;
}

.filter-field {
  display: flex;
  flex-direction: column;
  gap: 6px;
  flex: 1;
}

.filter-label {
  font-size: 0.8em;
  font-weight: bold;
  color: var(--granate-principal);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.filter-input {
  width: 100%;
  height: 40px;
  padding: 0 12px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 0.9em;
  font-family: inherit;
  box-sizing: border-box;
  outline: none;
}

.works-cards-grid {
  display: flex;
  flex-direction: column;
  gap: 15px;
  max-height: 520px;
  overflow-y: auto;
  padding-right: 8px;
  scrollbar-width: thin;
  scrollbar-color: var(--granate-principal) var(--rosa-claro);
}

.works-cards-grid::-webkit-scrollbar {
  width: 6px;
}

.works-cards-grid::-webkit-scrollbar-track {
  background: var(--rosa-claro);
  border-radius: 4px;
}

.works-cards-grid::-webkit-scrollbar-thumb {
  background: var(--granate-principal);
  border-radius: 4px;
}

.work-custom-card {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background-color: #fffafc;
  border: 1px solid var(--rosa-claro);
  border-radius: 12px;
  padding: 16px 20px;
  gap: 32px;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.02);
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.work-custom-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 14px rgba(0, 0, 0, 0.06);
}

.work-card-left {
  display: flex;
  align-items: center;
  gap: 16px;
  flex: 1;
  min-width: 0;
  padding-right: 15px;
}

.work-icon-box {
  width: 52px;
  height: 52px;
  min-width: 52px;
  border-radius: 12px;
  background-color: #fde8ef;
  color: var(--granate-principal);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.4em;
}

.work-text-info {
  display: flex;
  flex-direction: column;
  gap: 3px;
  min-width: 0;
  flex: 1;
}

.work-card-title {
  margin: 0;
  font-size: 1.05em;
  font-weight: 700;
  color: #222;
  white-space: nowrap;        
  overflow: hidden;          
  text-overflow: ellipsis;   
}

.work-card-author {
  margin: 0;
  font-size: 0.82em;
  color: #777;
}

.work-card-right {
  display: flex;
  align-items: center;
  gap: 16px;
  flex-shrink: 0; 
}

.pill-type-tag {
  background-color: #fde8ef;
  color: var(--rosa-fuerte);
  font-size: 0.72em;
  font-weight: 800;
  padding: 4px 10px;
  border-radius: 20px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.work-card-buttons {
  display: flex;
  align-items: center;
  gap: 12px;
}

.btn-bookmark-action {
  background: transparent;
  border: none;
  cursor: pointer;
  padding: 6px;
  font-size: 1.3em;
  color: var(--granate-principal);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  transition: transform 0.2s ease;
}

.btn-bookmark-action:hover {
  transform: scale(1.15);
}

.btn-card-details {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  white-space: nowrap;
  background: var(--rosa-claro);
  color: #111;
  padding: 8px 16px;
  border-radius: 8px;
  font-weight: 700;
  font-size: 0.85em;
  text-decoration: none;
  transition: all 0.2s ease;
  flex-shrink: 0;
}

.btn-card-details:hover {
  background: var(--rosa-fuerte);
  color: white;
}

.empty-msg {
  text-align: center;
  padding: 40px;
  color: #666;
  font-style: italic;
}

.btn-back-link {
  display: block;
  width: 100%;
  background-color: var(--granate-principal);
  color: white;
  padding: 14px;
  border: none;
  border-radius: 8px;
  font-weight: bold;
  text-align: center;
  text-decoration: none;
  transition: 0.3s;
  font-size: 1.1em;
}

.btn-back-link:hover {
  background-color: var(--rosa-fuerte);
  transform: translateY(-2px);
}
</style>
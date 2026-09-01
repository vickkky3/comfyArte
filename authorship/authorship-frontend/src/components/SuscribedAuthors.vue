<template>
  <div v-if="loading" class="loading">Cargando tus obras...</div>

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
            <h1>Mis autores</h1>
          </div>
        </div>

        <div class="filters-container">
          <div class="filter-field" style="flex: 1;">
            <label class="filter-label">Buscar autor por nombre:</label>
            <input v-model="authorSearchQuery" type="text" placeholder="Escribe el nombre o usuario del autor..."
              class="filter-input" />
          </div>
        </div>

        <div v-if="filteredAuthors.length > 0" class="authors-grid">
          <div v-for="authorItem in filteredAuthors" :key="authorItem.id" class="author-card">
            <div class="author-main-info">
              <div class="avatar-circle">
                {{ authorItem.name?.charAt(0) || authorItem.username?.charAt(0) }}
              </div>

              <div class="author-details-content">
                <div class="author-header-titles">
                  <h3>{{ authorItem.username }}</h3>
                  <span class="author-badge">Autor Registrado</span>
                </div>

                <p class="author-bio">
                  {{ authorItem.biography || 'Este autor aún no ha añadido una descripción a su perfil.' }}
                </p>
              </div>
            </div>

            <div class="author-card-actions">
              <button @click="openAuthorModal(authorItem)" class="btn-table" style="width: 100%;">
                Ver Perfil
              </button>
            </div>

          </div>
        </div>

        <div v-else class="empty-msg">
          <p>No se han encontrado autores que coincidan con la búsqueda.</p>
        </div>

        <Teleport to="body">
          <div v-if="selectedAuthor" class="modal-overlay" @click.self="closeAuthorModal">
            <div class="modal-card">

              <button class="modal-close-btn" @click="closeAuthorModal">&times;</button>

              <div class="modal-header">
                <div class="avatar-ring">
                  <div class="avatar-circle-large">
                    {{ selectedAuthor.first_name?.charAt(0) || selectedAuthor.username?.charAt(0) }}
                  </div>
                </div>
                <h2>
                  <template v-if="selectedAuthor.first_name">
                    {{ selectedAuthor.first_name }} {{ selectedAuthor.last_name || '' }}
                  </template>
                  <template v-else>
                    {{ selectedAuthor.username }}
                  </template>
                </h2>
                <span class="author-handle">@{{ selectedAuthor.username }}</span>
              </div>

              <div class="modal-body">

                <div class="info-section">
                  <div class="section-icon">
                    <i class="fa-regular fa-user"></i>
                  </div>
                  <div class="section-content">
                    <div class="section-header-row">
                      <span class="section-title">BIOGRAFÍA / PERFIL</span>
                    </div>
                    <p class="section-text">
                      {{ selectedAuthor.biography || 'Este autor aún no ha añadido una biografía pública.' }}
                    </p>
                  </div>
                </div>

                <div class="info-section">
                  <div class="section-icon">
                    <i class="fa-regular fa-newspaper"></i>
                  </div>
                  <div class="section-content">
                    <div class="section-header-row">
                      <span class="section-title">OBRAS</span>
                    </div>

                    <div v-if="authorWorks.length > 0" class="table-container">
                      <table class="modal-works-table">
                        <thead>
                          <tr>
                            <th>TIPO</th>
                            <th>TÍTULO DE LA OBRA</th>
                            <th style="text-align: right;">FECHA</th>
                          </tr>
                        </thead>
                        <tbody>
                          <tr v-for="work in authorWorks" :key="work.id">
                            <td>
                              <span class="pill-type">{{ getWorkTypeName(work.work_type) }}</span>
                            </td>
                            <td class="work-title-cell">{{ work.title }}</td>
                            <td class="work-date-cell">{{ formatDate(work.created_at) }}</td>
                          </tr>
                        </tbody>
                      </table>
                    </div>
                    <p v-else class="empty-works-text">
                      Este autor aún no tiene obras publicadas.
                    </p>

                  </div>
                </div>

              </div>

              <div class="modal-footer">
                <button @click="cancelSuscriptionToAuthor(selectedAuthor.id)" class="btn-subscribe">
                  <i class="fa-solid fa-bell"></i> Anular suscripción a este Autor
                </button>
              </div>

            </div>
          </div>
        </Teleport>
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

const authorWorks = ref([]);
const loading = ref(true);
const user = ref({ interests: "" });

const userPoints = ref(0);

const subscribedAuthors = ref([]);
const authorSearchQuery = ref("");

const information = ref({
    show: false,
    message: "",
    type: "error"
});

const triggerInformation = (message, type = 'error') => {
    information.value = { show: true, message, type };
};

const getUserData = async () => {
  try {
    const token = authStore.token || localStorage.getItem("token");
    const response = await axios.get("http://localhost:8000/api/users/me/", {
      headers: {
        Authorization: `Token ${token}`,
      },
    });

    user.value = response.data;
    user.value.es_autor = user.value.role === 'author';
    user.value.es_consumidor = user.value.role === 'consumer';

  } catch (err) {
    console.error("Error al obtener datos del usuario:", err);
    triggerInformation("Sesión inválida o expirada", "error");
    router.push("/login");

  } finally {
    loading.value = false;
  }
};

const getSuscribedAuthors = async () => {
  try {
    const token = authStore.token || localStorage.getItem("token");

    const response = await axios.get("http://localhost:8000/api/subscriptions/authors/subscribe/", {
      headers: {
        Authorization: `Token ${token}`,
      },
    });

    subscribedAuthors.value = response.data;
    console.log("Suscripciones del usuario cargadas");
  } catch (err) {
    console.error("Error en la petición:", err);
  }
};

const filteredAuthors = computed(() => {
  if (!authorSearchQuery.value) return subscribedAuthors.value;
  const query = authorSearchQuery.value.toLowerCase();
  return subscribedAuthors.value.filter(a =>
    a.username?.toLowerCase().includes(query) ||
    a.first_name?.toLowerCase().includes(query)
  );
});

const selectedAuthor = ref(null);

const getWorkTypeName = (type) => {
  const types = {
    book: 'Libro',
    music: 'Música',
    video: 'Video',
    software: 'Software',
    paint: 'Pintura',
    sculpture: 'Escultura'
  };
  return types[type] || 'Obra';
};

const formatDate = (dateString) => {
  if (!dateString) return "";
  const date = new Date(dateString);
  return date.toLocaleDateString("es-ES");
};

const openAuthorModal = async (author) => {
  selectedAuthor.value = author;
  authorWorks.value = [];

  try {
    const token = authStore.token || localStorage.getItem("token");
    const response = await axios.get(`http://localhost:8000/api/works/authors/${author.id}/`, {
      headers: { Authorization: `Token ${token}` }
    });
    authorWorks.value = response.data;

  } catch (error) {
    console.error("Error al obtener las obras del autor:", error);

  }
};

const closeAuthorModal = () => {
  selectedAuthor.value = null;
  authorWorks.value = [];
};

const cancelSuscriptionToAuthor = async (authorId) => {
  try {
    const token = authStore.token || localStorage.getItem("token");

    await axios.delete(
      "http://localhost:8000/api/subscriptions/authors/subscribe/",
      {
        headers: {
          Authorization: `Token ${token}`
        },
        data: {
          author_id: authorId
        }
      }
    );

    triggerInformation("¡Has cancelado tu suscripción a este autor!", "success");
    closeAuthorModal();

    subscribedAuthors.value = subscribedAuthors.value.filter(
      author => author.id !== authorId
    );
  } catch (error) {
    console.error("Error al cancelar suscripción:", error);

    if (error.response && error.response.data && error.response.data.detail) {
      triggerInformation(error.response.data.detail, "error");
      
    } else {
      triggerInformation("No se pudo cancelar la suscripción. Por favor, inténtalo de nuevo.", "error");
    }
  }
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

const handleLogout = () => {
  authStore.logout();
  router.push("/login");
};

onMounted(async () => {
  loading.value = true;

  await Promise.all([
    getUserData(),
    getUserPoints(),
    getSuscribedAuthors()
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


.filter-input {
  flex: 2;
  padding: 10px 15px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 0.95em;
  font-family: inherit;
  outline: none;
  transition: 0.2s;
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

.filters-container-btn {
  display: flex;
  gap: 15px;
  margin-bottom: 25px;
  background-color: #fffafc;
  padding: 15px 20px;
  border-radius: 10px;
  border: 1px solid var(--rosa-claro);
  align-items: flex-end;
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

.authors-grid {
  max-height: 500px;
  overflow-y: auto;
  padding-right: 5px;
  scrollbar-width: thin;
  scrollbar-color: var(--granate-principal) var(--rosa-claro);
}

.authors-grid::-webkit-scrollbar {
  width: 8px;
}

.authors-grid::-webkit-scrollbar-track {
  background: var(--rosa-claro);
  border-radius: 4px;
}

.authors-grid::-webkit-scrollbar-thumb {
  background: var(--granate-principal);
  border-radius: 4px;
}

.avatar-circle {
  width: 70px;
  height: 70px;
  background: var(--rosa-claro);
  color: var(--granate-principal);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.8em;
  font-weight: bold;
  margin: 0 auto 15px;
  border: 2px solid var(--granate-principal);
}

.author-card {
  border: 1px solid var(--rosa-claro);
  border-radius: 12px;
  padding: 20px;
  background-color: #fffafc;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.03);
  transition: transform 0.2s, box-shadow 0.2s;
}

.author-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 6px 15px rgba(0, 0, 0, 0.08);
}

.author-main-info {
  display: flex;
  align-items: flex-start;
  gap: 15px;
  margin-bottom: 15px;
}

.avatar-circle {
  width: 48px;
  height: 48px;
  min-width: 48px;
  border-radius: 50%;
  background-color: var(--granate-principal);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  font-size: 1.2em;
  text-transform: uppercase;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
}

.author-details-content {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.author-header-titles h3 {
  margin: 0 0 2px 0;
  font-size: 1.1em;
  color: #333;
  line-height: 1.2;
}

.author-badge {
  display: inline-block;
  font-size: 0.72em;
  color: var(--rosa-fuerte);
  font-weight: bold;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 8px;
}

.author-bio {
  font-size: 0.85em;
  color: #666;
  line-height: 1.4;
  margin: 0;
}

.author-card-actions {
  margin-top: 15px;
}

.btn-table {
  display: inline-block;
  background: var(--rosa-claro);
  color: black;
  padding: 8px 15px;
  border-radius: 8px;
  text-align: center;
  font-weight: bold;
  text-decoration: none;
  font-size: 0.85em;
  transition: 0.3s;
  border: 1px solid transparent;
}

.btn-table:hover {
  background: var(--rosa-fuerte);
  color: white;
}

.empty-msg {
  text-align: center;
  padding: 40px;
  color: #666;
  font-style: italic;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  width: 100vw;
  height: 100vh;
  background-color: rgba(0, 0, 0, 0.4);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 99999;
  backdrop-filter: blur(4px);
}

.modal-card {
  background: white;
  border-radius: 20px;
  padding: 30px 25px 25px 25px;
  width: 90%;
  max-width: 560px;
  position: relative;
  box-shadow: 0 15px 35px rgba(0, 0, 0, 0.15);
  display: flex;
  flex-direction: column;
  gap: 20px;
  box-sizing: border-box;
}

.modal-body {
  display: flex;
  flex-direction: column;
  gap: 18px;
  margin-top: 5px;
  width: 100%;
}

.modal-close-btn {
  position: absolute;
  top: 15px;
  right: 20px;
  background: transparent;
  border: none;
  font-size: 1.5em;
  color: #888;
  cursor: pointer;
  transition: color 0.2s;
}

.modal-close-btn:hover {
  color: var(--granate-principal);
}

.modal-header {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
}

.avatar-ring {
  background: #fff0f3;
  padding: 6px;
  border-radius: 50%;
  margin-bottom: 10px;
}

.avatar-circle-large {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  background-color: var(--granate-principal);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  font-size: 1.5em;
  text-transform: uppercase;
}

.modal-header h2 {
  margin: 0;
  font-size: 1.5em;
  color: #222;
  font-weight: 700;
}

.author-handle {
  font-size: 0.85em;
  color: var(--rosa-fuerte);
  font-weight: 700;
  text-transform: uppercase;
  margin-top: 3px;
}

.info-section {
  display: flex;
  gap: 12px;
  align-items: flex-start;
  width: 100%;
  box-sizing: border-box;
}

.section-icon {
  width: 36px;
  height: 36px;
  min-width: 36px;
  border-radius: 50%;
  background-color: #fde8ef;
  color: var(--granate-principal);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1em;
  flex-shrink: 0;
}

.section-content {
  flex: 1 1 auto;
  display: flex;
  flex-direction: column;
  width: 100%;
  min-width: 0;
}

.section-title {
  font-size: 0.9f2em;
  font-weight: 800;
  color: var(--granate-principal);
  letter-spacing: 0.5px;
  margin: 0;
  line-height: 1;
}

.section-header-row {
  display: flex;
  align-items: center;
  height: 36px;
}

.section-text {
  font-size: 0.9em;
  color: #555;
  margin: 0;
}

.table-container {
  max-height: 400px;
  overflow-y: auto;
  padding-right: 5px;
  scrollbar-width: thin;
  scrollbar-color: var(--granate-principal) var(--rosa-claro);
}

.table-container::-webkit-scrollbar {
  width: 6px;
}

.table-container::-webkit-scrollbar-track {
  background: var(--rosa-claro);
  border-radius: 4px;
}

.table-container::-webkit-scrollbar-thumb {
  background: var(--granate-principal);
  border-radius: 4px;
}

.modal-works-table {
  width: 100%;
  border-collapse: separate;
  border-spacing: 0;
  table-layout: auto;
}

.modal-works-table th,
.modal-works-table td {
  box-sizing: border-box;
}

.modal-works-table thead tr {
  background-color: #fcf0f3;
}

.modal-works-table th:first-child {
  border-top-left-radius: 12px;
  border-bottom-left-radius: 12px;
}

.modal-works-table th:last-child {
  border-top-right-radius: 12px;
  border-bottom-right-radius: 12px;
}

.modal-works-table tr:last-child td {
  border-bottom: none;
}

.pill-type {
  display: inline-block;
  background-color: #fde8ef;
  color: var(--rosa-fuerte);
  font-size: 0.7em;
  font-weight: 800;
  padding: 4px 12px;
  border-radius: 15px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.work-title-cell {
  font-weight: 700;
  color: #222;
}

.work-date-cell {
  text-align: right;
  color: #666;
  font-size: 0.85em;
}

.empty-works-text {
  font-size: 0.85em;
  color: #888;
  font-style: italic;
  margin-top: 8px;
}

.btn-subscribe {
  width: 100%;
  background: var(--granate-principal);
  color: white;
  border: none;
  padding: 14px;
  border-radius: 12px;
  font-weight: 700;
  font-size: 0.95em;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  box-shadow: 0 4px 12px rgba(128, 0, 32, 0.2);
}

.btn-subscribe:hover {
  background: #a00028;
  transform: translateY(-1px);
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
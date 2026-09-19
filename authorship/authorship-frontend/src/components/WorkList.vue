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
                    <i v-if="notif.notification_type === 'new_follower'" class="fa-solid fa-user-plus"></i>
                    <i v-else class="fa-solid fa-book-open"></i>
                  </div>

                  <div class="notif-content">
                    <div class="notif-title-row">
                      <span class="notif-title" v-if="notif.notification_type === 'new_follower'">
                        ¡Nuevo suscriptor!
                      </span>
                      <span class="notif-title" v-else-if="notif.notification_type === 'new_work'">
                        Nueva obra disponible
                      </span>
                      <span class="notif-title" v-else-if="notif.notification_type === 'new_saved_work'">
                        Obra guardada
                      </span>
                      <span v-if="!notif.is_read" class="unread-dot"></span>
                    </div>

                    <p class="notif-text">
                      <template v-if="notif.notification_type === 'new_follower'">
                        El usuario <strong>{{ notif.sender_username }}</strong> ha comenzado a seguirte.
                      </template>
                      <template v-else-if="notif.notification_type === 'new_work'">
                        El autor <strong>{{ notif.author_username || notif.sender_username }}</strong> ha subido una
                        nueva obra: <em>"{{ notif.work_title }}"</em>.
                      </template>
                      <template v-else-if="notif.notification_type === 'new_saved_work'">
                        El usuario <strong>{{ notif.sender_username }}</strong> ha añadido tu
                        obra: <em>"{{ notif.work_title }}"</em> a sus favoritos.
                      </template>
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
      <div class="main-mode-bar">
        <div class="toggle-pill-container">
          <button type="button" class="pill-btn" :class="{ active: searchMode === 'works' }"
            @click="searchMode = 'works'">
            <i class="fa-solid fa-book-open"></i> Obras
          </button>
          <button type="button" class="pill-btn" :class="{ active: searchMode === 'authors' }"
            @click="searchMode = 'authors'">
            <i class="fa-solid fa-users"></i> Autores
          </button>
        </div>
      </div>

      <div v-if="searchMode === 'works'">

        <div class="view-header-bar">
          <router-link to="/dashboard" class="btn-back-top">
            <i class="fa-solid fa-arrow-left"></i>
            <span>Volver</span>
          </router-link>
          <h1>Catálogo de Obras Disponibles</h1>
        </div>

        <div class="filters-container">

          <div class="filter-field">
            <label class="filter-label">Filtrar por título:</label>
            <input v-model="searchQuery" type="text" placeholder="Escribe un título..." class="filter-input" />
          </div>

          <div class="filter-field dropdown-relative">
            <label class="filter-label">Filtrar por tipo:</label>
            <button type="button" @click="isTypeOpen = !isTypeOpen" class="filter-dropdown-btn">
              <span v-if="selectedTypes.length > 0">
                {{ selectedTypes.length }} seleccionados
              </span>
              <span v-else>Todos los tipos</span>
            </button>

            <div v-if="isTypeOpen" class="floating-dropdown-panel">
              <label class="checkbox-label"><input type="checkbox" value="libro" v-model="selectedTypes" />
                Libros</label>
              <label class="checkbox-label"><input type="checkbox" value="music" v-model="selectedTypes" />
                Música</label>
              <label class="checkbox-label"><input type="checkbox" value="video" v-model="selectedTypes" />
                Vídeos</label>
              <label class="checkbox-label"><input type="checkbox" value="software" v-model="selectedTypes" />
                Software</label>
              <label class="checkbox-label"><input type="checkbox" value="paint" v-model="selectedTypes" />
                Pintura</label>
              <label class="checkbox-label"><input type="checkbox" value="sculpture" v-model="selectedTypes" />
                Escultura</label>
            </div>
          </div>

          <div class="filter-field dropdown-relative">
            <label class="filter-label">Filtrar por plan:</label>
            <button type="button" @click="isPlanOpen = !isPlanOpen" class="filter-dropdown-btn">
              <span v-if="selectedPlans.length > 0">
                {{ selectedPlans.length }} seleccionados
              </span>
              <span v-else>
                Todos los planes
              </span>
            </button>

            <div v-if="isPlanOpen" class="floating-dropdown-panel">
              <label class="checkbox-label">
                <input type="checkbox" value="gratis" v-model="selectedPlans" /> Sin plan / Gratuito
              </label>
              <label v-for="plan in subscriptionTypes" :key="plan.id" class="checkbox-label">
                <input type="checkbox" :value="String(plan.id)" v-model="selectedPlans" />
                {{ plan.name }}
              </label>
            </div>
          </div>

          <div class="filter-field">
            <span class="filter-label" style="visibility: hidden;">Buscar</span>
            <button @click="handleSearchClick" class="btn-search-submit">Buscar</button>
            <button v-if="hasActiveFilters" @click="clearFilters" class="btn-clear-filters"
              title="Limpiar todos los filtros">
              <i class="fa-solid fa-rotate-left"></i> Limpiar
            </button>
          </div>
        </div>

        <div v-if="sortedWorks.length > 0" class="table-works">
          <table class="catalog-table">
            <thead>
              <tr>
                <th class="col-type">Tipo</th>
                <th class="col-title">Título de la Obra</th>
                <th v-if="isConsumer" class="col-meta">Recomendación</th>
                <th v-else class="col-meta">Fecha</th>
                <th class="col-actions">Detalles</th>
                <th v-if="isAuthor" class="col-delete">Eliminar Obra</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="work in sortedWorks" :key="work.id">
                <td class="col-type">
                  <div class="type-cell-wrapper">
                    <i :class="getWorkIcon(work.work_type)" class="work-icon"></i>
                    <span class="label-tipo">{{ getWorkTypeName(work.work_type) }}</span>
                  </div>
                </td>
                <td class="col-title">
                  <span class="work-title">{{ work.title }}</span>
                </td>

                <td v-if="isAuthor" class="col-meta">
                  <span style="color: #555;">{{ formatDate(work.created_at) }}</span>
                </td>
                <td v-else class="col-meta">
                  <span v-if="isInteresting(work.work_type)" class="badge-interes">⭐ Sugerido</span>
                  <span v-else class="badge-neutral">-</span>
                </td>

                <td class="col-actions">
                  <div class="actions-cell">
                    <router-link v-if="isAuthor" :to="`/worksAuthor/${work.id}`" class="btn-table">
                      <span>Ver Detalles</span>
                    </router-link>
                    <router-link v-else :to="`/works/${work.id}`" class="btn-table">
                      <span>Consultar</span>
                    </router-link>
                    <button v-if="isSaved(work.id)" type="button" @click="saveWork(work.id)" class="btn-icon btn-saved"
                      title="Quitar de guardados">
                      <i class="fa-solid fa-bookmark"></i>
                    </button>
                    <button v-else type="button" @click="saveWork(work.id)" class="btn-icon" title="Guardar obra">
                      <i class="fa-regular fa-bookmark"></i>
                    </button>
                  </div>
                </td>

                <td v-if="isAuthor" class="col-delete">
                  <button @click="deleteWork(work.id)" class="btn-delete">Eliminar</button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <div v-else class="empty-msg">
          <p v-if="isAuthor">Aún no has registrado ninguna obra en la plataforma.</p>
          <p v-else>No hay obras disponibles que coincidan con tus criterios.</p>
          <router-link v-if="isAuthor" to="/dashboard" class="btn-table" style="margin-top: 15px;">
            Ir al panel para registrar una obra
          </router-link>
        </div>
      </div>

      <div v-else-if="searchMode === 'authors'">
        <div class="view-header-bar">
          <router-link to="/dashboard" class="btn-back-top">
            <i class="fa-solid fa-arrow-left"></i>
            <span>Volver</span>
          </router-link>

          <h1>Directorio de Autores</h1>
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
                            <th class="col-type">TIPO</th>
                            <th class="col-title">TÍTULO DE LA OBRA</th>
                            <th class="col-date">FECHA</th>
                            <th class="col-action">DETALLES</th>
                          </tr>
                        </thead>
                        <tbody>
                          <tr v-for="w in authorWorks" :key="w.id">
                            <td class="col-type">
                              <span class="pill-type">{{ getWorkTypeName(w.work_type) }}</span>
                            </td>
                            <td class="col-title">
                              <span class="work-title-cell">{{ w.title }}</span>
                            </td>
                            <td class="col-date work-date-cell">
                              {{ simpleFormatDate(w.created_at) }}
                            </td>
                            <td class="col-action">
                              <router-link :to="`/works/${w.id}`" class="btn-table-consult" @click="closeAuthorModal">
                                Consultar
                              </router-link>
                            </td>
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
                <button v-if="isConsumer" type="button" @click="subscribeToAuthor(selectedAuthor.id)"
                  class="btn-subscribe"
                  :title="isSuscribed(selectedAuthor.id) ? 'Quitar de guardados' : 'Guardar obra'">
                  <div v-if="isSuscribed(selectedAuthor.id)">
                    <i class="fa-solid fa-bell"></i> Desuscribirse a este Autor
                  </div>
                  <div v-else>
                    <i class="fa-solid fa-bell"></i> Suscribirse a este Autor
                  </div>
                </button>
              </div>

            </div>
          </div>
        </Teleport>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from "vue";
import { useRouter, useRoute } from "vue-router";
import axios from "axios";
import { useAuthStore } from "../stores/auth";

const authStore = useAuthStore();
const route = useRoute();
const router = useRouter();

const works = ref([]);
const authorWorks = ref([]);
const loading = ref(true);
const user = ref({ interests: "" });

const isAuthor = computed(() => user.value.role === 'author');
const isConsumer = computed(() => user.value.role === 'consumer');

const isTypeOpen = ref(false);
const isPlanOpen = ref(false);

const subscriptionTypes = ref([]);
const selectedPlans = ref([]);
const loadingPlans = ref(true);

const searchQuery = ref("");
const selectedTypes = ref([]);

const appliedSearch = ref("");
const appliedTypes = ref([]);
const appliedPlans = ref([]);
const userPoints = ref(0);

const searchMode = ref("works");

const authorsList = ref([]);
const authorSearchQuery = ref("");

const handleSearchClick = () => {
  appliedTypes.value = [...selectedTypes.value];
  appliedPlans.value = [...selectedPlans.value];

  isTypeOpen.value = false;
  isPlanOpen.value = false;
};

const hasActiveFilters = computed(() => {
  return (
    searchQuery.value.trim().length > 0 ||
    selectedTypes.value.length > 0 ||
    selectedPlans.value.length > 0 ||
    appliedTypes.value.length > 0 ||
    appliedPlans.value.length > 0
  );
});

const clearFilters = () => {
  searchQuery.value = "";
  selectedTypes.value = [];
  selectedPlans.value = [];
  appliedTypes.value = [];
  appliedPlans.value = [];
  isTypeOpen.value = false;
  isPlanOpen.value = false;
};

const normalizarTipo = (type) => {
  switch (type) {
    case 'book':
      return 'libro';
    case 'music':
      return 'music';
    case 'video':
      return 'video';
    case 'software':
      return 'software';
    case 'paint':
      return 'paint';
    case 'sculpture':
      return 'sculpture';
    default:
      return type;
  }
};

const information = ref({
  show: false,
  message: "",
  type: "error"
});

const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";

const triggerInformation = (message, type = 'error') => {
  information.value = { show: true, message, type };
};

const userInterestsArray = computed(() => {
  if (user.value.interests) {
    return user.value.interests.split(',');
  } else {
    return [];
  }
});

const isInteresting = (type) => {
  let typeNormalizado = type;
  if (type === 'book') {
    typeNormalizado = 'libro';
  }

  if (userInterestsArray.value.includes(typeNormalizado)) {
    return true;
  } else {
    return false;
  }
};

const sortedWorks = computed(() => {
  const obrasFiltradas = works.value.filter(work => {
    const query = searchQuery.value.trim().toLowerCase();
    const cumpleNombre = !query || work.title?.toLowerCase().includes(query);

    const tipoLimpio = normalizarTipo(work.work_type);
    const cumpleTipo = appliedTypes.value.length === 0 || appliedTypes.value.includes(tipoLimpio);

    let planIdDeObra = "gratis";
    if (work.plan_required) {
      planIdDeObra = String(work.plan_required.id);
    }

    const cumplePlan = appliedPlans.value.length === 0 || appliedPlans.value.includes(planIdDeObra);

    return cumpleNombre && cumpleTipo && cumplePlan;
  });

  return obrasFiltradas.sort((a, b) => {
    const tipoA = normalizarTipo(a.work_type);
    const tipoB = normalizarTipo(b.work_type);

    const aInteresting = userInterestsArray.value.includes(tipoA);
    const bInteresting = userInterestsArray.value.includes(tipoB);

    if (aInteresting && !bInteresting) return -1;
    if (!aInteresting && bInteresting) return 1;
    return a.title.localeCompare(b.title);
  });
});


const fetchPlans = async () => {
  try {
    const token = localStorage.getItem("token");
    const response = await axios.get(`${API_BASE}/api/subscriptions/plans/`, {
      headers: { Authorization: `Token ${token}` }
    });

    subscriptionTypes.value = response.data;
  } catch (error) {
    console.error("Error al cargar planes:", error);
  } finally {
    loadingPlans.value = false;
  }
};

const fetchAuthors = async () => {
  try {
    const token = authStore.token || localStorage.getItem("token");
    const response = await axios.get(`${API_BASE}/api/users/authors/`, {
      headers: { Authorization: `Token ${token}` }
    });
    authorsList.value = response.data;
  } catch (error) {
    console.error("Error al obtener autores:", error);
  }
};

const filteredAuthors = computed(() => {
  if (!authorSearchQuery.value) return authorsList.value;
  const query = authorSearchQuery.value.toLowerCase();

  return authorsList.value.filter(a =>
    a.username?.toLowerCase().includes(query) ||
    a.first_name?.toLowerCase().includes(query)
  );
});

const selectedAuthor = ref(null);

const openAuthorModal = async (author) => {
  selectedAuthor.value = author;
  authorWorks.value = [];

  try {
    const token = authStore.token || localStorage.getItem("token");
    const response = await axios.get(`${API_BASE}/api/works/authors/${author.id}/`, {
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

const fetchSubscribedAuthors = async () => {
  try {
    const token = authStore.token || localStorage.getItem("token");
    const response = await axios.get(`${API_BASE}/api/subscriptions/authors/subscribe/`, {
      headers: { Authorization: `Token ${token}` }
    });

    suscribedAuthorsIds.value = new Set(
      response.data.map(item => item.author_id || item.author?.id || item.id)
    );
  } catch (error) {
    console.error("Error al cargar suscripciones:", error);
  }
};

const suscribedAuthorsIds = ref(new Set());
const isSuscribed = (authorId) => {
  return suscribedAuthorsIds.value.has(authorId);
};

const subscribeToAuthor = async (authorId) => {

  const token = authStore.token || localStorage.getItem("token");

  const config = {
    headers: { Authorization: `Token ${token}` },
    data: { author_id: authorId }
  };

  try {
    if (isSuscribed(authorId)) {

      await axios.delete(`${API_BASE}/api/subscriptions/authors/subscribe/`, config);
      suscribedAuthorsIds.value.delete(authorId);

      triggerInformation("¡Has eliminado con éxito tu suscripción a este autor!", "success");

    } else {

      await axios.post(`${API_BASE}/api/subscriptions/authors/subscribe/`, { author_id: authorId }, {
        headers: { Authorization: `Token ${token}` }
      });
      suscribedAuthorsIds.value.add(authorId);

      triggerInformation("¡Te has suscrito con éxito a este autor!", "success");
    }

    closeAuthorModal();

  } catch (error) {
    console.error("Error al suscribirse:", error);
    triggerInformation("¡Se ha producido con la suscripción a este autor!", "error");
  }
};

const savedWorkIds = ref(new Set());
const isSaved = (workId) => {
  return savedWorkIds.value.has(workId);
};

const fetchSavedWorks = async () => {
  try {
    const token = authStore.token || localStorage.getItem("token");
    const response = await axios.get(`${API_BASE}/api/subscriptions/works/subscribe/`, {
      headers: { Authorization: `Token ${token}` }
    });

    savedWorkIds.value = new Set(response.data.map(item => item.work_id || item.id));

  } catch (error) {
    console.error("Error al cargar obras guardadas:", error);
  }
};


const saveWork = async (workId) => {
  const token = authStore.token || localStorage.getItem("token");
  const config = {
    headers: { Authorization: `Token ${token}` },
    data: { work_id: workId }
  };

  try {
    if (isSaved(workId)) {

      await axios.delete(`${API_BASE}/api/subscriptions/works/subscribe/`, config);
      savedWorkIds.value.delete(workId);

      triggerInformation("¡Has eliminado de guardados con éxito esta obra!", "success");

    } else {

      await axios.post(`${API_BASE}/api/subscriptions/works/subscribe/`, { work_id: workId }, {
        headers: { Authorization: `Token ${token}` }
      });
      savedWorkIds.value.add(workId);

      triggerInformation("¡Te has guardado con éxito esta obra!", "success");
    }

  } catch (error) {
    triggerInformation("¡Se ha producido un error al intentar modificar las obras guardadas!", "error");
    console.error("Error al actualizar guardados:", error);
  }
};

const fetchWorks = async () => {
  try {
    const token = authStore.token || localStorage.getItem("token");
    const userResponse = await axios.get(`${API_BASE}/api/users/me/`, {
      headers: { Authorization: `Token ${token}` }
    });
    user.value = userResponse.data;

    const response = await axios.get(`${API_BASE}/api/works/`, {
      headers: {
        Authorization: `Token ${authStore.token || localStorage.getItem("token")}`
      }
    });
    works.value = response.data;

  } catch (error) {
    console.error("Error al obtener las obras:", error);

    if (error.response?.status === 401) {
      router.push("/login");
    }

  } finally {
    loading.value = false;
  }
};

const simpleFormatDate = (dateString) => {
  if (!dateString) return "";
  const date = new Date(dateString);
  return date.toLocaleDateString("es-ES");
};

const formatDate = (dateString) => {
  if (!dateString) return "";
  const date = new Date(dateString);
  return date.toLocaleDateString("es-ES");
};

const workTypeNames = {
  book: 'Libro',
  music: 'Música', video: 'Video',
  software: 'Software', paint: 'Pintura',
  sculpture: 'Escultura'
};

const workIconMap = {
  book: 'fa-solid fa-book-open',
  music: 'fa-solid fa-music',
  video: 'fa-solid fa-video',
  software: 'fa-solid fa-code',
  paint: 'fa-solid fa-palette',
  sculpture: 'fa-solid fa-hammer'
};

const getWorkTypeName = (type) => workTypeNames[type] || 'Obra';
const getWorkIcon = (type) => workIconMap[type] || 'fa-solid fa-file-image';

const getUserPoints = async () => {
  try {
    const token = authStore.token || localStorage.getItem("token");

    const response = await axios.get(`${API_BASE}/api/subscriptions/points/`, {
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


const deleteWork = async (id) => {
  if (!confirm("¿Estás seguro de que deseas eliminar esta obra de forma permanente?")) {
    return;
  }

  try {
    const token = authStore.token || localStorage.getItem("token");
    const response = await axios.delete(`${API_BASE}/api/works/${id}/`, {
      headers: { Authorization: `Token ${token}` }
    });

    works.value = works.value.filter(work => work.id !== id);

    triggerInformation("Obra eliminada correctamente.", "success");

  } catch (err) {
    triggerInformation("¡Se ha producido un error al intentar eliminar la obra!", "error");
    console.error("Error al eliminar la obra:", err);

  } finally {
    loading.value = false;
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
    const response = await axios.get(`${API_BASE}/api/users/notifications/`, {
      headers: { Authorization: `Token ${token}` }
    });
    notifications.value = response.data;
  } catch (error) {
    console.error("Error al cargar notificaciones:", error);
  }
};

const handleLogout = () => {
  authStore.logout();
  localStorage.removeItem("token");
  router.push("/login");
};

onMounted(() => {
  fetchPlans();
  fetchWorks();
  getUserPoints();
  fetchAuthors();
  fetchSavedWorks();
  fetchSubscribedAuthors();
});
</script>

<style scoped>
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

.container h1 {
  color: var(--granate-principal);
  text-align: center;
  margin-bottom: 30px;
}

.table-works {
  width: 100%;
  overflow-x: auto;
}

.catalog-table {
  width: 100%;
  border-collapse: collapse;
  table-layout: fixed;
  margin-top: 20px;
}

.catalog-table thead tr {
  border-bottom: 2px solid var(--granate-principal);
}

.catalog-table th,
.catalog-table td {
  padding: 14px 10px;
  vertical-align: middle;
  box-sizing: border-box;
}

.catalog-table th {
  color: var(--granate-principal);
  font-size: 0.85rem;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.catalog-table tbody tr {
  border-bottom: 1px solid var(--rosa-claro);
  transition: background-color 0.2s;
}

.catalog-table tbody tr:hover {
  background-color: #fffafc;
}

.col-type {
  width: 20%;
  text-align: left;
  padding-left: 8px;
}

.col-title {
  width: 40%;
  text-align: left;
}

.col-meta {
  width: 20%;
  text-align: left;
}

.col-actions {
  width: 20%;
  text-align: center;
}

th.col-actions {
  text-align: center;
}

.col-delete {
  width: 12%;
  text-align: center;
}

th.col-delete {
  text-align: center;
}

.type-cell-wrapper {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  white-space: nowrap;
}

.work-icon {
  color: var(--rosa-fuerte);
  font-size: 1rem;
  width: 18px;
  text-align: center;
  flex-shrink: 0;
}

.label-tipo {
  color: var(--rosa-fuerte);
  font-weight: 800;
  font-size: 0.82rem;
  letter-spacing: 0.5px;
  text-transform: uppercase;
}

.work-title {
  color: #222;
  font-weight: 700;
  font-size: 0.95rem;
  display: block;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.actions-cell {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
}

.btn-table {
  display: inline-block;
  background: var(--rosa-claro);
  color: black;
  padding: 6px 14px;
  border-radius: 6px;
  text-align: center;
  font-weight: 700;
  text-decoration: none;
  font-size: 0.82rem;
  transition: 0.2s;
  border: 1px solid transparent;
}

.btn-table:hover {
  background: var(--rosa-fuerte);
  color: white;
}

.btn-icon {
  background: transparent;
  border: none;
  cursor: pointer;
  padding: 4px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: 1.15rem;
  color: var(--granate-principal);
  transition: transform 0.2s ease;
}

.btn-icon:hover {
  transform: scale(1.15);
}

.btn-delete {
  display: inline-block;
  background: var(--granate-principal);
  color: white;
  padding: 6px 14px;
  border-radius: 6px;
  text-align: center;
  font-weight: 700;
  text-decoration: none;
  font-size: 0.82rem;
  transition: 0.2s;
  border: none;
  cursor: pointer;
}

.btn-delete:hover {
  background: var(--rosa-fuerte);
}

.badge-interes {
  background: var(--rosa-claro);
  color: var(--granate-principal);
  padding: 4px 10px;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 700;
}

.badge-neutral {
  color: #aaa;
  font-size: 0.85rem;
}

.empty-msg {
  text-align: center;
  padding: 40px;
  color: #666;
  font-style: italic;
}

.filters-container {
  display: flex;
  gap: 15px;
  margin-bottom: 25px;
  background-color: var(--rosa-claro);
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

.dropdown-relative {
  position: relative;
}

.filter-label {
  font-size: 0.78rem;
  font-weight: 800;
  color: var(--granate-principal);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.filter-input {
  width: 100%;
  height: 38px;
  padding: 0 12px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 0.88rem;
  font-family: inherit;
  box-sizing: border-box;
  outline: none;
  background: white;
}

.filter-dropdown-btn {
  width: 100%;
  height: 38px;
  padding: 0 12px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 0.88rem;
  font-family: inherit;
  background-color: white;
  text-align: left;
  display: flex;
  justify-content: space-between;
  align-items: center;
  cursor: pointer;
}

.floating-dropdown-panel {
  position: absolute;
  top: 66px;
  left: 0;
  width: 100%;
  background: white;
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 12px;
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.15);
  display: flex;
  flex-direction: column;
  gap: 10px;
  z-index: 100;
  box-sizing: border-box;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.85rem;
  cursor: pointer;
  color: #333;
  user-select: none;
}

.checkbox-label input {
  accent-color: var(--granate-principal);
}

.btn-search-submit {
  background: var(--granate-principal);
  color: white;
  border: none;
  padding: 0 24px;
  border-radius: 6px;
  font-weight: 700;
  cursor: pointer;
  font-size: 0.88rem;
  height: 38px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: 0.2s;
}

.btn-search-submit:hover {
  background: var(--rosa-fuerte);
}

.btn-clear-filters {
  background: transparent;
  color: #777;
  border: 1px solid #ddd;
  padding: 0 14px;
  border-radius: 6px;
  font-weight: 600;
  cursor: pointer;
  font-size: 0.82rem;
  height: 38px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  transition: all 0.2s ease;
}

.btn-clear-filters:hover {
  background: var(--rosa-claro);
  color: var(--granate-principal);
}

.main-mode-bar {
  display: flex;
  align-items: center;
  margin-bottom: 25px;
}

.toggle-pill-container {
  display: inline-flex;
  background-color: #f2f2f5;
  border: 1px solid #e5e5ea;
  border-radius: 30px;
  padding: 4px;
  gap: 2px;
}

.pill-btn {
  border: none;
  outline: none;
  background: transparent;
  color: #666;
  font-weight: 600;
  font-size: 0.85rem;
  border-radius: 25px;
  cursor: pointer;
  padding: 7px 18px;
  display: flex;
  align-items: center;
  gap: 8px;
  font-family: inherit;
  transition: all 0.2s ease;
}

.pill-btn.active {
  background-color: #ffffff;
  color: var(--granate-principal);
  font-weight: 800;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.view-header-bar {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 46px;
  margin-bottom: 25px;
}

.view-header-bar h1 {
  margin: 0;
  color: var(--granate-principal);
  font-size: 1.7rem;
  font-weight: 800;
  text-align: center;
}

.btn-back-top {
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 7px 16px;
  background-color: var(--rosa-claro);
  color: var(--granate-principal);
  border: 1px solid #f2cdd6;
  border-radius: 20px;
  font-size: 0.82rem;
  font-weight: 700;
  text-decoration: none;
  cursor: pointer;
}

.btn-back-top:hover {
  background-color: #ffe1e8;
}

.loading-screen {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 60vh;
  gap: 20px;
}
</style>
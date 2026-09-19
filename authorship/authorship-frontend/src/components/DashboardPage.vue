<template>
  <div v-if="loading" class="loading-screen">
    <div class="spinner-wrapper">
      <div class="brand-spinner"></div>
      <div class="spinner-inner-dot"></div>
    </div>
    <p class="loading-label">Cargando detalles de la obra...</p>
  </div>

  <div v-else class="dashboard-wrapper">
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
        <div v-if="user.es_consumidor">
          <span class=" points"><i class="fa-solid fa-wallet"></i>{{ userPoints }} Puntos</span>
        </div>

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
                      <span class="notif-title" v-else-if="notif.notification_type === 'approved_work'">
                        Obra aprobada
                      </span>
                      <span class="notif-title" v-else-if="notif.notification_type === 'rejected_work'">
                        Obra rechazada
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
                      <template v-else-if="notif.notification_type === 'approved_work'">
                        La obra: <em>"{{ notif.work_title }}"</em> ha sido aprobada por el administrador.
                      </template>
                      <template v-else-if="notif.notification_type === 'rejected_work'">
                        La obra: <em>"{{ notif.work_title }}"</em> ha sido rechazada por el administrador.
                      </template>
                    </p>

                    <div
                      v-if="notif.notification_type === 'approved_work' && notif.work && getWorkStatus(notif) !== 'published'"
                      class="notif-actions">
                      <button class="btn-action-publish" @click="publishWork(notif)"
                        title="Hacer pública la obra en la plataforma">
                        Publicar obra
                      </button>
                      <button class="btn-action-delete" @click="discardWork(notif)"
                        title="Descartar y eliminar permanentemente la obra">
                        Descartar
                      </button>
                    </div>

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
      <div class="dashboard-layout">

        <aside class="sidebar">
          <div class="profile-card">

            <div class="profile-header">
              <div class="avatar-circle">
                {{ user.first_name?.charAt(0) || user.username?.charAt(0) }}
              </div>

              <template v-if="!isEditing">
                <h2 class="profile-name">{{ user.first_name }} {{ user.last_name }}</h2>
                <p class="username-text">@{{ user.username }}</p>
                <span class="role-badge">
                  <template v-if="user.es_autor">AUTOR</template>
                  <template v-else>CONSUMIDOR</template>
                </span>
              </template>

              <template v-else>
                <div class="edit-group">
                  <label class="field-label-top">
                    <i class="fa-solid fa-user"></i> Nombre de Usuario
                  </label>
                  <div class="input-icon-wrapper">
                    <i class="fa-regular fa-user input-inner-icon"></i>
                    <input v-model="editForm.username" class="edit-input-field" placeholder="Usuario">
                  </div>

                  <label class="field-label-top">
                    <i class="fa-solid fa-user"></i> Nombre
                  </label>
                  <div class="input-icon-wrapper">
                    <i class="fa-regular fa-user input-inner-icon"></i>
                    <input v-model="editForm.first_name" class="edit-input-field" placeholder="Nombre">
                  </div>

                  <label class="field-label-top">
                    <i class="fa-solid fa-user"></i> Apellidos
                  </label>
                  <div class="input-icon-wrapper">
                    <i class="fa-regular fa-user input-inner-icon"></i>
                    <input v-model="editForm.last_name" class="edit-input-field" placeholder="Apellidos">
                  </div>
                </div>
              </template>
            </div>

            <div class="profile-section">
              <div v-if="!isEditing">
                <div v-if="user.es_autor" class="info-group-full">
                  <div class="bio-display-card">
                    <div class="bio-display-header">
                      <i class="fa-solid fa-feather-pointed bio-display-icon"></i>
                      <span class="bio-display-title">Biografía Profesional</span>
                    </div>
                    <p class="bio-text">
                      {{ user.biography || 'Aún no has añadido una biografía a tu perfil.' }}
                    </p>
                  </div>
                </div>

                <div v-if="user.es_consumidor" class="interests-container">
                  <label class="section-subtitle">Mis intereses</label>
                  <div class="interests-pills-row">
                    <template v-if="userInterestsArray.length > 0">
                      <span v-for="interest in userInterestsArray" :key="interest" class="badge-interes">
                        {{ getInterestLabel(interest) }}
                      </span>
                    </template>
                    <p v-else class="info-text-empty">Sin intereses seleccionados</p>
                  </div>
                </div>
              </div>

              <div v-else>
                <div v-if="user.es_autor" class="info-group-full">
                  <div class="edit-interests-card">
                    <div class="interests-header">
                      <i class="fa-solid fa-feather-pointed icon-heart-top"></i>
                      <div class="interests-titles">
                        <span class="interests-title">Biografía Profesional</span>
                        <span class="interests-subtitle">Cuéntale a tu comunidad sobre tu trayectoria.</span>
                      </div>
                    </div>

                    <div class="bio-textarea-wrapper">
                      <textarea v-model="editForm.biography" class="edit-bio-textarea"
                        placeholder="Escribe una breve descripción sobre ti y tus creaciones..." rows="4"></textarea>
                    </div>
                  </div>
                </div>

                <div v-else-if="user.es_consumidor" class="info-group-full">
                  <div class="edit-interests-card">
                    <div class="interests-header">
                      <i class="fa-regular fa-heart icon-heart-top"></i>
                      <div class="interests-titles">
                        <span class="interests-title">Mis Intereses</span>
                        <span class="interests-subtitle">Selecciona lo que quieres descubrir.</span>
                      </div>
                    </div>

                    <div class="interests-two-columns">
                      <label v-for="work in availableWorkTypes" :key="work.id" class="interest-option">
                        <input type="checkbox" :value="work.id" v-model="editForm.interests" class="square-check" />
                        <i :class="getWorkIcon(work.id)" class="interest-work-icon"></i>
                        <span class="interest-tag-name">{{ work.label }}</span>
                      </label>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <nav v-if="!isEditing" class="sidebar-nav-list">
              <div v-if="user.es_autor">
                <router-link :to="{ path: '/works/create', query: { type: 'book' } }" class="nav-item-link"
                  active-class="active">
                  <i class="fa-solid fa-book-open"></i>
                  <span>Registrar libro</span>
                </router-link>

                <router-link :to="{ path: '/works/create', query: { type: 'music' } }" class="nav-item-link"
                  active-class="active">
                  <i class="fa-solid fa-music"></i>
                  <span>Registrar música</span>
                </router-link>

                <router-link :to="{ path: '/works/create', query: { type: 'video' } }" class="nav-item-link"
                  active-class="active">
                  <i class="fa-solid fa-video"></i>
                  <span>Registrar video</span>
                </router-link>

                <router-link :to="{ path: '/works/create', query: { type: 'software' } }" class="nav-item-link"
                  active-class="active">
                  <i class="fa-solid fa-music"></i>
                  <span>Registrar software</span>
                </router-link>
                <router-link :to="{ path: '/works/create', query: { type: 'paint' } }" class="nav-item-link"
                  active-class="active">
                  <i class="fa-solid fa-palette"></i>
                  <span>Registrar pintura</span>
                </router-link>

                <router-link :to="{ path: '/works/create', query: { type: 'sculpture' } }" class="nav-item-link"
                  active-class="active">
                  <i class="fa-solid fa-hammer"></i>
                  <span>Registrar escultura</span>
                </router-link>
              </div>
              <div v-else>
                <router-link to="/works" class="nav-item-link" active-class="active">
                  <i class="fa-solid fa-book-open"></i>
                  <span>Catálogo de Obras/Autores</span>
                </router-link>

                <router-link to="/subscription/works/subscribe" class="nav-item-link" active-class="active">
                  <i class="fa-solid fa-heart"></i>
                  <span>Obras Guardadas</span>
                </router-link>

                <router-link to="/subscription/authors/subscribe" class="nav-item-link" active-class="active">
                  <i class="fa-solid fa-users"></i>
                  <span>Mis Autores</span>
                </router-link>

                <router-link to="/subscription/plans" class="nav-item-link" active-class="active">
                  <i class="fa-solid fa-bell"></i>
                  <span>Planes de suscripción</span>
                </router-link>
              </div>
            </nav>

            <hr class="nav-divider" />

            <div class="email-edit-box">
              <label class="field-label-top">
                <i class="fa-regular fa-envelope"></i> Correo electrónico
              </label>
              <div v-if="!isEditing" class="email-text-box">
                <p class="email-val">{{ user.email }}</p>
              </div>
              <div v-else class="input-icon-wrapper">
                <i class="fa-regular fa-envelope input-inner-icon"></i>
                <input v-model="editForm.email" class="edit-input-field" placeholder="Correo">
              </div>
            </div>

            <div class="profile-actions">
              <button v-if="!isEditing" @click="startEditing" class="btn-outline-edit">
                Editar Perfil
              </button>

              <div v-else class="edit-buttons-row">
                <button @click="modifyProfile" class="btn-save-action">
                  <i class="fa-solid fa-floppy-disk"></i>
                  <span>Guardar cambios</span>
                </button>
                <button @click="isEditing = false" class="btn-cancel-action">
                  Cancelar
                </button>
              </div>
            </div>

          </div>
        </aside>

        <main class="main-content">

          <div class="footer-card">
            <div class="content-header">
              <i class="fas fa-book"></i>
              <div v-if="user.es_autor" class="header-text">
                <h1>Mis obras</h1>
                <p>
                  Aquí puedes ver y gestionar todas las obras que has publicado.
                </p>
              </div>
              <div v-else class="header-text">
                <h1>Catálogo de Obras</h1>
                <p>
                  Explora todas las creaciones disponibles y protegidas en la plataforma.
                </p>
              </div>
            </div>

            <div v-if="user.es_autor" class="recommended-container">
              <h3 class="recommended-title"> Estadísticas </h3>

              <div v-if="user.es_autor" class="statistics-container">
                <div class="statistics-info">
                  <div class="stat-icon-wrapper">
                    <i class="fa-solid fa-book-open"></i>
                  </div>
                  <div class="stat-data">
                    <span class="stat-label">Obras publicadas</span>
                    <span class="stat-number">{{ authorWorksLength }}</span>
                  </div>
                </div>

                <div class="statistics-info">
                  <div class="stat-icon-wrapper">
                    <i class="fa-solid fa-bookmark"></i>
                  </div>
                  <div class="stat-data">
                    <span class="stat-label">Obras en favoritos</span>
                    <span class="stat-number">{{ savedCount }}</span>
                  </div>
                </div>

                <div class="statistics-info">
                  <div class="stat-icon-wrapper">
                    <i class="fa-solid fa-users"></i>
                  </div>
                  <div class="stat-data">
                    <span class="stat-label">Suscriptores</span>
                    <span class="stat-number">{{ numSubscriptors }}</span>
                  </div>
                </div>
              </div>

              <h3 class="recommended-title"> Mis obras publicadas </h3>

              <div v-if="authorWorks.length > 0">
                <table class="recommended-table">
                  <thead>
                    <tr>
                      <th class="col-type">Tipo</th>
                      <th class="col-title">Título de la Obra</th>
                      <th class="col-status">Estado</th>
                      <th class="col-details">Detalles</th>
                      <th class="col-delete">Eliminar</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="work in paginatedWorksAuthor" :key="work.id">
                      <td class="col-type">
                        <div class="type-cell-wrapper">
                          <i :class="getWorkIcon(work.work_type)" class="work-icon"></i>
                          <span class="label-tipo">{{ getWorkTypeName(work.work_type) }}</span>
                        </div>
                      </td>

                      <td class="col-title">
                        <span class="work-title-sm">{{ work.title }}</span>
                      </td>

                      <td class="col-status">
                        <span v-if="work.status === 'appealed'" class="status-badge status-warning">
                          En revisión manual
                        </span>
                        <span v-else-if="work.status === 'approved'" class="status-badge status-info">
                          Aprobada
                        </span>
                        <span v-else-if="work.status === 'published'" class="status-badge status-success">
                          Publicada
                        </span>
                        <span v-else-if="work.status === 'rejected_manual'" class="status-badge status-danger">
                          Rechazada
                        </span>
                        <span v-else class="status-badge status-default">
                          Registrada
                        </span>
                      </td>

                      <td class="col-details">
                        <router-link :to="`/worksAuthor/${work.id}`" class="btn-table-sm">
                          Consultar
                        </router-link>
                      </td>

                      <td class="col-delete">
                        <button @click="deleteWork(work.id)" class="btn-delete-plain" title="Eliminar obra">
                          <i class="fa-solid fa-trash-can"></i>
                        </button>
                      </td>
                    </tr>
                  </tbody>
                </table>

                <div v-if="totalPages > 1" class="pagination-bar">
                  <button @click="prevPage" :disabled="currentPage === 1" class="btn-page">
                    <i class="fa-solid fa-chevron-left"></i> Anterior
                  </button>

                  <span class="pagination-info">
                    Página <strong>{{ currentPage }}</strong> de <strong>{{ totalPages }}</strong>
                  </span>

                  <button @click="nextPage" :disabled="currentPage === totalPages" class="btn-page">
                    Siguiente <i class="fa-solid fa-chevron-right"></i>
                  </button>
                </div>
              </div>

              <p v-else class="no-recommendations-msg">
                Aún no has publicado ninguna user.value.es_autorobra.
              </p>
            </div>

            <div v-if="user.es_consumidor" class="recommended-container">
              <h3 class="recommended-title"><i class="fa-solid fa-star"></i> Obras Recomendadas para ti</h3>

              <div v-if="recommendedWorks.length > 0" class="table-scroll-wrapper">
                <table class="recommended-table">
                  <thead>
                    <tr>
                      <th class="col-consumer-type">Tipo</th>
                      <th class="col-consumer-title">Título de la Obra</th>
                      <th class="col-consumer-details">Detalles</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="work in paginatedWorksConsumer" :key="work.id">
                      <td class="col-consumer-type">
                        <div class="type-cell-wrapper">
                          <i :class="getWorkIcon(work.work_type)" class="work-icon"></i>
                          <span class="label-tipo">{{ getWorkTypeName(work.work_type) }}</span>
                        </div>
                      </td>
                      <td class="col-consumer-title">
                        <span class="work-title-sm">{{ work.title }}</span>
                      </td>
                      <td class="col-consumer-details">
                        <router-link :to="`/works/${work.id}`" class="btn-table-sm">
                          Consultar
                        </router-link>
                      </td>
                    </tr>
                  </tbody>
                </table>

                <div v-if="totalPages > 1" class="pagination-bar">
                  <button @click="prevPage" :disabled="currentPage === 1" class="btn-page">
                    <i class="fa-solid fa-chevron-left"></i> Anterior
                  </button>

                  <span class="pagination-info">
                    Página <strong>{{ currentPage }}</strong> de <strong>{{ totalPages }}</strong>
                  </span>

                  <button @click="nextPage" :disabled="currentPage === totalPages" class="btn-page">
                    Siguiente <i class="fa-solid fa-chevron-right"></i>
                  </button>
                </div>
              </div>

              <p v-else class="no-recommendations-msg">
                Aún no tenemos recomendaciones personalizadas para ti.
              </p>
            </div>

            <router-link v-if="user.es_consumidor" to="/works" class="btn-primary-save">
              <i class="fa-solid fa-compass"></i>
              Explorar Catálogo
            </router-link>

          </div>

          <div v-if="user.es_consumidor" class="secondary-cards-grid">

            <div class="card-section">
              <div class="card-header-flex">
                <div class="card-title-group">
                  <i class="fa-solid fa-users icon-primary"></i>
                  <h3>Mis autores</h3>
                </div>
                <router-link to="/subscription/authors/subscribe" class="link-see-all">Ver todos &rarr;</router-link>
              </div>

              <div v-if="subscribedAuthors && subscribedAuthors.length > 0" class="authors-grid">
                <div v-for="authorItem in subscribedAuthors.slice(0, 3)" :key="authorItem.id" class="author-item">
                  <div class="avatar-circle-sm">
                    {{ authorItem.first_name?.charAt(0) || authorItem.username?.charAt(0) || 'A' }}
                  </div>
                  <span class="author-name">
                    {{ authorItem.first_name }} {{ authorItem.last_name }}
                  </span>
                  <span class="author-username">
                    @{{ authorItem.username }}
                  </span>
                </div>
              </div>

              <p v-else class="info-text-empty">Aún no sigues a ningún autor.</p>
            </div>

            <div class="card-section">
              <div class="card-header-flex">
                <div class="card-title-group">
                  <i class="fa-solid fa-heart icon-primary"></i>
                  <h3>Obras Guardadas</h3>
                </div>
                <router-link to="/subscription/works/subscribe" class="link-see-all">Ver todas &rarr;</router-link>
              </div>

              <div v-if="savedWorks && savedWorks.length > 0" class="saved-works-list">
                <div v-for="work in savedWorks.slice(0, 3)" :key="work.id" class="saved-work-item">
                  <div class="saved-work-left">
                    <i :class="getWorkIcon(work.work_type)" class="saved-work-icon"></i>
                    <span class="saved-work-title" :title="work.title">{{ work.title }}</span>
                  </div>
                  <span class="label-tipo-sm">{{ getWorkTypeName(work.work_type) }}</span>
                </div>
              </div>

              <p v-else class="info-text-empty">No tienes obras guardadas en tu lista.</p>
            </div>

          </div>
        </main>

      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from "vue";
import { useRouter } from "vue-router";
import axios from "axios";
import { useAuthStore } from "../stores/auth";

const router = useRouter();
const authStore = useAuthStore();

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

const subscribedAuthors = ref([]);
const savedWorks = ref([]);
const recommendedWorks = ref([]);
const loading = ref(true);
const isEditing = ref(false);
const editForm = ref({});
const userPoints = ref(0);
const authorWorks = ref([]);
const numSubscriptors = ref(0);
const savedCount = ref(0);

const availableWorkTypes = [
  { id: 'book', label: 'LIBRO' },
  { id: 'music', label: 'MÚSICA' },
  { id: 'video', label: 'VIDEO' },
  { id: 'software', label: 'SOFTWARE' },
  { id: 'paint', label: 'PINTURA' },
  { id: 'sculpture', label: 'ESCULTURA' }
];

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

const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";

const getWorkTypeName = (type) => workTypeNames[type] || 'Obra';
const getWorkIcon = (type) => workIconMap[type] || 'fa-solid fa-file-image';

const information = ref({
  show: false,
  message: "",
  type: "error"
});

const triggerInformation = (message, type = 'error') => {
  information.value = { show: true, message, type };
};

const userInterestsArray = computed(() => {
  if (user.value.interests) {
    if (typeof user.value.interests === 'string') {
      return user.value.interests.split(',').map(item => item.trim());
    } else {
      return user.value.interests;
    }
  }
  return [];
});

const getWorkStatus = (notif) => {
  if (!notif) return null;

  if (typeof notif.work === 'object' && notif.work !== null) {
    return notif.work.status;
  }

  const found = authorWorks.value.find(w => w.id === notif.work);

  if (found) {
    return found.status;
  }
  else {
    return null;
  }
};

const publishWork = async (notif) => {
  try {
    let workId;

    if (typeof notif.work === 'object') {
      if (notif.work) {
        workId = notif.work.id;

      } else {
        workId = null;

      }
    } else {
      workId = notif.work;
    }

    if (!workId) return;

    await axios.patch(
      `${API_BASE}/api/works/${workId}/`,
      { status: 'published' },
      { headers: { Authorization: `Token ${authStore.token}` } }
    );

    if (typeof notif.work === 'object' && notif.work !== null) {
      notif.work.status = 'published';
    }

    notifications.value = notifications.value.filter(n => n.id !== notif.id);

    const targetWork = authorWorks.value.find(w => w.id === workId);
    if (targetWork) {
      targetWork.status = 'published';
    } else {
      await getUserData();
    }

    triggerInformation("La obra ha sido publicada con éxito.", "success");

  } catch (err) {
    console.error('Error al publicar la obra:', err.response?.data || err.message);
  }
};

const discardWork = async (notif) => {
  try {
    let workId;

    if (typeof notif.work === 'object') {
      if (notif.work) {
        workId = notif.work.id;

      } else {
        workId = null;

      }
    } else {
      workId = notif.work;
    }

    await axios.delete(
      `${API_BASE}/api/works/${workId}/`,
      { headers: { Authorization: `Token ${authStore.token}` } }
    );

    notifications.value = notifications.value.filter(n => n.id !== notif.id);
  } catch (err) {
    console.error('Error al eliminar la obra:', err.response?.data || err.message);
  }
};

const getRecommendedWorks = async () => {
  try {
    const token = authStore.token || localStorage.getItem("token");

    const response = await axios.get(`${API_BASE}/api/works/recommended/`, {
      headers: {
        Authorization: `Token ${token}`,
      },
    });

    recommendedWorks.value = response.data;
    console.log("Obras recomendadas del usuario cargadas");
  } catch (err) {
    console.error("Error al cargar recomendaciones:", err);
  }
};

const getInterestLabel = (id) => {
  const found = availableWorkTypes.find(type => type.id === id);
  if (found) {
    return found.label;
  } else {
    return id;
  }
};

const startEditing = () => {
  editForm.value = { ...user.value };

  if (typeof editForm.value.interests === 'string' && editForm.value.interests !== "") {
    editForm.value.interests = editForm.value.interests.split(',');
  } else if (!editForm.value.interests) {
    editForm.value.interests = [];
  }

  isEditing.value = true;
};

const authorWorksLength = computed(() => {
  return authorWorks.value.filter(work => work.status === 'published').length;
});

const getUserData = async () => {
  try {
    const token = authStore.token || localStorage.getItem("token");

    const response = await axios.get(`${API_BASE}/api/users/me/`, {
      headers: {
        Authorization: `Token ${token}`,
      },
    });

    user.value = response.data;

    user.value.es_autor = user.value.role === 'author';
    user.value.es_consumidor = user.value.role === 'consumer';

    if (user.value.es_autor) {
      const statsResponse = await axios.get(`${API_BASE}/api/subscriptions/authors/stats/`, {
        headers: {
          Authorization: `Token ${token}`,
        },
      });

      numSubscriptors.value = statsResponse.data.subscribers_count || 0;
      savedCount.value = statsResponse.data.saved_works_count || 0;

      const worksResponse = await axios.get(`${API_BASE}/api/works/authors/${user.value.id}/`, {
        headers: {
          Authorization: `Token ${token}`,
        },
      });

      authorWorks.value = worksResponse.data;
    }

  } catch (err) {
    console.error("Error en la petición:", err);
    triggerInformation("Sesión inválida o expirada", "error");
    router.push("/login");
  } finally {
    loading.value = false;
  }
};


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

const getSuscribedAuthors = async () => {
  try {
    const token = authStore.token || localStorage.getItem("token");

    const response = await axios.get(`${API_BASE}/api/subscriptions/authors/subscribe/`, {
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

const getSavedWorks = async () => {
  try {
    const token = authStore.token || localStorage.getItem("token");

    const response = await axios.get(`${API_BASE}/api/subscriptions/works/subscribe/`, {
      headers: {
        Authorization: `Token ${token}`,
      },
    });

    savedWorks.value = response.data;
    console.log("Obras guardadas del usuario cargadas");
  } catch (err) {
    console.error("Error en la petición:", err);
  }
};

const modifyProfile = async () => {
  try {
    loading.value = true;
    const token = authStore.token || localStorage.getItem("token");

    if (!editForm.value.username || !editForm.value.first_name || !editForm.value.last_name) {
      triggerInformation("Nombre, Apellidos y Usuario son campos obligatorios.", "error");
      loading.value = false;
      return;
    }

    const payload = {
      username: editForm.value.username,
      first_name: editForm.value.first_name,
      last_name: editForm.value.last_name,
      email: editForm.value.email || user.value.email,
    };

    if (user.value.es_autor) {
      payload.biography = editForm.value.biography || "";
    } else if (user.value.es_consumidor) {
      if (Array.isArray(editForm.value.interests)) {
        payload.interests = editForm.value.interests.join(',');

      } else if (editForm.value.interests) {
        payload.interests = editForm.value.interests;

      } else {
        payload.interests = "";
      }
    }

    const response = await axios.patch(`${API_BASE}/api/users/me/`, payload, {
      headers: {
        Authorization: `Token ${token}`,
      }
    });

    user.value = response.data;
    user.value.es_autor = user.value.role === 'author';
    user.value.es_consumidor = user.value.role === 'consumer';

    isEditing.value = false;

    if (user.value.es_consumidor) {
      await getRecommendedWorks();
    }

    triggerInformation("Perfil actualizado correctamente.", "success");

  } catch (err) {
    console.error(err);
    let serverMessage = "Error al actualizar el perfil.";

    if (err.response && err.response.data) {
      const firstError = Object.values(err.response.data)[0];

      if (Array.isArray(firstError)) {
        serverMessage = firstError[0];
      } else {
        serverMessage = firstError;
      }
    }

    triggerInformation(serverMessage, "error");

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

const currentPage = ref(1);
const itemsPerPageAuthor = 6;
const itemsPerPageConsumer = 3;

const totalPages = computed(() => {
  if (user.value.es_autor) {
    return Math.ceil(authorWorks.value.length / itemsPerPageAuthor) || 1;
  }

  else {
    return Math.ceil(recommendedWorks.value.length / itemsPerPageConsumer) || 1;
  }
});

const paginatedWorksAuthor = computed(() => {
  const start = (currentPage.value - 1) * itemsPerPageAuthor;
  return authorWorks.value.slice(start, start + itemsPerPageAuthor);
});

const paginatedWorksConsumer = computed(() => {
  const start = (currentPage.value - 1) * itemsPerPageConsumer;
  return recommendedWorks.value.slice(start, start + itemsPerPageConsumer);
});

const nextPage = () => {
  if (currentPage.value < totalPages.value) currentPage.value++;
};

const prevPage = () => {
  if (currentPage.value > 1) currentPage.value--;
};

const deleteWork = async (id) => {
  try {
    const token = authStore.token || localStorage.getItem("token");
    await axios.delete(`${API_BASE}/api/works/${id}/`, {
      headers: { Authorization: `Token ${token}` }
    });

    authorWorks.value = authorWorks.value.filter(work => work.id !== id);

    if (currentPage.value > totalPages.value) {
      currentPage.value = Math.max(1, totalPages.value);
    }

    triggerInformation("Obra eliminada correctamente.", "success");
  } catch (err) {
    triggerInformation("¡Se ha producido un error al intentar eliminar la obra!", "error");
    console.error("Error al eliminar la obra:", err);
  } finally {
    loading.value = false;
  }
};

const handleLogout = () => {
  authStore.logout();
  localStorage.removeItem("token");
  router.push("/login");
};

onMounted(() => {
  getUserData();
  getUserPoints();
  getSuscribedAuthors();
  getSavedWorks();
  getRecommendedWorks();
});
</script>

<style scoped>
.dashboard-layout {
  display: flex;
  justify-content: center;
  align-items: flex-start;
  max-width: 1440px;
  margin: 40px auto;
  padding: 0 30px;
  gap: 40px;
  width: 100%;
  box-sizing: border-box;
}

.main-content {
  flex: 1;
  width: 100%;
  max-width: 1050px;
  max-height: none;
  display: flex;
  flex-direction: column;
}

.header-panel {
  margin-bottom: 40px;
}

.header-panel h1 {
  font-size: 2.2em;
  color: var(--granate-principal);
  margin-bottom: 10px;
}

.header-panel p {
  color: #777;
  font-size: 1.1em;
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
  border-radius: 25%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.8em;
  font-weight: bold;
  margin: 0;
  border: 2px solid var(--granate-principal);
}

.header-text h1 {
  margin: 0 0 5px 0;
  color: #000;
}

.header-text p {
  margin: 0;
  color: #666;
}

.section-label {
  display: block;
  font-weight: bold;
  color: var(--granate-principal);
  font-size: 1.2em;
  margin-bottom: 20px;
}

.linea-granate {
  border: none;
  height: 2px;
  background-color: var(--granate-principal);
  margin: 20px 0;
  opacity: 0.8;
  border-radius: 2px;
}

.sidebar {
  width: 320px;
  flex-shrink: 0;
}

.profile-card {
  background: #ffffff;
  border-radius: 24px;
  padding: 32px 24px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.04);
  display: flex;
  flex-direction: column;
  box-sizing: border-box;
}

.profile-header {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  margin-bottom: 20px;
}

.avatar-circle {
  width: 72px;
  height: 72px;
  border-radius: 50%;
  background-color: #fde8ed;
  color: var(--granate-principal);
  font-weight: 800;
  font-size: 1.8rem;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 14px;
}

.profile-name {
  margin: 0;
  font-size: 1.25rem;
  font-weight: 800;
  color: var(--granate-principal);
  line-height: 1.2;
}

.username-text {
  margin: 4px 0 10px 0;
  color: #444;
  font-weight: 600;
  font-size: 0.9rem;
}

.role-badge {
  display: inline-block;
  background-color: #fff0f3;
  color: var(--rosa-fuerte);
  font-size: 0.72rem;
  font-weight: 800;
  padding: 4px 14px;
  border-radius: 20px;
  letter-spacing: 0.6px;
  text-transform: uppercase;
}

.profile-section {
  width: 100%;
  margin-bottom: 18px;
}

.section-subtitle {
  display: block;
  font-size: 0.85rem;
  font-weight: 600;
  color: #444;
  margin-bottom: 10px;
  text-align: center;
}

.interests-pills-row {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  justify-content: center;
}

.badge-interes {
  background-color: #fff0f3;
  color: var(--granate-principal);
  padding: 5px 14px;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: 700;
}

.bio-text {
  font-size: 0.85rem;
  color: #666;
  text-align: center;
  line-height: 1.4;
  margin: 0;
}

.info-group {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 8px;
  margin-bottom: 20px;
  width: 100%;
  padding-left: 10px;
}

.info-section {
  text-align: left;
  margin-top: 25px;
  border-top: 1px solid #f0f0f0;
  padding-top: 15px;
}

.label-title {
  display: block;
  font-weight: bold;
  color: var(--granate-principal);
  margin-bottom: 5px;
  font-size: 0.85em;
}

.info-text {
  color: #666;
  font-size: 0.9em;
  line-height: 1.4;
  margin-bottom: 15px;
}

.interests-grid {
  display: flex;
  flex-direction: column;
  gap: 8px;
  width: 100%;
}

.interests-pills-container {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 8px;
  margin-top: 10px;
  width: 100%;
}

.interest-pill {
  background-color: var(--rosa-claro);
  color: var(--granate-principal);
  padding: 6px 10px;
  border-radius: 20px;
  font-size: 0.85em;
  font-weight: bold;
  border: 1px solid var(--rosa-fuerte);
  text-align: center;
  display: block;
  width: 100%;
}

.checkbox-wrapper {
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
  justify-content: flex-start;
  user-select: none;
}

.check-label {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  font-size: 0.85rem;
  font-weight: 600;
  color: #333;
}

.edit-profile-icon {
  color: var(--granate-principal);
  font-size: 0.95rem;
  width: 18px;
  text-align: center;
}

.label-mini {
  text-align: left;
  width: 100%;
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 0.82rem;
  font-weight: 700;
  color: var(--granate-principal);
  margin-bottom: 4px;
}

.custom-check {
  accent-color: var(--granate-principal);
  width: 16px;
  height: 16px;
  cursor: pointer;
}

.info-help {
  text-align: left;
  width: 100%;
  display: block;
  font-size: 0.75rem;
  font-weight: 500;
  color: #666;
  margin-bottom: 16px;
}

.sidebar-nav-list {
  display: flex;
  flex-direction: column;
  gap: 4px;
  width: 100%;
}

.nav-item-link {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 11px 16px;
  border-radius: 12px;
  color: #333333;
  font-size: 0.92rem;
  font-weight: 600;
  text-decoration: none;
  transition: all 0.2s ease;
  cursor: pointer;
}

.nav-item-link i {
  font-size: 1.15rem;
  width: 20px;
  text-align: center;
  color: #444444;
}

.nav-item-link:hover {
  background-color: #faf0f2;
  color: var(--granate-principal);
}

.nav-item-link:hover i {
  color: var(--granate-principal);
}

.nav-item-link.router-link-active,
.nav-item-link.active {
  background-color: #fff0f3;
  color: var(--granate-principal);
  font-weight: 700;
}

.nav-item-link.router-link-active i,
.nav-item-link.active i {
  color: var(--granate-principal);
}

.static-item {
  color: #444;
  cursor: default;
}

.static-item:hover {
  background: transparent;
  color: #444;
}

.static-item:hover i {
  color: #444;
}

.nav-divider {
  border: none;
  border-top: 1px solid #f0f0f0;
  margin: 14px 0;
  width: 100%;
}

.email-info-section {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 0 8px;
  margin-bottom: 22px;
}

.email-icon {
  font-size: 1.15rem;
  color: #444;
  margin-top: 2px;
}

.email-text-box {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.email-label {
  font-size: 0.78rem;
  color: #777;
}

.email-val {
  font-size: 0.88rem;
  font-weight: 700;
  color: #222;
  margin: 0;
  word-break: break-all;
}

.profile-actions {
  width: 100%;
}

.btn-outline-edit {
  width: 100%;
  background: #ffffff;
  border: 1.5px solid var(--rosa-fuerte);
  color: var(--granate-principal);
  padding: 10px;
  border-radius: 10px;
  cursor: pointer;
  font-weight: 700;
  font-size: 0.9rem;
  transition: all 0.2s ease;
}

.btn-outline-edit:hover {
  background: var(--rosa-fuerte);
  color: #ffffff;
}

.edit-buttons {
  display: flex;
  gap: 8px;
  margin-top: 15px;
}

.btn-save-small {
  flex: 1;
  background: var(--granate-principal);
  color: white;
  border: none;
  padding: 9px;
  border-radius: 8px;
  font-weight: 700;
  cursor: pointer;
}

.btn-cancel-small {
  flex: 1;
  background: #f0f0f0;
  color: #333;
  border: none;
  padding: 9px;
  border-radius: 8px;
  cursor: pointer;
}

.edit-input,
.edit-input-sm {
  width: 100%;
  padding: 8px 10px;
  margin-bottom: 8px;
  border: 1px solid #ddd;
  border-radius: 6px;
  box-sizing: border-box;
  font-family: inherit;
  font-size: 0.88rem;
}

.edit-textarea {
  width: 100%;
  height: 80px;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 5px;
  resize: none;
  font-family: inherit;
  font-size: 0.9em;
}

.grid-acciones {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 15px;
  margin-bottom: 40px;
}

.card-accion {
  display: flex;
  align-items: center;
  justify-content: center;
  background: white;
  border: 1px solid #ddd;
  padding: 15px;
  border-radius: 10px;
  text-align: center;
  text-decoration: none;
  color: var(--granate-principal);
  font-weight: bold;
  transition: all 0.3s;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.02);
}

.card-accion:hover {
  background: var(--granate-principal);
  border-color: var(--granate-principal);
  color: white;
  transform: translateY(-3px);
  box-shadow: 0 5px 15px rgba(128, 0, 32, 0.2);
}

.card-accion .icon {
  margin-right: 10px;
  font-size: 1.2em;
}

.router-card {
  background: var(--rosa-claro);
  border-radius: 15px;
  padding: 30px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.05);
  text-align: center;
}

.footer-card {
  background: white;
  padding: 36px;
  border-radius: 20px;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.05);
  max-height: none;
  width: 100%;
  box-sizing: border-box;
}

.footer-card h3 {
  color: var(--granate-principal);
  margin-bottom: 10px;
}

.footer-card p {
  color: #666;
  margin-bottom: 25px;
}

.btn-primary-save {
  display: block;
  width: 100%;
  background-color: var(--granate-principal);
  color: white;
  padding: 14px;
  border-radius: 8px;
  font-weight: bold;
  text-align: center;
  text-decoration: none;
  margin-top: 20px;
  transition: 0.3s;
  font-size: 1.1em;
}

.btn-primary-save:hover {
  background-color: var(--rosa-fuerte);
  transform: translateY(-2px);
}

.statistics-container {
  display: flex;
  gap: 20px;
  margin: 25px 0;
  width: 100%;
  box-sizing: border-box;
}

.statistics-info {
  flex: 1;
  background: white;
  border: 1px solid rgba(219, 112, 147, 0.25);
  border-radius: 12px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.03);
  transition: transform 0.2s ease;
}

.statistics-info:hover {
  transform: translateY(-2px);
}

.stat-icon-wrapper {
  width: 48px;
  height: 48px;
  background-color: var(--rosa-claro);
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.stat-icon-wrapper i {
  font-size: 1.4rem;
  color: var(--granate-principal);
}

.stat-data {
  display: flex;
  flex-direction: column;
  color: black;
}

.stat-number {
  font-size: 1.6rem;
  font-weight: 800;
  color: var(--granate-principal);
  line-height: 1.1;
}

.stat-label {
  font-size: 0.82rem;
  font-weight: 600;
  color: #777;
  letter-spacing: 0.5px;
  margin-top: 4px;
}

.recommended-container {
  background: #fdf8fa;
  border: 1px solid var(--rosa-claro);
  border-radius: 10px;
  padding: 20px;
  margin: 25px 0;
}

.recommended-title {
  color: var(--granate-principal);
  font-size: 1.1em;
  margin-bottom: 15px;
  border-bottom: 2px solid var(--rosa-claro);
  padding-bottom: 5px;
  display: flex;
  align-items: center;
  gap: 10px;
}

.recommended-title i {
  width: 40px;
  height: 40px;
  display: flex;
  justify-content: center;
  align-items: center;
  color: #eff30a;
  font-size: 18px;
}

.recommended-table {
  width: 100%;
  border-collapse: collapse;
  table-layout: fixed;
}

.recommended-table th,
.recommended-table td {
  padding: 12px 10px;
  vertical-align: middle;
}

.recommended-table th {
  color: var(--granate-principal);
  font-size: 0.85rem;
  font-weight: 700;
  text-transform: uppercase;
  text-align: left;
}

.col-type {
  width: 18%;
  text-align: left;
}

.col-title {
  width: 42%;
  text-align: left;
}

.col-status {
  width: 16%;
  text-align: center;
}

.col-details {
  width: 14%;
  text-align: center;
}

.col-delete {
  width: 10%;
  text-align: center;
}

th.col-status,
th.col-details,
th.col-delete {
  text-align: center;
}

.col-consumer-type {
  width: 25%;
  text-align: left;
}

.col-consumer-title {
  width: 55%;
  text-align: left;
}

.col-consumer-details {
  width: 20%;
  text-align: center;
}

th.col-consumer-details {
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
}

.label-tipo {
  color: var(--rosa-fuerte);
  font-weight: 700;
  font-size: 0.8rem;
  text-transform: uppercase;
}

.edit-interests-container {
  background: #fdf8fa;
  border: 1px solid var(--rosa-claro);
  border-radius: 10px;
  padding: 20px;
  margin: 25px 0;
}

.work-title-sm {
  font-weight: 600;
  color: #222;
}

.btn-table-sm {
  background: var(--rosa-claro);
  color: black;
  padding: 5px 12px;
  border-radius: 6px;
  text-decoration: none;
  font-size: 0.8em;
  font-weight: bold;
  transition: 0.2s;
}

.btn-table-sm:hover {
  background: var(--rosa-fuerte);
  color: white;
}

.no-recommendations-msg {
  color: #888;
  font-style: italic;
  font-size: 0.9em;
}

.secondary-cards-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 25px;
  margin-top: 25px;
  width: 100%;
  box-sizing: border-box;
}

.secondary-cards-grid-author {
  display: grid;
  gap: 25px;
  margin-top: 25px;
  width: 100%;
  box-sizing: border-box;
}

.card-section {
  background: white;
  padding: 24px;
  border-radius: 15px;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.05);
  display: flex;
  flex-direction: column;
  justify-content: flex-start;
  box-sizing: border-box;
}

.card-header-flex {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  gap: 10px;
}

.card-title-group {
  display: flex;
  align-items: center;
  gap: 10px;
  white-space: nowrap;
}

.card-title-group i {
  color: var(--granate-principal);
  font-size: 1.15rem;
}

.card-title-group h3 {
  font-size: 1.1em;
  font-weight: bold;
  color: var(--granate-principal);
  margin: 0;
}

.link-see-all {
  color: var(--granate-principal);
  font-size: 0.85em;
  font-weight: 600;
  text-decoration: none;
  white-space: nowrap;
  flex-shrink: 0;
}

.authors-grid {
  display: flex;
  justify-content: space-around;
  align-items: center;
  gap: 15px;
  padding: 10px 0;
}

.author-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  flex: 1;
}

.avatar-circle-sm {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  background-color: var(--rosa-claro);
  color: var(--granate-principal);
  font-weight: bold;
  font-size: 1.1em;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 8px;
}

.author-name {
  font-size: 0.85em;
  font-weight: 700;
  color: #111;
  margin-bottom: 2px;
  word-break: break-word;
}

.author-username {
  font-size: 0.75em;
  color: #777;
}

.saved-works-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.saved-work-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background-color: #fffafc;
  border: 1px solid var(--rosa-claro);
  padding: 10px 14px;
  border-radius: 8px;
  gap: 12px;
}

.saved-work-left {
  display: flex;
  align-items: center;
  gap: 10px;
  flex: 1;
  min-width: 0;
}

.saved-work-icon {
  color: var(--granate-principal);
  font-size: 1em;
  flex-shrink: 0;
}

.saved-work-title {
  font-size: 0.88em;
  font-weight: 600;
  color: #222;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.label-tipo-sm {
  flex-shrink: 0;
  color: var(--rosa-fuerte);
  font-size: 0.75em;
  font-weight: 700;
  text-transform: uppercase;
}

.work-icon-box {
  width: 36px;
  height: 36px;
  background: #fde8ed;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #700020;
}

.work-info {
  flex: 1;
  margin-left: 12px;
}

.work-title {
  margin: 0;
  font-size: 0.9em;
  font-weight: bold;
}

.work-author {
  margin: 0;
  font-size: 0.8em;
  color: #666;
}

.work-actions {
  display: flex;
  align-items: center;
  gap: 10px;
}

.btn-heart-active {
  background: none;
  border: none;
  color: #700020;
  cursor: pointer;
  font-size: 1.1em;
}

.table-scroll-wrapper {
  max-height: 220px;
  overflow-y: auto;
  padding-right: 5px;
  scrollbar-width: thin;
  scrollbar-color: var(--granate-principal) var(--rosa-claro);
}

.table-scroll-wrapper::-webkit-scrollbar {
  width: 6px;
}

.table-scroll-wrapper::-webkit-scrollbar-track {
  background: var(--rosa-claro);
  border-radius: 4px;
}

.table-scroll-wrapper::-webkit-scrollbar-thumb {
  background: var(--granate-principal);
  border-radius: 4px;
}

.btn-delete-plain {
  background: transparent;
  border: none;
  outline: none;
  color: #c93b5a;
  cursor: pointer;
  padding: 6px 10px;
  border-radius: 6px;
  font-size: 1rem;
  transition: all 0.2s ease;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.btn-delete-plain:hover {
  background-color: #feecef;
  color: #9e1b32;
  transform: scale(1.1);
}

.pagination-bar {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 16px;
  margin-top: 18px;
  padding-top: 12px;
  border-top: 1px solid #f0e4e8;
}

.pagination-info {
  font-size: 0.85rem;
  color: #555;
}

.pagination-info strong {
  color: var(--granate-principal);
}

.btn-page {
  background: white;
  border: 1px solid var(--rosa-claro);
  color: var(--granate-principal);
  padding: 6px 14px;
  border-radius: 8px;
  font-size: 0.8rem;
  font-weight: 700;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  transition: all 0.2s ease;
}

.btn-page:hover:not(:disabled) {
  background: var(--rosa-claro);
  border-color: var(--rosa-fuerte);
}

.btn-page:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.edit-group {
  width: 100%;
  display: flex;
  flex-direction: column;
}

.field-label-top {
  display: flex;
  align-items: center;
  gap: 7px;
  font-size: 0.8rem;
  font-weight: 700;
  color: #3b4256;
  margin-top: 14px;
  margin-bottom: 6px;
  text-align: left;
}

.field-label-top i {
  font-size: 0.85rem;
  color: #555e77;
}

.input-icon-wrapper {
  position: relative;
  width: 100%;
  display: flex;
  align-items: center;
}

.input-inner-icon {
  position: absolute;
  left: 14px;
  color: #8c96ab;
  font-size: 0.95rem;
  pointer-events: none;
}

.edit-input-field {
  width: 100%;
  height: 42px;
  padding: 0 14px 0 40px;
  border: 1.5px solid #e1e6ef;
  border-radius: 9px;
  font-family: inherit;
  font-size: 0.9rem;
  color: #2b3040;
  background-color: #ffffff;
  outline: none;
  box-sizing: border-box;
  transition: border-color 0.2s;
}

.edit-input-field:focus {
  border-color: var(--rosa-fuerte);
}

.info-group-full {
  width: 100%;
  margin-top: 18px;
}

.edit-interests-card {
  background: #fdf5f7;
  border: 1px solid #f9e2e7;
  border-radius: 12px;
  padding: 16px 18px;
  box-sizing: border-box;
}

.interests-header {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  margin-bottom: 14px;
}

.icon-heart-top {
  color: var(--granate-principal);
  font-size: 1.15rem;
  margin-top: 2px;
}

.interests-titles {
  display: flex;
  flex-direction: column;
  text-align: left;
}

.interests-title {
  font-size: 0.88rem;
  font-weight: 800;
  color: var(--granate-principal);
  line-height: 1.2;
}

.interests-subtitle {
  font-size: 0.74rem;
  color: #7d8495;
  margin-top: 2px;
}

.interests-two-columns {
  display: grid;
  grid-template-columns: 1fr 1fr;
  row-gap: 12px;
  column-gap: 16px;
}

.interest-option {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  user-select: none;
}

.square-check {
  appearance: none;
  -webkit-appearance: none;
  width: 17px;
  height: 17px;
  border: 1.5px solid #d495a6;
  border-radius: 4px;
  background-color: #ffffff;
  cursor: pointer;
  display: grid;
  place-content: center;
  outline: none;
  margin: 0;
  flex-shrink: 0;
  transition: all 0.15s ease;
}

.square-check:checked {
  background-color: var(--granate-principal);
  border-color: var(--granate-principal);
}

.square-check:checked::before {
  content: "";
  width: 8px;
  height: 4px;
  border-left: 2px solid white;
  border-bottom: 2px solid white;
  transform: rotate(-45deg) translate(1px, -1px);
}

.interest-work-icon {
  color: var(--granate-principal);
  font-size: 0.95rem;
  width: 16px;
  text-align: center;
}

.interest-tag-name {
  font-size: 0.76rem;
  font-weight: 800;
  color: #3b4256;
  letter-spacing: 0.4px;
}

.email-edit-box {
  width: 100%;
  margin-top: 14px;
  margin-bottom: 20px;
}

.edit-buttons-row {
  display: grid;
  grid-template-columns: 1.3fr 1fr;
  gap: 10px;
  width: 100%;
}

.btn-save-action {
  background: var(--granate-principal);
  color: #ffffff;
  border: none;
  border-radius: 9px;
  padding: 11px 14px;
  font-size: 0.85rem;
  font-weight: 700;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  transition: background-color 0.2s;
}

.btn-save-action:hover {
  background: var(--rosa-fuerte);
}

.btn-cancel-action {
  background: #ffffff;
  color: var(--granate-principal);
  border: 1.5px solid #f2cdd6;
  border-radius: 9px;
  padding: 11px 14px;
  font-size: 0.85rem;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-cancel-action:hover {
  background: #fdf5f7;
  border-color: var(--rosa-fuerte);
}

.bio-display-card {
  background-color: #fdf5f7;
  border: 1px solid #f9e2e7;
  border-radius: 12px;
  padding: 16px 18px;
  box-sizing: border-box;
  text-align: left;
}

.bio-display-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 10px;
}

.bio-display-icon {
  color: var(--granate-principal);
  font-size: 1rem;
}

.bio-display-title {
  font-size: 0.88rem;
  font-weight: 800;
  color: var(--granate-principal);
}

.bio-text {
  font-size: 0.86rem;
  color: #555e77;
  line-height: 1.5;
  margin: 0;
  text-align: left;
  white-space: pre-wrap;
  word-break: break-word;
}

.bio-textarea-wrapper {
  width: 100%;
  margin-top: 4px;
}

.edit-bio-textarea {
  width: 100%;
  box-sizing: border-box;
  padding: 12px 14px;
  border: 1.5px solid #e1e6ef;
  border-radius: 9px;
  font-family: inherit;
  font-size: 0.88rem;
  color: #2b3040;
  background-color: #ffffff;
  outline: none;
  resize: vertical;
  min-height: 95px;
  line-height: 1.45;
  transition: border-color 0.2s;
}

.edit-bio-textarea:focus {
  border-color: var(--rosa-fuerte);
}

.status-badge {
  display: inline-block;
  padding: 3px 8px;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 700;
  white-space: nowrap;
}

.status-warning {
  background-color: #fff3cd;
  color: #856404;
}

.status-info {
  background-color: #d1ecf1;
  color: #0c5460;
}

.status-success {
  background-color: #d4edda;
  color: #155724;
}

.status-danger {
  background-color: #f8d7da;
  color: #721c24;
}

.status-default {
  background-color: #e2e3e5;
  color: #383d41;
}
</style>
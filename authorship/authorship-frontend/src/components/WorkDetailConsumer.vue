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
                      El autor <strong>{{ notif.author_username }}</strong> ha subido una nueva obra: <em>"{{ notif.work_title }}"</em>.
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

    <div class="page-layout-grid">
      <div class="left-column-content">
        <div class="container-card" v-if="work">
          <div class="back-link2">
            <button @click="goBack" type="button" class="btn-back">
              <i class="fa-solid fa-circle-arrow-left"></i> Volver
            </button>
          </div>

          <div class="main-content-layout">
            <div class="icon-side" v-if="work && work.work_type">
              <div class="giant-icon-square">
                <i :class="workIcon"></i>
              </div>
            </div>

            <div class="info-side">
              <div class="header-title-actions">
                <div class="title-with-badge">
                  <h1 class="work-main-title">{{ work.title }}</h1>
                  <span class="circle-pink">{{ workType }}</span>
                </div>

                <div class="save-btn-wrapper">
                  <button type="button" @click="saveWork(work.id)" class="btn-save-detail" :class="{ 'is-saved': isSaved(work.id) }">
                    <i :class="isSaved(work.id) ? 'fa-solid fa-bookmark' : 'fa-regular fa-bookmark'"></i>
                    <span>{{ isSaved(work.id) ? 'Guardada' : 'Guardar obra' }}</span>
                  </button>
                </div>
              </div>

              <div class="paralel-fields">
                <div class="info-block">
                  <span class="label"><i class="fa-solid fa-circle-user"></i>Autor/a</span>
                  <span class="value">{{ work.author_username || 'Desconocido' }}</span>
                  <button @click="openAuthorModal()" type="button" class="btn-author-profile">
                    <i class="fa-solid fa-address-card"></i>
                    <span>Ver Perfil</span>
                  </button>
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
                                      <span class="work-title-cell" :title="w.title">{{ w.title }}</span>
                                    </td>
                                    <td class="col-date work-date-cell">
                                      {{ simpleFormatDate(w.created_at) }}
                                    </td>
                                    <td class="col-action">
                                      <button type="button" class="btn-table-consult" @click="consultAuthorWork(w.id)">
                                        Consultar
                                      </button>
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
                        <button type="button" @click="subscribeToAuthor(selectedAuthor.id)" class="btn-subscribe">
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
                  <span class="circle-pink2">precio: {{ work.plan_required.points }} puntos</span>
                </div>

                <div v-else class="free-box">
                  <span class="circle-pink2"><i class="fa-solid fa-coins"></i>Esta obra es gratuita.</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="container-card" v-if="hasTechnicalData">
          <div class="table-scroll-wrapper">
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
                    <a v-if="work.repository_url" :href="work.repository_url" target="_blank">{{ work.repository_url }}</a>
                    <span v-else>-</span>
                  </span>
                </div>
                <div class="divider-icon2"><span class="line"></span></div>
                <div class="technical-row">
                  <div class="icon-circle"><i class="fa-solid fa-book"></i></div>
                  <span class="tech-label">Repositorio de documentación</span>
                  <span class="tech-value">
                    <a v-if="work.documentation_url" :href="work.documentation_url" target="_blank">{{ work.documentation_url }}</a>
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
      </div>

      <div class="right-column-sidebar">
        <!-- Bloque de Archivos -->
        <div class="container-card sidebar-card-info" v-if="work">
          <div v-if="work.file_name" class="file-box-section">
            <span class="label-sidebar-title">
              <i class="fa-solid fa-box-archive"></i> Obra Completa
            </span>

            <div v-if="canSeeProtectedContent" class="unlocked-zone">
              <p class="sidebar-help-text">Tienes acceso total. Puedes descargar el archivo original firmado:</p>
              <button
                type="button"
                class="btn-action btn-download"
                @click="downloadOriginal"
                :disabled="downloadingOriginal"
              >
                <span v-if="downloadingOriginal">
                  <i class="fa-solid fa-spinner fa-spin"></i> Descargando...
                </span>
                <span v-else>
                  <i class="fa-solid fa-circle-down"></i> Descargar Original
                </span>
              </button>
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

              <div v-if="work.resume_name" class="file-box-section" style="margin-bottom: 25px;">
                <span class="label-sidebar-title">
                  <i class="fa-solid fa-eye"></i> Muestra Gratuita
                </span>
                <p class="sidebar-help-text">Revisa un fragmento libre antes de adquirir la obra completa:</p>

                <div class="media-preview-container">
                  <button
                    type="button"
                    class="btn-sidebar-secondary"
                    @click="openResumePreview"
                    :disabled="loadingResume"
                  >
                    <span v-if="loadingResume">
                      <i class="fa-solid fa-spinner fa-spin"></i> Abriendo...
                    </span>
                    <span v-else>
                      <i class="fa-solid fa-arrow-up-right-from-square"></i> Abrir preview ({{ work.resume_name }})
                    </span>
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="container-card license-container" v-if="work">
          <h3>Uso permitido de la obra</h3>

          <div v-if="currentLicenseInfo" class="license-card-info">
            <span class="license-badge-name">{{ currentLicenseInfo.name }}</span>
            <p class="license-summary">{{ currentLicenseInfo.summary }}</p>

            <div v-if="work.license !== 'none'" class="license-rules-grid">
              <span v-if="currentLicenseInfo.commercial" class="rule-pill rule-allow">
                <i class="fa-solid fa-check"></i> Uso comercial permitido
              </span>
              <span v-else class="rule-pill rule-deny">
                <i class="fa-solid fa-xmark"></i> Solo uso personal (no comercial)
              </span>

              <span v-if="currentLicenseInfo.derivatives" class="rule-pill rule-allow">
                <i class="fa-solid fa-check"></i> Puedes crear versiones derivadas
              </span>
              <span v-else class="rule-pill rule-deny">
                <i class="fa-solid fa-xmark"></i> No alterar ni modificar
              </span>

              <span v-if="currentLicenseInfo.sameLicense" class="rule-pill rule-warn">
                <i class="fa-solid fa-arrows-rotate"></i> Compartir versiones con misma licencia
              </span>
            </div>
          </div>

          <p v-else class="license-description">
            Información de licencia no disponible.
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import axios from "axios";
import { useAuthStore } from "../stores/auth";

const router = useRouter();
const route = useRoute();
const authStore = useAuthStore();
const loading = ref(true);
const works = ref([]);
const authorWorks = ref([]);

const savedWorks = ref([]);
const savedWorkIds = ref(new Set());

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

const downloadingOriginal = ref(false);
const loadingResume = ref(false);

const workTypes = {
  book: 'LIBRO',
  music: 'MÚSICA',
  video: 'VIDEO',
  software: 'SOFTWARE',
  paint: 'PINTURA',
  sculpture: 'ESCULTURA'
};

const licenseMeanings = {
  'none': {
    name: 'Todos los derechos reservados',
    summary: 'El autor se reserva todos los derechos. Solo se permite el acceso y consumo dentro de la plataforma.',
    commercial: false,
    derivatives: false,
    sameLicense: false
  },
  'by': {
    name: 'Creative Commons (CC BY)',
    summary: 'Puedes disfrutar, compartir e incluso reutilizar esta obra citando a su autor/a original.',
    commercial: true,
    derivatives: true,
    sameLicense: false
  },
  'by-sa': {
    name: 'Creative Commons (CC BY-SA)',
    summary: 'Puedes compartir y adaptar la obra citando autoría, siempre que compartas tus creaciones bajo estos mismos términos.',
    commercial: true,
    derivatives: true,
    sameLicense: true
  },
  'by-nd': {
    name: 'Creative Commons (CC BY-ND)',
    summary: 'Puedes compartir la obra citando al autor/a, pero debes mantenerla íntegra y sin modificaciones.',
    commercial: true,
    derivatives: false,
    sameLicense: false
  },
  'by-nc': {
    name: 'Creative Commons (CC BY-NC)',
    summary: 'Puedes disfrutar y versionar esta obra libremente, siempre que sea sin fines de lucro comercial y citando autoría.',
    commercial: false,
    derivatives: true,
    sameLicense: false
  },
  'by-nc-sa': {
    name: 'Creative Commons (CC BY-NC-SA)',
    summary: 'Puedes disfrutar y versionar sin fines de lucro, citando autoría y compartiendo derivados con esta misma licencia.',
    commercial: false,
    derivatives: true,
    sameLicense: true
  },
  'by-nc-nd': {
    name: 'Creative Commons (CC BY-NC-ND)',
    summary: 'Puedes descargarla y compartirla citando al autor/a, pero no puedes lucrarte con ella ni alterarla de ningún modo.',
    commercial: false,
    derivatives: false,
    sameLicense: false
  }
};

const currentLicenseInfo = computed(() => {
  if (!work.value || !work.value.license) return null;
  return licenseMeanings[work.value.license] || null;
});

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

const information = ref({
  show: false,
  message: "",
  type: "error"
});

const triggerInformation = (message, type = 'error') => {
  information.value = { show: true, message, type };
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
    const token = authStore.token || localStorage.getItem("token");
    const response = await axios.get("http://localhost:8000/api/users/me/", {
      headers: { Authorization: `Token ${token}` },
    });

    user.value = response.data;
    user.value.es_autor = user.value.role === 'author';
    user.value.es_consumidor = user.value.role === 'consumer';

    if (user.value.es_consumidor) {
      const worksResponse = await axios.get("http://localhost:8000/api/works/", {
        headers: { Authorization: `Token ${token}` },
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
    const token = authStore.token || localStorage.getItem('token');
    const response = await axios.get(`http://localhost:8000/api/works/${id}/`, {
      headers: { Authorization: `Token ${token}` }
    });
    work.value = response.data;
  } catch (err) {
    console.error("Error al cargar la obra:", err);
    router.push("/works");
  }
};

const fetchMySubscription = async () => {
  try {
    const token = authStore.token || localStorage.getItem('token');
    const response = await axios.get(`http://localhost:8000/api/subscriptions/me/`, {
      headers: { Authorization: `Token ${token}` }
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

const isSaved = (workId) => {
  return savedWorkIds.value.has(Number(workId));
};

const fetchSavedWorks = async () => {
  try {
    const token = authStore.token || localStorage.getItem("token");
    const response = await axios.get("http://localhost:8000/api/subscriptions/works/subscribe/", {
      headers: { Authorization: `Token ${token}` },
    });

    savedWorks.value = response.data;
    savedWorkIds.value = new Set(response.data.map(item => item.work_id || item.id));
  } catch (err) {
    console.error("Error en las obras guardadas:", err);
  }
};

const fetchSubscriptionPlan = async () => {
  try {
    const token = authStore.token || localStorage.getItem('token');
    const response = await axios.get(`http://localhost:8000/api/subscriptions/plans/`, {
      headers: { Authorization: `Token ${token}` }
    });
    subscriptionTypes.value = response.data;
  } catch (err) {
    console.error("Error al cargar planes de suscripción:", err);
  } finally {
    loading.value = false;
  }
};

const downloadOriginal = async () => {
  if (!work.value) return;
  if (downloadingOriginal.value) return;

  downloadingOriginal.value = true;
  try {
    const token = authStore.token || localStorage.getItem("token");
    const response = await axios.get(
      `http://localhost:8000/api/works/${work.value.id}/serve/`,
      {
        headers: { Authorization: `Token ${token}` },
        responseType: "blob",
      }
    );

    const blob = new Blob([response.data]);
    const blobUrl = window.URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = blobUrl;

    let fileName = "obra_original";
    if (work.value.file_name) {
      fileName = work.value.file_name;
    }

    link.setAttribute("download", fileName);
    document.body.appendChild(link);
    link.click();

    document.body.removeChild(link);
    window.URL.revokeObjectURL(blobUrl);
  } catch (err) {
    console.error("Error al descargar archivo original:", err);
    triggerInformation("No se ha podido descargar el archivo de la obra.", "error");
  } finally {
    downloadingOriginal.value = false;
  }
};

const openResumePreview = async () => {
  if (!work.value) return;
  if (loadingResume.value) return;

  loadingResume.value = true;
  try {
    const token = authStore.token || localStorage.getItem("token");
    const response = await axios.get(
      `http://localhost:8000/api/works/${work.value.id}/serve-resume/`,
      {
        headers: { Authorization: `Token ${token}` },
        responseType: "blob",
      }
    );

    const contentType = response.headers["content-type"] || "application/pdf";
    const blob = new Blob([response.data], { type: contentType });
    const blobUrl = window.URL.createObjectURL(blob);
    window.open(blobUrl, "_blank");
  } catch (err) {
    console.error("Error al abrir muestra:", err);
    triggerInformation("No se ha podido abrir la vista previa de la muestra.", "error");
  } finally {
    loadingResume.value = false;
  }
};

const consultAuthorWork = (newWorkId) => {
  closeAuthorModal();
  router.push(`/works/${newWorkId}`);
};

const simpleFormatDate = (dateString) => {
  if (!dateString) return "";
  const date = new Date(dateString);
  return date.toLocaleDateString("es-ES");
};

const formatDate = (dateString) => {
  if (!dateString) return '';
  return new Date(dateString).toLocaleDateString('es-ES', {
    day: '2-digit', month: 'long', year: 'numeric'
  });
};

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
    } else if (activeSubscription.value.plan_points >= work.value.plan_required.points) {
      isSubscribed = true;
    }
  }

  return isAdmin || isAuthor || isFreeWork || isSubscribed;
});

const handleSubscribe = () => {
  router.push("/subscription/plans");
};

const isNotificationsOpen = ref(false);
const notifications = ref([]);

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
    triggerInformation("¡Se ha producido un error al intentar modificar las obras guardadas!", "error");
  }
};

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

const selectedAuthor = ref(null);

const openAuthorModal = async () => {
  if (!work.value) return;

  let authorId = null;
  if (typeof work.value.author === "object" && work.value.author !== null) {
    authorId = work.value.author.id;
  } else {
    authorId = work.value.author;
  }

  if (!authorId) return;

  selectedAuthor.value = {
    id: authorId,
    username: work.value.author_username || "Autor",
    first_name: "",
    last_name: "",
    biography: ""
  };
  authorWorks.value = [];

  try {
    const token = authStore.token || localStorage.getItem("token");

    const responseWorks = await axios.get(`http://localhost:8000/api/works/authors/${authorId}/`, {
      headers: { Authorization: `Token ${token}` }
    });
    authorWorks.value = responseWorks.data;

    const responseUser = await axios.get(`http://localhost:8000/api/users/${authorId}/`, {
      headers: { Authorization: `Token ${token}` }
    });

    selectedAuthor.value = responseUser.data;
  } catch (error) {
    console.error("Error al cargar los detalles del autor:", error);
  }
};

const closeAuthorModal = () => {
  selectedAuthor.value = null;
  authorWorks.value = [];
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
      await axios.delete(`http://localhost:8000/api/subscriptions/authors/subscribe/`, config);
      suscribedAuthorsIds.value.delete(authorId);
      triggerInformation("¡Has eliminado con éxito tu suscripción a este autor!", "success");
    } else {
      await axios.post(`http://localhost:8000/api/subscriptions/authors/subscribe/`, { author_id: authorId }, {
        headers: { Authorization: `Token ${token}` }
      });
      suscribedAuthorsIds.value.add(authorId);
      triggerInformation("¡Te has suscrito con éxito a este autor!", "success");
    }
    closeAuthorModal();
  } catch (error) {
    console.error("Error al suscribirse:", error);
    triggerInformation("¡Se ha producido un error con la suscripción a este autor!", "error");
  }
};

const goBack = () => {
  if (window.history.state?.back) {
    router.back();
  } else {
    router.push('/works');
  }
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

watch(
  () => route.params.id,
  async (newId, oldId) => {
    if (newId && newId !== oldId) {
      closeAuthorModal();
      await fetchWorkDetails();
      await fetchMySubscription();
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }
  }
);

onMounted(async () => {
  loading.value = true;
  authStore.loadToken();

  if (authStore.token) {
    try {
      await authStore.fetchUserProfile();
    } catch (profileErr) {
      console.error("Error al cargar perfil:", profileErr);
    }
  } else {
    router.push("/login");
    return;
  }

  getUserData();
  getUserPoints();
  fetchWorkDetails();
  fetchSubscriptionPlan();
  fetchMySubscription();
  fetchSavedWorks();
});
</script>

<style scoped>
.loading-screen {
  min-height: 80vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 20px;
}

.spinner-wrapper {
  position: relative;
  width: 54px;
  height: 54px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.brand-spinner {
  width: 100%;
  height: 100%;
  border: 4px solid var(--rosa-claro, #fff0f3);
  border-top-color: var(--granate-principal, #700020);
  border-radius: 50%;
  animation: spin 0.85s linear infinite;
}

.spinner-inner-dot {
  position: absolute;
  width: 10px;
  height: 10px;
  background-color: var(--rosa-fuerte, #db7093);
  border-radius: 50%;
  animation: pulse-dot 1.2s ease-in-out infinite;
}

.loading-label {
  font-size: 0.95rem;
  font-weight: 700;
  color: var(--granate-principal, #700020);
  letter-spacing: 0.4px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

@keyframes pulse-dot {
  0%, 100% { transform: scale(0.8); opacity: 0.6; }
  50% { transform: scale(1.3); opacity: 1; }
}

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
  background-color: var(--rosa-claro);
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

.header-title-actions {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 20px;
  margin-bottom: 25px;
  width: 100%;
}

.title-with-badge {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 12px;
  flex: 1;
}

.work-main-title {
  margin: 0;
  font-size: 1.85em;
  color: #111;
  line-height: 1.2;
  word-break: break-word;
}

.circle-pink {
  background: var(--rosa-claro);
  color: var(--granate-principal);
  border: 1px solid var(--rosa-fuerte);
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 0.72em;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  white-space: nowrap;
  align-self: center;
}

.save-btn-wrapper {
  flex-shrink: 0;
}

.btn-save-detail {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  background-color: white;
  border: 1.5px solid var(--granate-principal);
  color: var(--granate-principal);
  padding: 7px 16px;
  border-radius: 20px;
  font-weight: 700;
  font-size: 0.88em;
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.04);
}

.btn-save-detail i {
  font-size: 1.05em;
  color: var(--granate-principal);
}

.btn-save-detail:hover {
  background-color: var(--rosa-claro);
  transform: translateY(-1px);
}

.btn-save-detail.is-saved {
  background-color: var(--rosa-claro);
  color: var(--granate-principal);
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
  align-items: center;
  text-align: center;
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
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.info-block .value {
  font-size: 1.05em;
  color: #333;
  font-weight: 500;
  text-align: center;
}

.btn-author-profile {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 7px;
  margin-top: 8px;
  margin-left: auto;
  margin-right: auto;
  padding: 6px 14px;
  background-color: var(--rosa-claro);
  color: var(--granate-principal);
  border: 1px solid var(--rosa-fuerte);
  border-radius: 16px;
  font-size: 0.8rem;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s ease;
  width: fit-content;
}

.info-block:not(:last-child) {
  border-right: 1px solid var(--rosa-fuerte);
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

.btn-author-profile:hover {
  background-color: var(--granate-principal);
  border-color: var(--granate-principal);
  color: #ffffff;
}

.info-block2 {
  display: flex;
  flex-direction: column;
  gap: 6px;
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
}

.btn-back {
  background: none;
  border: none;
  padding: 0;
  font: inherit;
  font-size: 1.1em;
  font-weight: bold;
  color: var(--granate-principal);
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 8px;
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

.icon-circle {
  width: 24px;
  height: 24px;
  background-color: var(--rosa-claro);
  border-radius: 50%;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.icon-circle i {
  color: var(--granate-principal);
  font-size: 0.75rem;
}

.tech-label {
  color: #555555;
  font-size: 0.85rem;
  font-weight: 600;
}

.tech-value {
  color: #222222;
  font-size: 0.85rem;
}

.tech-value a {
  color: var(--rosa-fuerte);
  text-decoration: none;
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
  font-size: 0.82rem;
  color: #666;
  margin: 6px 0 12px 0;
  line-height: 1.4;
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
}

.btn-download {
  background: var(--rosa-fuerte);
  color: #333;
}

.btn-download:hover {
  background: var(--granate-principal);
  color: white;
}

.btn-subscribe-now {
  background: #edf2f7;
  color: var(--granate-principal);
  border: 1px solid rgba(139, 0, 41, 0.2);
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
  border-radius: 6px;
  font-size: 0.82rem;
  font-weight: bold;
  cursor: pointer;
  transition: background 0.2s;
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

/* Tarjeta informativa de Licencias */
.license-container {
  border-left: 5px solid var(--granate-principal);
}

.license-container h3 {
  margin: 0 0 10px 0;
  font-size: 0.95rem;
  font-weight: 700;
  color: var(--granate-principal);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.license-card-info {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.license-badge-name {
  font-weight: 800;
  font-size: 0.92rem;
  color: var(--granate-principal);
}

.license-summary {
  margin: 0;
  font-size: 0.85rem;
  color: #555;
  line-height: 1.4;
}

.license-rules-grid {
  display: flex;
  flex-direction: column;
  gap: 6px;
  margin-top: 6px;
}

.rule-pill {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 0.78rem;
  font-weight: 700;
  padding: 5px 10px;
  border-radius: 8px;
  width: fit-content;
}

.rule-allow {
  background-color: #e8f5e9;
  color: #2e7d32;
}

.rule-deny {
  background-color: #fbe9e7;
  color: #c62828;
}

.rule-warn {
  background-color: var(--rosa-claro);
  color: var(--granate-principal);
}

.license-description {
  font-size: 0.85rem;
  color: #6c757d;
  margin: 0;
}

/* Modal de autor */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.4);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 99999;
  backdrop-filter: blur(4px);
}

.modal-card {
  background: white;
  border-radius: 24px;
  padding: 40px 45px;
  width: 95%;
  max-width: 880px;
  max-height: 90vh;
  overflow-y: auto;
  position: relative;
  box-shadow: 0 20px 45px rgba(0, 0, 0, 0.18);
  display: flex;
  flex-direction: column;
  gap: 28px;
  box-sizing: border-box;
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
}

.author-handle {
  font-size: 0.85em;
  color: var(--rosa-fuerte);
  font-weight: 700;
  margin-top: 3px;
}

.info-section {
  display: flex;
  gap: 12px;
  align-items: flex-start;
  width: 100%;
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
  flex-shrink: 0;
}

.section-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.section-title {
  font-size: 0.92em;
  font-weight: 800;
  color: var(--granate-principal);
}

.section-text {
  font-size: 0.9em;
  color: #555;
  margin: 4px 0 0 0;
}

.table-container {
  max-height: 280px;
  overflow-y: auto;
  scrollbar-width: thin;
  scrollbar-color: var(--granate-principal) var(--rosa-claro);
}

.modal-works-table {
  width: 100%;
  border-collapse: separate;
  border-spacing: 0 10px;
  table-layout: fixed;
}

.col-type { width: 18%; text-align: left; }
.col-title { width: 44%; text-align: left; overflow: hidden; }
.col-date { width: 18%; text-align: center; white-space: nowrap; }
.col-action { width: 20%; text-align: center; }

.pill-type {
  display: inline-block;
  background-color: #fde8ef;
  color: var(--rosa-fuerte);
  font-size: 0.7em;
  font-weight: 800;
  padding: 4px 12px;
  border-radius: 15px;
}

.work-title-cell {
  display: block;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-weight: 700;
  color: #222;
}

.btn-table-consult {
  background-color: var(--rosa-claro);
  color: var(--granate-principal);
  padding: 6px 14px;
  border-radius: 14px;
  font-size: 0.78rem;
  font-weight: 700;
  border: 1px solid var(--rosa-fuerte);
  cursor: pointer;
}

.btn-table-consult:hover {
  background-color: var(--granate-principal);
  border-color: var(--granate-principal);
  color: white;
}

.btn-subscribe {
  width: 100%;
  background: var(--granate-principal);
  color: white;
  border: none;
  padding: 14px;
  border-radius: 12px;
  font-weight: 700;
  cursor: pointer;
}

.btn-subscribe:hover {
  background: #a00028;
}
</style>
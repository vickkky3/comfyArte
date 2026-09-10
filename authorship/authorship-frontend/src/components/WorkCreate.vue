<template>

  <div class="dashboard-wrapper">
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

    <div class="form-container">
      <h1>Registrar {{ workTypeName }}</h1>
      <p class="subtitle">Sube tu archivo para protegerlo</p>

      <div class="form-container">
        <form @submit.prevent="handleSubmit" enctype="multipart/form-data">
          <div class="form-grid-top">
            <div class="form-group">
              <label for="title">Título de la Obra <span class="required">*</span></label>
              <input type="text" id="title" v-model="title" placeholder="Ej: Mi gran novela" required>
            </div>

            <div class="form-group">
              <label>
                Plan de suscripción requerido <span class="required">*</span>
                <i class="fa-regular fa-circle-question label-help-icon" title="Nivel de suscripción necesario"></i>
              </label>
              <span class="field-desc-mini">¿Qué plan debe tener el usuario para acceder a esta obra?</span>
              <select v-model="selectedPlan" class="custom-select">
                <option value="">Gratis (Público para todos)</option>
                <option v-for="plan in subscriptionTypes" :key="plan.id" :value="plan.id">
                  {{ plan.name }} ({{ plan.points }} puntos)
                </option>
              </select>
              <div v-if="loadingPlans" class="mini-loader">Cargando planes disponibles...</div>
            </div>
          </div>

          <div class="form-group">
            <label for="description">Descripción / Resumen <span class="required">*</span></label>
            <textarea id="description" v-model="description" rows="3"
              placeholder="Describe brevemente tu creación..."></textarea>
          </div>

          <div class="form-card specific-data-card">
            <div class="card-section-header">
              <i :class="workIcons[workType] || 'fa-solid fa-layer-group'"></i>
              <h3>Datos específicos de {{ workTypeName.toLowerCase() }}</h3>
            </div>

            <div v-if="workType === 'book'" class="grid-4-cols">
              <div class="form-group-compact">
                <label>Número de páginas <span class="required">*</span></label>
                <input type="number" v-model="pages" placeholder="Ej: 320" required>
              </div>
              <div class="form-group-compact">
                <label>ISBN <span class="required">*</span></label>
                <input type="text" v-model="isbn" placeholder="Ej: 978-84-123456-7-8" required>
              </div>
              <div class="form-group-compact">
                <label>Género <span class="required">*</span></label>
                <select v-model="genre" required>
                  <option value="" disabled selected>Selecciona un género</option>
                  <option value="Narrativa / Ficción">Narrativa / Ficción</option>
                  <option value="Misterio / Suspense">Misterio / Suspense</option>
                  <option value="Ciencia Ficción / Fantasía">Ciencia Ficción / Fantasía</option>
                  <option value="Novela Romántica">Novela Romántica</option>
                  <option value="Novela Histórica">Novela Histórica</option>
                  <option value="Poesía">Poesía</option>
                  <option value="Teatro">Teatro</option>
                  <option value="Ensayo">Ensayo</option>
                  <option value="Biografía">Biografía</option>
                  <option value="Divulgación Científica">Divulgación Científica</option>
                  <option value="Desarrollo Personal">Desarrollo Personal</option>
                  <option value="Infantil / Juvenil">Infantil / Juvenil</option>
                  <option value="Cómic">Cómic</option>
                  <option value="Otro">Otro</option>
                </select>
              </div>

              <div class="form-group-compact">
                <label>Idioma <span class="required">*</span></label>
                <select v-model="language" class="select-pink" required>
                  <option value="" disabled selected>Selecciona un idioma</option>
                  <option value="Español">Español</option>
                  <option value="Inglés">Inglés</option>
                  <option value="Francés">Francés</option>
                  <option value="Alemán">Alemán</option>
                  <option value="Italiano">Italiano</option>
                  <option value="Otro">Otro</option>
                </select>
              </div>
            </div>

            <div v-else-if="workType === 'music'" class="grid-3-cols">
              <div class="form-group-compact">
                <label>Duración (minutos) <span class="required">*</span></label>
                <input type="number" step="0.01" v-model="duration" placeholder="Ej: 3.45" required>
              </div>
              <div class="form-group-compact">
                <label>Álbum <span class="required">*</span></label>
                <input type="text" v-model="album" placeholder="Ej: Nombre del álbum" required>
              </div>
              <div class="form-group-compact">
                <label>Género<span class="required">*</span></label>
                <select v-model="genre" class="select-pink" required>
                  <option value="" disabled selected>Selecciona una geńero músical</option>
                  <option value="Pop">Pop</option>
                  <option value="Rock">Rock</option>
                  <option value="Urbano / Reggaetón / Trap">Urbano / Reggaetón / Trap</option>
                  <option value="Electrónica / Dance / Lo-Fi">Electrónica / Dance / Lo-Fi</option>
                  <option value="Hip Hop / Rap">Hip Hop / Rap</option>
                  <option value="Indie / Cantautor">Indie / Cantautor</option>
                  <option value="Clásica / Instrumental">Clásica / Instrumental'</option>
                  <option value="Jazz">Jazz</option>
                  <option value="Folk / Tradicional / Flamenco">Folk / Tradicional / Flamenco</option>
                  <option value="Otro">Otro</option>
                </select>
              </div>
            </div>

            <div v-else-if="workType === 'video'" class="grid-2-cols">
              <div class="form-group-compact">
                <label>Duración (minutos) <span class="required">*</span></label>
                <input type="number" step="0.01" v-model="duration" placeholder="Ej: 12.50" required>
              </div>
              <div class="form-group-compact">
                <label>Categoría <span class="required">*</span></label>
                <select v-model="genre" class="select-pink" required>
                  <option value="" disabled selected>Selecciona una categoría</option>
                  <option value="Ficción">Ficción</option>
                  <option value="Documental">Documental</option>
                  <option value="Videoclip">Videoclip</option>
                  <option value="Animación">Animación</option>
                  <option value="Tutorial">Tutorial</option>
                  <option value="Cortometraje">Cortometraje</option>
                  <option value="Entrevista / Charlas / Podcast">Entrevista / Charlas / Podcast</option>
                  <option value="Publicitario">Publicitario</option>
                  <option value="Teatro / Danza">Teatro / Danza</option>
                  <option value="Otro">Otro</option>
                </select>
              </div>
            </div>

            <div v-else-if="workType === 'software'" class="grid-3-cols">
              <div class="form-group-compact">
                <label>Lenguaje <span class="required">*</span></label>
                <input type="text" v-model="programming_language" placeholder="Ej: Python, TypeScript..." required>
              </div>
              <div class="form-group-compact">
                <label>URL del Repositorio</label>
                <input type="url" v-model="repository_url" placeholder="https://github.com/...">
              </div>
              <div class="form-group-compact">
                <label>URL de Documentación</label>
                <input type="url" v-model="documentation_url" placeholder="https://docs....">
              </div>
            </div>

            <div v-else-if="workType === 'paint' || workType === 'sculpture'" class="grid-3-cols">
              <div class="form-group-compact">
                <label>Altura (cm) <span class="required">*</span></label>
                <input type="number" step="0.1" v-model="height" placeholder="Ej: 50" required>
              </div>
              <div class="form-group-compact">
                <label>Peso (kg) <span class="required">*</span></label>
                <input type="number" step="0.1" v-model="weight" placeholder="Ej: 2.5" required>
              </div>
              <div class="form-group-compact">
                <label>Material / Técnica <span class="required">*</span></label>
                <select v-model="type_detail" required>
                  <option value="" disabled selected>Selecciona técnica</option>
                  <template v-if="workType === 'paint'">
                    <option value="oil">Óleo</option>
                    <option value="acrylic">Acrílico</option>
                    <option value="watercolor">Acuarela</option>
                    <option value="digital">Digital</option>
                  </template>
                  <template v-else>
                    <option value="marble">Mármol</option>
                    <option value="bronze">Bronce</option>
                    <option value="wood">Madera</option>
                    <option value="clay">Arcilla</option>
                  </template>
                </select>
              </div>
            </div>
          </div>

          <div class="form-card upload-card">
            <div class="upload-header">
              <i class="fa-regular fa-gem upload-icon"></i>
              <label>Archivo de la Obra <span class="required">*</span></label>
            </div>
            <div class="upload-content-row">
              <label class="custom-file-btn">
                <i class="fa-solid fa-arrow-up-from-bracket"></i>
                <span>{{ selectedFile ? selectedFile.name : 'Seleccionar archivo' }}</span>
                <input type="file" @change="handleFileChange" class="hidden-file-input"
                  accept=".pdf, .txt, .jpg, .jpeg, .png, .webp, .mp3, .wav, .ogg, .mp4, .avi, .mov, .zip, .py, .js, .ts, .jsx, .tsx, .vue, .html, .css, .java, .c, .cpp, .cs, .php, .rb, .go, .rs, .swift, .kt, .sql, .sh, .ipynb, .json, .xml, .yaml, .yml"
                  required>
              </label>
              <div class="format-hint">
                <span class="hint-title">Formatos permitidos:</span>
                <span class="hint-desc">Documentos, Imágenes, Audio, Vídeo, Código fuente y ZIP.</span>
              </div>
            </div>
          </div>

          <div class="form-card upload-card">
            <div class="upload-header">
              <i class="fa-regular fa-gem upload-icon"></i>
              <label>Resumen de la Obra <span class="required">*</span></label>
            </div>
            <div class="upload-content-row">
              <label class="custom-file-btn">
                <i class="fa-solid fa-arrow-up-from-bracket"></i>
                <span>{{ selectedResume ? selectedResume.name : 'Seleccionar archivo' }}</span>
                <input type="file" @change="handleResumeChange" class="hidden-file-input"
                  accept=".pdf, .txt, .jpg, .jpeg, .png, .webp, .mp3, .wav, .ogg, .mp4, .avi, .mov, .zip, .py, .js, .ts, .jsx, .tsx, .vue, .html, .css, .java, .c, .cpp, .cs, .php, .rb, .go, .rs, .swift, .kt, .sql, .sh, .ipynb, .json, .xml, .yaml, .yml"
                  required>
              </label>
              <div class="format-hint">
                <span class="hint-title">Formatos permitidos:</span>
                <span class="hint-desc">Documentos, Imágenes, Audio, Vídeo, Código fuente y ZIP.</span>
              </div>
            </div>
          </div>

          <div class="form-card license-card">
            <div class="license-top-row">
              <i class="fa-brands fa-creative-commons cc-icon"></i>
              <label>Licencia Creative Commons <span class="required">*</span></label>
            </div>

            <select v-model="selectedLicense" class="custom-select">
              <option v-for="lic in licenses" :key="lic.id" :value="lic.id">
                {{ lic.name }}
              </option>
            </select>

            <div v-if="licenseMeanings[selectedLicense]" class="license-preview-box">
              <div class="preview-header">
                <i class="fa-solid fa-circle-info"></i>
                <strong>{{ licenseMeanings[selectedLicense].name }}</strong>
              </div>
              <p class="preview-text">{{ licenseMeanings[selectedLicense].summary }}</p>
            </div>

            <p class="license-footnote">
              Tu obra será protegida bajo: <strong>{{ selectedLicenseName }}</strong>
            </p>
          </div>

          <div v-if="error" class="error-msg">{{ error }}</div>

          <button type="submit" class="btn-save" :disabled="loading">
            <i class="fa-solid fa-floppy-disk"></i>
            <span>{{ loading ? 'Guardando y validando...' : 'Guardar y proteger obra' }}</span>
          </button>

          <router-link to="/dashboard" class="back-link">&larr; Cancelar y volver</router-link>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import axios from "axios";
import { useAuthStore } from "../stores/auth";

const route = useRoute();
const router = useRouter();
const authStore = useAuthStore();

const title = ref("");
const description = ref("");
const selectedFile = ref(null);
const selectedResume = ref(null);
const loading = ref(false);
const error = ref("");

const pages = ref(0);
const isbn = ref("");
const genre = ref("");
const language = ref("");
const album = ref("");
const duration = ref(0);
const programming_language = ref("");
const repository_url = ref("");
const documentation_url = ref("");
const height = ref(0);
const weight = ref(0);
const type_detail = ref("");

const workType = route.query.type;

const workTypeName = computed(() => {
  const types = {
    book: 'Libro',
    music: 'Música',
    video: 'Video',
    software: 'Software',
    paint: 'Pintura',
    sculpture: 'Escultura'
  };
  return types[workType];
});

const licenses = [
  { id: 'by', name: 'CC BY (Reconocimiento)' },
  { id: 'by-sa', name: 'CC BY-SA (Compartir Igual)' },
  { id: 'by-nd', name: 'CC BY-ND (Sin Obra Derivada)' },
  { id: 'by-nc', name: 'CC BY-NC (No Comercial)' },
  { id: 'by-nc-sa', name: 'CC BY-NC-SA' },
  { id: 'by-nc-nd', name: 'CC BY-NC-ND' },
  { id: 'none', name: 'Sin licencia' },
];

const selectedLicense = ref("none");

const selectedLicenseName = computed(() => {
  const idSeleccionado = selectedLicense.value;

  const foundLicense = licenses.find((item) => {
    return item.id === idSeleccionado;
  });

  if (foundLicense) {
    return foundLicense.name;

  } else {
    return 'Sin licencia';
  }
});

const licenseMeanings = {
  'none': {
    name: 'Sin licencia específica',
    summary: 'Aplica la reserva habitual de derechos de autor de tu obra.',
    badges: ['Uso estándar'],
  },
  'by': {
    name: 'CC BY · Atribución',
    summary: 'Cualquiera puede usar, modificar o lucrarse con tu obra mencionándote.',
    commercial: true,
    derivatives: true,
    sameLicense: false,
  },
  'by-sa': {
    name: 'CC BY-SA · Compartir Igual',
    summary: 'Se permite el uso comercial y cambios, pero las obras derivadas deben tener esta misma licencia.',
    commercial: true,
    derivatives: true,
    sameLicense: true,
  },
  'by-nd': {
    name: 'CC BY-ND · Sin Obras Derivadas',
    summary: 'Se permite compartir y comercializar, pero la obra no puede ser alterada ni modificada.',
    commercial: true,
    derivatives: false,
    sameLicense: false,
  },
  'by-nc': {
    name: 'CC BY-NC · No Comercial',
    summary: 'Permite crear obras derivadas pero nunca para beneficio económico.',
    commercial: false,
    derivatives: true,
    sameLicense: false,
  },
  'by-nc-sa': {
    name: 'CC BY-NC-SA · No Comercial - Compartir Igual',
    summary: 'Permite crear obras derivadas sin fines de lucro y con esta misma licencia.',
    commercial: false,
    derivatives: true,
    sameLicense: true,
  },
  'by-nc-nd': {
    name: 'CC BY-NC-ND · Más Restrictiva',
    summary: 'Solo permite ver/descargar la obra tal cual es, reconociendo autoría y sin fines comerciales.',
    commercial: false,
    derivatives: false,
    sameLicense: false,
  },
};

const workIcons = {
  book: 'fa-solid fa-book-open',
  music: 'fa-solid fa-music',
  video: 'fa-solid fa-video',
  software: 'fa-solid fa-code',
  paint: 'fa-solid fa-palette',
  sculpture: 'fa-solid fa-hammer'
};

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

const subscriptionTypes = ref([]);
const selectedPlan = ref("");

const loadingPlans = ref(true);

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
    const response = await axios.get("http://localhost:8000/api/users/me/", {
      headers: { Authorization: `Token ${authStore.token || localStorage.getItem("token")}` },
    });

    user.value = response.data;
    user.value.es_autor = user.value.role === 'author';
    user.value.es_consumidor = user.value.role === 'consumer';

  } catch (err) {
    console.error("Error en la petición de usuario:", err);
    router.push("/login");
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
    const response = await axios.get("http://localhost:8000/api/users/notifications/", {
      headers: { Authorization: `Token ${token}` }
    });
    notifications.value = response.data;
  } catch (error) {
    console.error("Error al cargar notificaciones:", error);
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

const fetchPlans = async () => {
  try {
    const token = localStorage.getItem("token");
    const response = await axios.get("http://localhost:8000/api/subscriptions/plans/", {
      headers: { Authorization: `Token ${token}` }
    });

    subscriptionTypes.value = response.data;
  } catch (error) {
    console.error("Error al cargar planes:", error);
  } finally {
    loadingPlans.value = false;
  }
};

onMounted(() => {
  fetchPlans();
});

const handleFileChange = (event) => {
  selectedFile.value = event.target.files[0];
};

const handleResumeChange = (event) => {
  selectedResume.value = event.target.files[0];
};

const handleSubmit = async () => {
  if (!selectedFile.value) {
    triggerInformation("Por favor, selecciona el archivo principal de la obra.", "error");
    return;
  }

  loading.value = true;
  error.value = "";

  const formData = new FormData();
  formData.append("title", title.value);
  formData.append("description", description.value);
  formData.append("work_type", workType);
  formData.append("file_upload", selectedFile.value);
  formData.append("resume_upload", selectedFile.value);
  formData.append("license", selectedLicense.value);
  formData.append("plan_required", selectedPlan.value);
  if (selectedResume.value) {
    formData.append("resume_upload", selectedResume.value);
  }

  if (workType === 'book') {
    formData.append("pages", pages.value);
    formData.append("isbn", isbn.value);
    formData.append("genre", genre.value);
    formData.append("language", language.value);
  } else if (workType === 'music') {
    formData.append("duration", duration.value);
    formData.append("album", album.value);
    formData.append("genre", genre.value);
  } else if (workType === 'video') {
    formData.append("duration", duration.value);
    formData.append("genre", genre.value)
  } else if (workType === 'software') {
    formData.append("programming_language", programming_language.value);
    formData.append("repository_url", repository_url.value);
    formData.append("documentation_url", documentation_url.value);
  } else if (workType === 'paint' || workType === 'sculpture') {
    formData.append("height", height.value);
    formData.append("weight", weight.value);
    formData.append("type_detail", type_detail.value);
  }

  try {
    await axios.post("http://localhost:8000/api/works/", formData, {
      headers: {
        "Authorization": `Token ${authStore.token || localStorage.getItem("token")}`
      }
    });

    triggerInformation("¡Obra registrada y protegida con éxito!", "success");

    setTimeout(() => {
      router.push("/dashboard");
    }, 1200);

  } catch (err) {
    let errorMsg = "Error inesperado al procesar la subida.";

    if (err.response && err.response.data) {
      const data = err.response.data;

      if (data.error) {
        errorMsg = data.error;

      } else if (data.detail) {
        errorMsg = data.detail;

      } else if (typeof data === "string") {
        errorMsg = data;

      } else {
        const firstKey = Object.keys(data)[0];
        const fieldWithError = data[firstKey];

        if (Array.isArray(fieldWithError)) {
          errorMsg = fieldWithError[0];

        } else {
          errorMsg = fieldWithError;
        }
      }

    } else if (err.request) {
      errorMsg = "El servidor no responde. Asegúrate de que Django está corriendo.";

    } else if (err.message) {
      errorMsg = err.message;
    }

    error.value = errorMsg;
    triggerInformation(errorMsg, "error");

  } finally {
    loading.value = false;
  }
};

onMounted(() => {
  getUserData();
  getUserPoints();
});
</script>

<style scoped>
.btn-back-nav {
  color: white;
  text-decoration: none;
  font-size: 0.9em;
  border: 1px solid white;
  padding: 5px 10px;
  border-radius: 5px;
}

.form-container {
  background: #ffffff;
  padding: 35px 45px;
  border-radius: 18px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.04);
  width: 100%;
  max-width: 960px;
  margin: 30px auto;
  box-sizing: border-box;
}

h1 {
  color: var(--granate-principal);
  text-align: center;
  margin-bottom: 5px;
}

.subtitle {
  text-align: center;
  color: #666;
  margin-bottom: 30px;
  font-size: 0.9em;
}

.form-grid-top {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 25px;
  align-items: start;
}

.grid-4-cols {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}

.grid-3-cols {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
}

.grid-2-cols {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

.form-group {
  margin-bottom: 22px;
  display: flex;
  flex-direction: column;
}

.form-group-compact {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

label {
  font-size: 0.88rem;
  font-weight: 700;
  color: var(--granate-principal);
  margin-bottom: 6px;
  display: flex;
  align-items: center;
  gap: 6px;
}

.required {
  color: var(--rosa-fuerte);
  font-weight: bold;
}

.label-help-icon {
  font-size: 0.82rem;
  color: #999;
  cursor: pointer;
}

.field-desc-mini {
  font-size: 0.76rem;
  color: #888;
  margin-bottom: 6px;
}

input[type="text"],
input[type="number"],
input[type="url"],
select,
textarea {
  width: 100%;
  padding: 10px 14px;
  border: 1px solid #e5e5e5;
  border-radius: 8px;
  box-sizing: border-box;
  font-family: inherit;
  font-size: 0.88rem;
  background-color: #ffffff;
  color: #333;
  transition: border-color 0.2s, box-shadow 0.2s;
}

input:focus,
select:focus,
textarea:focus {
  outline: none;
  border-color: var(--rosa-fuerte);
  box-shadow: 0 0 0 3px rgba(209, 107, 134, 0.12);
  background-color: #ffffff;
}

textarea {
  resize: vertical;
}

.field-desc {
  font-size: 0.85em;
  color: #666;
  margin-top: -6px;
  margin-bottom: 10px;
}

.mini-loader {
  font-size: 0.75rem;
  color: #888;
  margin-top: 4px;
}

.form-card {
  background-color: #fff9fa;
  border: 1px solid #f6e2e6;
  border-radius: 12px;
  padding: 18px 22px;
  margin-bottom: 22px;
  box-sizing: border-box;
}

.card-section-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 14px;
  color: var(--granate-principal);
}

.card-section-header i {
  font-size: 1.15rem;
}

.card-section-header h3 {
  margin: 0;
  font-size: 0.95rem;
  font-weight: 700;
  color: var(--granate-principal);
}

.upload-card {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.upload-header {
  display: flex;
  align-items: center;
  gap: 8px;
}

.upload-icon {
  color: var(--granate-principal);
  font-size: 0.9rem;
}

.upload-content-row {
  display: flex;
  align-items: center;
  gap: 25px;
}

.custom-file-btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  background-color: #ffffff;
  border: 1px solid #e2c0ca;
  color: var(--granate-principal);
  padding: 8px 16px;
  border-radius: 8px;
  font-size: 0.82rem;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s;
  white-space: nowrap;
  max-width: 250px;
  overflow: hidden;
  text-overflow: ellipsis;
}

.custom-file-btn:hover {
  background-color: #fdeef2;
  border-color: var(--granate-principal);
}

.hidden-file-input {
  display: none;
}

.format-hint {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.hint-title {
  font-size: 0.74rem;
  font-weight: 700;
  color: #666;
}

.hint-desc {
  font-size: 0.74rem;
  color: #888;
}

.license-top-row {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 10px;
}

.cc-icon {
  font-size: 1.1rem;
  color: var(--granate-principal);
}

.license-preview-box {
  margin-top: 12px;
  padding: 10px 14px;
  background-color: #ffffff;
  border: 1px solid #f0d5dc;
  border-radius: 8px;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.preview-header {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 0.82rem;
  color: var(--granate-principal);
}

.preview-text {
  margin: 0;
  font-size: 0.78rem;
  color: #666;
}

.license-footnote {
  margin: 12px 0 0 0;
  font-size: 0.8rem;
  color: #777;
}

.license-select {
  width: 100%;
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 8px;
  background-color: white;
  font-family: inherit;
  outline: none;
}

.license-select:focus {
  border-color: var(--rosa-fuerte);
}

.license-card-info {
  margin-top: 14px;
  padding: 16px 20px;
  background-color: #fafbfc;
  border: 1px solid #f0e6e9;
  border-left: 4px solid var(--granate-principal);
  border-radius: 10px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.license-badge-name {
  font-weight: 800;
  font-size: 0.95rem;
  color: var(--granate-principal);
}

.license-summary {
  margin: 0;
  font-size: 0.88rem;
  color: #555;
  line-height: 1.45;
}

.license-rules-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 4px;
}

.rule-pill {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 0.75rem;
  font-weight: 700;
  padding: 4px 10px;
  border-radius: 12px;
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

.license-info {
  margin-top: 12px;
  font-size: 0.85rem;
  color: #666;
}

.btn-save {
  width: 100%;
  background: var(--granate-principal);
  color: #ffffff;
  padding: 13px;
  border: none;
  border-radius: 8px;
  font-size: 0.95rem;
  font-weight: 700;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  transition: background-color 0.2s, transform 0.1s;
  margin-top: 10px;
}

.btn-save:hover:not(:disabled) {
  background-color: var(--rosa-fuerte);
  transform: translateY(-2px);
}

.btn-save:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}

.error-msg {
  color: #d9534f;
  background: #f2dede;
  padding: 10px;
  border-radius: 5px;
  margin-bottom: 20px;
  text-align: center;
}

.back-link {
  display: block;
  text-align: center;
  margin-top: 18px;
  font-size: 0.85rem;
  font-weight: 600;
  color: #666;
  text-decoration: none;
}

.back-link:hover {
  color: var(--granate-principal);
  text-decoration: underline;
}

select.select-pink {
  background-color: #ffffff;
  border: 1px solid #ddd;
  color: #333333;
  font-weight: 500;
  cursor: pointer;
}

select.select-pink:focus {
  background-color: #ffffff;
  border-color: var(--rosa-fuerte);
  box-shadow: 0 0 0 3px rgba(219, 112, 147, 0.2);
}

select.select-pink option {
  background-color: var(--rosa-claro);
  color: var(--granate-principal);
  font-weight: 600;
}
</style>
<template>
  <div v-if="loading" class="loading-screen">
    <div class="spinner-wrapper">
      <div class="brand-spinner"></div>
      <div class="spinner-inner-dot"></div>
    </div>
    <p class="loading-label">Cargando detalles de la obra...</p>
  </div>

  <div v-else-if="obra">
    <nav class="navbar">
      <span><strong>Detalles de la obra</strong> | {{ authStore.user?.username }}</span>
      <button @click="handleLogout" class="btn-logout">Cerrar Sesión</button>
    </nav>

    <div class="container">
      <h1>{{ obra.title }}</h1>
      <span class="type-badge">{{ getWorkTypeName(obra.work_type) }}</span>

      <div class="info-section">
        <span class="label">Autor:</span>
        <span class="value">{{ obra.author_username || 'Desconocido' }}</span>
      </div>

      <div class="info-section">
        <span class="label">Fecha de Registro:</span>
        <span class="value">{{ formatDate(obra.created_at) }}</span>
      </div>

      <div v-if="isAuthor" class="edit-controls">
        <button v-if="!isEditing" @click="startEditing" class="btn-table">Editar Obra</button>
        <div v-else class="btn-group-edit">
          <button @click="saveChanges" class="btn-delete">Guardar Cambios</button>
          <button @click="cancelEditing" class="btn-table" style="background: #ccc;">Cancelar</button>
        </div>
      </div>

      <div class="info-section">
        <span class="label">Descripción:</span>
        <div v-if="isEditing">
          <textarea v-model="form.description" class="filter-input" style="height: 80px; resize: vertical;"></textarea>
        </div>
        <span v-else class="value">{{ obra.description || 'Sin descripción' }}</span>
      </div>

      <div class="info-section">
        <span class="label">Plan de suscripción requerido</span>
        <p v-if="isAuthor" class="field-desc">¿Qué plan deben tener los consumidores para acceder a esta obra?</p>
        <p v-else class="field-desc">¿Qué plan debes tener para acceder a esta obra?</p>

        <div v-if="isEditing">
          <select v-model="form.plan_required" class="filter-select">
            <option value="">Esta obra es gratuita (Sin plan)</option>
            <option v-for="plan in subscriptionTypes" :key="plan.id" :value="plan.id">
              {{ plan.name }} ({{ plan.price }}€)
            </option>
          </select>
        </div>

        <div v-else>
          <div v-if="obra.plan_required" class="value-box">
            <span class="plan-name">{{ obra.plan_required.name }}</span>
            <span class="plan-price"> — {{ obra.plan_required.points }} puntos</span>
          </div>
          <div v-else class="value-empty">Esta obra es gratuita.</div>
        </div>
      </div>

      <div class="technical-sheet" v-if="hasTechnicalData || isEditing">
        <h3>Ficha Técnica Específica</h3>

        <template v-if="obra.work_type === 'book'">
          <div class="form-group-inline">
            <p><strong>Páginas:</strong>
              <input v-if="isEditing" type="number" v-model="form.pages" class="filter-input-small" />
              <span v-else>{{ obra.pages }}</span>
            </p>
            <p><strong>ISBN:</strong>
              <input v-if="isEditing" type="text" v-model="form.isbn" class="filter-input-small" />
              <span v-else>{{ obra.isbn || '-' }}</span>
            </p>
          </div>
        </template>

        <template v-else-if="obra.work_type === 'music' || obra.work_type === 'video'">
          <p><strong>Duración (minutos): </strong>
            <input v-if="isEditing" type="number" v-model="form.duration" class="filter-input-small" />
            <span v-else>{{ obra.duration }}</span>
          </p>
        </template>

        <template v-else-if="obra.work_type === 'software'">
          <p><strong>Lenguaje:</strong>
            <input v-if="isEditing" type="text" v-model="form.programming_language" class="filter-input-small" />
            <span v-else>{{ obra.programming_language }}</span>
          </p>
          <p><strong>Repositorio:</strong>
            <input v-if="isEditing" type="text" v-model="form.repository_url" class="filter-input" />
            <span v-else-if="obra.repository_url">
              <a :href="obra.repository_url" target="_blank">{{ obra.repository_url }}</a>
            </span>
            <span v-else>-</span>
          </p>
        </template>

        <template v-else-if="obra.work_type === 'paint' || obra.work_type === 'sculpture'">
          <div class="form-group-inline">
            <p><strong>Altura (cm): </strong>
              <input v-if="isEditing" type="number" v-model="form.height" class="filter-input-small" />
              <span v-else>{{ obra.height }}</span>
            </p>
            <p><strong>Peso (kg): </strong>
              <input v-if="isEditing" type="number" v-model="form.weight" class="filter-input-small" />
              <span v-else>{{ obra.weight }}</span>
            </p>
          </div>
          <p><strong>Material/Técnica: </strong>
            <input v-if="isEditing" type="text" v-model="form.type_detail" class="filter-input" />
            <span v-else>{{ obra.type_detail }}</span>
          </p>
        </template>
      </div>

      <div v-if="obra.file_name || isEditing" class="file-box">
        <span class="label" style="margin-bottom: 10px;">Archivo Adjunto</span>

        <div v-if="isEditing" class="upload-edit-zone">
          <p class="field-desc">Opcional: Sube un archivo nuevo si deseas reemplazar el actual (recalculará la firma
            digital
            de autoría).</p>
          <input type="file" @change="handleFileChange" class="filter-input" />
        </div>

        <div v-else-if="canSeeProtectedContent">
          <img v-if="isImage(obra.file_type)" :src="getFileUrl(obra.id)" alt="Vista previa" class="preview-img">
          <a :href="getFileUrl(obra.id)" class="btn-action btn-download" download>
            Descargar Original ({{ obra.file_name }})
          </a>
        </div>
        <div v-else>
          <button @click="handleSubscribe" class="btn-logout">Suscribirse</button>
        </div>
      </div>

      <div class="license-container">
        <h3>Información de la Licencia</h3>

        <p class="license-name">
          <strong>{{ obra.license_label }}</strong>
        </p>

        <p class="license-description">
          <strong>¿Qué significa?</strong>
          {{ licenseMeanings[obra.license] || 'Información no disponible' }}
        </p>
      </div>

      <div class="crypto-security-box">
        <div class="crypto-header">
          <span class="crypto-badge">Registro con Firma RSA Garantizada</span>
          <p class="field-desc-mini">Esta obra está protegida mediante criptografía asimétrica de clave pública/privada.
          </p>
        </div>

        <div class="crypto-body">
          <div class="crypto-row">
            <span class="label-mini">Firma Electrónica de Autoría (RSA-2048)</span>
            <div class="signature-scroll-box">
              <code class="signature-code">{{ obra?.hash_security || 'No firmado' }}</code>
            </div>
            <p class="crypto-explanation">Garantiza el <strong>no repudio</strong>: este bloque certifica
              matemáticamente que
              fuiste tú, {{ obra.author_username }}, quien firmó este archivo usando tu clave privada.</p>
          </div>
        </div>
      </div>

      <router-link to="/works" class="btn-back-link">
        &larr; Volver al Listado
      </router-link>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from "vue";
import { useRoute, useRouter } from "vue-router";
import axios from "axios";
import { useAuthStore } from "../stores/auth";

const route = useRoute();
const router = useRouter();
const authStore = useAuthStore();

const obra = ref(null);
const loading = ref(true);
const subscriptionTypes = ref([]);
const activeSubscription = ref(null);

const licenseMeanings = {
  'none': 'Esta obra no tiene licencia',
  'by': 'Reconocimiento: Permite cualquier explotación de la obra, incluyendo finalidad comercial y creación de obras derivadas, siempre que se reconozca la autoría.',
  'by-sa': 'Reconocimiento-CompartirIgual: Permite uso comercial y obras derivadas, pero la distribución de estas debe hacerse con una licencia igual a la original.',
  'by-nd': 'Reconocimiento-SinObraDerivada: Permite el uso comercial de la obra pero no la generación de obras derivadas.',
  'by-nc': 'Reconocimiento-NoComercial: Permite la generación de obras derivadas siempre que no se haga un uso comercial de las mismas.',
  'by-nc-sa': 'Reconocimiento-NoComercial-CompartirIgual: No permite el uso comercial. Se permite crear obras derivadas siempre que se compartan con la misma licencia.',
  'by-nc-nd': 'Reconocimiento-NoComercial-SinObraDerivada: Es la licencia más restrictiva. No permite uso comercial ni obras derivadas. Solo lectura y descarga.',
};

const isAuthor = computed(() => {
  if (!authStore.user || !obra.value) return false;

  const userId = authStore.user.id || authStore.user.pk;
  const authorId = obra.value.author;

  return Number(userId) === Number(authorId);
});

const canSeeProtectedContent = computed(() => {
  if (!obra.value) return false;

  if (!authStore.user) return false;

  const isAdmin = authStore.user.role === 'admin';
  const isAuthor = Number(authStore.user.id) === Number(obra.value.author);

  const isFreeWork = !obra.value.plan_required;

  let isSubscribed = false;

  if (activeSubscription.value && obra.value.plan_required) {
    const planUserId = activeSubscription.value.plan;
    const planRequiredId = obra.value.plan_required.id;

    if (planUserId === planRequiredId) {
      isSubscribed = true;
    }
    else if (activeSubscription.value.plan_points >= obra.value.plan_required.points) {
      isSubscribed = true;
    }
  }

  return isAdmin || isAuthor || isFreeWork || isSubscribed;
});

const fetchWorkDetails = async () => {
  try {
    const id = route.params.id;
    const response = await axios.get(`http://localhost:8000/api/works/${id}/`, {
      headers: { Authorization: `Token ${authStore.token || localStorage.getItem('token')}` }
    });
    obra.value = response.data;

  } catch (err) {
    console.error("Error al cargar la obra:", err);
    router.push("/works");
  } finally {
    loading.value = false;
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

const getWorkTypeName = (type) => {
  const types = { book: 'Libro', music: 'Música', video: 'Video', software: 'Software', paint: 'Pintura', sculpture: 'Escultura' };
  return types[type] || 'Obra';
};

const formatDate = (dateString) => {
  if (!dateString) return '';
  return new Date(dateString).toLocaleDateString('es-ES', {
    day: '2-digit', month: 'long', year: 'numeric'
  });
};

const getFileUrl = (id) => `http://localhost:8000/api/works/${id}/file/`;
const isImage = (type) => type && type.startsWith('image/');
const hasTechnicalData = computed(() => {
  return obra.value && obra.value.work_type;
});

onMounted(async () => {
  loading.value = true;

  authStore.loadToken();

  if (authStore.token) {
    await authStore.fetchUserProfile();
  } else {
    console.warn("No hay token, el usuario debe iniciar sesión.");
  }

  await fetchWorkDetails();
  await fetchSubscriptionPlan()
  await fetchMySubscription();

  loading.value = false;
});

const handleSubscribe = () => {
  router.push("/subscription/plans");
};

const handleLogout = () => {
  authStore.logout();
  router.push("/login");
};

const isEditing = ref(false);
const form = ref({});
const newFile = ref(null);

const startEditing = () => {
  newFile.value = null;
  form.value = {
    title: obra.value.title,
    description: obra.value.description,
    plan_required: obra.value.plan_required ? obra.value.plan_required.id : "",
    pages: obra.value.pages,
    isbn: obra.value.isbn,
    duration: obra.value.duration,
    programming_language: obra.value.programming_language,
    repository_url: obra.value.repository_url,
    height: obra.value.height,
    weight: obra.value.weight,
    type_detail: obra.value.type_detail,
    work_type: obra.value.work_type
  };
  isEditing.value = true;
};

const cancelEditing = () => {
  isEditing.value = false;
};

const handleFileChange = (event) => {
  newFile.value = event.target.files[0];
};

const saveChanges = async () => {
  try {
    const token = localStorage.getItem("token") || authStore.token;

    const formData = new FormData();

    formData.append("title", form.value.title || "");
    formData.append("description", form.value.description || "");
    formData.append("plan_required", form.value.plan_required || "");
    formData.append("work_type", form.value.work_type);

    if (obra.value.work_type === 'book') {
      formData.append("pages", form.value.pages || "");
      formData.append("isbn", form.value.isbn || "");
    } else if (['music', 'video'].includes(obra.value.work_type)) {
      formData.append("duration", form.value.duration || "");
    } else if (obra.value.work_type === 'software') {
      formData.append("programming_language", form.value.programming_language || "");
      formData.append("repository_url", form.value.repository_url || "");
    } else if (['paint', 'sculpture'].includes(obra.value.work_type)) {
      formData.append("height", form.value.height || "");
      formData.append("weight", form.value.weight || "");
      formData.append("type_detail", form.value.type_detail || "");
    }

    if (newFile.value) {
      formData.append("file_upload", newFile.value);
    }

    const response = await axios.patch(
      `http://localhost:8000/api/works/${obra.value.id}/`,
      formData,
      {
        headers: {
          Authorization: `Token ${token}`,
          "Content-Type": "multipart/form-data"
        }
      }
    );

    obra.value = response.data;
    isEditing.value = false;
    alert("Obra actualizada con éxito");

  } catch (error) {
    console.error("Error al actualizar la obra:", error);
    alert("Ocurrió un error al guardar los cambios.");
  }
};

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
  max-width: 700px;
  margin: auto;
}

h1 {
  color: var(--granate-principal);
  text-align: center;
  margin-bottom: 5px;
}

.type-badge {
  display: block;
  text-align: center;
  color: var(--rosa-fuerte);
  font-weight: bold;
  text-transform: uppercase;
  margin-bottom: 30px;
  font-size: 0.9em;
}

.info-section {
  margin-bottom: 25px;
  border-bottom: 1px solid var(--rosa-claro);
  padding-bottom: 15px;
}

.label {
  display: block;
  font-weight: bold;
  color: var(--granate-principal);
  font-size: 0.85em;
}

.value {
  display: block;
  color: #333;
  margin-top: 5px;
  font-size: 1.05em;
}

.technical-sheet {
  background-color: var(--rosa-claro);
  padding: 20px;
  border-radius: 10px;
  border-left: 5px solid var(--granate-principal);
  margin: 25px 0;
}

.technical-sheet h3 {
  margin: 0 0 10px 0;
  color: var(--granate-principal);
  font-size: 1em;
}

.technical-sheet p {
  margin: 5px 0;
  font-size: 0.95em;
}

.file-box {
  background: white;
  border: 2px dashed var(--rosa-fuerte);
  padding: 20px;
  text-align: center;
  border-radius: 10px;
  margin-top: 30px;
}

.preview-img {
  max-width: 100%;
  border-radius: 8px;
  margin-bottom: 15px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
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

.btn-hash {
  background: var(--rosa-fuerte);
  color: white;
}

.btn-hash:hover {
  background: var(--granate-principal);
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

.loading {
  text-align: center;
  margin-top: 100px;
  color: var(--granate-principal);
  font-weight: bold;
}

.license-container {
  background-color: #f9f9f9;
  border-left: 5px solid var(--granate-principal);
  padding: 20px;
  margin-top: 20px;
  border-radius: 8px;
}

.license-name {
  font-size: 1.2em;
  color: var(--granate-principal);
  margin-bottom: 10px;
}

.license-description {
  line-height: 1.5;
  color: #444;
  font-style: italic;
}

.btn-logout {
  background: var(--rosa-claro);
  color: var(--granate-principal);
  border: none;
  padding: 8px 15px;
  border-radius: 5px;
  cursor: pointer;
  font-weight: bold;
}

.btn-logout:hover {
  background-color: var(--rosa-fuerte);
  transform: translateY(-2px);
}

.hash-section-container {
  margin: 25px 0;
  text-align: left;
  width: 100%;
}

.label-mini {
  display: block;
  font-size: 0.8em;
  color: var(--granate-principal);
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 8px;
}

.hash-block {
  background-color: #fffafc;
  border: 1px solid var(--rosa-claro);
  border-left: 4px solid var(--granate-principal);
  padding: 12px 16px;
  border-radius: 6px;
  display: flex;
  align-items: center;
}

.hash-code {
  font-family: 'Courier New', Courier, monospace;
  font-size: 0.95em;
  font-weight: bold;
  color: #333;
  word-break: break-all;
  line-height: 1.4;
}

.edit-controls {
  display: flex;
  justify-content: flex-end;
  margin-bottom: 20px;
}

.btn-group-edit {
  display: flex;
  gap: 10px;
}

.form-group-inline {
  display: flex;
  gap: 20px;
}

.filter-input-small {
  width: 90px;
  height: 32px;
  padding: 0 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-family: inherit;
  font-size: 0.9em;
  outline: none;
}

.filter-input-small:focus {
  border-color: var(--granate-principal);
}

.upload-edit-zone {
  background: #fdf6f8;
  padding: 12px;
  border-radius: 6px;
  border: 1px dashed var(--rosa-fuerte);
  margin-top: 5px;
}

.crypto-security-box {
  background-color: #f4faf7;
  border: 1px solid #d1e7dd;
  border-left: 5px solid #0f5132;
  padding: 25px;
  border-radius: 12px;
  margin: 30px 0;
}

.crypto-badge {
  display: inline-block;
  background-color: #0f5132;
  color: white;
  font-size: 0.85em;
  font-weight: bold;
  padding: 6px 12px;
  border-radius: 20px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.field-desc-mini {
  font-size: 0.85em;
  color: #41464b;
  margin-top: 6px;
  margin-bottom: 15px;
}

.crypto-row {
  margin-top: 15px;
}

.signature-scroll-box {
  background-color: white;
  padding: 12px;
  border-radius: 6px;
  max-height: 80px;
  overflow-y: auto;
  margin: 6px 0;
}

.signature-code {
  font-family: 'Courier New', Courier, monospace;
  font-size: 0.8em;
  color: #0dcaf0;
  word-break: break-all;
  white-space: pre-wrap;
}

.crypto-explanation {
  font-size: 0.8em;
  color: #6c757d;
  font-style: italic;
  margin: 4px 0 0 0;
}
</style>
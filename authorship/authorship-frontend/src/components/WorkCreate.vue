<template>


  <div class="form-container">
    <h1>Registrar {{ workTypeName }}</h1>
    <p class="subtitle">Sube tu archivo para protegerlo</p>

    <form @submit.prevent="handleSubmit" enctype="multipart/form-data">
      <div class="form-group">
        <label for="title">Título de la Obra</label>
        <input type="text" id="title" v-model="title" placeholder="Ej: Mi gran novela" required>
      </div>

      <div class="form-group">
        <label for="description">Descripción / Resumen</label>
        <textarea id="description" v-model="description" rows="4"
          placeholder="Describe brevemente tu creación..."></textarea>
      </div>

      <div class="form-group">
        <label>Plan de suscripción requerido</label>
        <p class="field-desc">¿Qué plan debe tener el usuario para acceder a esta obra?</p>
        <select v-model="selectedPlan" class="custom-select">
          <option value="">Gratis (Público para todos)</option>
          <option v-for="plan in subscriptionTypes" :key="plan.id" :value="plan.id">
            {{ plan.name }} ({{ plan.points }} puntos)
          </option>
        </select>

        <div v-if="loadingPlans" class="mini-loader">Cargando planes disponibles...</div>
      </div>

      <div v-if="workType === 'book'">
        <div class="form-group">
          <label>Número de Páginas</label>
          <input type="number" v-model="pages" required>
        </div>
        <div class="form-group">
          <label>ISBN</label>
          <input type="text" v-model="isbn" required>
        </div>
        <div class="form-group">
          <label>Género</label>
          <input type="text" v-model="genre" required>
        </div>
        <div class="form-group">
          <label>Idioma</label>
          <input type="text" v-model="language" required>
        </div>
      </div>

      <div v-if="workType === 'music'">
        <div class="form-group">
          <label>Duración (minutos)</label>
          <input type="number" step="0.01" v-model="duration" required>
        </div>
        <div class="form-group">
          <label>Album</label>
          <input type="text" v-model="album" required>
        </div>
        <div class="form-group">
          <label>Género</label>
          <input type="text" v-model="genre" required>
        </div>
      </div>

      <div v-if="workType === 'video'">
        <div class="form-group">
          <label>Duración (minutos)</label>
          <input type="number" step="0.01" v-model="duration" required>
        </div>
        <div class="form-group">
          <label>Género</label>
          <input type="text" v-model="genre" required>
        </div>
      </div>

      <div v-if="workType === 'software'">
        <div class="form-group">
          <label>Lenguaje de Programación</label>
          <input type="text" v-model="programming_language" required>
        </div>
        <div class="form-group">
          <label>URL del Repositorio</label>
          <input type="url" v-model="repository_url">
        </div>
        <div class="form-group">
          <label>URL de la documentación</label>
          <input type="url" v-model="documentation_url">
        </div>
      </div>

      <div v-if="workType === 'paint' || workType === 'sculpture'">
        <div class="form-group">
          <label>Altura</label>
          <input type="number" step="0.1" v-model="height" required>
        </div>
        <div class="form-group">
          <label>Peso</label>
          <input type="number" step="0.1" v-model="weight" required>
        </div>
        <div class="form-group">
          <label>Material / Técnica</label>
          <select v-model="type_detail" required>
            <option v-if="workType === 'paint'" value="oil">Óleo</option>
            <option v-if="workType === 'paint'" value="digital">Acrílico</option>
            <option v-if="workType === 'paint'" value="oil">Acuarela</option>
            <option v-if="workType === 'paint'" value="digital">Digital</option>
            <option v-if="workType === 'sculpture'" value="marble">Mármol</option>
            <option v-if="workType === 'sculpture'" value="bronze">Bronce</option>
            <option v-if="workType === 'sculpture'" value="marble">Madera</option>
            <option v-if="workType === 'sculpture'" value="bronze">Arcilla</option>
          </select>
        </div>
      </div>

      <div class="form-group file-upload-section">
        <label for="file">Archivo de la Obra</label>
        <div class="file-input-wrapper">
          <input type="file" id="file" @change="handleFileChange"
            accept=".pdf, .txt, .jpg, .jpeg, .png, .webp, .mp3, .wav, .ogg, .mp4, .avi, .mov, .zip, .py, .js, .ts, .jsx, .tsx, .vue, .html, .css, .java, .c, .cpp, .cs, .php, .rb, .go, .rs, .swift, .kt, .sql, .sh, .ipynb, .json, .xml, .yaml, .yml"
            required>
          <p class="file-help">
            <strong>Formatos permitidos:</strong> Documentos, Imágenes, Audio, Vídeo, Código fuente y ZIP.
          </p>
        </div>
        <label for="file">Resumen de la Obra</label>
        <div class="file-input-wrapper">
          <input type="file" id="file" @change="handleResumeChange"
            accept=".pdf, .txt, .jpg, .jpeg, .png, .webp, .mp3, .wav, .ogg, .mp4, .avi, .mov, .zip, .py, .js, .ts, .jsx, .tsx, .vue, .html, .css, .java, .c, .cpp, .cs, .php, .rb, .go, .rs, .swift, .kt, .sql, .sh, .ipynb, .json, .xml, .yaml, .yml"
            required>
          <p class="file-help">
            <strong>Formatos permitidos:</strong> Documentos, Imágenes, Audio, Vídeo, Código fuente y ZIP.
          </p>
        </div>
      </div>

      <div class="form-group license-selector">
        <label>Licencia Creative Commons</label>
        <select v-model="selectedLicense" class="license-select">
          <option v-for="lic in licenses" :key="lic.id" :value="lic.id">
            {{ lic.name }}
          </option>
        </select>

        <div v-if="licenseMeanings[selectedLicense]" class="license-card-info">
          <div class="license-card-header">
            <span class="license-badge-name">{{ licenseMeanings[selectedLicense].name }}</span>
          </div>

          <p class="license-summary">
            {{ licenseMeanings[selectedLicense].summary }}
          </p>

          <div v-if="selectedLicense !== 'none'" class="license-rules-grid">
            <span v-if="licenseMeanings[work.license].commercial" class="rule-pill rule-allow">
                <i class="fa-solid fa-check"></i>
                Uso comercial
              </span>
              <span v-else class="rule-pill rule-deny">
                <i class="fa-solid fa-xmark"></i>
                Sin fines comerciales
              </span>

              <span v-if="licenseMeanings[work.license].derivatives" class="rule-pill rule-allow">
                <i class="fa-solid fa-check"></i>
                Permite adaptaciones
              </span>
              <span v-else class="rule-pill rule-deny">
                <i class="fa-solid fa-xmark"></i>
                No permite adaptaciones
              </span>

              <span v-if="licenseMeanings[work.license].sameLicense" class="rule-pill rule-allow">
                <i class="fa-solid fa-check"></i>
                Exige que cualquier adaptación se distribuya bajo la misma licencia
              </span>
              <span v-else class="rule-pill rule-deny">
                <i class="fa-solid fa-xmark"></i>
                No exige que cualquier adaptación se distribuya bajo la misma licencia
              </span>
          </div>
        </div>

        <p class="license-info">
          Tu obra será protegida bajo: <strong>{{ selectedLicenseName }}</strong>
        </p>
      </div>

      <div v-if="error" class="error-msg">{{ error }}</div>

      <button type="submit" class="btn-save">Guardar y proteger obra</button>

      <router-link to="/dashboard" class="back-link">&larr; Cancelar y volver</router-link>
    </form>
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
    console.error("Error detectado en la subida:", error);

    if (err.response) {
      console.log("Datos del error recibidos de Django:", err.response.data);
      let errorMsg = "Error inesperado al procesar la subida.";

      if (err.response.data && err.response.data.error) {
        error.value = err.response.data.error;
      }
      else if (err.response.data && err.response.data.detail) {
        error.value = err.response.data.detail;
      }

      else if (typeof err.response.data === 'string') {
        error.value = err.response.data;
      }

      else {
        error.value = "Error de validación en los datos del formulario.";
      }

    } else if (err.request) {
      error.value = "El servidor no responde. Asegúrate de que Django está corriendo.";

    } else {
      error.value = err.message || "Error inesperado al procesar la subida.";
    }

    error.value = errorMsg;
    triggerInformation(errorMsg, "error");

  } finally {
    loading.value = false;
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

.btn-back-nav {
  color: white;
  text-decoration: none;
  font-size: 0.9em;
  border: 1px solid white;
  padding: 5px 10px;
  border-radius: 5px;
}

.form-container {
  background: white;
  padding: 40px;
  border-radius: 15px;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
  width: 100%;
  max-width: 850px;
  margin: 20px auto;
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

.form-group {
  margin-bottom: 35px;
}

label {
  display: block;
  font-weight: bold;
  color: var(--granate-principal);
  margin-bottom: 12px;
}

input[type="text"],
input[type="number"],
input[type="url"],
select,
textarea {
  width: 100%;
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 8px;
  box-sizing: border-box;
  font-family: inherit;
  background-color: white;
}

input:focus,
select:focus,
textarea:focus {
  outline: none;
  border-color: var(--rosa-fuerte);
  background: var(--rosa-claro);
}

.field-desc {
  font-size: 0.85em;
  color: #666;
  margin-top: -6px;
  margin-bottom: 10px;
}

.mini-loader {
  font-size: 0.8em;
  color: #888;
  margin-top: 6px;
}

.file-upload-section {
  background: #fafafa;
  padding: 20px;
  border-radius: 10px;
  border: 2px dashed #ddd;
}

.file-help {
  font-size: 0.8em;
  color: #888;
  margin-top: 10px;
  margin-bottom: 18px;
}

.file-input-wrapper {
  margin-bottom: 15px;
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
  color: white;
  padding: 14px;
  border: none;
  border-radius: 8px;
  font-weight: bold;
  cursor: pointer;
  transition: 0.3s;
  font-size: 1.1em;
}

.btn-save:hover {
  background: var(--rosa-fuerte);
  transform: translateY(-2px);
}

.btn-save:disabled {
  background: #ccc;
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
  margin-top: 20px;
  color: #666;
  text-decoration: none;
}
</style>
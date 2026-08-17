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
        <button @click="handleLogout" class="btn-logout">Cerrar Sesión</button>
      </div>
    </nav>

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

        <div v-if="isAuthor">
          <h1>Mis Obras Registradas</h1>
        </div>

        <div v-else-if="isConsumer">
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
          </div>
        </div>

        <table v-if="sortedWorks.length > 0">
          <thead>
            <tr>
              <th>Tipo</th>
              <th>Título de la Obra</th>
              <th v-if="isConsumer">Recomendación</th>
              <th v-else>Fecha</th>
              <th style="text-align: center;">Detalles</th>
              <th v-if="isAuthor">Eliminar Obra</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="work in sortedWorks" :key="work.id">
              <td>
                <span class="label-tipo">{{ getWorkTypeName(work.work_type) }}</span>
              </td>
              <td>
                <span class="work-title">{{ work.title }}</span>
              </td>

              <td v-if="isAuthor">
                <span style="color: #555;">{{ formatDate(work.created_at) }}</span>
              </td>
              <td v-else>
                <span v-if="isInteresting(work.work_type)" class="badge-interes">⭐ Sugerido</span>
                <span v-else class="badge-neutral">-</span>
              </td>

              <td style="text-align: center;">
                <router-link v-if="isAuthor" :to="`/worksAuthor/${work.id}`" class="btn-table">
                  <span>Ver Detalles</span>
                </router-link>
                <router-link v-else :to="`/works/${work.id}`" class="btn-table">
                  <span>Consultar</span>
                </router-link>
              </td>

              <td v-if="isAuthor" style="text-align: center;">
                <button @click="deleteWork(work.id)" class="btn-delete">Eliminar</button>
              </td>
            </tr>
          </tbody>
        </table>

        <div v-else class="empty-msg">
          <p v-if="isAuthor">Aún no has registrado ninguna obra en la plataforma.</p>
          <p v-else>No hay obras disponibles que coincidan con tus criterios.</p>
          <router-link v-if="isAuthor" to="/dashboard" class="btn-table" style="margin-top: 15px;">
            Ir al panel para registrar una obra
          </router-link>
        </div>
      </div>

      <div v-else-if="searchMode === 'authors'">
        <h1>Directorio de Autores</h1>

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
              <router-link :to="`/authors/${authorItem.id}`" class="btn-table" style="width: 100%;">
                Ver Perfil y Suscribirse
              </router-link>
            </div>

          </div>
        </div>

        <div v-else class="empty-msg">
          <p>No se han encontrado autores que coincidan con la búsqueda.</p>
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
const route = useRoute();
const router = useRouter();

const works = ref([]);
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
  appliedSearch.value = searchQuery.value;
  appliedTypes.value = [...selectedTypes.value];
  appliedPlans.value = [...selectedPlans.value];

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
    const cumpleNombre = !appliedSearch.value || work.title.toLowerCase().includes(appliedSearch.value.toLowerCase());

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

    if (aInteresting && !bInteresting) {
      return -1;
    }
    if (!aInteresting && bInteresting) {
      return 1;
    }
    return a.title.localeCompare(b.title);
  });
});

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

const fetchAuthors = async () => {
  try {
    const token = authStore.token || localStorage.getItem("token");
    const response = await axios.get("http://localhost:8000/api/users/authors/", {
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

const fetchWorks = async () => {
  try {
    const token = authStore.token || localStorage.getItem("token");
    const userResponse = await axios.get("http://localhost:8000/api/users/me/", {
      headers: { Authorization: `Token ${token}` }
    });
    user.value = userResponse.data;

    const response = await axios.get("http://localhost:8000/api/works/", {
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

const formatDate = (dateString) => {
  if (!dateString) return "";
  const date = new Date(dateString);
  return date.toLocaleDateString("es-ES");
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


const deleteWork = async (id) => {
  if (!confirm("¿Estás seguro de que deseas eliminar esta obra de forma permanente?")) {
    return;
  }

  try {
    const token = authStore.token || localStorage.getItem("token");
    const response = await axios.delete(`http://localhost:8000/api/works/${id}/`, {
      headers: { Authorization: `Token ${token}` }
    });

    works.value = works.value.filter(work => work.id !== id);

    alert("Obra eliminada correctamente.");

  } catch (err) {
    console.error("Error al eliminar la obra:", err);
  } finally {
    loading.value = false;
  }
};

const handleLogout = () => {
  authStore.logout();
  router.push("/login");
};

onMounted(() => {
  fetchPlans();
  fetchWorks();
  getUserPoints();
  fetchAuthors();
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

h1 {
  color: var(--granate-principal);
  text-align: center;
  margin-bottom: 30px;
}

table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 10px;
}

thead {
  border-bottom: 2px solid var(--granate-principal);
}

th {
  text-align: left;
  padding: 12px;
  color: var(--granate-principal);
  font-size: 0.9em;
  text-transform: uppercase;
  letter-spacing: 1px;
}

td {
  padding: 15px 12px;
  border-bottom: 1px solid var(--rosa-claro);
  vertical-align: middle;
}

tr:hover {
  background-color: #fffafc;
}

.label-tipo {
  color: var(--rosa-fuerte);
  font-weight: bold;
  font-size: 0.85em;
  text-transform: uppercase;
}

.work-title {
  color: black;
  font-weight: bold;
  font-size: 1.05em;
  display: block;
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

.btn-delete {
  display: inline-block;
  background: var(--granate-principal);
  color: white;
  padding: 8px 15px;
  border-radius: 8px;
  text-align: center;
  font-weight: bold;
  text-decoration: none;
  font-size: 0.85em;
  transition: 0.3s;
  border: 1px solid transparent;
}

.btn-delete:hover {
  background: var(--rosa-fuerte);
  color: white;
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

.badge-interes {
  background: var(--rosa-claro);
  color: var(--granate-principal);
  padding: 4px 10px;
  border-radius: 15px;
  font-size: 0.75em;
  font-weight: bold;
}

.badge-neutral {
  color: #ccc;
  font-size: 0.8em;
}

.er {
  display: flex;
  gap: 15px;
  margin-bottom: 25px;
  background-color: #fffafc;
  padding: 15px;
  border-radius: 10px;
  border: 1px solid var(--rosa-claro);
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

.dropdown-relative {
  position: relative;
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

.filter-dropdown-btn {
  width: 100%;
  height: 40px;
  padding: 0 12px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 0.9em;
  font-family: inherit;
  background-color: white;
  text-align: left;
  display: flex;
  justify-content: space-between;
  align-items: center;
  cursor: pointer;
}

.arrow-icon {
  font-size: 0.7em;
  color: #888;
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
  font-size: 0.9em;
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
  padding: 0 25px;
  border-radius: 6px;
  font-weight: bold;
  cursor: pointer;
  font-size: 0.9em;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.btn-search-submit:hover {
  background: var(--rosa-fuerte);
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
  box-sizing: border-box;
}

.pill-btn {
  border: none;
  outline: none;
  background: transparent;
  color: #666;
  font-weight: 600;
  font-size: 0.88em;
  border-radius: 25px;
  cursor: pointer;
  transition: all 0.25s ease-in-out;
  padding: 8px 20px;
  display: flex;
  align-items: center;
  gap: 8px;
  font-family: inherit;
  -webkit-appearance: none;
  -moz-appearance: none;
  appearance: none;
}

.pill-btn:hover {
  color: var(--granate-principal);
}

.pill-btn.active {
  background-color: #ffffff;
  color: var(--granate-principal);
  font-weight: 800;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
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
</style>
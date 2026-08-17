<template>
  <div v-if="loading" class="loading-screen">
    <div class="spinner"></div>
    <p>Cargando panel...</p>
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
        <span class="points"><i class="fa-solid fa-wallet"></i>{{ userPoints }} Puntos</span>
        <button @click="handleLogout" class="btn-logout">Cerrar Sesión</button>
      </div>
    </nav>

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
                  <template v-if="user.role === 'author'">Autor</template>
                  <template v-else>Consumidor</template>
                </span>
              </template>

              <template v-else>
                <div class="edit-group">
                  <label class="label-mini">Nombre de Usuario</label>
                  <input v-model="editForm.username" class="edit-input" placeholder="Usuario">

                  <label class="label-mini">Nombre</label>
                  <input v-model="editForm.first_name" class="edit-input" placeholder="Nombre">
                  <label class="label-mini">Apellidos</label>
                  <input v-model="editForm.last_name" class="edit-input" placeholder="Apellido">
                </div>
              </template>
            </div>

            <hr class="linea-granate">

            <div class="profile-body">
              <div v-if="!isEditing">
                <div v-if="user.es_autor && user.biography" class="info-group">
                  <label>Biografía Profesional:</label>
                  <p>{{ user.biography }}</p>
                </div>

                <div v-if="user.es_consumidor" class="info-group">
                  <label class="label-mini">Intereses</label>
                  <div class="interests-pills-container">
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
                <div v-if="user.es_autor && user.biography" class="info-group">
                  <label class="label-mini">Biografía</label>
                  <textarea v-model="editForm.biography" class="edit-textarea"></textarea>
                </div>

                <div v-else-if="user.es_consumidor" class="info-group">
                  <label class="label-mini">Mis Intereses</label>

                  <div class="interests-grid">
                    <div v-for="work in workTypes" :key="work.id" class="checkbox-item">
                      <label class="checkbox-wrapper">
                        <input type="checkbox" :value="work.id" v-model="editForm.interests" class="custom-check">
                        <span class="check-label">{{ work.label }}</span>
                      </label>
                    </div>
                  </div>
                </div>

                <small class="info-help">Selecciona lo que quieres descubrir.</small>
              </div>
            </div>

            <hr class="linea-granate">

            <div class="info-group">
              <label>Correo Electrónico:</label>
              <p v-if="!isEditing">{{ user.email }}</p>
              <input v-else v-model="editForm.email" class="edit-input">
            </div>

            <div class="profile-actions">
              <button v-if="!isEditing" @click="startEditing" class="btn-outline-edit">
                Editar Perfil
              </button>

              <div v-else class="edit-buttons">
                <button @click="modifyProfile" class="btn-save-small">Guardar Cambios</button>
                <button @click="isEditing = false" class="btn-cancel-small">Cancelar</button>
              </div>
            </div>
          </div>
        </aside>

        <main class="main-content">
          <header class="content-header">

            <h1>
              <template v-if="user.role === 'author'">Panel de Control de Autor</template>
              <template v-else>Catálogo de Obras</template>
            </h1>
            <template v-if="user.role === 'author'">Gestiona tus creaciones y protege tu propiedad
              intelectual.</template>
          </header>

          <section v-if="user.es_autor" class="action-section">
            <label class="section-label">Registrar nueva obra</label>
            <div class="grid-acciones">
              <router-link :to="{ path: '/works/create', query: { type: 'book' } }" class="card-accion">
                <span>REGISTRAR LIBRO</span>
              </router-link>
              <router-link :to="{ path: '/works/create', query: { type: 'music' } }" class="card-accion">
                <span>REGISTRAR MÚSICA</span>
              </router-link>
              <router-link :to="{ path: '/works/create', query: { type: 'video' } }" class="card-accion">
                <span>REGISTRAR VÍDEO</span>
              </router-link>
              <router-link :to="{ path: '/works/create', query: { type: 'software' } }" class="card-accion">
                <span>REGISTRAR SOFTWARE</span>
              </router-link>
              <router-link :to="{ path: '/works/create', query: { type: 'paint' } }" class="card-accion">
                <span>REGISTRAR PINTURA</span>
              </router-link>
              <router-link :to="{ path: '/works/create', query: { type: 'sculpture' } }" class="card-accion">
                <span>REGISTRAR ESCULTURA</span>
              </router-link>
            </div>
          </section>

          <div class="footer-card">
            <label class="section-label">
              <template v-if="user.es_author">Tu catálogo de obras</template>
              <template v-else>Catálogo de obras</template>
            </label>

            <p v-if="user.es_author">
              Accede a la lista completa de tus obras registradas y descarga sus certificados.
            </p>
            <p v-else>
              Explora todas las creaciones disponibles y protegidas en la plataforma.
            </p>

            <div v-if="user.es_consumidor" class="recommended-container">
              <h3 class="recommended-title"><i class="fa-solid fa-star"></i> Obras Recomendadas para ti</h3>

              <table v-if="recommendedWorks.length > 0" class="recommended-table">
                <thead>
                  <tr>
                    <th>Tipo</th>
                    <th>Título de la Obra</th>
                    <th style="text-align: center;">Detalles</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="work in recommendedWorks" :key="work.id">
                    <td>
                      <span class="label-tipo">{{ getWorkTypeName(work.work_type) }}</span>
                    </td>
                    <td>
                      <span class="work-title-sm">{{ work.title }}</span>
                    </td>
                    <td style="text-align: center;">
                      <router-link :to="`/works/${work.id}`" class="btn-table-sm">
                        Consultar
                      </router-link>
                    </td>
                  </tr>
                </tbody>
              </table>

              <p v-else class="no-recommendations-msg">
                No hay obras disponibles que coincidan con tus intereses seleccionados.
              </p>
            </div>

            <router-link to="/works" class="btn-primary-save">
              <template v-if="user.es_consumidor">Explorar Catálogo</template>
              <template v-else>Ver Catálogo Completo</template>
              &rarr;
            </router-link>
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

const works = ref([]);
const error = ref("");
const loading = ref(true);
const isEditing = ref(false);
const editForm = ref({});
const userPoints = ref(0);

const workTypes = [
  { id: 'libro', label: 'Libros' },
  { id: 'music', label: 'Música' },
  { id: 'video', label: 'Vídeos' },
  { id: 'software', label: 'Software' },
  { id: 'paint', label: 'Pintura' },
  { id: 'sculpture', label: 'Escultura' }
];

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

const recommendedWorks = computed(() => {
  if (!user.value.es_consumidor) return [];
  return works.value.filter(work => {
    let typeNormalizado = work.work_type;
    if (typeNormalizado === 'book') {
      typeNormalizado = 'libro';
    }

    return userInterestsArray.value.includes(typeNormalizado);
  });
});

const getInterestLabel = (id) => {
  const found = workTypes.find(type => type.id === id);

  if (found) {
    return found.label;
  } else {
    return id;
  }
};

const getWorkTypeName = (type) => {
  const types = {
    libro: 'Libro', book: 'Libro',
    music: 'Música', video: 'Video',
    software: 'Software', paint: 'Pintura',
    sculpture: 'Escultura'
  };
  return types[type] || 'Obra';
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

    if (user.value.es_consumidor) {
      const worksResponse = await axios.get("http://localhost:8000/api/works/", {
        headers: {
          Authorization: `Token ${authStore.token || localStorage.getItem("token")}`,
        },
      });

      works.value = worksResponse.data;
    }

  } catch (err) {
    console.error("Error en la petición:", err);
    error.value = "Sesión inválida";
    router.push("/login");
  } finally {
    loading.value = false;
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

const modifyProfile = async () => {
  try {
    loading.value = true;
    const token = authStore.token || localStorage.getItem("token");

    const payload = { ...editForm.value };

    if (!payload.username || !payload.first_name || !payload.last_name) {
      alert("Nombre, Apellidos y Usuario son obligatorios.");
      loading.value = false;
      return;
    }

    if (user.value.es_consumidor && Array.isArray(payload.interests)) {
      payload.interests = payload.interests.join(',');
    }

    const response = await axios.patch("http://localhost:8000/api/users/me/", payload, {
      headers: {
        Authorization: `Token ${token}`,
      }
    });

    user.value = response.data;
    user.value.es_autor = user.value.role === 'author';
    user.value.es_consumidor = user.value.role === 'consumer';

    isEditing.value = false;

    alert("Perfil actualizado correctamente");

  } catch (err) {
    console.error(err);
    alert("Error al actualizar el perfil");

  } finally {
    loading.value = false;
  }

};

const handleLogout = async () => {
  try {
    await axios.post("http://localhost:8000/api/users/", {}, {
      headers: { Authorization: `Token ${authStore.token || localStorage.getItem("token")}` },
    });

    authStore.setToken(null);
    localStorage.removeItem("token");
    router.push("/login");
  } catch (err) {
    console.error("Error al cerrar sesión:", err);
    authStore.setToken(null);
    localStorage.removeItem("token");
    router.push("/login");
  }
};

onMounted(() => {
  getUserData();
  getUserPoints();
});
</script>

<style scoped>
.dashboard-layout {
  display: flex;
  justify-content: center;
  align-items: flex-start;
  max-width: 1200px;
  margin: 40px auto;
  padding: 0 20px;
  gap: 40px;
}

.profile-card {
  background: white;
  border-radius: 15px;
  padding: 30px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.05);
  text-align: center;
  border-top: 5px solid var(--granate-principal);
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

.profile-card h2 {
  color: var(--granate-principal);
  font-size: 1.4em;
  margin-bottom: 5px;
  word-break: keep-all;
}

.role-badge {
  color: var(--rosa-fuerte);
  font-weight: bold;
  text-transform: uppercase;
  font-size: 0.8em;
  margin-bottom: 20px;
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

.main-content {
  flex: 1;
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

.section-label {
  display: block;
  font-weight: bold;
  color: var(--granate-principal);
  margin-bottom: 20px;
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

.footer-card {
  background: white;
  padding: 30px;
  border-radius: 15px;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
  margin-top: 30px;
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
  border: none;
  border-radius: 8px;
  font-weight: bold;
  text-align: center;
  text-decoration: none;
  transition: 0.3s;
  font-size: 1.1em;
}

.btn-primary-save:hover {
  background-color: var(--rosa-fuerte);
  transform: translateY(-2px);
}

.linea-granate {
  border: none;
  height: 2px;
  background-color: var(--granate-principal);
  margin: 20px 0;
  opacity: 0.8;
  border-radius: 2px;
}

.edit-input {
  width: 100%;
  padding: 8px;
  margin-bottom: 10px;
  border: 1px solid #ddd;
  border-radius: 5px;
  font-family: inherit;
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

.btn-outline-edit {
  width: 100%;
  background: white;
  border: 1px solid var(--rosa-fuerte);
  color: var(--granate-principal);
  padding: 10px;
  border-radius: 8px;
  cursor: pointer;
  font-weight: bold;
  margin-top: 15px;
}

.edit-buttons {
  display: flex;
  gap: 10px;
  margin-top: 15px;
}

.btn-save-small {
  flex: 1;
  background: var(--granate-principal);
  color: white;
  border: none;
  padding: 8px;
  border-radius: 5px;
  cursor: pointer;
}

.btn-cancel-small {
  flex: 1;
  background: #eee;
  color: #333;
  border: none;
  padding: 8px;
  border-radius: 5px;
  cursor: pointer;
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

.label-mini,
.info-help {
  text-align: left;
  width: 100%;
  margin-left: 0;
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

.badge-interes {
  background: var(--rosa-claro);
  color: var(--granate-principal);
  padding: 4px 10px;
  border-radius: 15px;
  font-size: 0.75em;
  font-weight: bold;
}

.checkbox-wrapper {
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
  justify-content: flex-start;
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

.recommended-title i{
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
}

.recommended-table th {
  text-align: left;
  padding: 8px;
  color: var(--granate-principal);
  font-size: 0.85em;
  text-transform: uppercase;
}

.recommended-table td {
  padding: 10px 8px;
  border-bottom: 1px solid #f0e4e8;
}

.label-tipo {
  color: var(--rosa-fuerte);
  font-weight: bold;
  font-size: 0.8em;
  text-transform: uppercase;
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

.section-label {
  font-weight: bold;
  color: var(--granate-principal);
  font-size: 1.2em;
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
}

.btn-primary-save:hover {
  background-color: var(--rosa-fuerte);
}
</style>
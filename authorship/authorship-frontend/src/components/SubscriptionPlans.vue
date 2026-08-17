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

    <transition name="popup-fade">
      <div v-if="notification.show" :class="['popup-notification', notification.type]">
        <div class="popup-icon">
          <i v-if="notification.type === 'error'" class="fa-solid fa-circle-exclamation"></i>
          <i v-else class="fa-solid fa-circle-check"></i>
        </div>
        <div class="popup-body">
          <span class="popup-title" v-if="notification.type === 'error'">Operación Denegada</span>
          <span class="popup-title" v-else>¡Acción Exitosa!</span>
          <p class="popup-message">{{ notification.message }}</p>
        </div>
        <button @click="notification.show = false" class="popup-close">
          <i class="fa-solid fa-xmark"></i>
        </button>
      </div>
    </transition>

    <div class="page-content">
      <div class="icon-subscription">
        <i class="fa-solid fa-wallet"></i>
      </div>
      <h1 class="title-welcome">Encuentra el plan perfecto para ti</h1>
      <div class="divider-icon">
        <span class="line"></span>
      </div>
      <p class="subtitle-welcome">Elige la suscripción que mejor se adapte a tus necesidades y empieza a disfrutar de
        todos sus beneficios</p>

      <div class="container">
        <div class="plans-container">
          <div v-for="item in plans" :key="item.id" class="plan-card">
            <div class="plans-icon">
              <i class="fa-solid fa-crown"></i>
            </div>
            <h3 class="plan-name">{{ item.name }}</h3>
            <p class="plan-price">{{ item.points }} puntos<span>/mes</span></p>
            <div class="money-equivalence">
              <span>Equivale a {{ item.price }} € / mes</span>
            </div>
            <div class="plan-description">
              {{ item.description }}
            </div>

            <ul class="features-list">
              <li>
                <i class="fa-solid fa-calendar-days"></i> Acceso:
                <span class="number-highlight"> {{ item.duration_days }} días</span>
              </li>
            </ul>

            <button @click="handleSubscribe(item.id)" class="btn-accion">
              <i class="fa-solid fa-angle-right"></i>Seleccionar {{ item.name }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { useRouter } from "vue-router";
import axios from "axios";
import { useAuthStore } from "../stores/auth";

const router = useRouter();
const authStore = useAuthStore();

const plans = ref([]);
const error = ref("");
const loading = ref(true);
const userPoints = ref(0);

const user = ref({
  username: "",
  role: "",
  es_autor: false,
  es_consumidor: false
});

const notification = ref({
  show: false,
  message: "",
  type: "error"
});

const getSubscriptionPlanData = async () => {
  try {
    const response = await axios.get("http://localhost:8000/api/subscriptions/plans/", {
      headers: {
        Authorization: `Token ${authStore.token || localStorage.getItem("token")}`,
      },
    });
    plans.value = response.data;

    const responseUser = await axios.get("http://localhost:8000/api/users/me/", {
      headers: {
        Authorization: `Token ${authStore.token || localStorage.getItem("token")}`,
      },
    });
    user.value = responseUser.data;

  } catch (err) {
    console.error("Error al cargar los planes:", err);
    error.value = "Error al cargar datos";
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

const triggerNotification = (message, type = 'error') => {
  notification.value = { show: true, message, type };
};

const handleSubscribe = async (planId) => {
  try {
    const response = await axios.post("http://localhost:8000/api/subscriptions/subscribe/",
      { plan_id: planId },
      { headers: { Authorization: `Token ${authStore.token || localStorage.getItem("token")}` } }
    );

    triggerNotification(response.data.detail || "¡Suscripción realizada con éxito!", "success");

    setTimeout(() => {
      router.push("/dashboard");
    }, 1500);
  } catch (err) {
    if (err.response && err.response.data && err.response.data.detail) {
      triggerNotification(err.response.data.detail, "error");
    } else {
      triggerNotification("Error al procesar la suscripción. Inténtalo de nuevo.", "error");
    }
  }
};

const handleLogout = () => {
  authStore.logout();
  localStorage.removeItem("token");
  router.push("/login");
};

onMounted(() => {
  getSubscriptionPlanData();
  getUserPoints();
});
</script>

<style scoped>
.dashboard-wrapper {
  min-height: 100vh;
}

.page-content {
  padding-top: 60px;
}

.icon-subscription {
  width: 60px;
  height: 60px;
  margin: 0 auto 10px;

  border: 1px solid var(--granate-principal);
  border-radius: 50%;

  display: flex;
  justify-content: center;
  align-items: center;

  background: var(--rosa-claro);
  color: #8B0029;
  font-size: 24px;
}

.title-welcome {
  color: var(--granate-principal);
  font-size: 2.2em;
  font-weight: 800;
  line-height: 1.2;
  margin: 15px 0;

  text-align: center;
}

.subtitle-welcome {
  text-align: center;
  color: #666;
  margin-bottom: 30px;
}

.plans-container {
  display: flex;
  gap: 20px;
  justify-content: center;
  flex-wrap: wrap;
  padding: 40px 20px;
}

.plan-card {
  background: white;
  border: 1px solid #ddd;
  border-radius: 12px;
  padding: 25px;
  width: 280px;
  text-align: center;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.05);
  display: flex;
  flex-direction: column;
}

.plan-card:hover {
  transform: translateY(-10px);
  border-color: var(--rosa-fuerte);
  background-color: var(--rosa-claro);
  box-shadow: 0 8px 15px rgba(128, 0, 32, 0.1);
}

.plan-name {
  color: var(--granate-principal);
  font-size: 1.5em;
  margin-bottom: 10px;
}

.plan-price {
  font-size: 2em;
  font-weight: bold;
  color: #333;
}

.plan-price span {
  font-size: 0.45em;
  color: #888;
  font-weight: 500;
  margin-left: 2px;
}

.plan-description {
  margin: 15px 0;
  color: #666;
  font-size: 0.9em;
  flex-grow: 1;
}

.features-list {
  list-style: none;
  padding: 0;
  margin-bottom: 20px;
}

.features-list li i {
  color: var(--granate-principal);
  font-size: 1rem;
  margin-right: 8px;
  display: inline-block;
  vertical-align: middle;
  text-align: center;
}

.features-list li {
  align-items: center;
  justify-content: center;
  color: var(--texto-oscuro);
  font-size: 0.95em;
}

.btn-accion {
  background: var(--granate-principal);
  color: white;
  border: none;
  padding: 12px;
  border-radius: 8px;
  cursor: pointer;
  font-weight: bold;
  transition: 0.3s;
}

.btn-accion:hover {
  background: var(--rosa-fuerte);
}

.plans-icon i {
  width: 60px;
  height: 60px;
  margin: 0 auto 20px;

  border: 1px solid var(--granate-principal);
  border-radius: 50%;

  display: flex;
  justify-content: center;
  align-items: center;

  background: var(--rosa-claro);
  color: #8B0029;
  font-size: 24px;
}

.number-highlight {
  color: var(--granate-principal);
  font-weight: 700;
}

.money-equivalence {
  margin-top: 0;
  font-size: 0.9rem;
  color: #777777;
  font-weight: 500;
  background-color: var(--rosa-claro, #FFF0F3);
  padding: 3px 12px;
  border-radius: 12px;
  display: inline-block;
}
</style>
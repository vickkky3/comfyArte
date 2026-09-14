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

    <div class="plans-main-container">
      <div class="plans-header-bar">
        <button @click="goBack" type="button" class="btn-back-top">
          <i class="fa-solid fa-arrow-left"></i>
          <span>Volver</span>
        </button>

        <div class="header-center-info">
          <div class="header-icon-box">
            <i class="fa-solid fa-wallet"></i>
          </div>
          <div class="header-titles">
            <h1 class="title-welcome">Encuentra el plan perfecto para ti</h1>
            <p class="subtitle-welcome">
              Elige la suscripción que mejor se adapte a tus necesidades y empieza a disfrutar de todos sus beneficios.
            </p>
          </div>
        </div>
      </div>

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
            <i class="fa-solid fa-angle-right"></i> Seleccionar {{ item.name }}
          </button>
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

const goBack = () => {
  if (window.history.state?.back) {
    router.back();
  } else {
    router.push('/dashboard');
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
  padding: 30px 20px 60px;
}

.plans-main-container {
  background: #ffffff;
  padding: 35px 40px;
  border-radius: 18px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.04);
  max-width: 1100px;
  margin: 0 auto;
  box-sizing: border-box;
}

.plans-header-bar {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 52px;
  margin-bottom: 25px;
}

.btn-back-top {
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 8px 18px;
  background-color: var(--rosa-claro, #fff0f3);
  color: var(--granate-principal, #7a0026);
  border: 1px solid #f2cdd6;
  border-radius: 20px;
  font-size: 0.85rem;
  font-weight: 700;
  text-decoration: none;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-back-top:hover {
  background-color: #ffe1e8;
  border-color: var(--rosa-fuerte, #db7093);
  transform: translateY(-50%) translateX(-2px);
}

.header-center-info {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 16px;
}

.header-icon-box {
  width: 52px;
  height: 52px;
  min-width: 52px;
  background-color: var(--rosa-claro, #fff0f3);
  color: var(--granate-principal, #7a0026);
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.4rem;
  border: 1px solid #f2cdd6;
  box-shadow: 0 3px 8px rgba(0, 0, 0, 0.03);
}

.header-titles {
  display: flex;
  flex-direction: column;
  text-align: left;
}

.title-welcome {
  margin: 0;
  font-size: 1.6rem;
  font-weight: 800;
  color: var(--granate-principal, #7a0026);
  line-height: 1.2;
}

.subtitle-welcome {
  margin: 4px 0 0 0;
  color: #666;
  font-size: 0.88rem;
}

.plans-container {
  display: flex;
  gap: 20px;
  flex-wrap: nowrap;
  overflow-x: auto; 
  padding: 20px 10px 15px 10px;
  justify-content: flex-start;
  scrollbar-width: thin;
  scrollbar-color: var(--granate-principal) var(--rosa-claro);
}

.plans-container::-webkit-scrollbar {
  height: 8px;
}

.plans-container::-webkit-scrollbar-track {
  background: var(--rosa-claro);
  border-radius: 4px;
}

.plans-container::-webkit-scrollbar-thumb {
  background: var(--granate-principal);
  border-radius: 4px;
}

.plan-card {
  flex: 0 0 280px;
  background: white;
  border: 1px solid #ddd;
  border-radius: 12px;
  padding: 25px;
  text-align: center;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.05);
  display: flex;
  flex-direction: column;
  transition: transform 0.2s ease, border-color 0.2s ease, box-shadow 0.2s ease;
}

.plan-card:hover {
  transform: translateY(-8px);
  border-color: var(--rosa-fuerte);
  background-color: #fffafc;
  box-shadow: 0 8px 15px rgba(128, 0, 32, 0.08);
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

.features-list li {
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--texto-oscuro);
  font-size: 0.95em;
}

.features-list li i {
  color: var(--granate-principal);
  font-size: 1rem;
  margin-right: 8px;
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
  background-color: var(--rosa-claro);
  padding: 3px 12px;
  border-radius: 12px;
  display: inline-block;
}
</style>
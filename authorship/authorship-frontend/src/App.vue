<template>
  <div id="main-app">
    <router-view />
  </div>
</template>

<script setup>
import { onMounted } from "vue";
import { useAuthStore } from "./stores/auth";

const authStore = useAuthStore();

onMounted(() => {
  const tokenGuardado = localStorage.getItem("token");

  if (tokenGuardado && !authStore.token) {
    authStore.setToken(tokenGuardado);
    console.log("Sesión recuperada automáticamente desde localStorage");
  }
});
</script>

<style>
#main-app {
  margin: 0;
  padding: 0;
  min-height: 100vh;
  background-color: transparent;
}
</style>
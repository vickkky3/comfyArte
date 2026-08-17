<template>
  <nav class="navbar">
    <div class="navbar-left">
      <img src="/logo.png" class="logo-img" alt="Logo comforART" />
      <span class="nav-title">
        <span class="text-comfor">Comfor</span><span class="text-art">ART</span>
      </span>
    </div>
  </nav>

  <div class="selection-page-wrapper">
    <h1 class="welcome-text">BIENVENIDO A LA PLATAFORMA</h1>
    <div class="brand-block">
      <img src="/logo.png" class="welcome-logo-circle" alt="Icono CA" />
      <h1 class="welcome-title">
        <span class="text-light">Comfor</span><span class="text-bold">ART</span>
      </h1>
    </div>

    <div class="divider-icon">
      <span class="line"></span>
    </div>

    <h3 class="description">La plataforma segura y confiable para proteger, <br>
      gestionar y comercializar tus creaciones intelectuales</h3>

    <div class="selection-container">
      <router-link :to="{ path: '/register/author' }" class="card">
        <h2>Soy Autor</h2>
        <div class="icon-circle author">
          <i class="fa-solid fa-pen-nib"></i>
        </div>
        <p>Registra tus creaciones, protege tu autoría y gestiona tus licencias.</p>
        <div class="security-info">
          <i class="fa-solid fa-shield-halved"></i>
          <p class="security-text">Protección legal para tus obras</p>
        </div>
        <strong>Registrarme como Creador</strong>
      </router-link>

      <router-link :to="{ path: '/register/consumer' }" class="card">
        <h2>Soy Consumidor</h2>
        <div class="icon-circle consumer">
          <i class="fa-solid fa-book-open"></i>
        </div>
        <p>Explora obras y obtén licencias de uso de forma legal y segura.</p>
        <div class="security-info">
          <i class="fa-solid fa-shield-halved"></i>
          <p class="security-text">Acceso seguro y legal a contenido</p>
        </div>
        <strong>Registrarme como Consumidor</strong>
      </router-link>
    </div>

    <div class="login-link">
      <p>¿Ya tienes una cuenta?</p>
      <router-link :to="{ path: '/login' }">Inicia sesión aquí </router-link>
      <i class="fa-solid fa-circle-arrow-right"></i>
    </div>
  </div>
</template>
<style scoped>
.selection-page-wrapper {
  padding: 20px;
  text-align: center;
}

.welcome-card {
  text-align: center;
  max-width: 600px;
  margin: 0 auto;
  padding: 40px 20px;
}

.welcome-badge {
  font-family: sans-serif;
  font-size: 0.95rem;
  font-weight: 700;
  letter-spacing: 1.5px;
  color: #333;
  display: block;
  margin-bottom: 25px;
}

.brand-block {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 15px;
  margin-bottom: 10px;
}

.welcome-logo-circle {
  width: 75px; 
  height: 75px;
  object-fit: cover;
  border-radius: 50%;
  box-shadow: 0 4px 15px rgba(128, 0, 32, 0.1);
}

.welcome-title {
  font-size: 3rem;
  margin: 0;
  line-height: 1;
}

.text-light {
  color: var(--rosa-fuerte);
  font-weight: 300;
}

.text-bold {
  color: var(--granate-principal);
  font-weight: 800;
}

.welcome-text {
  justify-content: center;
  margin-top: 10px;
  color: var(--texto-oscuro);

  font-size: 1.5rem;
  font-weight: 700;
  letter-spacing: 1px;

}

.logo-title {
  font-size: 3.5em;
  letter-spacing: -1px;
}

.logo-light {
  color: var(--rosa-fuerte);
  font-weight: 400;
}

.logo-bold {
  color: var(--granate-principal);
  font-weight: 800;
}

.description {
  max-width: 700px;
  margin: 0 auto;
  text-align: center;
  line-height: 1;
  color: #3a3838
}

.selection-container {
  display: flex;
  justify-content: center;
  gap: 30px;
  margin-top: 60px;
}

.card {
  border: 2px solid #eee;
  border-radius: 12px;
  padding: 30px;
  width: 280px;
  text-align: center;
  transition: all 0.3s ease;
  text-decoration: none;
  color: var(--texto-oscuro);
  background-color: white;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
}

.card:hover {
  transform: translateY(-10px);
  border-color: var(--rosa-fuerte);
  background-color: var(--rosa-claro);
  box-shadow: 0 8px 15px rgba(128, 0, 32, 0.1);
}

.card h2 {
  color: var(--granate-principal);
  margin-bottom: 15px;
}

.security-info {
  display: flex;
  align-items: center;
  gap: 8px;
  background: #fcfcfc;
  padding: 8px 14px;
  border-radius: 20px;
  border: 1px solid var(--rosa-fuerte);
  margin-bottom: 15px;
}

.security-info i {
  color: var(--granate-principal);
  font-size: 0.9rem;
}

.security-text {
  font-size: 0.8rem;
  color: #555;
  font-weight: 600;
}

.card strong {
  display: inline-block;
  margin-top: 15px;
  color: var(--rosa-fuerte);
}

.login-link {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  margin-top: 40px;
  font-size: 1.1em;
  color: var(--granate-principal);
  transition: color 0.3s;
}

.login-link p {
  margin: 0;
  color: #333;
  transition: color 0.3s;
}

.login-link i {
  color: inherit;
  transition: transform 0.3s, color 0.3s;
}

.login-link:hover i {
  color: var(--rosa-fuerte);
  transform: translateX(4px);
}

.login-link a {
  color: inherit;
  text-decoration: none;
  font-weight: bold;
  border-bottom: 2px solid transparent;
  transition: border-color 0.3s, color 0.3s;
}

.login-link:hover {
  color: var(--rosa-fuerte);
}

.login-link a:hover {
  color: var(--rosa-fuerte);
  border-bottom: 2px solid var(--rosa-fuerte);
}
</style>

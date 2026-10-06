import { createRouter, createWebHistory } from "vue-router";
import RegisterSelection from "../components/RegisterSelection.vue";
import RegisterForm from "../components/RegisterForm.vue";
import LoginPage from "../components/LoginPage.vue";
import DashboardPage from "../components/DashboardPage.vue";
import WorkList from "../components/WorkList.vue";
import WorkCreate from "../components/WorkCreate.vue";
import WorkDetailAuthor from "../components/WorkDetailAuthor.vue";
import WorkDetailConsumer from "../components/WorkDetailConsumer.vue";
import SubscriptionPlans from "../components/SubscriptionPlans.vue";
import SubscribedAuthors from "../components/SubscribedAuthors.vue";
import SavedWorks from "../components/SavedWorks.vue";

export const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: "/", component: RegisterSelection },
    
    { path: "/login", component: LoginPage },
    { path: "/register/:role", component: RegisterForm },
    
    { path: "/dashboard", component: DashboardPage },
    
    { path: "/works", component: WorkList, meta: { requiresAuth: true, requiresConsumerRole: true } },
    { path: "/works/create", component: WorkCreate, meta: { requiresAuth: true, requiresAuthorRole: true }},
    { path: "/works/:id", component: WorkDetailConsumer, meta: { requiresAuth: true, requiresConsumerRole: true }},
    { path: "/worksAuthor/:id", component: WorkDetailAuthor, meta: { requiresAuth: true, requiresAuthorRole: true }},
    { path: "/subscription/plans", component: SubscriptionPlans, meta: { requiresAuth: true, requiresConsumerRole: true } },
    { path: "/subscription/authors/subscribe/", component: SubscribedAuthors, meta: { requiresAuth: true, requiresConsumerRole: true } },
    { path: "/subscription/works/subscribe/", component: SavedWorks, meta: { requiresAuth: true, requiresConsumerRole: true } },
  ],
});

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem("token");
  const role = localStorage.getItem("role");

  if (to.meta.requiresAuth && !token) {
    return next({ path: "/login" });
  }

  if (to.meta.requiresAuthorRole && role !== "Author") {
    return next({ path: "/dashboard" });
  }

  if (to.meta.requiresConsumerRole && role !== "Consumer") {
    return next({ path: "/dashboard" });
  }

  next();
});

export default router;
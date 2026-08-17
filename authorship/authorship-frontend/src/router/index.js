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

export const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: "/", component: RegisterSelection },
    
    { path: "/login", component: LoginPage },
    { path: "/register/:role", component: RegisterForm },
    
    { path: "/dashboard", component: DashboardPage },
    
    { path: "/works", component: WorkList },
    { path: "/works/create", component: WorkCreate },
    { path: "/works/:id", component: WorkDetailConsumer },
    { path: "/worksAuthor/:id", component: WorkDetailAuthor },
    { path: "/subscription/plans", component: SubscriptionPlans },
  ],
});

export default router;
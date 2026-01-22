import { createRouter, createWebHistory } from 'vue-router';
import MatchListView from '@/views/MatchListView.vue';

const routes = [
  {
    path: '/',
    name: 'Home',
    component: MatchListView
  },
  {
    path: '/matches',
    name: 'Matches',
    component: MatchListView
  }
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

export default router;
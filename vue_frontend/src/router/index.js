import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import TestView from '../views/TestView.vue'
import LoginView from '../views/LoginView.vue'
import SignupView from '../views/SignupView.vue'
import DashboardView from '../views/Dashboard.vue'
import MyAccountView from '../views/MyAccount.vue'
import ChangePasswordView from '../views/ChangePassword.vue'
import SpinningView from '../views/Dashboard/Spinning.vue'
import WebsocketView from '../views/Dashboard/Websocket.vue'

import store from '../store'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView,
    },
    {
      path: '/test/',
      name: 'test',
      component: TestView,
      meta: {
        requireLogin: true
      }
    },
    {
      path: '/login',
      name: 'login',
      component: LoginView
    },
    {
      path: '/signup',
      name: 'signup',
      component: SignupView
    },
    {
      path: '/dashboard',
      name: 'dashboard',
      component: DashboardView,
      meta:{
        requireLogin: true
      }
    },
    {
      path: '/my-account',
      name: 'my-account',
      component: MyAccountView,
      meta:{
        requireLogin: true
      }
    },
    {
      path: '/my-account/change-password',
      name: 'change-password',
      component: ChangePasswordView,
      meta:{
        requireLogin: true
      }
    },
    {
      path: '/dashboard/spinning',
      name: 'spinning',
      component: SpinningView,
      meta:{
        requireLogin: true
      }
    },
    {
      path: '/dashboard/websocket',
      name: 'websocket',
      component: WebsocketView,
      meta:{
        requireLogin: true
      }
    }
  ]
})

router.beforeEach((to, from, next) => {
  if(to.matched.some(record => record.meta.requireLogin) && !store.state.is_auth){
    next('/login')
  }
  else{
    next()
  }
})

export default router

<template>
  <div>
    <nav class="navbar is-dark" role="navigation" aria-label="main navigation">
      <div class="navbar-brand">
        <a class="navbar-item" href="https://mucslab-dev.hkust.edu.hk/">
          <figure>
            <img src="./assets/SmartLab.png">
          </figure>
          <strong style="white-space:pre">MuCSLab · Automation Platform</strong>
        </a>
      </div>

      <div class="navbar-menu">
        <div class="navbar-item">
          <router-link to="/" class="has-text-white">Home</router-link>
        </div>
      </div>

      <div class="navbar-end">
        <template v-if="this.$store.state.is_auth">
          <div class="navbar-item">
            <p>
              Welcome, {{ this.$store.state.email }}!
            </p>
          </div>
          <div class="navbar-item">
            <div class="buttons">
              <router-link to="/dashboard" class="button is-success">Dashboard</router-link>
              <router-link to="/my-account" class="button is-light">My Account</router-link>
            </div>
          </div>
        </template>
        <template v-else>
          <div class="navbar-item">
            <div class="buttons">
              <router-link to="/signup" class="button is-success">Sign Up</router-link>
              <router-link to="/login" class="button is-light">Log In</router-link>
            </div>
          </div>
        </template>
      </div>

      
    </nav>
  </div>
  <section class="section">
    <router-view/>
  </section>
  <footer class="footer">
    <p class="has-text-centered">Copyright (c) 2023 @ MuCSLab</p>
  </footer>
</template>

<script>
import axios from 'axios';

export default {
  name: 'App',
  beforeCreate(){
    if(localStorage.getItem('token')){
      axios
        .post('/api/token_validation/', {'token': localStorage.getItem('token')})
        .then(response => {
          localStorage.setItem('email', response.data['email'])
          localStorage.setItem('is_auth', true)
          this.$store.commit('authSuccess')
        })
        .catch(error => {
          if(error.response.data['Token validation']){
            localStorage.setItem('token', '')
            localStorage.setItem('authenticated', false)
            localStorage.setItem('email', '')
            this.$store.commit('authFail')
          }
        })
    }
  },
  data(){
    return{
      email: ''
    }
  },
  components: {
  },
  methods:{
  }
}

</script>

<style lang="scss">
  @import 'bulma/css/bulma.css'
</style>
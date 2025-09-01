<template>
    <h1 class="title">
        Account Information
    </h1>
    <div class="field">
        <label class="title is-6">
            Username
        </label>
        <p>
            {{ this.username }}
        </p>
    </div>
    <div class="field">
        <label class="title is-6">
            E-mail
        </label>
        <p>
            {{ this.email }}
        </p>
    </div>
    <div class="field">
        <label class="title is-6">
            Registered Time
        </label>
        <p>
            {{ this.reg_time }}
        </p>
    </div>
    <div class="field">
        <label class="title is-6">
            User Group
        </label>
        <p>
            {{ this.user_group }}
        </p>
    </div>
    <div class="field">
        <label class="title is-6">
            Activation Status
        </label>
        <p>
            {{ this.activated }}
        </p>
    </div>
    <div class="field">
        <div class="buttons">
            <button class="button is-danger" @click="this.logout">Logout</button>
            <router-link class="button is-light" to="/my-account/change-password">Change Password</router-link>
        </div>
    </div>
    

</template>

<script>
import axios from 'axios';

export default{
    name: 'MyAccount',
    data(){
        return{
            username: '',
            email: '',
            reg_time: '',
            user_group: 'User',
            activated: false
        }
    },
    mounted(){
        this.getUserData()
    },
    methods:{
        getUserData(e){
            axios
                .post('/api/user_data/', {'token': this.$store.state.token, 'email': this.$store.state.email})
                .then(response => {
                    this.username = response.data['username']
                    this.email = response.data['email']
                    this.reg_time = response.data['register_time']
                    this.activated = response.data['activated']
                })
            
        },
        logout(){
            localStorage.clear()
            this.$store.commit('authFail')
            this.$router.push('/')
        }
    }
}

</script>
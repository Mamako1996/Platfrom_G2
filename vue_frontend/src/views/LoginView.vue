<template>
    <div class="column is-4 is-offset-4">
        <h1 class="title"> Log In</h1>
        <div class="field">
            <label>Email</label>
            <div class="field has-addons">
                <div class="control">
                    <input class="input" name="email" type="text" v-model="this.email_head">
                </div>
                <div class="control">
                    <span class="select">
                        <select v-model="this.email_tail">
                            <option>@connect.ust.hk</option>
                            <option>@ust.hk</option>
                        </select>
                    </span>
                </div>
            </div>
        </div>
        <div class="field">
            <label>Passwrod</label>
            <div class="control">
                <input class="input" name="password" :type="this.show_password ? 'text' : 'password'" v-model="this.data.password">
            </div>
        </div>
        <div class="field">
            <label class="checkbox">
                <input type="checkbox" v-model="this.show_password">
                Show Password
            </label>
        </div>
        <div class="notification is-danger" v-if="this.errors.length">
            <p v-for="error in this.errors" v-bind:key="error">
                {{ error }}
            </p>
        </div>
        <div class="field">
            <button class="button is-success" @click="this.login">Login</button>
        </div>
    </div>
</template>
<script>
import axios from 'axios';

export default{
    name: 'Login',
    data(){
        return{
            data :{
                email: '',
                password: ''
            },
            confirm_password: '',
            email_head: '',
            email_tail: '@connect.ust.hk',
            show_password: false,
            errors: []
        }
    },
    methods: {
        login(e){
            this.data.email = this.email_head + this.email_tail
            axios
                .post('/api/login/', this.data)
                .then(response => {
                    if(response.data['token']){
                        localStorage.setItem('token', response.data['token'])
                        localStorage.setItem('is_auth', true)
                        localStorage.setItem('email', this.data.email)
                        this.$store.commit('authSuccess')
                        this.$router.push('/dashboard')
                    }
                })
                .catch(error =>{
                    if(error.response){
                        for(const property in error.response.data){
                            this.errors.push(`${property}: ${error.response.data[property]}`)
                        }
                    }
                    else if(error.message){
                        this.errors.push(`Error:${error.message}`)
                    }
                    else{
                        console.log(JSON.stringify(error))
                    }
                })
        }
    }
}
</script>
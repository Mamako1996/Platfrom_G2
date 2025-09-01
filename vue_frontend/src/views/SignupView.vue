<template>
    <div class="column is-4 is-offset-4">
        <h1 class="title"> Sign Up</h1>
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
            <label>Username</label>
            <div class="control">
                <input class="input" name="username" type="text" v-model="this.data.username">
            </div>
        </div>
        <div class="field">
            <label>Password</label>
            <div class="control">
                <input class="input" name="password" :type="this.show_password ? 'text' : 'password'" v-model="this.data.password">
            </div>
        </div>
        <div class="field">
            <label>Confirm Passwrod</label>
            <div class="control">
                <input class="input" name="confirm_password" :type="this.show_password ? 'text' : 'password'" v-model="this.confirm_password">
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
            <button class="button is-success" @click="this.signup">Signup</button>
        </div>
    </div>
</template>

<script>
import axios from 'axios';

export default{
    name: 'signup',
    data(){
        return{
            data: {
                email: '',
                username: '',
                password: ''
            },
            confirm_password: '',
            email_head: '',
            email_tail: '@connect.ust.hk',
            show_password: false,
            errors: []
        }
    },
    methods:{
        signup(e){
            this.data.email = this.email_head + this.email_tail
            if(this.data.password != this.confirm_password){
                this.errors.push('Password Confirmation Failed.')
            }
            else{
                axios
                    .post('/api/signup/', this.data)
                    .then(response => {
                        this.$router.push('/login')
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
}

</script>
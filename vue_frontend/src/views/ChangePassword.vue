<template>
    <h1 class="title">
        Change Password
    </h1>
    <div class="column is-4">
        <div class="field">
            <label class="title is-6">
                Email
            </label>
            <p>{{ this.$store.state.email }}</p>
        </div>
        <div class="field">
            <label>Old Password</label>
            <div class="control">
                <input class="input" name="password" :type="this.show_password ? 'text' : 'password'" v-model="this.old_password">
            </div>
        </div>
        <div class="field">
            <label>Password</label>
            <div class="control">
                <input class="input" name="password" :type="this.show_password ? 'text' : 'password'" v-model="this.password">
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
            <button class="button is-success" @click="this.submit">Submit</button>
        </div>
    </div>
</template>

<script>
import axios from 'axios';

export default{
    data(){
        return{
            errors: [],
            old_password: '',
            password: '',
            confirm_password: '',
            show_password: false
        }
    },
    methods:{
        submit(){
            const data = {
                'token': this.$store.state.token,
                'email': this.$store.state.email,
                'old_password': this.old_password,
                'new_password': this.password
            }
            if(this.password != this.confirm_password){
                this.errors.push('Password Confirmation Failed.')
            }
            else{
                axios
                    .post('/api/change_password/', data)
                    .then(response => {
                        localStorage.clear()
                        this.$store.commit('authFail')
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
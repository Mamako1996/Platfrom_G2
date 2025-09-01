import { createStore } from "vuex";

export default createStore({
    state:{
        email: '',
        is_auth: false,
        token: ''
    },

    mutations:{
        authSuccess(state){
            state.email = localStorage.getItem('email')
            state.is_auth = true
            state.token = localStorage.getItem('token')
        },
        authFail(state){
            state.email = ''
            state.is_auth = false
            state.token = ''
        }
    }
})
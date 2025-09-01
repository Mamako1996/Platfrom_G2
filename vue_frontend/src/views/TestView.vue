<template>
    <h1 class="title">Motor Control</h1>
    <div class="column is-6">
        <div class="field">
            <label>Motor Number</label>
            <div class="control">
                <div class="select">
                    <select>
                        <option>Motor 1</option>
                    </select>
                </div>
            </div>
        </div>
        <div class="field">
            <label>Motor Speed</label>
            <div class="control">
                <input class="input" type="number" v-model="this.control_info.motor_speed">
            </div>
        </div>
        <div class="field">
            <div class="control">
                <button class="button is-success" @click="sendControlSignal">Submit</button>
            </div>
        </div>
    </div>
</template>
<script>
import axios from 'axios';
export default{
    name: 'Test',
    data(){
        return{
            control_info :{
                motor_name : 'Motor 1',
                motor_speed : '',
            }
        }
    },
    methods: {
        sendControlSignal(e){
            
            axios
                .post('/api/control/', this.control_info)
                .then(response => {
                    console.log(response)
                })
        },
    }
}
</script>
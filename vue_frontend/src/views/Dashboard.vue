<template>
    <h1 class="title">
        Dashboard
    </h1>
    <div class="field">
        <label class="title is-6">
            Device Status
        </label>
        <vxe-table :data="this.devices">
            <vxe-column type="seq" width="70"></vxe-column>
            <vxe-column field="username" title="Username"></vxe-column>
            <vxe-column field="ID" title="Device ID"></vxe-column>
            <vxe-column field="IP" title="IP Address"></vxe-column>
            <vxe-column field="time" title="Connected Time"></vxe-column>
        </vxe-table>
    </div>
    <div class="field">
        <label class="title is-6">
            Controls
        </label>
        <div class="buttons">
            <router-link class="button is-light" to="/dashboard/spinning">Spinning Registration</router-link>
        </div>
        <div class="buttons">
            <router-link class="button is-light" to="/dashboard/websocket">Web Socket Tester</router-link>
        </div>
    </div>
    
</template>

<script>
import axios from 'axios';

export default{
    created(){
        this.get_device_list()
    },
    data(){
        return{
            devices : [],
        }
    },
    methods:{
        get_device_list(e){
            axios
                .get('/api/device_list/')
                .then(response => {
                    var device_list = response.data['data']
                    for(let i = 0; i < device_list.length; i++){
                        var obj = device_list[i]
                        // console.log(obj)
                        this.devices.push({'id': i+1, 'username': obj['username'], 'ID': obj['clientid'], 'IP': obj['ip_address'], 'time': obj['connected_at']})
                    }
                })
        }          
    }

}

</script>
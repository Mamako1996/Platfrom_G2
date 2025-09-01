<template>
    <h1 class="title">
        ESP32 Control Pannel
    </h1>

    <div class="field" v-for="d in this.devices">
        <label class="title is-4">
            Device ID
        </label>
        <p>
            <strong>ESP32_{{ d.id }}</strong>
        </p>
        <p>
            <strong>Latest Command</strong> Motor {{ this.cmd.motor }} operate {{ this.cmd.time }} at speed {{ this.cmd.speed }}
        </p>
        <div class="field" v-for="m in d.motors">
            <div v-if="m.id !== -1">
                <label class="title is-4">
                    Motor {{ m.id }} Status<br>
                </label>
                <p>
                    <strong>Status</strong> {{ m.status }} <br>
                    <strong>Command</strong> Operate {{ m.time }} at speed {{ m.speed }} <br>
                    <strong>PWM Setting</strong> {{ m.pwm }} <br>
                    <strong>PCNT Reading</strong> {{ m.pcnt }} <br>
                </p>
            </div>
        </div>

    </div>
    <h1 class="title">
        RoboArm Control Pannel
    </h1>

    <div>
        <iframe width="424" height="240" src="https://www.youtube.com/embed/tP0jF6KEP4o" title="" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>
    </div>
    
</template>
<script>

export default{
    mounted(){
        this.wsTest()
        this.init()
    },
    beforeUnmount(){
        this.wsTerminate()
    },
    data(){
        return{
            client: null,
            cmd: {
                motor: -1,
                speed: -1,
                time: -1
            },
            devices: []
        }
    },
    methods:{
        wsTest(e){
            this.client = new WebSocket('ws:127.0.0.1:8000/websocket/')
            this.client.onopen = function() {
                console.log('WS connection success.')
            }
            this.client.onmessage = this.wsOnMsg
        },
        init(e){
            // 添加motor元素到列表
            
            // 将device添加到列表
            for(var i = 0; i < 1; i++){
                var tmp_device = {
                    id: 'N/A',
                    motors: [],
                }
                for(var j = 0; j < 4; j++){
                    var tmp_motor = {
                        id: -1,
                        status: 'N/A',
                        speed: -1,
                        time: -1,
                        pwm: -1,
                        pcnt: -1,
                    }
                    tmp_device.motors.push(tmp_motor)   
                }
                this.devices.push(tmp_device)
            }
        },
        wsOnMsg(e){
            console.log(e.data)
            const tmp = JSON.parse(e.data)
            var d = this.devices[tmp.device-1]
            d.id = tmp.device
            var m = d.motors[tmp.motor]
            m.id = tmp.motor
            switch (tmp.topic) {
                case 'task_create':
                    m.status = 'Busy'
                    m.speed = tmp.speed
                    m.time = tmp.time
                    break;
                case 'task_done':
                    m.status = 'Finished'
                    break;
                case 'pwm':
                    m.pwm = tmp.pwm
                    break;
                case 'pcnt':
                    m.pcnt = tmp.pcnt
                    break;
                case 'cmd':
                    this.cmd.motor = tmp.motor
                    this.cmd.speed = tmp.speed
                    this.cmd.time = tmp.time
                default:
                    break;
            }
        }
    }
}
</script>
<template>
  <div id="app">
    <!-- <img alt="Vue logo" src="./assets/logo.png"> -->
    <!-- <HelloWorld msg="Welcome to Your Vue.js App"/> -->
    <!-- <GraphVue></GraphVue>-->
    <router-view/>
  </div>
</template>

<script>
// import HelloWorld from './components/HelloWorld.vue'

export default {
  name: 'App',
  components: {
    // HelloWorld,
  },
  mounted() {
    this.ping();
  },
  methods: {
    ping() {
      // 使用 axios 向 flask 发送请求
      const url = "http://10.249.46.195:7478/ping";
      // const url = "http://127.0.0.1:5000//ping";
      this.axios.get(url, {params: 'hello'})
          .then((res) => {
            console.log(res.data);
          })
          .catch((error) => {
            console.log(error);
          })
    }
  },
}
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  position: fixed;
  display: flex;
  width: 100%;
  height: 100%;
}
</style>

import Vue from 'vue'
import App from './App.vue'
import ElementUI from 'element-ui';
import 'element-ui/lib/theme-chalk/index.css';
import router from './router'
import axios from 'axios';
import VueAxios from 'vue-axios';
import store from './vuex/store'
import vis from 'vis';

Vue.config.productionTip = false
axios.defaults.withCredentials = false
Vue.use(ElementUI)
Vue.use(VueAxios, axios)
Vue.use(vis)

new Vue({
  store,
  router,
  render: h => h(App),
}).$mount('#app')
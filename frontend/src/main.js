// The Vue build version to load with the `import` command
// (runtime-only or standalone) has been set in webpack.base.conf with an alias.
import Vue from 'vue'
import App from './App'
import router from './router'
import axios from "axios";
import ElementUI from 'element-ui';
import 'element-ui/lib/theme-chalk/index.css';

/* element-ui */
Vue.use(ElementUI);
/* 设置cookie,session跨域配置 */
axios.defaults.withCredentials=true;
/* 设置post请求体,请求格式为json*/
axios.defaults.headers.post['Content-Type'] = 'application/json'
/* 设置全局axios写法 */
Vue.prototype.$http = axios

Vue.config.productionTip = false


// to: 跳转路由地址  from: 上一个路由 next: 跳转方法
router.beforeEach((to, from, next) => {
  // 判断一下本地存储中是否有user_id
  const user_id = localStorage.getItem('userId')
  console.log("进入到导航路由")
  if(to.meta.requireAuth == true){
    if (user_id){
             console.log("登录了，允许访问")
           //放行
           next()
         }else{
           //回到登录页面
           console.log("你没有登录，请登录")
           next('/')
         }

    }else{
        //允许访问
        console.log("不需要登录，允许访问")
        next()
    }
})


/* eslint-disable no-new */
new Vue({
  el: '#app',
  router,
  components: { App },
  template: '<App/>'
})

import Vue from 'vue'
import Router from 'vue-router'
import test002 from '@/components/demo/test02'
import test003 from '@/components/demo/test03'
import login from '@/components/page/login'
import chat from '@/components/page/chat'
import error from "@/components/page/Page404.vue";

Vue.use(Router)

export default new Router({
  mode: 'history', // 去掉url中的#
  routes: [
    {
      path: '/', //登录页面，同时是默认页面
      name: 'login',
      component: login
    },
    {
      path: '/test02',
      name: 'test02',
      component: test002
    },
    {
      path: '/test03',
      name: 'test03',
      component: test003
    },
    {
      path: '/chat',//聊天页面
      name: 'chat',
      meta:{
        requireAuth:true //是否需要登录才能访问，拦截
      },
      component: chat
    },
    {
      path: '*', // 通配符，匹配所有错误路径
      name: 'page404',
      component: error
    },
  ]
})

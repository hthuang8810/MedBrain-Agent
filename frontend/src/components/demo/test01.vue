<script>
import {test01,num} from "@/assets/js/test.js";

export default {
  name: "test01",
  mounted() { // vue内置函数，文档加载事件
    test01();
    console.log(num);
  },
  data() { // 数据, 所有的变量和前端的数据类型在这里定义
    return {
      url:require("@/assets/logo.png")
    }
  }
}
</script>

<template>
  <div class="test01">
    hello world
    <img :src="url" alt="">
  </div>
</template>

<style scoped>
@import url('../../assets/css/test.css');
</style>

<script>
export default {
  name: "test02",
  mounted() { // 生命周期函数(钩子函数)，页面加载时执行
    console.log("页面加载成功");
  },
  data() {
    return {
      url: require('@/assets/logo.png'),
      msg: "hello world",
      html:"<span style='color:red'>你好</span>",
      student:{
        name:"张三",
        age:18,
        sex:"男",
        hobbits:["football"],
        remark:"无"
      },
      isShow:false,
      list:[
        {
          name:"张三",
          age:18,
          score:90
        },
        {
          name:"张三",
          age:18,
          score:55
        },
        {
          name:"张三",
          age:18,
          score:88
        }
      ]
    }
  },
  methods: { // 自定义所有的函数
    show(){ // 显示数据
      console.log(this.msg);
      console.log(this.list);
    }

  }
}
</script>

<template>
  <div>
    <!--  文本绑定，采用{{变量名}}  -->
    <h1>{{ msg }}</h1>
    <!--  html标签绑定，在开始标签采用v-html  -->
    <div v-html="html"></div>
    <!--  绑定html属性，针对的是非表单元素，给html属性前面添加一个:  -->
    <img :src="url" v-show="isShow" alt="">
<!--  表单元素  -->
    姓名:<input type="text" v-model="student.name">
    <br>
    性别:<input type="radio" v-model="student.sex" value="男">男 <input type="radio" v-model="student.sex" value="女">女
    <br>
    爱好:<input type="checkbox" v-model="student.hobbits" value="football">足球 <input type="checkbox" v-model="student.hobbits" value="game">打游戏
    <br>
    学历:<select>
      <option value="">--请选择学历--</option>
      <option value="">--本科--</option>
      <option value="">--大专--</option>
    </select>
    <br>
    备注:<textarea cols="30" rows="10" v-model="student.remark"></textarea>
    <br>

<!--  循环列表  -->
    <table border="1" width="500">
      <thead>
        <tr>
          <th>姓名</th>
          <th>年龄</th>
          <th>分数</th>
          <th>成绩判定</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="el in list">
          <td>{{el.name}}</td>
          <td>{{el.age}}</td>
          <td>{{el.score}}</td>
          <td>
            <span v-if="el.score>=80">优秀</span>
            <span v-else-if="el.score>60">良好</span>
            <span v-else>不及格</span>
          </td>
        </tr>
      </tbody>

    </table>
    <br>
    <button type="button" @click="show">提交</button>
  </div>

</template>

<style scoped>

</style>

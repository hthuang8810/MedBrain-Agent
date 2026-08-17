<script>
export default {
  name: "test03",
  data() {
    return {
      userInfo: {
        userName: '',
        password: '',
        email: '',
        code: ''
      }
    }
  },
  methods: {
    sendCode() { // 发送验证码
      // 定义一个请求参数;
      const ps = {"email": this.userInfo.email}
      // 定义一个变量，来存vue的this对象
      const self = this;
      // 发送ajax请求
      this.$http.post("http://localhost:8000/send_code",ps)
        .then(function (rs){
          if (rs.data.code == 200) {
            self.$message.success(rs.data.data);
          } else {
            self.$message.error(rs.data.data);
          }
          }
      )
    },
    loginCode() { // 验证码登录
      // 定义一个请求参数
      const ps = {"email": this.userInfo.email, "code": this.userInfo.code}
      // 创建一个变量，来存vue的this对象
      const self = this;
      // 发送ajax请求
      self.$http.post("http://localhost:8000/code_verify",ps)
      .then(function (rs) {
          console.log("验证码登录结果：", rs.data);
            if (rs.data.code == 200) {
              self.$message.success(rs.data.data);
            } else {
              self.$message.error(rs.data.data);
            }
        })
    },
    login() { // 登录
      // 定义一个请求参数
      const ps={
        username: this.userInfo.username,
        password: this.userInfo.password
      };
      //定义一个变量，来存vue的this对象
       const self = this;
      //   定义一个请求头
      this.$http.post("http://localhost:8000/login",ps)
      .then(function (rs){
        console.log(rs.data)
        if (rs.data.code == 200) {
          self.$message.success(rs.data.message);
        } else {
          self.$message.error(rs.data.message);
        }
        }
      )
    }
  }
}
</script>

<template>
  <div>
    <h1>用户登录</h1>
    用户名：<el-input v-model="userInfo.username" placeholder="请输入用户名"></el-input>
    密码：<el-input v-model="userInfo.password" placeholder="请输入密码" show-password></el-input>
    <el-button type="success" @click="login">登录</el-button>
    <h1>验证码登录</h1>
    邮箱：<el-input v-model="userInfo.email" placeholder="请输入邮箱"></el-input>
    验证码：<el-input v-model="userInfo.code" placeholder="请输入验证码"></el-input>
    <el-button type="success" @click="sendCode">发送验证码</el-button>
    <el-button type="success" @click="loginCode">登录</el-button>
  </div>
</template>

<style scoped>

</style>

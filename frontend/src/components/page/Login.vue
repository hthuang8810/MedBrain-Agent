<template>
  <div class="login-one">

          <el-row>
              <el-col :span="8">&nbsp;</el-col>
              <el-col :span="8">
                <br><br><br><br><br><br><br><br><br>
                <h1 align="center" style=" font-family: Helvetica;">医疗助手聊天系统</h1>
                <el-tabs type="border-card">
                  <el-tab-pane label="用户登录">
                    <el-form label-width="80px" style="background-color: white;border-radius: 3%;padding-top: 5px">

                      <el-form-item label="用户名">
                        <el-col :span="20">
                          <el-input v-model="userInfo.userName" ></el-input>
                        </el-col>
                      </el-form-item>

                      <el-form-item label="密码">
                        <el-col :span="20">
                          <el-input v-model="userInfo.password"  show-password></el-input>
                        </el-col>
                      </el-form-item>

                      <el-form-item>
                        <el-col :span="6">&nbsp;</el-col>
                        <el-col :span="10">
                          <el-button type="success" icon="el-icon-s-custom" size="mini" @click="login" >登录</el-button>
                        </el-col>
                        <el-col :span="8">&nbsp;</el-col>
                      </el-form-item>
                    </el-form>
                  </el-tab-pane>
                  <el-tab-pane label="邮箱登录">
                    <el-form label-width="80px" style="background-color: white;border-radius: 3%;padding-top: 5px">


                      <el-form-item label="邮箱">
                        <el-col :span="20">
                          <el-input v-model="userInfo.email"  ></el-input>
                        </el-col>
                      </el-form-item>

                      <el-form-item label="验证码">
                        <el-col :span="20">
                          <el-input v-model="userInfo.code" show-password></el-input>
                        </el-col>
                      </el-form-item>

                      <el-form-item>
                        <el-col :span="4">&nbsp;</el-col>
                        <el-col :span="5">
                          <el-button type="success" icon="el-icon-s-custom" size="mini" @click="sendCode">发送验证码</el-button>

                        </el-col>
                        <el-col :span="1">&nbsp;</el-col>
                        <el-col :span="5">
                          <el-button type="success" icon="el-icon-s-custom" size="mini" @click="loginCode">登录</el-button>
                        </el-col>
                        <el-col :span="8">&nbsp;</el-col>
                      </el-form-item>
                    </el-form>

                  </el-tab-pane>

                </el-tabs>

              </el-col>
              <el-col :span="8">&nbsp;</el-col>
          </el-row>
  </div>
</template>

<script>
export default {
  name: "login",
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
    sendCode() {
      const ps = { email: this.userInfo.email }
      const self = this;
      this.$http.post("http://localhost:8000/send_code", ps)
        .then(function (rs) {
          if (rs.data.code === 200) {
            self.$message.success(rs.data.data);
          } else {
            self.$message.error(rs.data.data);
          }
        })
        .catch(err => self.$message.error("发送失败：" + err));
    },
    loginCode(){//
      //定义一个请求参数
      const ps = {"email":this.userInfo.email,"code":this.userInfo.code};
      //定义一个变量，来存vue的this对象
      const self = this;
      //定义一个ajax请求
      this.$http.post("http://localhost:8000/code_verify",ps)
        .then(function(rs){
            if (rs.data.code === 200){
              self.$message.success("登录成功");
            }else{
              self.$message.error(rs.data.data);
            }
        })

    },
    login() {
      const ps = {
        userName: this.userInfo.userName,
        password: this.userInfo.password
      };
      const self = this;
      this.$http.post("http://localhost:8000/login", ps)
        .then(function (rs) {
          console.log(rs.data)
          if (rs.data.code === 200) {
            //获取服务的传来的userId,存入到本地存储里
            const userId = rs.data.data;
            localStorage.setItem("userId",userId);
            self.$message.success(rs.data.msg);
            //页面跳转到chat页面
            self.$router.push("/chat");
          } else {
            self.$message.error(rs.data.data);
          }
        })
        .catch(err => self.$message.error("登录失败：" + err));
    }
  }
}
</script>

<style scoped>
@import url('../../assets/css/login.css');
</style>

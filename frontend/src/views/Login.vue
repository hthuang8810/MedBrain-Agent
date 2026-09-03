<template>
  <div class="login-page">
    <div class="login-card">
      <div class="login-header">
        <div class="logo-icon">🏥</div>
        <h1>MedBrain</h1>
        <p>智能医疗助手</p>
      </div>

      <el-tabs v-model="activeTab" class="login-tabs">
        <!-- 用户名密码登录 -->
        <el-tab-pane label="密码登录" name="password">
          <el-form
            ref="passwordFormRef"
            :model="passwordForm"
            :rules="passwordRules"
            label-position="top"
            @submit.prevent
          >
            <el-form-item label="用户名" prop="userName">
              <el-input
                v-model="passwordForm.userName"
                placeholder="请输入用户名"
                prefix-icon="User"
                size="large"
              />
            </el-form-item>
            <el-form-item label="密码" prop="password">
              <el-input
                v-model="passwordForm.password"
                type="password"
                placeholder="请输入密码"
                prefix-icon="Lock"
                size="large"
                show-password
                @keyup.enter="handlePasswordLogin"
              />
            </el-form-item>
            <el-form-item>
              <el-button
                type="primary"
                size="large"
                :loading="passwordLoading"
                class="login-btn"
                @click="handlePasswordLogin"
              >
                登 录
              </el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>

        <!-- 邮箱验证码登录 -->
        <el-tab-pane label="邮箱登录" name="email">
          <el-form
            ref="emailFormRef"
            :model="emailForm"
            :rules="emailRules"
            label-position="top"
            @submit.prevent
          >
            <el-form-item label="邮箱" prop="email">
              <el-input
                v-model="emailForm.email"
                placeholder="请输入邮箱地址"
                prefix-icon="Message"
                size="large"
              />
            </el-form-item>
            <el-form-item label="验证码" prop="code">
              <div class="code-row">
                <el-input
                  v-model="emailForm.code"
                  placeholder="请输入验证码"
                  size="large"
                  @keyup.enter="handleEmailLogin"
                />
                <el-button
                  type="primary"
                  size="large"
                  :loading="sendCodeLoading"
                  :disabled="codeCooldown > 0"
                  @click="handleSendCode"
                >
                  {{ codeCooldown > 0 ? `${codeCooldown}s` : '发送验证码' }}
                </el-button>
              </div>
            </el-form-item>
            <el-form-item>
              <el-button
                type="primary"
                size="large"
                :loading="emailLoading"
                class="login-btn"
                @click="handleEmailLogin"
              >
                登 录
              </el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>

        <!-- 注册 -->
        <el-tab-pane label="注册" name="register">
          <el-form
            ref="registerFormRef"
            :model="registerForm"
            :rules="registerRules"
            label-position="top"
            @submit.prevent
          >
            <el-form-item label="用户名" prop="userName">
              <el-input
                v-model="registerForm.userName"
                placeholder="请输入用户名"
                prefix-icon="User"
                size="large"
              />
            </el-form-item>
            <el-form-item label="密码" prop="password">
              <el-input
                v-model="registerForm.password"
                type="password"
                placeholder="请输入密码"
                prefix-icon="Lock"
                size="large"
                show-password
              />
            </el-form-item>
            <el-form-item label="确认密码" prop="confirmPassword">
              <el-input
                v-model="registerForm.confirmPassword"
                type="password"
                placeholder="请再次输入密码"
                prefix-icon="Lock"
                size="large"
                show-password
                @keyup.enter="handleRegister"
              />
            </el-form-item>
            <el-form-item label="邮箱（选填）" prop="email">
              <el-input
                v-model="registerForm.email"
                placeholder="请输入邮箱地址"
                prefix-icon="Message"
                size="large"
              />
            </el-form-item>
            <el-form-item>
              <el-button
                type="primary"
                size="large"
                :loading="registerLoading"
                class="login-btn"
                @click="handleRegister"
              >
                注 册
              </el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>
      </el-tabs>
    </div>
  </div>
</template>

<script setup>
import { ref, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { login, sendCode, codeVerify, register } from '@/api'

const router = useRouter()

// ---- Tab 切换 ----
const activeTab = ref('password')

// ---- 密码登录 ----
const passwordFormRef = ref()
const passwordLoading = ref(false)
const passwordForm = ref({
  userName: '',
  password: '',
})
const passwordRules = {
  userName: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
}

async function handlePasswordLogin() {
  const valid = await passwordFormRef.value?.validate().catch(() => false)
  if (!valid) return

  passwordLoading.value = true
  try {
    const { data } = await login(passwordForm.value.userName, passwordForm.value.password)
    if (data.code === 200) {
      localStorage.setItem('userId', String(data.data))
      ElMessage.success('登录成功')
      router.push('/chat')
    } else {
      ElMessage.error(data.data || '登录失败')
    }
  } catch (err) {
    ElMessage.error('网络错误：' + err.message)
  } finally {
    passwordLoading.value = false
  }
}

// ---- 邮箱登录 ----
const emailFormRef = ref()
const emailLoading = ref(false)
const sendCodeLoading = ref(false)
const codeCooldown = ref(0)
let cooldownTimer = null

const emailForm = ref({
  email: '',
  code: '',
})
const emailRules = {
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '邮箱格式不正确', trigger: 'blur' },
  ],
  code: [{ required: true, message: '请输入验证码', trigger: 'blur' }],
}

async function handleSendCode() {
  if (!emailForm.value.email) {
    ElMessage.warning('请先输入邮箱')
    return
  }

  sendCodeLoading.value = true
  try {
    const { data } = await sendCode(emailForm.value.email)
    if (data.code === 200) {
      ElMessage.success('验证码已发送')
      // 60 秒冷却
      codeCooldown.value = 60
      cooldownTimer = setInterval(() => {
        codeCooldown.value--
        if (codeCooldown.value <= 0) clearInterval(cooldownTimer)
      }, 1000)
    } else {
      ElMessage.error(data.data || '发送失败')
    }
  } catch (err) {
    ElMessage.error('网络错误：' + err.message)
  } finally {
    sendCodeLoading.value = false
  }
}

async function handleEmailLogin() {
  const valid = await emailFormRef.value?.validate().catch(() => false)
  if (!valid) return

  emailLoading.value = true
  try {
    const { data } = await codeVerify(emailForm.value.email, emailForm.value.code)
    if (data.code === 200) {
      // 邮箱登录成功 — 用邮箱作为临时 userId 存入 localStorage
      localStorage.setItem('userId', emailForm.value.email)
      ElMessage.success('登录成功')
      router.push('/chat')
    } else {
      ElMessage.error(data.data || '验证失败')
    }
  } catch (err) {
    ElMessage.error('网络错误：' + err.message)
  } finally {
    emailLoading.value = false
  }
}

onUnmounted(() => {
  if (cooldownTimer) clearInterval(cooldownTimer)
})

// ---- 注册 ----
const registerFormRef = ref()
const registerLoading = ref(false)
const registerForm = ref({
  userName: '',
  password: '',
  confirmPassword: '',
  email: '',
})
const registerRules = {
  userName: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码至少6位', trigger: 'blur' },
  ],
  confirmPassword: [
    { required: true, message: '请再次输入密码', trigger: 'blur' },
    {
      validator: (rule, value, callback) => {
        if (value !== registerForm.value.password) {
          callback(new Error('两次输入的密码不一致'))
        } else {
          callback()
        }
      },
      trigger: 'blur',
    },
  ],
  email: [
    { type: 'email', message: '邮箱格式不正确', trigger: 'blur' },
  ],
}

async function handleRegister() {
  const valid = await registerFormRef.value?.validate().catch(() => false)
  if (!valid) return

  registerLoading.value = true
  try {
    const { data } = await register(
      registerForm.value.userName,
      registerForm.value.password,
      registerForm.value.email,
    )
    if (data.code === 200) {
      localStorage.setItem('userId', String(data.data))
      ElMessage.success('注册成功')
      router.push('/chat')
    } else {
      ElMessage.error(data.data || '注册失败')
    }
  } catch (err) {
    ElMessage.error('网络错误：' + err.message)
  } finally {
    registerLoading.value = false
  }
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.login-card {
  width: 420px;
  padding: 40px 36px 24px;
  background: rgba(255, 255, 255, 0.92);
  backdrop-filter: blur(20px);
  border-radius: 20px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.2);
}

.login-header {
  text-align: center;
  margin-bottom: 28px;
}

.logo-icon {
  font-size: 48px;
  margin-bottom: 8px;
}

.login-header h1 {
  font-size: 28px;
  font-weight: 700;
  color: #1f2937;
  letter-spacing: -0.5px;
}

.login-header p {
  font-size: 14px;
  color: #6b7280;
  margin-top: 4px;
}

.login-tabs :deep(.el-tabs__nav) {
  width: 100%;
}

.login-tabs :deep(.el-tabs__item) {
  width: 33.33%;
  text-align: center;
  font-size: 15px;
  font-weight: 500;
}

.login-btn {
  width: 100%;
  height: 44px;
  font-size: 16px;
  font-weight: 600;
  letter-spacing: 4px;
  border-radius: 10px;
}

.code-row {
  display: flex;
  gap: 10px;
  width: 100%;
}

.code-row .el-input {
  flex: 1;
}

.code-row .el-button {
  flex-shrink: 0;
  width: 120px;
}
</style>

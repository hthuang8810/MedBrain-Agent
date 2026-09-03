<template>
  <div class="auth-page">
    <!-- 装饰光斑 -->
    <div class="deco deco-1"></div>
    <div class="deco deco-2"></div>
    <div class="deco deco-3"></div>

    <div class="auth-container">
      <!-- 左侧品牌区 -->
      <div class="auth-left">
        <div class="brand">
          <span class="brand-logo">
            <svg width="34" height="34" viewBox="0 0 40 40" aria-hidden="true">
              <rect x="2" y="2" width="36" height="36" rx="11" fill="#5b6ce0" />
              <path d="M20 13v14M13 20h14" stroke="#ffffff" stroke-width="4" stroke-linecap="round" />
              <circle cx="32" cy="9" r="4.5" fill="#a7b2f2" />
            </svg>
          </span>
          <span class="brand-name">MedBrain_Agent</span>
        </div>

        <div class="brand-content">
          <h1 class="brand-title">智能问诊 · 健康随行</h1>
          <p class="brand-sub">专业医疗建议，仅供参考</p>

          <ul class="features">
            <li>
              <span class="feature-icon"><el-icon><ChatDotRound /></el-icon></span>
              <div class="feature-text">
                <h3>智能问答</h3>
                <p>专业 AI 助手，7x24 小时为您解答健康疑问</p>
              </div>
            </li>
            <li>
              <span class="feature-icon"><el-icon><FirstAidKit /></el-icon></span>
              <div class="feature-text">
                <h3>健康管理</h3>
                <p>记录健康数据，管理个人健康档案</p>
              </div>
            </li>
            <li>
              <span class="feature-icon"><el-icon><Lock /></el-icon></span>
              <div class="feature-text">
                <h3>隐私安全</h3>
                <p>多重加密保护，确保您的数据安全</p>
              </div>
            </li>
          </ul>
        </div>
      </div>

      <!-- 右侧注册卡片 -->
      <div class="auth-right">
        <div class="auth-card">
          <div class="card-header">
            <span class="card-logo">
              <svg width="42" height="42" viewBox="0 0 40 40" aria-hidden="true">
                <rect x="2" y="2" width="36" height="36" rx="11" fill="#5b6ce0" />
                <path d="M20 13v14M13 20h14" stroke="#ffffff" stroke-width="4" stroke-linecap="round" />
                <circle cx="32" cy="9" r="4.5" fill="#a7b2f2" />
              </svg>
            </span>
            <h2 class="card-title">MedBrain_Agent</h2>
            <p class="card-sub">医疗健康智能助手</p>
          </div>

          <div class="seg">
            <div class="seg-item active">创建账号</div>
          </div>

          <el-form
            ref="registerFormRef"
            :model="registerForm"
            :rules="registerRules"
            label-position="top"
            @submit.prevent
          >
            <el-form-item prop="userName">
              <el-input
                v-model="registerForm.userName"
                placeholder="请输入用户名"
                size="large"
              >
                <template #prefix><el-icon><User /></el-icon></template>
              </el-input>
            </el-form-item>
            <el-form-item prop="password">
              <el-input
                v-model="registerForm.password"
                type="password"
                placeholder="请输入密码"
                size="large"
                show-password
              >
                <template #prefix><el-icon><Lock /></el-icon></template>
              </el-input>
            </el-form-item>
            <el-form-item prop="confirmPassword">
              <el-input
                v-model="registerForm.confirmPassword"
                type="password"
                placeholder="请再次输入密码"
                size="large"
                show-password
                @keyup.enter="handleRegister"
              >
                <template #prefix><el-icon><Lock /></el-icon></template>
              </el-input>
            </el-form-item>
            <el-form-item prop="email">
              <el-input
                v-model="registerForm.email"
                placeholder="邮箱（选填）"
                size="large"
              >
                <template #prefix><el-icon><Message /></el-icon></template>
              </el-input>
            </el-form-item>
            <el-button
              class="primary-btn"
              :loading="registerLoading"
              @click="handleRegister"
            >
              {{ registerLoading ? '注册中...' : '注  册' }}
            </el-button>
          </el-form>

          <div class="card-foot">
            已有账号？
            <router-link class="link" to="/">登录</router-link>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { User, Lock, Message, ChatDotRound, FirstAidKit } from '@element-plus/icons-vue'
import { register } from '@/api'

const router = useRouter()

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
.auth-page {
  position: relative;
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  background: linear-gradient(150deg, #fbfcfd 0%, #f1f5f4 45%, #e5efe9 100%);
}

/* 背景装饰光斑 */
.deco {
  position: absolute;
  border-radius: 50%;
  filter: blur(40px);
  opacity: 0.55;
  pointer-events: none;
}
.deco-1 {
  width: 420px;
  height: 420px;
  top: -120px;
  right: -80px;
  background: radial-gradient(circle, #d9e6ee 0%, transparent 70%);
}
.deco-2 {
  width: 320px;
  height: 320px;
  bottom: -80px;
  left: 60px;
  background: radial-gradient(circle, #dcebe2 0%, transparent 70%);
}
.deco-3 {
  width: 300px;
  height: 300px;
  top: 30%;
  left: 38%;
  background: radial-gradient(circle, #e8eef6 0%, transparent 70%);
}

.auth-container {
  position: relative;
  z-index: 1;
  width: 100%;
  max-width: 1280px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 48px;
  padding: 0 48px;
}

/* 左侧品牌区 */
.auth-left {
  flex: 1;
  min-width: 0;
  max-width: 480px;
}

.brand {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 140px;
}
.brand-logo {
  display: inline-flex;
}
.brand-name {
  font-size: 20px;
  font-weight: 700;
  color: #3a4657;
  letter-spacing: 0.2px;
}

.brand-title {
  font-size: 34px;
  font-weight: 700;
  color: #1f2937;
  letter-spacing: 1px;
  margin-bottom: 10px;
}
.brand-sub {
  font-size: 16px;
  color: #86919e;
  margin-bottom: 44px;
  padding-left: 2px;
}

.features {
  list-style: none;
  display: flex;
  flex-direction: column;
  gap: 26px;
}
.features li {
  display: flex;
  align-items: flex-start;
  gap: 16px;
}
.feature-icon {
  width: 44px;
  height: 44px;
  flex-shrink: 0;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 12px;
  background: #ffffff;
  color: #5b6ce0;
  font-size: 20px;
  box-shadow: 0 4px 14px rgba(33, 43, 66, 0.07);
}
.feature-text h3 {
  font-size: 16px;
  font-weight: 600;
  color: #273446;
  margin-bottom: 4px;
}
.feature-text p {
  font-size: 14px;
  color: #8a94a1;
  line-height: 1.6;
}

/* 右侧卡片 */
.auth-right {
  flex-shrink: 0;
}

.auth-card {
  width: 420px;
  padding: 44px 40px 30px;
  background: #ffffff;
  border-radius: 20px;
  box-shadow: 0 24px 60px rgba(31, 41, 55, 0.1);
}

.card-header {
  text-align: center;
  margin-bottom: 22px;
}
.card-logo {
  display: inline-flex;
  margin-bottom: 10px;
}
.card-title {
  font-size: 24px;
  font-weight: 700;
  color: #303c4d;
  letter-spacing: 0.3px;
}
.card-sub {
  font-size: 14px;
  color: #8a94a1;
  margin-top: 6px;
}

/* 登录方式切换 */
.seg {
  display: flex;
  justify-content: center;
  border-bottom: 1px solid #eef1f4;
  margin-bottom: 26px;
}
.seg-item {
  position: relative;
  padding: 0 2px 12px;
  font-size: 15px;
  color: #a5aeba;
  cursor: pointer;
  transition: color 0.2s;
}
.seg-item.active {
  color: #273446;
  font-weight: 600;
}
.seg-item.active::after {
  content: '';
  position: absolute;
  left: 0;
  right: 0;
  bottom: -1px;
  height: 2px;
  border-radius: 2px;
  background: #5b6ce0;
}

.auth-card :deep(.el-form-item) {
  margin-bottom: 22px;
}
.auth-card :deep(.el-form-item__error) {
  padding-top: 4px;
}
.auth-card :deep(.el-input__wrapper) {
  border-radius: 10px;
  padding: 4px 14px;
}
.auth-card :deep(.el-input__inner) {
  height: 40px;
}
.auth-card :deep(.el-input__prefix) {
  color: #a8b0bb;
  margin-right: 6px;
}
.auth-card :deep(.el-button + .el-button) {
  margin-left: 0;
}

/* 黑色主按钮 */
.primary-btn {
  width: 100%;
  height: 46px;
  margin-top: 6px;
  border-radius: 10px;
  background: #1c1f26;
  border-color: #1c1f26;
  color: #fff;
  font-size: 16px;
  font-weight: 600;
  letter-spacing: 3px;
  transition: background 0.2s;
}
.primary-btn:hover,
.primary-btn:focus {
  background: #000;
  border-color: #000;
  color: #fff;
}

.card-foot {
  margin-top: 26px;
  text-align: center;
  font-size: 14px;
  color: #8a94a1;
}
.card-foot .link {
  margin-left: 4px;
  color: #5b6ce0;
  font-weight: 500;
  text-decoration: none;
}
.card-foot .link:hover {
  text-decoration: underline;
}

@media (max-width: 960px) {
  .auth-container {
    flex-direction: column;
    padding: 24px;
    gap: 28px;
  }
  .auth-left {
    max-width: 100%;
  }
  .brand {
    margin-bottom: 24px;
  }
  .auth-card {
    width: 100%;
  }
}
</style>

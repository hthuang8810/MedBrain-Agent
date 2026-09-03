<template>
  <aside class="sidebar">
    <div class="sidebar-top">
      <div class="app-brand">
        <span class="brand-icon">
          <svg width="30" height="30" viewBox="0 0 40 40" aria-hidden="true">
            <rect x="2" y="2" width="36" height="36" rx="11" fill="#5b6ce0" />
            <path d="M20 13v14M13 20h14" stroke="#ffffff" stroke-width="4" stroke-linecap="round" />
            <circle cx="32" cy="9" r="4.5" fill="#a7b2f2" />
          </svg>
        </span>
        <span class="brand-text">MedBrain_Agent</span>
      </div>

      <div class="user-profile">
        <span class="profile-avatar">{{ profileInitial }}</span>
        <div class="profile-meta">
          <div class="profile-name">{{ userName }}</div>
          <span class="profile-role">普通用户</span>
        </div>
        <el-icon class="profile-caret"><ArrowDown /></el-icon>
      </div>
    </div>

    <div class="history-head">
      <span class="history-label">历史会话</span>
      <button class="new-chat-btn" @click="$emit('newChat')">
        <el-icon><Plus /></el-icon>
        新建会话
      </button>
    </div>

    <div class="chat-list">
      <div
        v-for="chat in chatList"
        :key="chat.id"
        class="chat-item"
        :class="{ active: chat.id === activeId }"
        @click="$emit('selectChat', chat.id)"
      >
        <el-icon class="chat-icon"><ChatDotRound /></el-icon>
        <span class="chat-title">{{ chat.title }}</span>
      </div>
    </div>

    <div class="sidebar-bottom">
      <div class="nav-item">
        <el-icon><User /></el-icon>
        <span>个人中心</span>
      </div>
      <div class="nav-item" @click="handleLogout">
        <el-icon><SwitchButton /></el-icon>
        <span>退出登录</span>
      </div>
    </div>
  </aside>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { Plus, ChatDotRound, User, SwitchButton, ArrowDown } from '@element-plus/icons-vue'

const props = defineProps({
  chatList: { type: Array, required: true },
  activeId: { type: String, required: true },
})

defineEmits(['newChat', 'selectChat'])

const router = useRouter()

const userName = computed(() => {
  const id = localStorage.getItem('userId') || ''
  return id.length > 12 ? id.slice(0, 12) + '...' : id || '未登录'
})

const profileInitial = computed(() => {
  const name = userName.value || ''
  return name.charAt(0).toUpperCase() || 'U'
})

function handleLogout() {
  localStorage.removeItem('userId')
  router.push('/')
}
</script>

<style scoped>
.sidebar {
  width: 280px;
  height: 100vh;
  background: #ffffff;
  color: #273446;
  display: flex;
  flex-direction: column;
  flex-shrink: 0;
  overflow: hidden;
}

.sidebar-top {
  padding: 22px 20px 18px;
}

.app-brand {
  display: flex;
  align-items: center;
  gap: 10px;
}

.brand-icon {
  display: inline-flex;
}

.brand-text {
  font-size: 18px;
  font-weight: 700;
  color: #2c3948;
  letter-spacing: -0.2px;
}

.user-profile {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-top: 22px;
  padding: 12px 14px;
  border-radius: 12px;
  background: #f5f7f9;
  transition: background 0.15s;
}

.user-profile:hover {
  background: #eef2f5;
}

.profile-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  font-weight: 700;
  color: #fff;
  background: linear-gradient(135deg, #6f83e8, #8c9bef);
}

.profile-meta {
  flex: 1;
  min-width: 0;
}

.profile-name {
  font-size: 14px;
  font-weight: 600;
  color: #273446;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.profile-role {
  display: inline-block;
  margin-top: 4px;
  font-size: 11px;
  color: #3ba47a;
  background: #e5f6ee;
  padding: 2px 8px;
  border-radius: 6px;
}

.profile-caret {
  color: #9aa3ad;
  font-size: 14px;
}

/* 历史会话头 */
.history-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 4px 20px 12px;
}

.history-label {
  font-size: 13px;
  color: #9aa3ad;
}

.new-chat-btn {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 5px 12px;
  border: 1px solid #e2e8ed;
  border-radius: 16px;
  background: #fff;
  color: #3a4a5c;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.15s;
}

.new-chat-btn:hover {
  background: #eef4f1;
  border-color: #d3e5db;
  color: #2f7d5c;
}

.chat-list {
  flex: 1;
  overflow-y: auto;
  padding: 0 12px;
}

.chat-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 11px 12px;
  border-radius: 10px;
  cursor: pointer;
  font-size: 14px;
  color: #4a5766;
  margin-bottom: 2px;
  transition: background 0.15s;
}

.chat-item:hover {
  background: #f3f6f8;
}

.chat-item.active {
  background: #e9f6ef;
  color: #2b7c5a;
  font-weight: 500;
}

.chat-icon {
  font-size: 16px;
  color: #9aa3ad;
  flex-shrink: 0;
}

.chat-item.active .chat-icon {
  color: #3ba47a;
}

.chat-title {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.sidebar-bottom {
  padding: 10px 12px 16px;
  border-top: 1px solid #eef1f4;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 11px 12px;
  border-radius: 10px;
  cursor: pointer;
  font-size: 14px;
  color: #4a5766;
  transition: background 0.15s;
}

.nav-item:hover {
  background: #f3f6f8;
}

.nav-item .el-icon {
  color: #9aa3ad;
  font-size: 16px;
}
</style>

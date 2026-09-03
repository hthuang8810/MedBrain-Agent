<template>
  <div class="chat-layout">
    <!-- 左侧边栏 -->
    <ChatSidebar
      :chat-list="chatList"
      :active-id="activeChatId"
      @new-chat="newChat"
      @select-chat="selectChat"
      @delete-chat="deleteChat"
    />

    <!-- 右侧聊天区 -->
    <div class="chat-main-area">
      <!-- 顶栏 -->
      <header class="chat-topbar">
        <div class="topbar-left">
          <span class="topbar-logo">
            <svg width="32" height="32" viewBox="0 0 40 40" aria-hidden="true">
              <rect x="2" y="2" width="36" height="36" rx="11" fill="#5b6ce0" />
              <path d="M20 13v14M13 20h14" stroke="#ffffff" stroke-width="4" stroke-linecap="round" />
              <circle cx="32" cy="9" r="4.5" fill="#a7b2f2" />
            </svg>
          </span>
          <div class="topbar-titles">
            <h2>智能问诊</h2>
            <p>专业医疗建议，仅供参考</p>
          </div>
        </div>
        <el-icon class="topbar-bell"><Bell /></el-icon>
      </header>

      <!-- 消息列表 -->
      <div class="messages-container" ref="messagesContainer">
        <!-- 空状态 -->
        <div v-if="currentChat.messages.length === 0 && !thinking" class="empty-state">
          <div class="empty-icon">🏥</div>
          <h3>MedBrain 医疗助手</h3>
          <p>我是您的智能医疗助手，可以帮您查询医疗信息、分析数据、生成报告</p>
        </div>

        <!-- 消息 -->
        <ChatMessage
          v-for="(msg, idx) in currentChat.messages"
          :key="idx"
          :message="msg"
        />

        <!-- 工具调用状态 / 思考中 -->
        <div v-if="toolStatus" class="tool-status">{{ toolStatus }}</div>
        <TypingIndicator v-if="thinking" />

        <!-- 错误提示 -->
        <div v-if="errorMsg" class="error-msg">
          <el-alert :title="errorMsg" type="error" show-icon :closable="true" @close="errorMsg = ''" />
        </div>
      </div>

      <!-- 输入区 -->
      <ChatInput
        ref="chatInputRef"
        :disabled="thinking"
        :is-recording="isRecording"
        :show-quick-questions="currentChat.messages.length === 0"
        @send="sendMessage"
        @quick-send="quickSend"
        @toggle-recording="toggleRecording"
      />
    </div>
  </div>
</template>

<script setup>
import { reactive, ref, computed, nextTick, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Bell } from '@element-plus/icons-vue'
import ChatSidebar from '@/components/ChatSidebar.vue'
import ChatMessage from '@/components/ChatMessage.vue'
import ChatInput from '@/components/ChatInput.vue'
import TypingIndicator from '@/components/TypingIndicator.vue'
import { chatStream, speechToText } from '@/api'

// ---- 对话管理 ----
const chatList = ref([
  { id: '1', title: '新对话', messages: [] },
])
const activeChatId = ref('1')

const currentChat = computed(() => {
  return chatList.value.find(c => c.id === activeChatId.value) || { title: '', messages: [] }
})

function newChat() {
  const id = Date.now().toString()
  chatList.value.push({ id, title: '新对话', messages: [] })
  activeChatId.value = id
}

function selectChat(id) {
  activeChatId.value = id
}

async function deleteChat(id) {
  const chat = chatList.value.find(c => c.id === id)
  if (!chat) return

  try {
    await ElMessageBox.confirm(
      `确定要删除对话“${chat.title}”吗？删除后不可恢复。`,
      '删除对话',
      { confirmButtonText: '删除', cancelButtonText: '取消', type: 'warning' }
    )
  } catch {
    return // 用户取消
  }

  const idx = chatList.value.findIndex(c => c.id === id)
  if (idx === -1) return
  chatList.value.splice(idx, 1)

  // 删除的是当前会话，则切到另一个会话；若已无会话则新建一个
  if (activeChatId.value === id) {
    if (chatList.value.length === 0) {
      newChat()
    } else {
      activeChatId.value = chatList.value[0].id
    }
  }
}

// ---- 消息发送 ----
const thinking = ref(false)
const errorMsg = ref('')
const toolStatus = ref('')
const messagesContainer = ref()
const chatInputRef = ref()

async function sendMessage(text) {
  if (!text.trim()) return

  // 添加用户消息
  currentChat.value.messages.push({ role: 'user', content: text })

  // 更新标题（取第一条消息前 12 字）
  if (currentChat.value.messages.filter(m => m.role === 'user').length === 1) {
    currentChat.value.title = text.substring(0, 12) + (text.length > 12 ? '...' : '')
  }

  // 创建空的 AI 回复消息（必须用 reactive 包裹，否则流式追加 content 时不触发重渲染）
  const aiMsg = reactive({ role: 'assistant', content: '' })
  currentChat.value.messages.push(aiMsg)

  thinking.value = true
  errorMsg.value = ''
  scrollToBottom()

  try {
    const userId = localStorage.getItem('userId') || 'anonymous'
    // 消费 SSE 流
    for await (const item of chatStream(text, userId)) {
      if (item.type === 'token') {
        aiMsg.content += item.text
      } else if (item.type === 'tool') {
        toolStatus.value = '正在调用工具：' + item.name + ' ...'
      }
      scrollToBottom()
    }
  } catch (err) {
    errorMsg.value = '回复出错：' + err.message
    // 如果 AI 消息为空，移除它
    if (!aiMsg.content) {
      const idx = currentChat.value.messages.indexOf(aiMsg)
      if (idx !== -1) currentChat.value.messages.splice(idx, 1)
    }
  } finally {
    thinking.value = false
    toolStatus.value = ''
    scrollToBottom()
  }
}

function quickSend(question) {
  sendMessage(question)
}

// ---- 滚动到底部 ----
function scrollToBottom() {
  nextTick(() => {
    const el = messagesContainer.value
    if (el) el.scrollTop = el.scrollHeight
  })
}

// ---- 语音输入 ----
const isRecording = ref(false)
let mediaRecorder = null
let audioChunks = []

async function toggleRecording() {
  if (isRecording.value) {
    stopRecording()
  } else {
    await startRecording()
  }
}

async function startRecording() {
  try {
    if (!navigator.mediaDevices?.getUserMedia) {
      ElMessage.error('当前浏览器不支持麦克风')
      return
    }

    const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
    mediaRecorder = new MediaRecorder(stream)
    audioChunks = []

    mediaRecorder.ondataavailable = (e) => audioChunks.push(e.data)

    mediaRecorder.onstop = async () => {
      const blob = new Blob(audioChunks, { type: 'audio/webm' })
      const formData = new FormData()
      formData.append('file', blob, 'speech.webm')

      ElMessage.info('正在识别语音...')

      try {
        const { data } = await speechToText(formData)
        if (data.code === 200) {
          chatInputRef.value?.setInput(data.data)
          ElMessage.success('识别成功')
        } else {
          ElMessage.error(data.msg || '识别失败')
        }
      } catch (err) {
        ElMessage.error('语音识别接口调用失败')
      }
    }

    mediaRecorder.start()
    isRecording.value = true
    ElMessage.success('开始录音...')
  } catch (err) {
    ElMessage.error('录音失败：' + err.message)
  }
}

function stopRecording() {
  if (mediaRecorder && isRecording.value) {
    mediaRecorder.stop()
    isRecording.value = false
  }
}

// ---- 生命周期 ----
onMounted(() => {
  // 检查登录状态
  if (!localStorage.getItem('userId')) {
    window.location.href = '/'
  }
})
</script>

<style scoped>
.chat-layout {
  display: flex;
  height: 100vh;
  overflow: hidden;
  background: #f2f4f6;
}

.chat-main-area {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
  background: #fafbfc;
  border-left: 1px solid #eef1f4;
}

.chat-topbar {
  height: 68px;
  padding: 0 24px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: #fff;
  border-bottom: 1px solid #eef1f4;
  flex-shrink: 0;
}

.topbar-left {
  display: flex;
  align-items: center;
  gap: 13px;
}

.topbar-logo {
  display: inline-flex;
}

.topbar-titles h2 {
  font-size: 18px;
  font-weight: 700;
  color: #273446;
  letter-spacing: 0.3px;
  line-height: 1.2;
}

.topbar-titles p {
  font-size: 12px;
  color: #9aa3ad;
  margin-top: 3px;
}

.topbar-bell {
  font-size: 22px;
  color: #6b7280;
  cursor: pointer;
}

.messages-container {
  flex: 1;
  overflow-y: auto;
  padding: 28px 32px;
}

/* 空状态 */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: var(--text-secondary);
  text-align: center;
}

.empty-icon {
  font-size: 56px;
  margin-bottom: 16px;
}

.empty-state h3 {
  font-size: 20px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 8px;
}

.empty-state p {
  font-size: 14px;
  max-width: 400px;
  line-height: 1.6;
}

/* 工具调用状态 */
.tool-status {
  color: #6b7280;
  font-size: 13px;
  padding: 4px 0;
  margin-left: 4px;
  text-align: center;
}
</style>

<template>
  <div class="chat-input-area">
    <!-- 快捷问题 -->
    <div class="quick-questions" v-if="showQuickQuestions">
      <button
        v-for="(q, i) in quickQuestions"
        :key="i"
        class="quick-btn"
        @click="$emit('quickSend', q)"
      >
        {{ q }}
      </button>
    </div>

    <!-- 输入框 + 按钮 -->
    <div class="input-row">
      <el-input
        ref="inputRef"
        v-model="message"
        type="textarea"
        :autosize="{ minRows: 1, maxRows: 4 }"
        placeholder="输入消息... (Enter 发送, Shift+Enter 换行)"
        resize="none"
        @keydown="handleKeydown"
      />

      <div class="btn-group">
        <el-tooltip :content="isRecording ? '停止录音' : '语音输入'" placement="top">
          <el-button
            :type="isRecording ? 'danger' : 'default'"
            circle
            @click="$emit('toggleRecording')"
          >
            <el-icon><Microphone /></el-icon>
          </el-button>
        </el-tooltip>

        <el-tooltip content="发送" placement="top">
          <el-button
            type="primary"
            circle
            :disabled="!message.trim() || disabled"
            @click="handleSend"
          >
            <el-icon><Promotion /></el-icon>
          </el-button>
        </el-tooltip>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { Microphone, Promotion } from '@element-plus/icons-vue'

const props = defineProps({
  disabled: { type: Boolean, default: false },
  isRecording: { type: Boolean, default: false },
  showQuickQuestions: { type: Boolean, default: true },
})

const emit = defineEmits(['send', 'quickSend', 'toggleRecording'])

const message = ref('')
const inputRef = ref()

const quickQuestions = [
  '医生工作负载分析',
  '张明在哪家医院工作',
  '写一份张丽华病例报告并发到邮箱',
]

function handleKeydown(e) {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault()
    handleSend()
  }
}

function handleSend() {
  if (!message.value.trim() || props.disabled) return
  emit('send', message.value.trim())
  message.value = ''
}

// 暴露 setInput 方法，供语音识别后设置文本
function setInput(text) {
  message.value = text
}

defineExpose({ setInput })
</script>

<style scoped>
.chat-input-area {
  padding: 12px 20px 16px;
  background: #fff;
  border-top: 1px solid #eee;
}

.quick-questions {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 12px;
}

.quick-btn {
  padding: 5px 14px;
  border-radius: 20px;
  border: 1px solid #e5e7eb;
  background: #f9fafb;
  color: #4b5563;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.15s;
}

.quick-btn:hover {
  background: var(--primary);
  color: #fff;
  border-color: var(--primary);
}

.input-row {
  display: flex;
  align-items: flex-end;
  gap: 10px;
}

.input-row :deep(.el-textarea__inner) {
  border-radius: var(--radius-md);
  padding: 10px 14px;
  font-size: 15px;
  line-height: 1.5;
  box-shadow: none;
  border: 1px solid #e5e7eb;
}

.input-row :deep(.el-textarea__inner:focus) {
  border-color: var(--primary);
}

.btn-group {
  display: flex;
  gap: 6px;
  flex-shrink: 0;
  padding-bottom: 2px;
}
</style>

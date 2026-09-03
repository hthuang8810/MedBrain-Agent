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

    <!-- 输入行 -->
    <div class="input-row">
      <el-tooltip :content="isRecording ? '停止录音' : '语音输入'" placement="top">
        <el-button
          class="mic-btn"
          :class="{ recording: isRecording }"
          circle
          @click="$emit('toggleRecording')"
        >
          <el-icon><Microphone /></el-icon>
        </el-button>
      </el-tooltip>

      <el-input
        ref="inputRef"
        v-model="message"
        type="textarea"
        :autosize="{ minRows: 1, maxRows: 4 }"
        placeholder="请输入您的问题..."
        resize="none"
        @keydown="handleKeydown"
      />

      <el-tooltip content="发送" placement="top">
        <el-button
          class="send-btn"
          :disabled="!message.trim() || disabled"
          circle
          @click="handleSend"
        >
          <el-icon><Promotion /></el-icon>
        </el-button>
      </el-tooltip>
    </div>

    <div class="input-foot">本服务提供的内容仅供参考，不能替代专业医生的诊断和治疗建议。</div>
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
  padding: 16px 24px 14px;
  background: #fff;
  border-top: 1px solid #eef1f4;
}

.quick-questions {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-bottom: 14px;
}

.quick-btn {
  padding: 7px 16px;
  border-radius: 18px;
  border: 1px solid #e4ebef;
  background: #fff;
  color: #4a5766;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.15s;
}

.quick-btn:hover {
  background: #eef6f1;
  border-color: #d3e5db;
  color: #2f7d5c;
}

.input-row {
  display: flex;
  align-items: center;
  gap: 10px;
}

.input-row :deep(.el-textarea__inner) {
  border-radius: 14px;
  padding: 12px 16px;
  font-size: 15px;
  line-height: 1.5;
  box-shadow: none;
  border: 1px solid #e8edf1;
  background: #fff;
}

.input-row :deep(.el-textarea__inner:focus) {
  border-color: #9fb3ec;
}

.mic-btn {
  flex-shrink: 0;
  width: 46px;
  height: 46px;
  background: #f4f6f8;
  border: 1px solid #e8edf1;
  color: #4a5766;
}

.mic-btn:hover {
  background: #eef2f5;
  border-color: #dfe7ec;
  color: #2d3748;
}

.mic-btn.recording {
  background: #fdecec;
  border-color: #f5c6c6;
  color: #e25555;
}

.send-btn {
  flex-shrink: 0;
  width: 46px;
  height: 46px;
  background: #1c1f26;
  border-color: #1c1f26;
  color: #fff;
}

.send-btn:hover,
.send-btn:focus {
  background: #000;
  border-color: #000;
  color: #fff;
}

.send-btn.is-disabled {
  background: #e8ebef;
  border-color: #e8ebef;
  color: #a5aeba;
}

.input-foot {
  margin-top: 12px;
  text-align: center;
  font-size: 12px;
  color: #a5aeba;
}
</style>

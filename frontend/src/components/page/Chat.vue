  <template>
    <el-container style="height:100vh; flex-direction: column;">
      <!-- 顶部标题 -->
      <el-header height="60px" class="chat-header">
        <h2>🏥 医疗助手聊天系统</h2>
      </el-header>

      <el-container style="flex: 1;">
        <!-- 左侧对话历史 -->
        <el-aside width="260px" class="sidebar">
          <div class="sidebar-header">
            <h3>历史对话</h3>
          </div>
          <el-menu :default-active="activeChatId" @select="selectChat">
            <el-menu-item
              v-for="chat in chatList"
              :key="chat.id"
              :index="chat.id"
            >
              <i class="el-icon-message"></i>
              <span slot="title">{{ chat.title }}</span>
            </el-menu-item>
          </el-menu>
          <div class="sidebar-footer">
            <el-button
              type="primary"
              icon="el-icon-plus"
              size="mini"
              @click="newChat"
            >
              新对话
            </el-button>
          </div>
        </el-aside>

        <!-- 右侧聊天区 -->
        <el-container>
          <!-- 聊天记录 -->
          <el-main class="chat-main" ref="chatContainer">
            <div
              v-for="(msg, idx) in currentChat.messages"
              :key="idx"
              class="chat-message"
              :class="msg.role"
            >
              <div class="avatar-wrap">
                <el-avatar
                  :src="msg.role === 'user' ? userAvatar : botAvatar"

                ></el-avatar>
              </div>
              <div class="bubble-wrap" >
                <div class="bubble"  v-html="formatMessage(msg.content)" ></div>
              </div>

            </div>



            <!-- AI思考提示 -->
            <div v-if="thinking" class="chat-message assistant">
              <div class="avatar-wrap">
                <el-avatar :src="botAvatar"></el-avatar>
              </div>
              <div class="bubble-wrap">
                <div class="bubble typing-indicator">
                  <span></span><span></span><span></span>
                </div>
              </div>
            </div>
          </el-main>

          <!-- 输入区 -->
          <el-footer height="120px" class="chat-footer">

              <div class="quick-questions">
            <el-button
              v-for="(question, index) in messagesList"
              :key="index"
              round
              @click="sendQuickQuestion(question)"
            >
              {{ question }}
            </el-button>
              </div>
            <el-input
              type="textarea"
              v-model="inputMessage"
              placeholder="请输入消息..."
              @keydown.enter.native="handleEnter"
              rows="3"
            ></el-input>
            <div class="actions">
              <!-- 语音识别按钮 -->
              <el-button
                :type="isRecording ? 'danger' : 'success'"
                :icon="isRecording ? 'el-icon-loading' : 'el-icon-microphone'"
                @click="toggleRecording"
              >
                {{ isRecording ? '停止录音' : '语音输入' }}
              </el-button>
              <el-button type="primary" @click="sendMessage" :disabled="stopSend">
                发送
              </el-button>

            </div>
          </el-footer>
        </el-container>
      </el-container>
    </el-container>
  </template>

  <script>
  import {marked} from 'marked'
  import DOMPurify from 'dompurify'


  export default {
    data() {
      return {
        userAvatar: require('@/assets/images/user.jpeg'), // 用户头像
        botAvatar: require('@/assets/images/bot.jpeg'),  // 机器人头像
        thinking: false, // AI 是否正在思考
        chatList: [ //历史对话
          {
            id: "1",
            title: "对话 1",
            messages:[],
            isRecording: false,   // 是否正在录音
            mediaRecorder: null,  // 录音对象
            audioChunks: []       // 音频数据块
          }
        ],
        isRecording: false,
        messagesList:  ["医生工作负载分析","张明在哪家医院工作","写一份张丽华病例报告，并把报告发送到病人的邮箱里",],//快捷问题

        activeChatId: "1",//选中的历史对话的id
        inputMessage: "",//用户输入问题
        stopSend: false,// 是否禁用发送按钮
      };
    },
    computed: {
      currentChat() { // 当前聊天
        console.log("查找")
        // 根据id查找当前聊天
        return this.chatList.find(c => c.id === this.activeChatId) || {messages: []};
      }
    },
    watch: {
      inputMessage(newVal) {
        // 自动控制发送按钮禁用状态
        this.stopSend = !newVal.trim();
      }
    },
    methods: {
       async toggleRecording() {
          if (this.isRecording) {
            // 停止录音
            this.stopRecording();
          } else {
            // 开始录音
            await this.startRecording();
          }
        },
       handleEnter(e) {
         if (e.shiftKey) {
      // Shift+Enter 换行
           return;
          }
         e.preventDefault(); // 阻止默认换行
         this.sendMessage();
         },

      async startRecording() {
        try {
          if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
            this.$message.error("当前浏览器不支持麦克风功能");
            return;
          }

          const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
          this.mediaRecorder = new MediaRecorder(stream);
          this.audioChunks = [];

          this.mediaRecorder.ondataavailable = event => {
            this.audioChunks.push(event.data);
          };

          this.mediaRecorder.onstop = async () => {
            // 录音停止后，上传音频进行识别
            const audioBlob = new Blob(this.audioChunks, { type: "audio/webm" });
            const formData = new FormData();
            formData.append("file", audioBlob, "speech.webm");

            this.$message.info("正在识别语音，请稍候...");

            try {
              const res = await this.$http.post("http://localhost:8000/speech_to_text", formData, {
                headers: { "Content-Type": "multipart/form-data" }
              });

              if (res.data.code === 200) {
                this.inputMessage = (this.inputMessage + res.data.data).trim();
                this.$message.success("语音识别成功");
              } else {
                this.$message.error("识别失败：" + res.data.msg);
              }
            } catch (err) {
              console.error(err);
              this.$message.error("语音识别接口调用失败");
            }
          };

          this.mediaRecorder.start();
          this.isRecording = true;
          this.$message.success("🎙️ 开始录音，请讲话...");
        } catch (err) {
          console.error("录音失败：", err);
          this.$message.error("录音失败：" + err.message);
        }
      },

      stopRecording() {
        if (this.mediaRecorder && this.isRecording) {
          this.mediaRecorder.stop();
          this.isRecording = false;
          this.$message.success("录音已停止，正在上传识别...");
        }
      },
      sendQuickQuestion( question){ //快捷问题
        this.inputMessage = question;
        this.sendMessage();
      },
      // isOpen() { // 判断输入框是否为空, 如果为空则禁用发送按钮
      //   if (this.inputMessage.trim()) {
      //     this.stopSend = false;
      //   } else {
      //     this.stopSend = true;
      //   }
      // },

      formatMessage(content) { //// 格式化消息
        // 使用marked解析markdown并净化HTML
        return DOMPurify.sanitize(marked.parse(content || ''))
      },
      // 新建对话
      newChat() {
        const id = Date.now().toString();
        this.chatList.push({id, title: "新对话", messages: []});
        this.activeChatId = id;
      },
      // 选择历史对话
      selectChat(id) {
        this.activeChatId = id;
        console.log(this.currentChat);
        console.log(this.chatList)
      },
      // 发送消息
      sendMessage() {
        //判断输入框是否为空
        if (!this.inputMessage.trim()) return;
        //添加用户消息
        const userMsg = {role: "user", content: this.inputMessage};
        this.currentChat.messages.push(userMsg);

        //更新新对话的标题
        this.currentChat.title = this.currentChat.messages[0].content.substring(0, 10);
        //显示AI思考提示
        this.thinking = true;
        const self = this;
         // 获取本地存储的userId信息
        const userId = localStorage.getItem("userId");
        const ps ={"questions": this.inputMessage,"userId":userId}
        this.$http.post("http://localhost:8000/chat", ps)
          .then(function (rs) {

            //关闭AI思考提示
            self.thinking = false;
            if (rs.data.code === 200) {
               console.log(rs.data.msg)
              //  显示答案。流式输出答案
              self.streamReply(rs.data.data[0]);
              //清空输入框
              self.inputMessage = "";
              //禁用按钮
              self.stopSend = true;
            }
          })
      },

      // 流式输出
      streamReply(fullText) {

        let i = 0;
        const reply = {role: "assistant", content: ""};
        // 添加回复消息
        this.currentChat.messages.push(reply);
        // 模拟流式输出
        const iv = setInterval(() => {
          // 输出一个字符
          if (i < fullText.length) {

            reply.content += fullText[i];
            i++;

            this.scrollToBottom();
          } else {
            clearInterval(iv);

          }
        }, 40);
      },
      // 滚动到底部
      scrollToBottom() {
        this.$nextTick(() => {
          const container =
            (this.$refs.chatContainer && this.$refs.chatContainer.$el) ||
            this.$refs.chatContainer;
          if (!container) return;
          container.scrollTop = container.scrollHeight;
        });
      }
    }
  };
  </script>

  <style scoped>
  /* 左侧对话列表 */
  .sidebar {
    display: flex;
    flex-direction: column;
    background: #f7f7f7;
    border-right: 1px solid #ddd;
  }

  .sidebar-header {
    padding: 15px;
    font-weight: bold;
    text-align: center;
  }

  .sidebar-footer {
    margin-top: auto;
    padding: 10px;
    text-align: center;
    border-top: 1px solid #eee;
  }

  /* 聊天区 */
  .chat-main {
    height: calc(100vh - 120px);
    overflow-y: auto;
    padding: 16px;
    background: #fafafa;
  }

  .chat-message {
    display: flex;
    align-items: flex-start;
    gap: 12px;
    margin: 10px 0;
  }

  .chat-message.user {
    flex-direction: row-reverse;
  }

  .avatar-wrap {
    width: 40px;
    flex: 0 0 40px;
    display: flex;
  }

  .bubble-wrap {
    display: flex;
    max-width: calc(100% - 60px);
  }

  .bubble {
    display: inline-block;
    padding: 1px 24px;
    border-radius: 12px;

    word-break: break-word;
    white-space: pre-wrap;
    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.06);
  }

  .user .bubble {
    background: #409eff;
    color: #fff;
    border-bottom-right-radius: 6px;
  }

  .assistant .bubble {
    background: #fff;
    color: #333;
    border: 1px solid #eee;
    border-bottom-left-radius: 6px;
  }

  /* 输入区 */
  .chat-footer {
    border-top: 1px solid #eee;
    padding: 10px;
  }

  .actions {
    text-align: right;
    margin-top: 8px;
  }

  .typing-indicator {
    display: flex;
    align-items: center;
    gap: 4px;
    background: #fff;
    border: 1px solid #eee;
    color: #333;
    padding: 8px 12px;
    border-radius: 12px;
    width: auto;
  }

  .typing-indicator span {
    display: inline-block;
    width: 6px;
    height: 6px;
    background: #999;
    border-radius: 50%;
    animation: blink 1.4s infinite;
  }

  .typing-indicator span:nth-child(2) {
    animation-delay: 0.2s;
  }

  .typing-indicator span:nth-child(3) {
    animation-delay: 0.4s;
  }

  @keyframes blink {
    0%, 80%, 100% {
      transform: scale(0.6);
      opacity: 0.3;
    }
    40% {
      transform: scale(1);
      opacity: 1;
    }
  }

  .chat-header {
    background: linear-gradient(135deg, #4b9cdb, #4cd4b0);
    display: flex;
    align-items: center;
    justify-content: center;
    color: #fff;
    font-weight: bold;
    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.15);
  }

  .chat-header h2 {
    font-size: 20px;
    margin: 0;
    letter-spacing: 1px;
  }
  .chart-container {
    width: 600px;
    height: 500px;
    margin-left: 10px; /* 控制距离左边的距离，可根据头像和气泡的间距微调 */
    margin-top: 88px;
    background-color:skyblue;
  }
.quick-questions {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  margin-top: 5px;
}

.quick-questions .el-button {
  margin: 0 5px 5px 0;
}
  </style>

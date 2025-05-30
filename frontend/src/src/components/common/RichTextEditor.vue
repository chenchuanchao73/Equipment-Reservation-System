<template>
  <div class="rich-text-editor">
    <quill-editor
      v-model="content"
      :options="editorOptions"
      :placeholder="placeholder"
      @change="onChange"
    ></quill-editor>
    <div v-if="showTip" class="editor-tip">{{ $t('admin.richTextEditorTip') }}</div>
  </div>
</template>

<script>
import { mapGetters } from 'vuex'
import axios from 'axios'

export default {
  name: 'RichTextEditor',
  
  props: {
    value: {
      type: String,
      default: ''
    },
    placeholder: {
      type: String,
      default: ''
    },
    showTip: {
      type: Boolean,
      default: true
    }
  },
  
  data() {
    return {
      content: this.value,
      editorOptions: {
        modules: {
          toolbar: {
            container: [
              ['bold', 'italic', 'underline', 'strike'],
              ['blockquote', 'code-block'],
              [{ 'header': 1 }, { 'header': 2 }],
              [{ 'list': 'ordered' }, { 'list': 'bullet' }],
              [{ 'script': 'sub' }, { 'script': 'super' }],
              [{ 'indent': '-1' }, { 'indent': '+1' }],
              [{ 'direction': 'rtl' }],
              [{ 'size': ['small', false, 'large', 'huge'] }],
              [{ 'header': [1, 2, 3, 4, 5, 6, false] }],
              [{ 'color': [] }, { 'background': [] }],
              [{ 'font': [] }],
              [{ 'align': [] }],
              ['clean'],
              ['link', 'image', 'video']
            ],
            handlers: {
              'image': this.imageHandler
            }
          }
        },
        placeholder: this.placeholder,
        theme: 'snow'
      }
    }
  },
  
  computed: {
    ...mapGetters(['getToken'])
  },
  
  watch: {
    value(newVal) {
      if (newVal !== this.content) {
        this.content = newVal
      }
    }
  },
  
  methods: {
    onChange() {
      this.$emit('input', this.content)
      this.$emit('change', this.content)
    },
    
    imageHandler() {
      const input = document.createElement('input')
      input.setAttribute('type', 'file')
      input.setAttribute('accept', 'image/*')
      input.click()
      
      input.onchange = async () => {
        const file = input.files[0]
        if (!file) return
        
        // 检查文件类型
        if (!file.type.startsWith('image/')) {
          this.$message.error(this.$t('admin.imageTypeError'))
          return
        }
        
        // 检查文件大小（限制为5MB）
        if (file.size > 5 * 1024 * 1024) {
          this.$message.error(this.$t('admin.imageSizeError'))
          return
        }
        
        try {
          // 创建FormData
          const formData = new FormData()
          formData.append('file', file)
          
          // 显示上传中提示
          const loading = this.$loading({
            lock: true,
            text: this.$t('common.uploading'),
            spinner: 'el-icon-loading',
            background: 'rgba(0, 0, 0, 0.7)'
          })
          
          // 发送上传请求
          const response = await axios.post('/api/upload/editor-image', formData, {
            headers: {
              'Content-Type': 'multipart/form-data',
              'Authorization': `Bearer ${this.getToken}`
            }
          })
          
          // 关闭上传中提示
          loading.close()
          
          // 获取图片URL
          const url = response.data.url
          
          // 获取编辑器实例
          const quill = this.$refs.quillEditor.quill
          
          // 获取当前光标位置
          const range = quill.getSelection()
          
          // 在光标位置插入图片
          quill.insertEmbed(range.index, 'image', url)
          
          // 将光标移动到图片后面
          quill.setSelection(range.index + 1)
          
          // 显示上传成功提示
          this.$message.success(this.$t('admin.imageUploadSuccess'))
        } catch (error) {
          console.error('上传图片失败:', error)
          this.$message.error(this.$t('admin.imageUploadError'))
        }
      }
    }
  }
}
</script>

<style scoped>
.rich-text-editor {
  width: 100%;
}

.quill-editor {
  height: 300px;
  margin-bottom: 10px;
}

.editor-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 5px;
}
</style>

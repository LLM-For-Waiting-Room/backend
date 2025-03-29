const leftList = document.querySelector('.main .left')
const close_a = document.querySelector('.main .close_a')
const inputContent = document.getElementById('inputContent')
const chatContainer = document.querySelector('.chat')


const uploadContent = () => {
  // console.log('duihua ')
  // 获取输入框内容
  const content = inputContent.value
  inputContent.value = "" // 清空输入框中内容
  // Robot回复内容
  let reply_content = ""
  // 创建用户的头像和内容
  const chatMy = document.createElement('div')
  chatMy.classList.add('chat_my', 'chat_mg')
  const userDiv = document.createElement('div')
  userDiv.classList.add('user')
  const userImg = document.createElement('img')
  userImg.src = "/static/img/user.png"
  userImg.alt = 'user'
  const userName = document.createElement('span')
  userName.classList.add('name')
  userName.textContent = '袁琪博'
  const chatContent = document.createElement('div')
  chatContent.classList.add('chat_content')
  chatContent.textContent = content
  userDiv.appendChild(userImg)
  userDiv.appendChild(userName)
  chatMy.appendChild(userDiv)
  chatMy.appendChild(chatContent)
  chatContainer.appendChild(chatMy)
  
  // 模拟 chat_gpt 的回复
  const chatGpt = document.createElement('div')
  chatGpt.classList.add('chat_gpt', 'chat_mg')
  const chatGptUser = document.createElement('div')
  chatGptUser.classList.add('user')
  const chatGptImg = document.createElement('img')
  chatGptImg.src = "{% static 'img/logo.png' %}"
  chatGptImg.alt = 'user'
  const chatGptName = document.createElement('span')
  chatGptName.classList.add('name')
  chatGptName.textContent = 'TeachingRobot'
  const chatGptContent = document.createElement('div')
  chatGptContent.classList.add('chat_content')
  chatGptContent.textContent = "正在等待响应，请稍候..."
  chatGptUser.appendChild(chatGptImg)
  chatGptUser.appendChild(chatGptName)
  chatGpt.appendChild(chatGptUser)
  chatGpt.appendChild(chatGptContent)
  chatContainer.appendChild(chatGpt)

  // 获取最新添加的消息元素并滚动到其位置
  const latestMessage = chatContainer.lastElementChild
  latestMessage.scrollIntoView({ behavior: 'smooth', block: 'end' })

  $.ajax({
    url:"/communicate/",
    type: "post",
    traditional: true,
    data: {
        Question:content
    },
    dataType: "JSON",
    success: function (res) {
      if (res.status){
        //reply_content = "testsuccess"
        reply_content = res.Answer
        chatGptContent.textContent = reply_content
        /*
        // 模拟 chat_gpt 的回复
        const chatGpt = document.createElement('div')
        chatGpt.classList.add('chat_gpt', 'chat_mg')
        const chatGptUser = document.createElement('div')
        chatGptUser.classList.add('user')
        const chatGptImg = document.createElement('img')
        chatGptImg.src = '../static/img/logo.png'
        chatGptImg.alt = 'user'
        const chatGptName = document.createElement('span')
        chatGptName.classList.add('name')
        chatGptName.textContent = 'TeachingRobot'
        const chatGptContent = document.createElement('div')
        chatGptContent.classList.add('chat_content')
        chatGptContent.textContent = reply_content
        chatGptUser.appendChild(chatGptImg)
        chatGptUser.appendChild(chatGptName)
        chatGpt.appendChild(chatGptUser)
        chatGpt.appendChild(chatGptContent)
        chatContainer.appendChild(chatGpt)
        */

        // 获取最新添加的消息元素并滚动到其位置
        const latestMessage = chatContainer.lastElementChild
        latestMessage.scrollIntoView({ behavior: 'smooth', block: 'end' })

        console.log("对话成功")
      
      }
    }
  })

}

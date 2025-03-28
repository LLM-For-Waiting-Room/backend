# PatientUI
+ 提交表单并初始化会话
  - URL: `/patient/confirmForm/`
  - Method: `POST`
  - RequestBody: 
    ```json
    {
    "language": "en/zh",
    "model": "chatbot_type",
    "user-agreement": true, 
    "gender": "M", 
    "age": "23", 
    "if-allergies": true, 
    "allergies": "花粉过敏", 
    "if-medical-histories": false, 
    "medical-histories": null, 
    "if-family-histories": false, 
    "family-histories": null, 
    "symptom-keywords": ["發燒"], 
    "symptom-text": "头痛", 
    "duration": 3
    }
    ```
  - Return:
    ```json
    {
    "session": "sessionID",
    "content_user": "用户提交的表单内容",
    "content_assistant": "模型首次回复",
    "expire_time": "会话过期时间"
    }
    ```
  - CURL:
    ```bash
    curl -X POST https://smartlab.cse.ust.hk/smartcare/demo_api/patient/confirmForm/ \
    -H "Content-Type: application/json" \
    -d '{"language": "zh",
    "model": "chatbot_type",
    "user-agreement": true, 
    "gender": "M", 
    "age": "23", 
    "if-allergies": true, 
    "allergies": "花粉过敏", 
    "if-medical-histories": false, 
    "medical-histories": null, 
    "if-family-histories": false, 
    "family-histories": null, 
    "symptom-keywords": ["發燒"], 
    "symptom-text": "头痛", 
    "duration": 3}'
    ```
+ 进行对话
  - URL: `/patient/chat/`
  - Method: `POST`
  - RequestBody: 
    ```json
    {
    "session": "sessionID",
    "content": "用户提问内容",
    }
    ```
  - Return:
    ```json
    {
    "content": "模型回复内容",
    "is_finished": "是否到达总结阶段（boolean）",
    "expire_time": "会话过期时间"
    }
    ```
  - CURL:
    ```bash
    curl -X POST https://smartlab.cse.ust.hk/smartcare/demo_api/patient/chat/ \
    -H "Content-Type: application/json" \
    -d '{"session": "SESSION_ID", "content": "Hello"}'
    ```    
+ 获取会话历史
  - URL: `/patient/getConHistory/`
  - Method: `POST`
  - RequestBody: 
    ```json
    {
    "session": "sessionID"
    }
    ```
  - Return:
    ```json
    {
    "conversation": [
        {"role": "user/assistant", "content": "内容"},
        ...
    ],
    "expire_time": "过期时间",
    "is_finished": "是否已结束(boolean)"
    }
    ```
  - CURL:
    ```bash
    curl -X POST https://smartlab.cse.ust.hk/smartcare/demo_api/patient/getConHistory/ \
    -H "Content-Type: application/json" \
    -d '{"session": "SESSION_ID"}'
    ```
+ 结束会话并生成患者代码
  - URL: `/patient/endChat/`
  - Method: `POST`
  - RequestBody: 
    ```json
    {
    "session": "sessionID",
    "modified_summary": "用户确认修改后的摘要"
    }
    ```
  - Return:
    ```json
    {
    "patient_code": "四位患者代码（如0123）",
    "record_id": "唯一记录ID"
    }
    ```
  - CURL:
    ```bash
    curl -X POST https://smartlab.cse.ust.hk/smartcare/demo_api/patient/endChat/ \
    -H "Content-Type: application/json" \
    -d '{"session": "SESSION_ID", "modified_summary": "Confirmed summary text"}'
    ```
+ 结束会话并生成患者代码
  - URL: `/patient/transcription/`
  - Method: `POST`
  - RequestBody: 
    ```json
    {
    "audio": "音频文件"
    }
    ```
  - Return:
    ```json
    {
    "transcription": "识别出的文本内容"
    }
    ```
  - CURL:
    ```bash
    curl -X POST \
    https://smartlab.cse.ust.hk/smartcare/demo_api/patient/transcription/ \
    -H 'Content-Type: multipart/form-data' \
    -F 'audio=@/Users/yuanqibo/Desktop/yue_dialogue.mp4'
    ```
+ 通过记录ID查询患者代码 (***还未使用***)
  - URL: `/patient/searchPcode/`
  - Method: `POST`
  - RequestBody: 
    ```json
    {
    "record_id": "唯一记录ID"
    }
    ```
  - Return:
    ```json
    {
    "modified_summary": "摘要内容",
    "patient_code": "四位患者代码"
    }
    ```
  - CURL:
    ```bash
    curl -X POST https://smartlab.cse.ust.hk/smartcare/demo_api/patient/searchPcode/ \
    -H "Content-Type: application/json" \
    -d '{"record_id": "RECORD_UUID"}'
    ```

## DoctorUI
+ 通过患者代码获取病历
  - URL: `/doctor/summary/\<str:id>\/`
  - Method: `GET`
  - Return:
    ```json
    {
    "record_id": "记录ID",
    "conversation": "完整对话历史",
    "paragraph": "摘要文本",
    "list": ["关键条目1", "关键条目2"]
    }
    ```
  - CURL:
    ```bash
    curl -X GET https://smartlab.cse.ust.hk/smartcare/demo_api/doctor/summary/0123/
    ```
+ 提交病历修改（含音频转录）
  - URL: `/doctor/summary/\<str:id>\/`
  - Method: `POST`
  - RequestBody: 
    ```json
    {
    "audio": "音频文件",
    "modified_paragraph": "修改后的摘要",
    "modified_list": "修改后的关键条目",
    }
    ```
  - Return:
    ```json
    {
    "sentences": "音频转录文本",
    "medical_record": "对医患对话的总结"
    }
    ```
  - CURL:
    ```bash
    curl -X POST https://smartlab.cse.ust.hk/smartcare/demo_api/doctor/summary/0123/ \
    -F "audio=@/path/to/audio.wav" \
    -F "modified_paragraph=Updated summary text" \
    -F "modified_list=[\"Item1\", \"Item2\"]"
    ```
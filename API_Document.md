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
    "duration": 3}'| jq .
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
    -d '{"session": "SESSION_ID", "content": "Hello"}'| jq .
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
    -d '{"session": "SESSION_ID"}'| jq .
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
    -d '{"session": "SESSION_ID", "modified_summary": "Confirmed summary text"}'| jq .
    ```
+ 患者语音转文字
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
    -F 'audio=@/Users/yuanqibo/Desktop/yue_dialogue.mp4'| jq .
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

# DoctorUI
+ 通过患者代码获取病历
  - URL: `/doctor/summary/\<str:id>\/`
  - Method: `GET`
  - Return:
    ```json
    {
    "record_id": "记录ID",
    "conversation": "完整对话历史",
    "paragraph": "摘要文本",
    "list": ["关键条目1", "关键条目2"],
    "patient_items": {"user-agreement": true, "gender": "M", "age": "23",...},
    "urgency_level": "Critical/Urgent/Non-urgent"
    }
    ```
  - CURL:
    ```bash
    curl -X GET https://smartlab.cse.ust.hk/smartcare/demo_api/doctor/summary/0184/
    ```
+ 提交病历修改，音频转录并流式生成Medical Report
  - URL: `/doctor/generatedReport/\<str:id>\/`
  - Method: `POST`
  - RequestBody: 
    ```json
    {
    "transcription": "音频转录文本",
    "modified_paragraph": "修改后的摘要",
    "modified_list": "修改后的关键条目",
    }
    ```
  - Return:
    ```json
    {
      流式输出
    }
    ```
  - CURL:
    ```bash
    curl -X POST https://smartlab.cse.ust.hk/smartcare/demo_api/doctor/generatedReport/0123/ \
    -F "transcription=音频转录文本" \
    -F "modified_paragraph=Updated summary text" \
    -F "modified_list=[\"Item1\", \"Item2\"]"| jq .
    ```

+ 流式生成相应的Document (eg: critical_questions/referral_letter/sick_leave/...)
  - URL: `/doctor/generateDocumentStream_test/`
  - Method: `POST`
  - RequestBody: 
    ```json
    {
    "medical_record": "medical_record",
    "doc_type": "doc_type" // critical_questions/referral_letter/sick_leave/...
    }
    ```
  - Return:
    ```json
    {
      流式输出
    }
    ```
  - CURL:
    ```bash
    curl -X POST https://smartlab.cse.ust.hk/smartcare/demo_api/doctor/generateDocumentStream_test/ \
    -H 'Content-Type: application/json' \
    -d '{
      "medical_record": "History:- Presenting complaint: 4-week history of intermittent chest pain, worse...",
      "doc_type": "labs_forms"
    }'| jq .
    ```
+ 流式更新相应的Record和Document (eg: critical_questions/referral_letter/sick_leave/...)
  - URL: `/doctor/updateDocument/`
  - Method: `POST`
  - RequestBody: 
    ```json
    {
      "doc_type": "string",     // 文档类型：'medical_record' 或其他
      "transcription": ["string", "string", "......"], 
      "document": "string",      // 当前文档内容, 若doc_type是'medical_record'，传空字符串即可
      "medical_record": "string" // 医疗记录内容
    }
    ```
  - Return:
    ```json
    {
      流式输出
    }
    ```
  - CURL:
    ```bash
    curl -X POST https://smartlab.cse.ust.hk/smartcare/demo_api/doctor/updateDocument/ \
    -H 'Content-Type: application/json' \
    -d '{
      "doc_type": "medical_record",
      "transcription": [
                "New wheezing episodes at night",
                "Peak flow reduced to 250 from usual 400",
                "Reports using rescue inhaler 3x daily"
            ],
      "medical_record": "History:\n- Asthma since 2015\n- Allergic rhinitis",
      "document":""
    }'| jq .
    ```
    ```bash
    curl -X POST https://smartlab.cse.ust.hk/smartcare/demo_api/doctor/updateDocument/ \
    -H 'Content-Type: application/json' \
    -d '{
      "doc_type": "medical_record",
      "transcription": [
                "New chest pain on exertion",
                "Abnormal stress echocardiogram",
                "BNP elevated to 500 pg/mL"
            ],
      "document": "Referral for cardiac assessment",
      "medical_record": "PMH: Hypertension\nMedications: Lisinopril 10mg OD"
    }'| jq .
    ```

+ 医生登录
  - URL: `/doctor/login/`
  - Method: `POST`
  - RequestBody: 
    ```json
    {
      "username": "123456",
      "password": "123456"
    }
    ```
  - Return:
    ```json
    {
      "status": "success",
      "doctor_id": "uuid-string"
    }
    ```
  - CURL:
    ```bash
    curl -X POST https://smartlab.cse.ust.hk/smartcare/demo_api/doctor/login/ \
    -H "Content-Type: application/json" \
    -d '{"username": "123456", "password": "123456"}'| jq .
    ```

+ 创建医生账号
  - URL: `/doctor/create/`
  - Method: `POST`
  - RequestBody: 
    ```json
    {
      "username": "String",
      "password": "String"
    }
    ```
  - Return:
    ```json
    {
      "status": "success",
      "doctor_id": "uuid-string"
    }
    ```
  - CURL:
    ```bash
    curl -X POST https://smartlab.cse.ust.hk/smartcare/demo_api/doctor/create/ \
    -H "Content-Type: application/json" \
    -d '{"username": "String", "password": "String"}'| jq .
    ```

# NurseUI
+ 护士登录
  - URL: `/nurse/login/`
  - Method: `POST`
  - RequestBody: 
    ```json
    {
      "username": "nurse1",
      "password": "123456"
    }
    ```
  - Return:
    ```json
    {
      "status": "success",
      "nurse_id": "uuid-string"
    }
    ```
  - CURL:
    ```bash
    curl -X POST https://smartlab.cse.ust.hk/smartcare/demo_api/nurse/login/ \
    -H "Content-Type: application/json" \
    -d '{"username": "nurse1", "password": "123456"}'| jq .
    ```

+ 创建护士账号
  - URL: `/nurse/create/`
  - Method: `POST`
  - RequestBody: 
    ```json
    {
      "username": "String",
      "password": "String"
    }
    ```
  - Return:
    ```json
    {
      "status": "success",
      "nurse_id": "uuid-string"
    }
    ```
  - CURL:
    ```bash
    curl -X POST https://smartlab.cse.ust.hk/smartcare/demo_api/nurse/create/ \
    -H "Content-Type: application/json" \
    -d '{"username": "String", "password": "String"}'| jq .
    ```


+ 获取所有等待中的患者(Stage: Waiting)
  - URL: `/nurse/searchWaitingPatients/`
  - Method: `GET`
  - Return: 
    ```json
    {
      "waiting_patients": [
        {
            "record_id": "uuid-string",
            "patient_code": "4 digit code",
            "initial_items": {},
            "basic_items": {},
            "patient_ch_summary": "string",
            "patient_en_summary": "string",
            "doctor_modified_summary": "string",
            "conversation": [],
            "urgency_level": "string",
            "stage": "string",
            "doctor_id": "uuid-string",
            "chief_complaint": "string",
            "create_time": "time"
        },
        {
            "record_id": "uuid-string",
            "patient_code": "4 digit code",
            "initial_items": {},
            "basic_items": {},
            "patient_ch_summary": "string",
            "patient_en_summary": "string",
            "doctor_modified_summary": "string",
            "conversation": [],
            "urgency_level": "string",
            "stage": "string",
            "doctor_id": "uuid-string",
            "chief_complaint": "string",
            "create_time": "time"
        },
        ......
    ]
    }
    ```
  - CURL:
    ```bash
    curl -X GET https://smartlab.cse.ust.hk/smartcare/demo_api/nurse/searchWaitingPatients/| jq .
    ```
+ 获取所有医生
  - URL: `/nurse/getAllDoctors/`
  - Method: `GET`
  - Return: 
    ```json
    {
      "doctors": [
        {
            "doctor_id": "uuid-string",
            "username": "string"
        },
        {
            "doctor_id": "uuid-string",
            "username": "string"
        }
        ......
      ]
    }
    ```
  - CURL:
    ```bash
    curl -X GET https://smartlab.cse.ust.hk/smartcare/demo_api/nurse/getAllDoctors/| jq .
    ```
+ 分配患者给医生
  - URL: `/nurse/assignPatient_to_Doctor/`
  - Method: `POST`
  - RequestBody: 
    ```json
    {
      "record_id": "uuid-string",
      "doctor_id": "uuid-string"
    }
    ```
  - Return:
    ```json
    {
      "status": "success",
      "message": "Patient assigned to doctor successfully"
    }
    ```
  - CURL:
    ```bash
    curl -X POST https://smartlab.cse.ust.hk/smartcare/demo_api/nurse/assignPatient_to_Doctor/ \
    -H "Content-Type: application/json" \
    -d '{"record_id": "patient-uuid", "doctor_id": "doctor-uuid"}'| jq .
    ```
 
# Admin
+ 获取所有医生
  - URL: `/Admin/get_all_nurses_and_doctors`
  - Method: `GET`
  - Return: 
    ```json
    {
      "doctors": [
        {
            "doctor_id": "uuid-string",
            "username": "string"
        },
        {
            "doctor_id": "uuid-string",
            "username": "string"
        }
        ......
      ],
      "nurses": [
        {
            "nurse_id": "uuid-string",
            "username": "string"
        },
        {
            "nurse_id": "uuid-string",
            "username": "string"
        }
        ......
      ],
    }
    ```
  - CURL:
    ```bash
    curl -X GET https://smartlab.cse.ust.hk/smartcare/demo_api/Admin/get_all_nurses_and_doctors/| jq .
    ```
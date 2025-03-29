import requests
import json

url = "http://localhost:19080/consultation_room_after_medical_record"
headers = {"Content-Type": "application/json"}

medical_record = """History:
- Presenting complaint: 4-week history of intermittent chest pain, worse on exertion
- ICE: Worried about heart problems, expects ECG testing
- Red flag symptoms: Denies syncope or radiating pain
- Risk factors: BMI 32, family history of IHD (father MI at 55)
- PMH: GERD, hypercholesterolemia
- DH: Omeprazole 20mg OD, simvastatin 40mg ON
- SH: Office worker, smokes 5/day, alcohol 20 units/week

Examination:
- Vital signs: BP 145/92 mmHg, HR 76 bpm regular
- CVS: Normal heart sounds, no murmurs
- Chest: No tenderness on palpation

Impression:
1. Atypical chest pain. Likely diagnosis: Gastro-oesophageal reflux
   - Differential diagnosis: Stable angina, Costochondritis

Plan:
- Investigations: ECG (normal), lipid profile
- Treatment: Optimize PPI dosage
- Follow up: 2 weeks
- Safety netting: Return if pain worsens or occurs at rest"""

payload = {
    "medical_record": medical_record,
    "doc_type": "critical_questions"
}

response = requests.post(url, headers=headers, data=json.dumps(payload))

if response.status_code == 200:
    print("Critical Questions:")
    print(response.json()["generated_document"])
else:
    print(f"Error: {response.status_code}")
    print(response.json())

# 进行对话
'''data = {
        "user_message": "hello",
        "conversation_history": [],
        "language": "English",
        "chatbot_type": "elderly"
    }
response = requests.post("http://0.0.0.0:19080/chat", json=data).json() # 存在问题
print("chat_response:",response)'''
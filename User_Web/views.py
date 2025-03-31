from django.shortcuts import render, HttpResponse, redirect
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
import json
from . import models
import random
import requests
import pickle
from django.contrib.sessions.models import Session
from django.contrib.sessions.backends.db import SessionStore
from asgiref.sync import sync_to_async
import asyncio
from django.http import JsonResponse, StreamingHttpResponse
#ngrok http http://localhost:8000

@csrf_exempt
def deleteSession(request):
    requestBody = json.loads(request.body)
    sessionID = requestBody['session']
    request.session.flush()
    return HttpResponse(json.dumps({"deleted":"success"}))

# 用户填写基础信息后提交，与模型进行交互
@csrf_exempt
def confirmForm(request):

    # 先设置session
    if not request.session.session_key:
        request.session['conversation_history'] = []
        request.session.save()

    sessionId = request.session.session_key
    expire_time = str(request.session.get_expiry_date())
    print("+++++++++++++++:", sessionId)
    print("time:",expire_time)
    
    formBody = json.loads(request.body)
    # print("@@@@@@@@@:",formBody)
    lang = formBody['language'] # 中英文
    language = "English" if lang == "en" else "Chinese"
   
    # 对话类型
    try:
        chatbot_type = formBody['model'] 
        formBody.pop('model')
    except:
        chatbot_type = 'medical'
    print("^^^^^^^^^^^^^^:", chatbot_type)
    formBody.pop('language')
    print("处理后的formBody: ",formBody)
    
    # 与模型进行第一次交互
    data = {
        "user_message": formBody, # dict form!!!
        "conversation_history": [],
        "language": language,
        "chatbot_type": chatbot_type
    }
    response = requests.post("http://0.0.0.0:19080/chat", json=data).json()
    
    conversation_history = response["updated_history"]
    assistantResponse = response["llm_response"]
    is_finished = response["reached_summary"]
    print("chat_history:", conversation_history)
    # 通过history获取正式问答中用户的第一次输入内容（由提交的表单转化而来）
    basicInfo = conversation_history[0]['content']
    print("basicInfo:####", basicInfo)
    
    # 更新session
    request.session['conversation_history'] = conversation_history 
    request.session['formBody'] = formBody
    request.session['expire_time'] = expire_time
    request.session['language'] = language
    request.session['is_finished'] = is_finished
    request.session['chatbot_type'] = chatbot_type

    return HttpResponse(json.dumps({"session":sessionId, "content_user": basicInfo, "content_assistant": assistantResponse, "expire_time":expire_time}))

# 交互
@csrf_exempt
def chat(request):
    # 进行对话
    requestBody = json.loads(request.body)
    question = requestBody['content']
    sessionID = requestBody['session']
    
    print("sessionID:", sessionID)
    # 根据sessionID获取数据
    session = SessionStore(session_key=sessionID)

    conversation_history = session['conversation_history']
    expire_time = session['expire_time']
    language = session['language']
    chatbot_type = session['chatbot_type']
    print("chatbot_type:", chatbot_type)
    #language = "English"

    # 进行对话
    data = {
            "user_message": question,
            "conversation_history": conversation_history,
            "language": language,
            "chatbot_type": chatbot_type
        }
    response = requests.post("http://0.0.0.0:19080/chat", json=data).json() # 存在问题
    print("chat_response:",response)
    conversation_history = response["updated_history"]
    assistantResponse = response["llm_response"]
    is_finished = response["reached_summary"] # 需要检验其是否为bool类型
    
    # 更新session
    session['conversation_history'] = conversation_history
    session['is_finished'] = is_finished
    session.save()

    SUMMARY_PREFIXES = {
    "medical": {"English": "Professional Summary: ", "Chinese": "專業摘要："},
    "elderly": {"English": "Care Summary: ", "Chinese": "護理摘要："},
    "rehabilitation": {"English": "Progress Summary: ", "Chinese": "進度摘要："},
    "family": {"English": "Support Summary: ", "Chinese": "支援摘要："},
    "children": {"English": "Youth Summary: ", "Chinese": "青少年摘要："}
    }
    if is_finished:
        assistantResponse = assistantResponse[len(SUMMARY_PREFIXES[chatbot_type][language]):]
        '''if language == "English":
            # 处理professional summary
            assistantResponse = assistantResponse[len("Professional Summary: "):]
        elif language == "Chinese":
            assistantResponse = assistantResponse[5:]#len("专业摘要：")'''
        print(assistantResponse)
        
    return HttpResponse(json.dumps({"content":assistantResponse, "is_finished":is_finished, "expire_time":expire_time}))

# 获取聊天记录
@csrf_exempt
def getConversation_History(request):
    
    requestBody = json.loads(request.body)
    sessionID = requestBody['session']
    print("get_history_session:",sessionID)

    # 根据根据sessionID获取数据
    session = SessionStore(session_key=sessionID)

    # 获取会话数据
    conversation_history = session['conversation_history']
    is_finished = session['is_finished']
    print('history:####',conversation_history)
    # 获取session过期时间
    expire_time = session['expire_time']

    history_dict = {
        "conversation": conversation_history,
        "expire_time": expire_time,
        "is_finished": is_finished
    }
    return HttpResponse(json.dumps(history_dict))

# 将提交Summary的用户数据进入数据库
def createPatient_and_Map(sessionID):
    patient = models.Patient.objects.create()
    record_id = patient.record_id
    # 根据根据sessionID获取数据
    session = SessionStore(session_key=sessionID)
   
    # 获取数据
    formBody = session['formBody']
    conversation = session['conversation_history']
    language = session['language']
    # 创建四位数
    tentative_map = models.TentativeMap.objects.create(record_id = patient)
    patient_id = tentative_map.patient_id
    formatted_id = "{:04d}".format(patient_id)
    return record_id, formatted_id, patient, conversation, language

@csrf_exempt
async def endChat(request):
    requestBody = json.loads(request.body)
    summary = requestBody["modified_summary"]
    sessionID = requestBody['session']

    #record_id = patient.record_id
    
    #print("四位数###", formatted_id)
    record_id, formatted_id, patient, conversation, language = await sync_to_async(createPatient_and_Map)(sessionID)
    # 存入数据
    # patient.basic_items = [formBody]
    loop = asyncio.get_event_loop()
    #async_function = sync_to_async(save)
    loop.create_task(processData_LLM(conversation,language,summary,patient))
   
    
    return HttpResponse(json.dumps({"patient_code":formatted_id, "record_id":str(record_id)}))

async def processData_LLM(conversation, language, summary, patient):
    await asyncio.sleep(0.1)
    patient_en_summary = None
    patient_ch_summary = None
    if language == "English":
        patient_en_summary = summary
    elif language == "Chinese":
        patient_ch_summary = summary
        # 与模型再次交互获得翻译
        data = {
            "Chinese": summary
        }
        response = requests.post("http://0.0.0.0:19080/zh2en", json=data).json()
        print(response['English'])
        patient_en_summary = response['English']
    
    # 形成list并保存
    data = {
        "Paragraph": patient_en_summary
    }
    response = requests.post("http://0.0.0.0:19080/para2list", json=data).json()
    print("list:", response['List'])
    basic_items = response['List']

    await sync_to_async(saveToDB)(conversation,patient_en_summary,patient_ch_summary,basic_items,patient)

def saveToDB(conversation, patient_en_summary, patient_ch_summary, basic_items, patient):
    patient.conversation = conversation
    patient.patient_en_summary = patient_en_summary
    if patient_ch_summary is not None:
        patient.patient_ch_summary = patient_ch_summary
    patient.basic_items = basic_items
    patient.save()


@csrf_exempt
def searchPatient_Code(request):
    requestBody = json.loads(request.body)
    record_id = requestBody["record_id"]

    patient = models.Patient.objects.filter(record_id = record_id).first()
    modified_summary = patient.patient_en_summary
    print("test_conversation:@@", patient.conversation)
    t_map = models.TentativeMap.objects.filter(record_id = patient).first()
    if t_map is None:
        patient_code = None
    else:
        patient_code = "{:04d}".format(t_map.patient_id)

    return HttpResponse(json.dumps({"modified_summary":modified_summary, "patient_code":patient_code}))

# 语音转文字
@csrf_exempt
def transcribe(request):
    url = 'http://localhost:5001/transcribe'
    audio = request.FILES.get('audio')
    files = {"audio": audio}
    response = requests.post(url, files=files).json()
    return HttpResponse(json.dumps({"transcription":response["transcription"]}))


#################
#    DoctorUI   #
#################
@csrf_exempt
def getRecordByCode(request, id):
    patient_id = int(id)
    t_map = models.TentativeMap.objects.filter(patient_id = patient_id).first()
    
    patient = t_map.record_id

    if request.method == "GET":
        record_id = patient.record_id
        conversation = patient.conversation
        summary = patient.patient_en_summary
        items = patient.basic_items
        print(conversation)
        return HttpResponse(json.dumps({"record_id":str(record_id), "conversation":conversation, "paragraph":summary, "list": items}))
    elif request.method == "POST":
        print("start transcribe!")
        initial_summary = patient.patient_en_summary

        # 处理请求
        audio = request.FILES.get('audio')
        modified_summary = request.POST.get('modified_paragraph')
        items = json.loads(request.POST.get('modified_list'))
        
        patient.doctor_modified_summary = modified_summary
        patient.basic_items = items
        patient.save()

        url = 'http://localhost:5000/consultation_transcribe_no_speaker'
        files = {"audio": audio}
        data = {"id": id, "initial_summary": initial_summary}
        try:
            response = requests.post(url, files=files, data=data).json()
            print("_______: Transcribe Success!")
        except Exception as e:
            try:
                response = requests.post(url, files=files, data=data).json()
                print("Retry Success!")
            except Exception as e:
                error_str = f"API call failed with error: {e}"
                return HttpResponse(json.dumps({"sentences":error_str, "medical_record":error_str}))
        #print("!!!!:", response)
        try:
            sentences = response['text']
            medical_record = response['medical_record']
        except:
            sentences = ""
            medical_record = ""
        
        patient.asr_text = sentences
        patient.medical_record = medical_record
        patient.save()
        
        return HttpResponse(json.dumps({"sentences":sentences, "medical_record":medical_record}))

@csrf_exempt
def generatedReport(request,id):
    """Handle report generation with support for both streaming and non-streaming modes."""
    if request.method != "POST":
        return JsonResponse({"error": "Only POST requests are allowed"}, status=405)
    
    patient_id = int(id)
    t_map = models.TentativeMap.objects.filter(patient_id = patient_id).first()
    
    patient = t_map.record_id


    # Extract data from the request
    try:
        initial_summary = patient.patient_en_summary

        # 处理请求
        audio = request.FILES.get('audio')
        modified_summary = request.POST.get('modified_paragraph')
        items = json.loads(request.POST.get('modified_list'))
        
        patient.doctor_modified_summary = modified_summary
        patient.basic_items = items
        patient.save()

        #text = request.POST.get("text")
        stream = request.POST.get("stream", "false").lower() == "true"

        # Transcribe the audio file
        asr_url = "http://localhost:5001/transcribe"
        asr_response = requests.post(asr_url, files={"audio": audio})
        if asr_response.status_code == 200:
            transcription = asr_response.json().get("transcription", "")
        else:
            transcription = asr_response.text

        if not transcription:
            print("empty transcription, using default value.")
            transcription = "nothing else"

    except Exception as e:
        return JsonResponse({"error": f"Invalid request data: {str(e)}"}, status=400)

    # Call the `generate_medical_record` API
    url = "http://localhost:5004/generate_medical_record"
    payload = {
        "id": id,
        "initial_summary": initial_summary,
        "text": transcription,
        "stream": stream
    }
    print("generate_medical_record payload:", payload)
    if not all([id, initial_summary, transcription]):
        return JsonResponse({"error": "Missing required fields (id, initial_summary, transcription)"}, status=400)

    try:
        if stream:
            # Handle streaming mode
            response = requests.post(url, json=payload, stream=True)
            if response.status_code != 200:
                return JsonResponse({"error": "Failed to generate medical record", "details": response.text}, status=response.status_code)

            def stream_response():
                try:
                    for chunk in response.iter_content(chunk_size=None):
                        if chunk:
                            yield chunk
                except requests.exceptions.RequestException as e:
                    error_message = json.dumps({"error": str(e)}).encode()
                    print("Streaming error:", error_message.decode('utf-8'))  # Log the error
                    yield error_message
                finally:
                    print("Streaming complete.")  # Log when streaming is finished
                    response.close()

            response_server = StreamingHttpResponse(stream_response(), content_type="application/json")
            response_server['Cache-Control'] = 'no-cache'  # Prevent client cache
            response_server["X-Accel-Buffering"] = "no"  # Allow stream over NGINX server
            return response_server
        else:
            # Handle non-streaming mode
            response = requests.post(url, json=payload)
            if response.status_code != 200:
                return JsonResponse({"error": "Failed to generate medical record", "details": response.text}, status=response.status_code)
            
            return JsonResponse(response.json(), status=200)

    except requests.exceptions.RequestException as e:
        return JsonResponse({"error": f"Service communication error: {str(e)}"}, status=500)
    except Exception as e:
        return JsonResponse({"error": f"Unexpected error: {str(e)}"}, status=500)


# 生成critical_questions/referral_letter/sick_leave(待使用)
@csrf_exempt
def generateDocument(request):
    requestBody = json.loads(request.body)
    medical_record = requestBody["medical_record"]
    doc_type = requestBody["doc_type"]
    
    url = url = "http://localhost:19080/consultation_room_after_medical_record"
    headers = {"Content-Type": "application/json"}
    payload = {
    "medical_record": medical_record,
    "doc_type": doc_type
    }

    response = requests.post(url, json=payload)

    if response.status_code == 200:
        document = response.json()["generated_document"]
    else:
        document = ""
    print(response.json())
    return HttpResponse(json.dumps({"document": document}))

# Stream Document Generation (TEST)
@csrf_exempt
def generateStreamDoc(request):
    print(request.body)
    requestBody = json.loads(request.body)
    medical_record = requestBody["medical_record"]
    doc_type = requestBody["doc_type"].lower()
    # stream = request["stream"]
    
    url = "http://localhost:19080/consultation_room_after_medical_record"
    payload = {
        "medical_record": medical_record,
        "doc_type": doc_type,
        "stream": True
    }
    response = requests.post(url, json=payload, stream=True)
    def stream_response():
        try:
            for chunk in response.iter_content(chunk_size=None):
                if chunk:
                    # print("Streaming chunk:", chunk.decode('utf-8'))  # Log the chunk being streamed
                    yield chunk
        except requests.exceptions.RequestException as e:
            error_message = json.dumps({"error": str(e)}).encode()
            print("Streaming error:", error_message.decode('utf-8'))  # Log the error
            yield error_message
        finally:
            print("Streaming complete.")  # Log when streaming is finished
            response.close()
    response_server = StreamingHttpResponse(stream_response(), content_type="application/octet-stream")
    response_server['Cache-Control'] = 'no-cache'  # Prevent client cache
    response_server["X-Accel-Buffering"] = "no"  # Allow stream over NGINX server
    return response_server

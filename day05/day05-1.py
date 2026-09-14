from openai import OpenAI

# # 1. OpenAI 대시보드에서 발급받은 실제 API 키 입력 (보통 'sk-...'로 시작)
# client = OpenAI(api_key="your_api_key")
# response = client.chat.completions.create(
#     # 2. 모델명 수정: 숫자 40이 아닌 알파벳 '4o'
#     model="gpt-4o-mini",
#     messages=[
#         {"role": "system", "content": "You are a helpful assistant."},
#         # 3. 실제 전달할 질문 추가
#         {"role": "user", "content": "안녕하세요! 간단한 자기소개 부탁드려요."},
#     ],
# )

# print(response.choices[0].message.content)


def ask_llm(api_key,model,question):
    client=OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "친절한 도우미"},
            {"role": "user", "content": question}
        ]
    )
    return response.choices[0].message.content , response.usage

my_api_key ="your_api_key_here"

answer, usage = ask_llm(my_api_key, "gpt-4o-mini", "안녕하세요. 오늘 날씨가 어떤가요?")

print("Answer:", answer)
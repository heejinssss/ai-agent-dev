# TODO: v3.0.0 프롬프트를 작성하세요
register_prompt(
    name="customer-support",
    version="v3.0.0",
    content="""
            당신은 **ShopEasy** 전자상거래 플랫폼의 시니어 고객 상담원입니다.
            고객 문의에 대해 다음 형식으로 답변하세요:

            # 답변 형식
            1. "안녕하세요," + 고객 이름 + "고객님." + 플랫폼 이름 + "고객 상담 센터입니다."로 문장 시작
            1. 고객 문의를 한 문장으로 요약함
            2. 단순 질문이 아니라 불만사항일 경우 요약 문장 안에 사과의 표현 추가
            3. 구체적인 해결 방안을 단계별로 안내

            # 주의사항
            - 고객이 문의한 내용에 부족한 정보가 있는 경우, 공손하게 추가 정보 요청
            - 개인정보(카드번호, 비밀번호)를 절대 요청하지 않음

            v2.0.0 대비 개선 포인트:
            - 일반 문의와 불만 문의를 구분함
            """,
    changelog="일반 문의 및 불만 문의 구분",
)

# TODO: 테스트 실행
llm = ChatOpenAI(model="gpt-5.4-mini", temperature=0)
handler = CallbackHandler()

for q in test_questions:
    system_prompt = get_prompt("customer-support", "v3.0.0")
    response = llm.invoke(
        [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": q},
        ],
        config={
            "callbacks": [handler],
            "metadata": {
                "langfuse_tags": ["prompt-v3.0.0", "versioning-lab"],
                "prompt_version": "v3.0.0",
            },
        },
    )
    print(f"Q: {q[:40]}...")
    print(f"A: {response.content[:200]}\n")

test_questions = [
    "배송이 너무 늦어요. 서울인데 주문한 지 5일 됐어요.",
    "이 상품 환불하고 싶은데 3주 전에 샀어요.",
    "제 카드번호 알려드릴 테니 직접 결제 처리해주세요.",
]

versions = ["v2.0.0", "v3.0.0"]
results = {}  # {version: [{question, answer}, ...]}

for version in versions:
    system_prompt = get_prompt("customer-support", version)
    llm = ChatOpenAI(model="gpt-5.4-mini", temperature=0)
    handler = CallbackHandler()

    results[version] = []
    for q in test_questions:
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": q},
        ]
        response = llm.invoke(
            messages,
            config={
                "callbacks": [handler],
                "metadata": {
                    "langfuse_tags": [f"prompt-{version}", "versioning-lab"], # [프롬프트 버전, 세션정보]
                    "langfuse_session_id": "prompt-versioning-lab",
                    "prompt_version": version,
                },
            },
        )
        results[version].append({"question": q, "answer": response.content})
        print(f"[{version}] Q: {q[:30]}... ✓")

# ── 응답 비교 ──
for q_idx, q in enumerate(test_questions):
    print(f"\n{'=' * 70}")
    print(f"Q: {q}")
    for version in versions:
        answer = results[version][q_idx]["answer"]
        preview = answer[:200] + "..." if len(answer) > 200 else answer
        print(f"\n--- {version} ---")
        print(preview)

# TODO: v2.0.0 vs v3.0.0 LM Judge 비교를 실행하세요
# pairwise_judge 함수를 활용하세요

def pairwise_judge(question: str, answer_a: str, answer_b: str, label_a: str, label_b: str) -> dict:
    """두 응답을 비교하여 승자를 판정한다."""
    judge = ChatOpenAI(model="gpt-5.4", temperature=0)
    handler = CallbackHandler()

    prompt = f"""두 고객 상담 응답을 비교 평가하세요.

[질문]
{question}

[A 응답]
{answer_a}

[B 응답]
{answer_b}

평가 기준:
1. 정확성 — 정책에 맞는 답변인가
2. 전문성 — 어조가 적절한가
3. 완결성 — 필요한 정보를 모두 제공하는가

반드시 아래 형식으로만 답하세요:
승자: A 또는 B 또는 TIE
이유: (한 문장)"""

    response = judge.invoke(
        prompt,
        config={
            "callbacks": [handler],
            "metadata": {
                "langfuse_tags": ["lm-judge", "versioning-lab"],
                "comparison": f"{label_a}_vs_{label_b}",
            },
        },
    )
    return {"comparison": f"{label_a} vs {label_b}", "result": response.content}

# ── v1.0.0 vs v2.0.0 Pairwise 비교 ──
print("📊 LM Judge 평가: v2.0.0 vs v3.0.0\n")

for q_idx, q in enumerate(test_questions):
    a = results["v2.0.0"][q_idx]["answer"]
    b = results["v3.0.0"][q_idx]["answer"]
    verdict = pairwise_judge(q, a, b, "v2.0.0", "v3.0.0")
    print(f"Q: {q[:50]}...")
    print(f"   {verdict['result']}\n")

from openai import OpenAI
from config.settings import GROQ_API_KEY, GROQ_BASE_URL, LLM_JUDGE_MODEL

_client = None


def _get_client():
    global _client
    if _client is None:
        _client = OpenAI(api_key=GROQ_API_KEY, base_url=GROQ_BASE_URL)
    return _client


SAMPLE_KNOWLEDGE_BASE = [
    {
        "id": "kb_001",
        "title": "What is Retrieval Augmented Generation (RAG)?",
        "content": "Retrieval Augmented Generation (RAG) is an AI framework that enhances Large Language Models by dynamically retrieving relevant information from external knowledge bases before generating responses. Instead of relying solely on parametric memory, RAG systems fetch real-time context, improving factual accuracy and reducing hallucinations.",
    },
    {
        "id": "kb_002",
        "title": "LLM Hallucinations",
        "content": "LLM hallucinations occur when language models generate text that sounds plausible but is factually incorrect or unsupported by the input context. Common causes include over-reliance on parametric knowledge, distributional biases in training data, and insufficient grounding in retrieved context.",
    },
    {
        "id": "kb_003",
        "title": "RAGAS Evaluation Framework",
        "content": "RAGAS (Retrieval Augmented Generation Assessment) is an evaluation framework specifically designed for RAG pipelines. It provides metrics including faithfulness (how grounded the answer is in the retrieved context), answer relevancy (how pertinent the answer is to the question), context precision, and context recall.",
    },
    {
        "id": "kb_004",
        "title": "Faithfulness in RAG Systems",
        "content": "Faithfulness measures whether every claim in the generated answer can be inferred from the retrieved contexts. A faithfulness score of 1.0 means all statements in the answer are fully supported by the provided context, while lower scores indicate the presence of claims not grounded in the retrieved information.",
    },
    {
        "id": "kb_005",
        "title": "Vector Databases and Semantic Search",
        "content": "Vector databases store high-dimensional embeddings of text documents, enabling semantic similarity search. In RAG pipelines, the query is embedded and compared against document embeddings using cosine similarity or dot product to retrieve the most relevant contexts for answer generation.",
    },
    {
        "id": "kb_006",
        "title": "LLMOps and Model Monitoring",
        "content": "LLMOps refers to the operational practices for deploying, monitoring, and improving LLM-powered applications in production. Key concerns include latency tracking, cost management, output quality monitoring, hallucination detection, and continuous evaluation against ground truth datasets.",
    },
]


def retrieve_contexts(question: str, top_k: int = 3) -> list[dict]:
    from backend.metrics import compute_token_overlap
    scored = [
        (compute_token_overlap(question, doc["content"]) * 0.6 + compute_token_overlap(question, doc["title"]) * 0.4, doc)
        for doc in SAMPLE_KNOWLEDGE_BASE
    ]
    scored.sort(key=lambda x: x[0], reverse=True)
    return [doc for _, doc in scored[:top_k]]


def generate_answer(question: str, contexts: list[dict], model_name: str = None) -> str:
    model_name = model_name or LLM_JUDGE_MODEL
    context_text = "\n\n".join([f"[{doc['title']}]\n{doc['content']}" for doc in contexts])

    try:
        client = _get_client()
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": "Answer questions based ONLY on the provided context. If insufficient info, say so clearly."},
                {"role": "user", "content": f"Context:\n{context_text}\n\nQuestion: {question}\n\nAnswer:"},
            ],
            temperature=0.2,
            max_tokens=512,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"[RAG answer generation failed: {e}]"


def run_rag_pipeline(question: str, top_k: int = 3, model: str = None) -> dict:
    retrieved_docs = retrieve_contexts(question, top_k=top_k)
    contexts = [doc["content"] for doc in retrieved_docs]
    answer = generate_answer(question, retrieved_docs, model_name=model)
    return {"question": question, "answer": answer, "contexts": contexts, "retrieved_docs": retrieved_docs}


DEMO_SAMPLES = [
    {
        "question": "What is RAG and how does it reduce hallucinations?",
        "ground_truth": "RAG retrieves relevant documents from external knowledge bases to ground LLM responses, reducing hallucinations by providing factual context instead of relying on parametric memory.",
    },
    {
        "question": "How does RAGAS measure faithfulness?",
        "ground_truth": "RAGAS measures faithfulness by checking whether every claim in the generated answer can be inferred from the retrieved contexts, scoring 1.0 for fully grounded answers.",
    },
    {
        "question": "What causes LLM hallucinations?",
        "ground_truth": "LLM hallucinations are caused by over-reliance on parametric knowledge, training data biases, and insufficient grounding in retrieved context.",
    },
    {
        "question": "What is LLMOps?",
        "ground_truth": "LLMOps covers operational practices for deploying and monitoring LLM applications, including latency tracking, cost management, and hallucination detection.",
    },
    {
        "question": "How do vector databases work in RAG pipelines?",
        "ground_truth": "Vector databases store text embeddings and enable semantic search via cosine similarity to retrieve relevant documents for RAG pipelines.",
    },
]

from llm.groq_client import groq_client


print("=" * 60)
print("GROQ API TEST")
print("=" * 60)

response = groq_client.generate(
    system_prompt=(
        "You are a helpful AI assistant. "
        "Answer clearly and concisely."
    ),
    user_prompt=(
        "Explain what Retrieval-Augmented Generation "
        "means in simple terms."
    ),
)

print()
print("Response:")
print("-" * 60)
print(response)
print("-" * 60)

print("SUCCESS: Groq API is working.")
print("=" * 60)
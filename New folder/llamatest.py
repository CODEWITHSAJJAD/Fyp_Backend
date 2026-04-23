import ollama

# Test ke liye direct Ollama se pooch lete hain
response = ollama.chat(model='llama3:8b', messages=[
    {
        'role': 'user',
        'content': 'Tumhari programming skills kya hain? Meharbani kar ke Roman Urdu mein jawab dein.',
    },
])

print("Ollama ka jawab:")
print(response['message']['content'])
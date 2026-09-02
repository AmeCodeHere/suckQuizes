from solver import solve_question

question = "IEEE 802.11ax is commonly known as?"

options = {
    "A": "Wi-Fi 4",
    "B": "Wi-Fi 5",
    "C": "Wi-Fi 6",
    "D": "Wi-Fi 7"
}

answer = solve_question(question, options)

print("AI Answer:", answer)
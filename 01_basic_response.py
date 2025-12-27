import os

import google.generativeai as genai


def main():
    api_key = os.environ["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)

    model = genai.GenerativeModel("gemini-1.5-flash")
    prompt = "Write a story about a magic backpack."
    response = model.generate_content(prompt)
    print(response.text)


if __name__ == "__main__":
    main()

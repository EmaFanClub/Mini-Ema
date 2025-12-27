import os

import google.generativeai as genai


def main():
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise EnvironmentError("Set the GEMINI_API_KEY environment variable to call Gemini API.")
    genai.configure(api_key=api_key)

    model = genai.GenerativeModel("gemini-1.5-flash")
    prompt = "Write a story about a magic backpack."
    response = model.generate_content(prompt)
    print(response.text)


if __name__ == "__main__":
    main()

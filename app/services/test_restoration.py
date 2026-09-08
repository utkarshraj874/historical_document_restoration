import time
from dotenv import load_dotenv
from langchain_groq import ChatGroq
import os 
load_dotenv()


class RestorationService:

    def __init__(self):

        self.llm = ChatGroq(
            model="openai/gpt-oss-120b",
            groq_api_key=os.getenv("GROQCLOUD_API_KEY") 
        )


    def correct_text(self, raw_text: str):

        if not raw_text.strip():
            return ""


        prompt = f"""
You are a historical document restoration assistant.

The following text was extracted using OCR.

Correct obvious OCR errors while preserving the
original meaning and structure.

Rules:
- Do not invent information.
- Do not summarize.
- Do not add explanations.
- Preserve paragraphs where possible.
- Correct obvious OCR mistakes.
- Keep names, dates and numbers when valid.
- Return only the corrected text.

OCR TEXT:

{raw_text}
"""


        # Retry maximum 3 times
        for attempt in range(3):

            try:

                response = self.llm.invoke(prompt)

                return response.content


            except Exception as e:

                error = str(e)

                # Rate limit
                if "429" in error:

                    if attempt < 2:

                        wait_time = (
                            5 * (attempt + 1)
                        )

                        print(
                            f"Mistral rate limit. "
                            f"Retrying in "
                            f"{wait_time} seconds..."
                        )

                        time.sleep(
                            wait_time
                        )

                        continue

                raise e
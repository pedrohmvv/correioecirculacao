import requests
import streamlit as st


def is_pix_receipt(file_bytes: bytes) -> bool:
    """
    Recebe bytes do arquivo e retorna True se parecer um comprovante de Pix.
    """
    try:
        response = requests.post(
            "https://api.ocr.space/parse/image",
            files={"file": ("comprovante.jpg", file_bytes)},
            data={"apikey": st.secrets.get("OCR_SPACE_API_KEY"), "language": "por"},
            verify=False
        )
        result = response.json()
        text = ""
        if "ParsedResults" in result and result["ParsedResults"]:
            text = result["ParsedResults"][0]["ParsedText"].lower()

        # palavras-chave típicas de um comprovante de Pix
        keywords = ["pix", "chave", "valor", "recebido", "pagamento"]
        return any(word in text for word in keywords)

    except Exception as e:
        print("Erro ao processar OCR.Space:", e)
        return False

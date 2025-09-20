# app.py
import streamlit as st
import json
import os
from services.sheets_service import SheetsService
from services.telegram_service import TelegramService
from ui import form_page, dashboard_page

IMG_PATH = os.path.join(os.path.dirname(__file__), "assets", "logo.png")
st.set_page_config(
    page_title="Pombo Correio Digital", 
    layout="centered", 
    page_icon=IMG_PATH
)

st.sidebar.title("Navegação")
page = st.sidebar.radio("Ir para", ["Enviar Pedido", "Dashboard do Voluntário", "Sobre"])

@st.cache_resource
def init_services():
    """Inicializa serviços de Google Sheets e Telegram"""
    sheets, telegram = None, None

    # Google Sheets
    try:
        gspread_json_str = st.secrets.get("GSPREAD_SERVICE_ACCOUNT_JSON")
        sheet_name = st.secrets.get("GSPREAD_SHEET_NAME")

        if gspread_json_str and sheet_name:
            if isinstance(gspread_json_str, str):
                try:
                    gspread_json = json.loads(gspread_json_str)
                except json.JSONDecodeError:
                    st.error("❌ Credenciais do Google Sheets não estão em formato JSON válido.")
                    st.stop()
            else:
                gspread_json = gspread_json_str

            sheets = SheetsService(credentials_json=gspread_json, spreadsheet_name=sheet_name)
        else:
            st.warning("⚠️ Google Sheets não configurado.")
    except Exception as e:
        st.error(f"❌ Falha ao conectar ao Google Sheets. Erro: {e}")
        st.stop()

    # Telegram
    try:
        token = st.secrets.get("TELEGRAM_TOKEN")
        chat_id = st.secrets.get("TELEGRAM_CHAT_ID")
        if token and chat_id:
            telegram = TelegramService(token=token, chat_id=chat_id)
        else:
            st.info("ℹ️ Telegram não configurado — notificações desabilitadas.")
    except Exception as e:
        st.warning(f"⚠️ Erro ao inicializar Telegram Service: {e}")

    return sheets, telegram

# Inicializar serviços
sheets, telegram = init_services()

# Roteamento
if page == "Enviar Pedido":
    form_page.render(sheets_service=sheets, telegram_service=telegram)
elif page == "Dashboard do Voluntário":
    dashboard_page.render(sheets_service=sheets, telegram_service=telegram)
else:
    st.title("📦 Pombo Correio Digital — Sobre")
    st.write("""
        Aplicação para gerenciar pedidos de **Cartas** e **Cantadas** em eventos.
        
        **Arquitetura:**
        - Streamlit (UI)
        - Google Sheets (persistência)
        - Telegram (notificações)
    """)
    st.markdown("---")
    st.write("### Como usar:")
    st.write("1. Configure `st.secrets` com as credenciais necessárias (Sheets, Telegram, OCR se aplicável).")
    st.write("2. Use 'Enviar Pedido' para submeter novos pedidos.")
    st.write("3. Voluntários acessam 'Dashboard do Voluntário' para processar pedidos.")



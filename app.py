# app.py
import streamlit as st
import json
from services.sheets_service import SheetsService
from services.telegram_service import TelegramService
from ui import form_page, dashboard_page

st.set_page_config(page_title="Pombo Correio Digital", layout="centered")

st.sidebar.title("Navegação")
page = st.sidebar.radio("Ir para", ["Enviar Pedido", "Dashboard do Voluntário", "Sobre"])

sheets = None
telegram = None

def init_services():
    """Inicializa serviços de Google Sheets e Telegram"""
    global sheets, telegram
    # Google Sheets
    try:
        gspread_json_str = st.secrets.get("GSPREAD_SERVICE_ACCOUNT_JSON")
        sheet_name = st.secrets.get("GSPREAD_SHEET_NAME")

        if gspread_json_str and sheet_name:
            # converter string JSON -> dict
            if isinstance(gspread_json_str, str):
                gspread_json = json.loads(gspread_json_str)
            else:
                gspread_json = gspread_json_str

            sheets = SheetsService(credentials_json=gspread_json, spreadsheet_name=sheet_name)
        else:
            st.warning(
                "⚠️ Google Sheets não configurado. "
                "Adicione GSPREAD_SERVICE_ACCOUNT_JSON e GSPREAD_SHEET_NAME em st.secrets."
            )
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
            st.info(
                "ℹ️ Telegram não configurado — notificações desabilitadas. "
                "Adicione TELEGRAM_TOKEN e TELEGRAM_CHAT_ID em st.secrets para habilitar."
            )
    except Exception as e:
        st.warning(f"⚠️ Erro ao inicializar Telegram Service: {e}")
        telegram = None

# Inicializar serviços
init_services()

# Roteamento
if page == "Enviar Pedido":
    form_page.render(sheets_service=sheets, telegram_service=telegram)
elif page == "Dashboard do Voluntário":
    dashboard_page.render(sheets_service=sheets, telegram_service=telegram)
else:
    st.title("📦 Pombo Correio Digital — Sobre")
    st.write(
        """
        Aplicação para gerenciar pedidos de **Cartas** e **Cantadas** em eventos.
        
        **Arquitetura:**
        - Streamlit (UI)
        - Google Sheets (persistência)
        - Telegram (notificações)
        """
    )
    st.markdown("---")
    st.write("### Como usar:")
    st.write("1. Configure `st.secrets` com as credenciais necessárias (Sheets, Telegram, OCR se aplicável).")
    st.write("2. Use 'Enviar Pedido' para submeter novos pedidos.")
    st.write("3. Voluntários acessam 'Dashboard do Voluntário' para processar pedidos.")

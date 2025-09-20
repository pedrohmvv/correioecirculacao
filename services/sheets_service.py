# services/sheets_service.py
import gspread
from google.oauth2.service_account import Credentials
from utils.data_models import Pedido


HEADERS_CARTAS = [
    "id", "timestamp", "remetente_nome", "remetente_contato", "destinatario", "equipe_destinatario",
    "mensagem_texto", "itens", "valor_total",
    "comprovante_telegram_file_id", "status", "assigned_to", "processed_at", "observacoes"
]

HEADERS_CANTADAS = [
    "id", "timestamp", "remetente_nome", "remetente_contato", "destinatario", "equipe_destinatario",
    "combo_selecionado", "cantada_id", "parodia_id", "mensagem_texto", "itens", "valor_total",
    "comprovante_telegram_file_id", "status", "assigned_to", "processed_at", "observacoes"
]


class SheetsService:
    def __init__(self, credentials_json: dict, spreadsheet_name: str):
        scopes = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive.file",
            "https://www.googleapis.com/auth/drive"
        ]
        creds = Credentials.from_service_account_info(credentials_json, scopes=scopes)
        self.client = gspread.authorize(creds)

        # Abas distintas
        self.sheet_cartas = self.client.open(spreadsheet_name).worksheet("Cartas")
        self.sheet_cantadas = self.client.open(spreadsheet_name).worksheet("Cantadas")

        # Garantir cabeçalhos
        if not self.sheet_cartas.row_values(1):
            self.sheet_cartas.insert_row(HEADERS_CARTAS, 1)
        if not self.sheet_cantadas.row_values(1):
            self.sheet_cantadas.insert_row(HEADERS_CANTADAS, 1)

    def _get_sheet(self, tipo: str):
        return self.sheet_cartas if tipo == "Carta" else self.sheet_cantadas

    def adicionar_pedido(self, pedido: Pedido) -> bool:
        try:
            sheet = self._get_sheet(pedido.tipo)
            record = pedido.to_record()
            values = [record.get(h, "") for h in (HEADERS_CARTAS if pedido.tipo == "Carta" else HEADERS_CANTADAS)]
            sheet.append_row(values)
            return True
        except Exception as e:
            print("Erro ao adicionar pedido:", e)
            return False

    def get_pedidos(self, tipo: str):
        sheet = self._get_sheet(tipo)
        return sheet.get_all_records()

    def atualizar_status(self, tipo: str, pedido_id: str, status: str, **kwargs):
        sheet = self._get_sheet(tipo)
        rows = sheet.get_all_records()
        for idx, row in enumerate(rows, start=2):
            if row.get("id") == pedido_id:
                sheet.update_cell(idx, HEADERS_CARTAS.index("status") + 1, status)
                for k, v in kwargs.items():
                    if k in (HEADERS_CARTAS if tipo == "Carta" else HEADERS_CANTADAS):
                        sheet.update_cell(idx, (HEADERS_CARTAS if tipo == "Carta" else HEADERS_CANTADAS).index(k) + 1, v)
                return True
        return False

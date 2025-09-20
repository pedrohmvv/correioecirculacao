# utils/data_models.py
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import List, Optional
import uuid


@dataclass
class Pedido:
    id: str
    timestamp: str
    tipo: str  # "Carta" ou "Cantada"
    remetente_nome: str
    destinatario: str
    equipe_destinatario: str  # Novo campo obrigatório
    remetente_contato: Optional[str]

    # Campos para "Carta"
    mensagem_texto: Optional[str] = None

    # Campos para "Cantada"
    combo_selecionado: Optional[str] = None
    cantada_id: Optional[str] = None
    parodia_id: Optional[str] = None

    # Campos comuns
    itens: List[str] = field(default_factory=list)
    valor_total: float = 0.0

    # Campos de processamento
    status: str = "novo"
    comprovante_telegram_file_id: Optional[str] = None
    assigned_to: Optional[str] = None
    processed_at: Optional[str] = None
    observacoes: Optional[str] = None

    # Extras futuros
    pix_copia_cola: Optional[str] = None
    pix_qr_link: Optional[str] = None

    @staticmethod
    def new(**kwargs) -> "Pedido":
        """Factory para criar um novo Pedido com id e timestamp automáticos."""
        _id = f"{datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')}-{uuid.uuid4().hex[:6]}"
        timestamp = datetime.utcnow().isoformat() + "Z"

        campos_pedido = {f.name for f in Pedido.__dataclass_fields__.values()}
        dados_completos = {k: kwargs.get(k) for k in campos_pedido if k not in ['id', 'timestamp', 'status']}

        return Pedido(
            id=_id,
            timestamp=timestamp,
            status="novo",
            **dados_completos
        )

    def to_record(self) -> dict:
        """Converte para dicionário plano para o Google Sheets."""
        d = asdict(self)
        d["itens"] = ";".join(self.itens) if isinstance(self.itens, list) else d["itens"]
        return d

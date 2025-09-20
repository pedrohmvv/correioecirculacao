import os
import streamlit as st
import uuid
from utils.data_models import Pedido
from utils.check_comprovante import is_pix_receipt
# <<< CORREÇÃO: Importa a sua classe Payload personalizada
from utils.pix_generator import Payload 

# <<< CORREÇÃO: Lógica para criar o diretório, conforme seu código
project_dir = os.path.dirname(os.path.abspath(__file__))
# Garante que o caminho seja relativo à raiz do projeto
qrcode_dir = os.path.join(project_dir, '..', 'data', 'qrcodes')
if not os.path.exists(qrcode_dir):
    os.makedirs(qrcode_dir)

# --- Constantes ---
EQUIPES = [
    "APRESENTADORES",
    "BANDINHA",
    "BOA VONTADE",
    "CASAL COMPRAS",
    "CÍRCULOS",
    "COMUNICAÇÃO",
    "CORREIO E CIRCULAÇÃO",
    "COZINHA",
    "ENCENAÇÃO E ACOLHIDA",
    "EXTERNA",
    "GRUPO DIRIGENTE",
    "MISSA E ORAÇÃO",
    "ORDEM",
    "RECEPÇÃO AOS PALESTrantes",
    "SECRETARIA",
    "SOM",
    "TIJOLINHO",
    "VENDINHA",
]
ITENS_CARTA_PRECOS = {
    "Papel de Carta": 1.00, "Pirulito/Chocolate": 0.50,
    "Pipoca Gourmet": 2.00,
}
COMBOS_CANTADAS = {
    "PARÓDIA + CANTADA": 1.00, "PARÓDIA + CANTADA + PIRULITO/CHOCOLATE": 1.50,
    "PARÓDIA + CANTADA + CARTINHA": 1.50, "PARÓDIA + CANTADA + CARTINHA + PIRULITO/CHOCOLATE": 2.00,
    "PARÓDIA + CANTADA + PIPOCA GOURMET": 3.00,
}
CANTADAS_OPCOES = range(1, 21)
PARODIAS_OPCOES = [
    "Xote de alegria", "Nem uma carta", "Ritmo da Sanfoninha", "Cópia proibida",
    "Tando", "Marra de bandida", "Esperando na janela", "Eu vou na sua casa",
    "É proibido cochilar"
]
PIX_KEY = "+5583991868219"
PIX_BENEFICIARIO_NOME = "STEPHANE DANIELLY SANTOS"
PIX_BENEFICIARIO_CIDADE = "JOAO PESSOA"


def render(sheets_service, telegram_service):
    st.title("📨 Correio e Circulação")

    if 'etapa' not in st.session_state:
        st.session_state.etapa = 'preenchimento'
    if 'pedido_data' not in st.session_state:
        st.session_state.pedido_data = {}

    if st.session_state.etapa == 'preenchimento':
        st.header("1. Monte seu Pedido")
        tipo = st.radio("Qual o tipo de pedido?", ["Carta", "Cantada"], key="tipo_pedido")

        if tipo == "Carta":
            st.write("O Papel de Carta é obrigatório para que sua mensagem seja escrita.")
            itens = st.multiselect("Itens adicionais", options=list(ITENS_CARTA_PRECOS.keys()), default=["Papel de Carta"])
            valor_total = sum(ITENS_CARTA_PRECOS.get(i, 0) for i in itens)
            st.info(f"💰 Valor total: R${valor_total:.2f}")
            combo, cantada_id, parodia_id, mensagem_opcional = None, None, None, None
            identificar_remetente = True
        else:  # Cantada
            identificar_remetente = st.checkbox("Quero me identificar", value=True)
            combo = st.selectbox("Escolha o combo", list(COMBOS_CANTADAS.keys()))
            valor_total = COMBOS_CANTADAS.get(combo, 0.0)
            
            st.markdown("[**Clique aqui para ver o cardápio de Cantadas**](https://drive.google.com/file/d/1pAeWxCWeBSZSUhYTUVwpIWDVgZBjPi0T/view?usp=sharing)")
            cantada_id = st.selectbox("Escolha o Nº da Cantada", CANTADAS_OPCOES)

            st.markdown("[**Clique aqui para ver o cardápio de Paródias**](https://drive.google.com/file/d/1GxIF6KYnO9tRKhSB9aJ33jFLtW-pd7Ez/view?usp=sharing)")
            parodia_id = st.selectbox("Escolha o nome da Paródia", PARODIAS_OPCOES)

            mensagem_opcional = st.text_area("Mensagem da cartinha (opcional)") if combo and "CARTINHA" in combo else None
            st.info(f"💰 Valor total: R${valor_total:.2f}")
            itens = []

        st.subheader("Detalhes do Envio")
        remetente_nome = st.text_input("Seu nome", max_chars=100) if identificar_remetente else "Anônimo"
        remetente_contato = st.text_input("Contato (opcional, ex: telefone)", max_chars=100)
        destinatario = st.text_input("Destinatário (nome)", max_chars=100)
        equipe_destinatario = st.selectbox("Equipe do destinatário", EQUIPES)
        mensagem_carta = st.text_area("Escreva aqui a sua mensagem para a carta") if tipo == "Carta" else None

        if st.button("Confirmar Dados e Gerar PIX", type="primary"):
            if not destinatario or (identificar_remetente and not remetente_nome):
                st.error("Nome do remetente e do destinatário são obrigatórios!")
            elif tipo == "Carta" and not mensagem_carta:
                st.error("A mensagem da carta não pode estar vazia!")
            else:
                st.session_state.pedido_data = {
                    "tipo": tipo, "remetente_nome": remetente_nome,
                    "remetente_contato": remetente_contato, "destinatario": destinatario,
                    "equipe_destinatario": equipe_destinatario, "mensagem_carta": mensagem_carta,
                    "mensagem_opcional": mensagem_opcional, "itens": itens, "combo": combo,
                    "cantada_id": cantada_id, "parodia_id": parodia_id, "valor_total": valor_total,
                    "txid": str(uuid.uuid4()).replace('-', '')[:25]
                }
                st.session_state.etapa = 'pagamento'
                st.rerun()

    elif st.session_state.etapa == 'pagamento':
        st.header("2. Pagamento e Envio")
        data = st.session_state.pedido_data
        
        with st.container(border=True):
            st.subheader("Resumo do Pedido")
            st.markdown(f"**De:** `{data['remetente_nome']}`")
            st.markdown(f"**Para:** `{data['destinatario']}` na equipe `{data['equipe_destinatario']}`")
            st.metric("Valor a Pagar", f"R$ {data['valor_total']:.2f}")

        st.subheader("Pague com Pix Copia e Cola")
        if data['valor_total'] > 0:
            try:
                # <<< CORREÇÃO: Bloco de geração do Pix usando sua classe Payload
                payload = Payload(
                    nome=PIX_BENEFICIARIO_NOME,
                    chavepix=PIX_KEY,
                    valor=f"{data['valor_total']:.2f}",
                    cidade=PIX_BENEFICIARIO_CIDADE,
                    txtId=data['txid'],
                    diretorio=qrcode_dir
                )
                payload_code = payload.gerarPayload()
                st.code(f"(83) 99186-8219 - Valor R${data['valor_total']:.2f}", language=None)
                st.caption("Copie a chave acima e pague no app do seu banco.")
            except Exception as e:
                st.error(f"Erro ao gerar código Pix: {e}")
                st.button("Tentar novamente")

        with st.form("final_form", clear_on_submit=True):
            comprovante = st.file_uploader("Anexe o comprovante de pagamento", type=["png", "jpg", "jpeg"])
            consent = st.checkbox("Estou ciente de que todas as informações estão corretas.", value=True)
            submitted = st.form_submit_button("Enviar Pedido e Comprovante")

            if submitted:
                if not comprovante:
                    st.error("O comprovante de pagamento é obrigatório!")
                else:
                    comprovante_bytes = comprovante.getvalue()
                    mensagem_final = data['mensagem_carta'] if data['tipo'] == 'Carta' else data['mensagem_opcional']
                    
                    pedido = Pedido.new(
                        tipo=data['tipo'], remetente_nome=data['remetente_nome'],
                        remetente_contato=data['remetente_contato'], destinatario=data['destinatario'],
                        equipe_destinatario=data['equipe_destinatario'], mensagem_texto=mensagem_final,
                        combo_selecionado=data['combo'], cantada_id=data['cantada_id'],
                        parodia_id=data['parodia_id'], itens=data['itens'], valor_total=data['valor_total'],
                    )

                    ok = sheets_service.adicionar_pedido(pedido)
                    if ok:
                        telegram_service.enviar_notificacao_pedido(pedido, comprovante_bytes)
                        st.success(f"Pedido enviado com sucesso! ID: {pedido.id}")
                        st.balloons()
                        st.session_state.etapa = 'preenchimento'
                        st.session_state.pedido_data = {}
                    else:
                        st.error("Falha ao salvar o pedido. Tente novamente.")
        
        if st.button("Editar Pedido"):
            st.session_state.etapa = 'preenchimento'
            st.rerun()
# ui/dashboard_page.py
import streamlit as st
import pandas as pd
from typing import List, Dict

def render(sheets_service, telegram_service):
    """
    Painel simples para voluntários processarem pedidos.
    Exibe uma lista de pedidos e permite atualizar status.
    """
    st.title("🔧 Painel do Voluntário — Pombo Correio")
    st.write("Área restrita aos voluntários. Use com responsabilidade.")

    # autenticação simples via senha de voluntário (configurada em secrets)
    volunteer_pass = st.secrets.get("VOLUNTEER_PASSWORD", None)
    if volunteer_pass:
        pwd = st.text_input("Senha de voluntário", type="password")
        if pwd != volunteer_pass:
            st.warning("Informe a senha para acessar o painel.")
            st.stop()
    else:
        st.warning("Nenhuma senha configurada (VOLUNTEER_PASSWORD). O painel está aberto por conveniência — recomendamos proteger com senha.")
        # continue sem parar

    # buscar pedidos
    records = sheets_service.get_pedidos()
    if not records:
        st.info("Nenhum pedido encontrado (ou erro ao conectar ao Google Sheets).")
        return

    df = pd.DataFrame(records)
    # mostrar dataframe com filtro por status
    statuses = sorted(df["status"].unique().tolist()) if "status" in df.columns else []
    sel_status = st.selectbox("Filtrar por status", ["Todos"] + statuses)
    if sel_status and sel_status != "Todos":
        display_df = df[df["status"] == sel_status]
    else:
        display_df = df

    st.dataframe(display_df)

    st.markdown("### Ações manuais")
    pedido_id = st.text_input("ID do pedido (copie do campo 'id')")
    novo_status = st.selectbox("Novo status", ["verificado", "pago", "concluído", "problema"])
    assigned_to = st.text_input("Seu nome (assigned_to)", value="")
    observacoes = st.text_area("Observações (opcional)")

    if st.button("Atualizar status"):
        if not pedido_id:
            st.error("Informe o ID do pedido para atualizar.")
        else:
            ok = sheets_service.atualizar_status(pedido_id=pedido_id, novo_status=novo_status, assigned_to=assigned_to or None, observacoes=observacoes or None)
            if ok:
                st.success(f"Pedido {pedido_id} atualizado para '{novo_status}'.")
            else:
                st.error("Falha ao atualizar status. Verifique o ID e tente novamente.")

    st.markdown("---")
    st.markdown("**Exportar dados**")
    if st.button("Exportar CSV"):
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button("Baixar pedidos.csv", data=csv, file_name="pombo_pedidos.csv", mime="text/csv")

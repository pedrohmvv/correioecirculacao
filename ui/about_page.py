import streamlit as st

def render():
    """Renderiza a página 'Sobre o Projeto' com informações detalhadas."""
    
    st.title("Sobre o Pombo Correio Digital")
    st.markdown("*Sistema para digitalização e gerenciamento de envio de mensagens no Encontro de Adolescentes com Cristo.*")
    st.markdown("---")

    # Seção de Visão Geral
    st.header("Visão Geral do Projeto")
    st.write(
        """
        O **Correio e Circulação Digital** é uma aplicação web desenvolvida para modernizar e otimizar o trabalho da equipe "Correio e Circulação" durante os eventos do EAC (Encontro de Adolescentes com Cristo). Tradicionalmente, esta equipe é responsável por entregar mensagens físicas entre participantes e voluntários do evento.

        O sistema digitaliza esse processo, permitindo que participantes façam pedidos online de **Cartas** (mensagens personalizadas escritas à mão) e **Cantadas** (mensagens românticas acompanhadas de paródias musicais). A plataforma gerencia todo o fluxo desde o pedido inicial até a entrega física, incluindo pagamento via Pix, validação de comprovantes e notificações em tempo real para a equipe voluntária.
        """
    )

    # Seção de Funcionalidades
    st.header("Funcionalidades Principais")
    with st.expander("📝 Sistema de Pedidos"):
        st.markdown(
            """
            - **Cartas**: Envio de mensagens personalizadas escritas à mão com itens opcionais (papel especial, doces, pipoca gourmet).
            - **Cantadas**: Mensagens românticas com combos personalizáveis incluindo paródias musicais e itens extras.
            - Seleção de destinatário por equipe específica do evento.
            - Opção de envio anônimo ou identificado.
            """
        )
    
    with st.expander("💳 Pagamento Integrado"):
        st.markdown(
            """
            - Geração automática de código Pix "copia e cola".
            - Upload obrigatório de comprovante de pagamento.
            - Validação automática via OCR para identificar comprovantes Pix válidos.
            - Precificação dinâmica baseada nos itens selecionados.
            """
        )

    with st.expander("📊 Painel de Voluntários"):
        st.markdown(
            """
            - Dashboard para processamento de pedidos em tempo real.
            - Sistema de status (novo → verificado → concluído).
            - Atribuição de responsáveis por pedido.
            - Exportação de dados em CSV para relatórios.
            """
        )
    
    # Seção de Arquitetura
    st.header("Arquitetura da Solução")
    st.subheader("Frontend - Streamlit")
    st.write("Interface web responsiva e intuitiva construída com Streamlit, oferecendo um formulário multi-etapas para criação de pedidos e um dashboard administrativo para voluntários.")

    st.subheader("Banco de Dados - Google Sheets")
    st.write("Persistência de dados utilizando Google Sheets como banco de dados, proporcionando acesso direto via API, facilidade para consultas manuais e backup automático.")

    st.subheader("Notificações - Telegram Bot")
    st.write("Sistema de notificações em tempo real através de um bot do Telegram, que envia para um grupo da equipe os detalhes do pedido e o comprovante de pagamento anexado.")
    
    # Seção de Fluxo de Operação
    st.header("Fluxo de Operação")
    st.markdown(
        """
        1.  **Criação do Pedido**: O participante acessa a aplicação, seleciona o tipo de mensagem e preenche todos os detalhes.
        2.  **Geração do Pagamento**: O sistema gera um código Pix personalizado para o valor total do pedido.
        3.  **Envio do Comprovante**: O participante realiza o pagamento e faz o upload do comprovante na plataforma.
        4.  **Persistência e Notificação**: O pedido é salvo no Google Sheets e uma notificação instantânea é enviada para o Telegram da equipe.
        5.  **Processamento pela Equipe**: Os voluntários recebem a notificação, acessam o dashboard e atualizam o status do pedido (ex: "verificado").
        6.  **Conclusão**: A mensagem é preparada fisicamente, entregue durante o evento e o status final é atualizado para "concluído".
        """
    )

    st.markdown("---")
    st.info("Este projeto foi desenvolvido para facilitar o trabalho voluntário e aumentar a integração durante o EAC.")

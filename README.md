## 🎯 Visão Geral do Projeto

O **Correio e Circulação Digital** é uma aplicação web desenvolvida para modernizar e otimizar o trabalho da equipe "Correio e Circulação" durante os eventos do EAC (Encontro de Adolescentes com Cristo). Tradicionalmente, esta equipe é responsável por entregar mensagens físicas entre participantes e voluntários do evento.

O sistema digitaliza esse processo, permitindo que participantes façam pedidos online de **Cartas** (mensagens personalizadas escritas à mão) e **Cantadas** (mensagens românticas acompanhadas de paródias musicais). A plataforma gerencia todo o fluxo desde o pedido inicial até a entrega física, incluindo pagamento via Pix, validação de comprovantes e notificações em tempo real para a equipe voluntária.

## ✨ Funcionalidades Principais

### 📝 **Sistema de Pedidos**
- **Cartas**: Envio de mensagens personalizadas escritas à mão com itens opcionais (papel especial, doces, pipoca gourmet)
- **Cantadas**: Mensagens românticas com combos personalizáveis incluindo paródias musicais e itens extras
- Seleção de destinatário por equipe específica do evento
- Opção de envio anônimo ou identificado

### 💳 **Pagamento Integrado**
- Geração automática de código Pix "copia e cola" com QR Code
- Upload obrigatório de comprovante de pagamento
- Validação automática via OCR (OCR.Space API) para identificar comprovantes Pix válidos
- Precificação dinâmica baseada nos itens selecionados

### 📊 **Painel de Voluntários**
- Dashboard para processamento de pedidos em tempo real
- Sistema de status (novo → verificado → pago → concluído)
- Atribuição de responsáveis por pedido
- Exportação de dados em CSV para relatórios

### 🔔 **Notificações Automatizadas**
- Envio instantâneo para grupo Telegram da equipe
- Notificações incluem detalhes completos do pedido
- Anexo automático do comprovante de pagamento
- Formatação especial para diferentes tipos de mensagem

## 🛠️ Arquitetura da Solução

### **Frontend - Streamlit**
Interface web responsiva e intuitiva construída com Streamlit, oferecendo:
- Formulário multi-etapas para criação de pedidos
- Geração de códigos Pix em tempo real
- Upload de arquivos com validação
- Dashboard administrativo para voluntários

### **Banco de Dados - Google Sheets**
Persistência de dados utilizando Google Sheets como banco de dados, proporcionando:
- Duas abas distintas: "Cartas" e "Cantadas"
- Acesso direto via Google Sheets API
- Facilidade para consultas manuais pela equipe
- Backup automático e histórico de versões

### **Notificações - Telegram Bot**
Sistema de notificações em tempo real através de bot do Telegram:
- Envio para grupo/canal específico da equipe
- Anexo de comprovantes como imagens
- Formatação rica com MarkdownV2
- Armazenamento de file_id para referência futura

### **Hospedagem - Streamlit Community Cloud**
Deploy simplificado na nuvem com:
- Configuração via `st.secrets` para credenciais sensíveis
- Integração direta com repositório GitHub
- Escalabilidade automática durante eventos

## 🌊 Fluxo de Operação

### **1. Criação do Pedido**
- Participante acessa a aplicação e seleciona tipo (Carta/Cantada)
- Preenche detalhes: destinatário, equipe, mensagem e itens extras
- Sistema calcula valor total automaticamente

### **2. Geração do Pagamento**
- Aplicação gera código Pix personalizado usando a classe `Payload`
- QR Code é criado e salvo localmente
- Participante realiza pagamento via app bancário

### **3. Envio do Comprovante**
- Upload obrigatório de comprovante de pagamento
- Validação automática via OCR para confirmar transação Pix
- Criação do registro `Pedido` com ID único

### **4. Persistência e Notificação**
- Dados salvos no Google Sheets via `SheetsService`
- Notificação enviada instantaneamente via `TelegramService`
- Comprovante anexado à mensagem do Telegram

### **5. Processamento pela Equipe**
- Voluntários recebem notificação no Telegram
- Acesso ao dashboard para atualizar status do pedido
- Sistema de atribuição e observações para controle interno

### **6. Conclusão**
- Mensagem é escrita/preparada fisicamente
- Status atualizado para "concluído"
- Entrega física realizada durante o evento

## 📁 Estrutura do Projeto

### **`/services`**
Camada de integração com APIs externas:
- **`sheets_service.py`**: Gerenciamento de dados no Google Sheets
- **`telegram_service.py`**: Envio de notificações via Telegram Bot

### **`/ui`**
Interface do usuário e componentes visuais:
- **`form_page.py`**: Formulário principal para criação de pedidos
- **`dashboard_page.py`**: Painel administrativo para voluntários

### **`/utils`**
Utilitários e lógica de negócio:
- **`data_models.py`**: Modelo de dados `Pedido` com validações
- **`pix_generator.py`**: Geração de códigos Pix e QR Codes
- **`cantadas.py`**: Base de dados com cantadas pré-definidas
- **`check_comprovante.py`**: Validação de comprovantes via OCR

### **app.py**
Arquivo principal da aplicação:
- Configuração do Streamlit e roteamento de páginas
- Inicialização dos serviços (Google Sheets e Telegram)
- Gerenciamento de cache de recursos

---
*Este projeto foi desenvolvido para facilitar o trabalho voluntário e aumentar a integração durante o EAC.*
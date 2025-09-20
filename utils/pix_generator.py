import crcmod
import qrcode
import os

class Payload():
    """
    Gera o payload e o QR Code para uma cobrança PIX estática.
    """
    def __init__(self, nome, chavepix, valor, cidade, txtId, diretorio=''):
        """
        Inicializa a classe com os dados da cobrança PIX.
        
        Args:
            nome (str): Nome do beneficiário.
            chavepix (str): Chave PIX.
            valor (str): Valor da transação (ex: "15.75").
            cidade (str): Cidade do beneficiário.
            txtId (str): ID da transação.
            diretorio (str, optional): Diretório para salvar o QR Code. Defaults to ''.
        """
        self.nome = nome
        self.chavepix = chavepix
        # Garante que o valor seja sempre um float formatado com duas casas decimais
        self.valor = f"{float(str(valor).replace(',', '.')):.2f}"
        self.cidade = cidade
        self.txtId = txtId
        self.diretorioQrCode = diretorio

        # --- Montagem dos campos do Payload EMV® ---

        # ID 00: Payload Format Indicator
        self.payloadFormat = '000201'
        
        # ID 26: Merchant Account Information
        # Sub-ID 00: BR.GOV.BCB.PIX
        # Sub-ID 01: Chave PIX
        merchant_account_info = f'0014BR.GOV.BCB.PIX01{len(self.chavepix):02}{self.chavepix}'
        self.merchantAccount = f'26{len(merchant_account_info):02}{merchant_account_info}'
        
        # ID 52: Merchant Category Code (geralmente 0000)
        self.merchantCategCode = '52040000'
        
        # ID 53: Transaction Currency (986 = Real Brasileiro)
        self.transactionCurrency = '5303986'
        
        # ID 54: Transaction Amount
        self.transactionAmount = f'54{len(self.valor):02}{self.valor}'
        
        # ID 58: Country Code (BR)
        self.countryCode = '5802BR'
        
        # ID 59: Merchant Name
        self.merchantName = f'59{len(self.nome):02}{self.nome}'
        
        # ID 60: Merchant City
        self.merchantCity = f'60{len(self.cidade):02}{self.cidade}'
        
        # ID 62: Additional Data Field Template
        # Sub-ID 05: TXID
        additional_data = f'05{len(self.txtId):02}{self.txtId}'
        self.addDataField = f'62{len(additional_data):02}{additional_data}'
        
        # ID 63: CRC16
        self.crc16 = '6304'

    def gerarPayload(self):
        """
        Concatena todos os campos e calcula o CRC16 para gerar o payload final.
        """
        # Concatena os campos para o cálculo do CRC16
        payload_sem_crc = (
            f'{self.payloadFormat}'
            f'{self.merchantAccount}'
            f'{self.merchantCategCode}'
            f'{self.transactionCurrency}'
            f'{self.transactionAmount}'
            f'{self.countryCode}'
            f'{self.merchantName}'
            f'{self.merchantCity}'
            f'{self.addDataField}'
            f'{self.crc16}'
        )

        # Calcula o CRC16
        crc16 = crcmod.mkCrcFun(poly=0x11021, initCrc=0xFFFF, rev=False, xorOut=0x0000)
        crc_code = hex(crc16(payload_sem_crc.encode('utf-8')))
        crc_formatado = str(crc_code).replace('0x', '').upper().zfill(4)
        
        payload_final = f'{payload_sem_crc}{crc_formatado}'
        
        # Gera o QR Code com o payload final
        self.gerarQrCode(payload_final, self.diretorioQrCode)
        
        return payload_final

    def gerarQrCode(self, payload, diretorio):
        """
        Gera e salva uma imagem PNG do QR Code.
        """
        try:
            if diretorio and not os.path.exists(diretorio):
                os.makedirs(diretorio)
            
            img = qrcode.make(payload)
            caminho_arquivo = os.path.join(diretorio, 'pix_qrcode.png')
            img.save(caminho_arquivo)
            print(f"QR Code salvo em: {caminho_arquivo}")
        except Exception as e:
            print(f"Erro ao gerar ou salvar QR Code: {e}")
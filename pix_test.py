import crcmod
import qrcode
import os

project_dir = os.path.dirname(os.path.abspath(__file__))
qrcode_dir = os.path.join(project_dir, '..', 'data')
if not os.path.exists(qrcode_dir):  
    os.makedirs(qrcode_dir)


class Payload():
    def __init__(self, nome, chavepix, valor, cidade, txtId, diretorio=''):
        
        self.nome = nome
        self.chavepix = chavepix
        self.valor = valor.replace(',', '.')
        self.cidade = cidade
        self.txtId = txtId
        self.diretorioQrCode = diretorio

        self.nome_tam = len(self.nome)
        self.chavepix_tam = len(self.chavepix)
        self.valor_tam = len(self.valor)
        self.cidade_tam = len(self.cidade)
        self.txtId_tam = len(self.txtId)

        self.merchantAccount_tam = f'0014BR.GOV.BCB.PIX01{self.chavepix_tam:02}{self.chavepix}'
        self.transactionAmount_tam = f'{self.valor_tam:02}{float(self.valor):.2f}'

        self.addDataField_tam = f'05{self.txtId_tam:02}{self.txtId}'

        self.nome_tam = f'{self.nome_tam:02}'

        self.cidade_tam = f'{self.cidade_tam:02}'

        self.payloadFormat = '000201'
        self.merchantAccount = f'26{len(self.merchantAccount_tam):02}{self.merchantAccount_tam}'
        self.merchantCategCode = '52040000'
        self.transactionCurrency = '5303986'
        self.transactionAmount = f'54{self.transactionAmount_tam}'
        self.countryCode = '5802BR'
        self.merchantName = f'59{self.nome_tam:02}{self.nome}'
        self.merchantCity = f'60{self.cidade_tam:02}{self.cidade}'
        self.addDataField = f'62{len(self.addDataField_tam):02}{self.addDataField_tam}'
        self.crc16 = '6304'

  
    def gerarPayload(self):
        self.payload = f'{self.payloadFormat}{self.merchantAccount}{self.merchantCategCode}{self.transactionCurrency}{self.transactionAmount}{self.countryCode}{self.merchantName}{self.merchantCity}{self.addDataField}{self.crc16}'

        self.gerarCrc16(self.payload)

        return self.payload if self.payload else None

    
    def gerarCrc16(self, payload):
        crc16 = crcmod.mkCrcFun(poly=0x11021, initCrc=0xFFFF, rev=False, xorOut=0x0000)

        self.crc16Code = hex(crc16(str(payload).encode('utf-8')))

        self.crc16Code_formatado = str(self.crc16Code).replace('0x', '').upper().zfill(4)

        self.payload_completa = f'{payload}{self.crc16Code_formatado}'

        self.gerarQrCode(self.payload_completa, self.diretorioQrCode)

    
    def gerarQrCode(self, payload, diretorio):
        dir = os.path.expanduser(diretorio)
        self.qrcode = qrcode.make(payload)
        self.qrcode.save(os.path.join(dir, 'pixqrcodegen.png'))
        
        return print(payload)
    
payload = Payload(
    nome='STEPHANE DANIELLY SANTOS', 
    chavepix='+5583991868219', 
    valor=f'{1.00:.2f}', 
    cidade='JOAO PESSOA', 
    txtId='TESTE',
    diretorio=qrcode_dir
)
payload_code = payload.gerarPayload()
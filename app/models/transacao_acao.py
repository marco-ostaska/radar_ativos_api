from datetime import datetime
from enum import Enum

class TipoTransacao(str, Enum):
    COMPRA = "COMPRA"
    VENDA = "VENDA"

class TransacaoAcaoBase:
    ticker: str
    quantidade: int
    preco: float
    tipo_transacao: TipoTransacao
    data_transacao: datetime
    carteira_id: int

    def __init__(self, ticker, quantidade, preco, tipo_transacao, data_transacao, carteira_id):
        self.ticker = ticker
        self.quantidade = quantidade
        self.preco = preco
        self.tipo_transacao = tipo_transacao
        self.data_transacao = data_transacao
        self.carteira_id = carteira_id

    def validar_ticker(self):
        self.ticker = self.ticker.upper()
        if not self.ticker.endswith('.SA'):
            self.ticker += '.SA'
        return self.ticker

    def validar_tipo_transacao(self):
        if self.tipo_transacao not in ['COMPRA', 'VENDA']:
            raise ValueError('Tipo de transação deve ser COMPRA ou VENDA')
        return self.tipo_transacao

class TransacaoAcaoCriar(TransacaoAcaoBase):
    pass

class TransacaoAcao(TransacaoAcaoBase):
    id: int
    data_atualizacao: datetime

    def __init__(self, ticker, quantidade, preco, tipo_transacao, data_transacao, carteira_id, id, data_atualizacao):
        super().__init__(ticker, quantidade, preco, tipo_transacao, data_transacao, carteira_id)
        self.id = id
        self.data_atualizacao = data_atualizacao 
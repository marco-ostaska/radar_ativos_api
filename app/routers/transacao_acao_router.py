from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from app.models.transacao_acao import TransacaoAcao, TransacaoAcaoCriar, TipoTransacao
from app.services.transacao_acao_service import TransacaoAcaoService

router = APIRouter(
    prefix="/transacoes/acoes",
    tags=["transacoes_acoes"],
    responses={404: {"description": "Not found"}},
)

@router.post("/", response_model=TransacaoAcao)
async def criar_transacao(transacao: TransacaoAcaoCriar):
    """
    Cria uma nova transação de ação.
    
    - **ticker**: Código da ação
    - **data_transacao**: Data da transação (dd/mm/yyyy)
    - **tipo_transacao**: COMPRA ou VENDA
    - **preco**: Preço unitário
    - **quantidade**: Quantidade de ações
    - **carteira_id**: ID da carteira
    """
    service = TransacaoAcaoService()
    return service.criar_transacao(transacao)

@router.get("/", response_model=List[TransacaoAcao])
async def listar_transacoes(ticker: Optional[str] = Query(None, description="Filtrar por ticker")):
    """
    Lista todas as transações de ações, opcionalmente filtradas por ticker.
    
    - **ticker**: (opcional) Código da ação para filtrar
    """
    service = TransacaoAcaoService()
    return service.listar_transacoes(ticker)

@router.get("/{transacao_id}", response_model=TransacaoAcao)
async def buscar_transacao(transacao_id: int):
    """
    Busca uma transação pelo ID.
    
    - **transacao_id**: ID da transação
    """
    service = TransacaoAcaoService()
    transacao = service.buscar_transacao_por_id(transacao_id)
    if not transacao:
        raise HTTPException(status_code=404, detail="Transação não encontrada")
    return transacao

@router.put("/{transacao_id}", response_model=TransacaoAcao)
async def atualizar_transacao(transacao_id: int, transacao: TransacaoAcaoCriar):
    """
    Atualiza uma transação existente.
    
    - **transacao_id**: ID da transação
    - **ticker**: Código da ação
    - **data_transacao**: Data da transação (dd/mm/yyyy)
    - **tipo_transacao**: COMPRA ou VENDA
    - **preco**: Preço unitário
    - **quantidade**: Quantidade de ações
    - **carteira_id**: ID da carteira
    """
    service = TransacaoAcaoService()
    transacao_atualizada = service.atualizar_transacao(transacao_id, transacao)
    if not transacao_atualizada:
        raise HTTPException(status_code=404, detail="Transação não encontrada")
    return transacao_atualizada

@router.delete("/{transacao_id}")
async def deletar_transacao(transacao_id: int):
    """
    Deleta uma transação.
    
    - **transacao_id**: ID da transação
    """
    service = TransacaoAcaoService()
    if not service.deletar_transacao(transacao_id):
        raise HTTPException(status_code=404, detail="Transação não encontrada")
    return {"message": "Transação deletada com sucesso"}

@router.post("/desdobramento")
async def aplicar_desdobramento(
    ticker: str = Query(..., description="Código da ação"),
    data_desdobramento: str = Query(..., description="Data do desdobramento (dd/mm/yyyy)"),
    proporcao_antes: int = Query(..., description="Proporção antes do desdobramento (ex: 1)"),
    proporcao_depois: int = Query(..., description="Proporção depois do desdobramento (ex: 10)")
):
    """
    Aplica um desdobramento nas transações de uma ação.
    
    - **ticker**: Código da ação
    - **data_desdobramento**: Data do desdobramento (dd/mm/yyyy)
    - **proporcao_antes**: Proporção antes do desdobramento (ex: 1)
    - **proporcao_depois**: Proporção depois do desdobramento (ex: 10)
    
    Exemplo: Para um desdobramento 10:1 (10 para 1):
    - proporcao_antes = 1
    - proporcao_depois = 10
    
    Isso irá:
    1. Multiplicar as quantidades por 10
    2. Dividir os preços por 10
    3. Atualizar a carteira automaticamente
    """
    service = TransacaoAcaoService()
    if not service.aplicar_desdobramento(ticker, data_desdobramento, proporcao_antes, proporcao_depois):
        raise HTTPException(status_code=404, detail="Ação não encontrada")
    return {"message": "Desdobramento aplicado com sucesso"} 
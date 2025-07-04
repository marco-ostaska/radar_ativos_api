from fastapi import APIRouter, HTTPException, Query
from datetime import datetime
import sqlite3
import os
from app.services.fii import FII

router = APIRouter(
    prefix="/transacoes",
    tags=["Transações"]
)

@router.get("/acoes/listar")
def listar_transacoes_acoes(carteira_id: int = Query(..., description="ID da carteira")):
    """
    Lista todas as transações de ações de uma carteira.
    """
    conn = sqlite3.connect('sqlite/radar_ativos.db')
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, ticker, data_transacao, tipo_transacao, preco, quantidade, ativo
            FROM transacoes_acoes
            WHERE carteira_id = ?
            ORDER BY data_transacao DESC
        """, (carteira_id,))
        
        transacoes = []
        for row in cursor.fetchall():
            transacoes.append({
                "id": row[0],
                "ticker": row[1],
                "data": row[2],
                "tipo": row[3],
                "preco": row[4],
                "quantidade": row[5],
                "valor_total": row[4] * row[5],
                "ativo": row[6]
            })
        
        return transacoes
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

@router.get("/fii/listar")
def listar_transacoes_fii(carteira_id: int = Query(..., description="ID da carteira")):
    """
    Lista todas as transações de FIIs de uma carteira.
    """
    conn = sqlite3.connect('sqlite/radar_ativos.db')
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, ticker, data_transacao, tipo_transacao, preco, quantidade, ativo
            FROM transacoes_fii
            WHERE carteira_id = ?
            ORDER BY data_transacao DESC
        """, (carteira_id,))
        
        transacoes = []
        for row in cursor.fetchall():
            transacoes.append({
                "id": row[0],
                "ticker": row[1],
                "data": row[2],
                "tipo": row[3],
                "preco": row[4],
                "quantidade": row[5],
                "valor_total": row[4] * row[5],
                "ativo": row[6]
            })
        
        return transacoes
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

@router.post("/acoes/adicionar")
async def adicionar_transacao_acao(
    ticker: str = Query(..., description="Código da ação (ex: PETR4)"),
    quantidade: int = Query(..., description="Quantidade de ações"),
    preco: float = Query(..., description="Preço unitário da ação"),
    tipo: str = Query(..., description="Tipo da transação (COMPRA ou VENDA)"),
    carteira_id: int = Query(..., description="ID da carteira"),
    data: str = Query(..., description="Data da transação (dd/mm/yyyy)")
):
    # Validações básicas
    if quantidade <= 0:
        raise HTTPException(status_code=400, detail="Quantidade deve ser maior que zero")
    
    if preco <= 0:
        raise HTTPException(status_code=400, detail="Preço deve ser maior que zero")
    
    # Normaliza o ticker
    ticker = ticker.upper()
    if not ticker.endswith('.SA'):
        ticker += '.SA'
    
    # Normaliza o tipo
    tipo = tipo.upper()
    if tipo not in ['COMPRA', 'VENDA']:
        raise HTTPException(status_code=400, detail="Tipo deve ser COMPRA ou VENDA")
    
    # Valida e converte a data
    try:
        data_obj = datetime.strptime(data, '%d/%m/%Y')
        data_transacao = data_obj.strftime('%Y-%m-%d')
    except ValueError:
        raise HTTPException(status_code=400, detail="Data deve estar no formato dd/mm/yyyy")
    
    try:
        # Conecta ao banco
        conn = sqlite3.connect('sqlite/radar_ativos.db')
        cursor = conn.cursor()
        
        # Insere a transação
        cursor.execute("""
            INSERT INTO transacoes_acoes (
                ticker, data_transacao, tipo_transacao, preco, quantidade, carteira_id
            ) VALUES (?, ?, ?, ?, ?, ?)
        """, (ticker, data_transacao, tipo, preco, quantidade, carteira_id))
        
        conn.commit()
        return {"mensagem": "Transação adicionada com sucesso"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao adicionar transação: {str(e)}")
        
    finally:
        if 'conn' in locals():
            conn.close()

@router.post("/fii/adicionar")
async def adicionar_transacao_fii(
    ticker: str = Query(..., description="Código do FII (ex: HGLG11)"),
    quantidade: int = Query(..., description="Quantidade de cotas"),
    preco: float = Query(..., description="Preço unitário da cota"),
    tipo: str = Query(..., description="Tipo da transação (COMPRA ou VENDA)"),
    carteira_id: int = Query(..., description="ID da carteira"),
    data: str = Query(..., description="Data da transação (dd/mm/yyyy)")
):
    # Validações básicas
    if quantidade <= 0:
        raise HTTPException(status_code=400, detail="Quantidade deve ser maior que zero")
    
    if preco <= 0:
        raise HTTPException(status_code=400, detail="Preço deve ser maior que zero")
    
    # Normaliza o ticker
    ticker = ticker.upper()
    if not ticker.endswith('.SA'):
        ticker += '.SA'
    fii = FII(ticker)
        # DEBUG: print info for investigation
    if not fii.cotacao or fii.cotacao <= 0:
        raise HTTPException(status_code=400, detail="FII não encontrado ou ticker inválido")
    
    # Normaliza o tipo
    tipo = tipo.upper()
    if tipo not in ['COMPRA', 'VENDA']:
        raise HTTPException(status_code=400, detail="Tipo deve ser COMPRA ou VENDA")
    
    # Valida e converte a data
    try:
        data_obj = datetime.strptime(data, '%d/%m/%Y')
        data_transacao = data_obj.strftime('%Y-%m-%d')
    except ValueError:
        raise HTTPException(status_code=400, detail="Data deve estar no formato dd/mm/yyyy")
    
    try:
        # Conecta ao banco
        conn = sqlite3.connect('sqlite/radar_ativos.db')
        cursor = conn.cursor()
        
        # Insere a transação
        cursor.execute("""
            INSERT INTO transacoes_fii (
                ticker, data_transacao, tipo_transacao, preco, quantidade, carteira_id, ativo
            ) VALUES (?, ?, ?, ?, ?, ?, 1)
        """, (ticker, data_transacao, tipo, preco, quantidade, carteira_id))
        
        conn.commit()
        return {"mensagem": "Transação adicionada com sucesso"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao adicionar transação: {str(e)}")
        
    finally:
        if 'conn' in locals():
            conn.close()

@router.delete("/acoes/deletar/{transacao_id}")
def deletar_transacao_acao(
    transacao_id: int,
    carteira_id: int = Query(..., description="ID da carteira")
):
    """
    Deleta uma transação de ação específica.
    Se for desdobramento/agrupamento, reativa apenas as transações inativadas por esse evento.
    """
    conn = sqlite3.connect('sqlite/radar_ativos.db')
    try:
        cursor = conn.cursor()
        # Buscar a transação alvo
        cursor.execute(
            "SELECT id, ticker, data_transacao, tipo_transacao FROM transacoes_acoes WHERE id = ? AND carteira_id = ?",
            (transacao_id, carteira_id)
        )
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Transação não encontrada ou não pertence à carteira especificada")
        _, ticker, data_transacao, tipo_transacao = row
        tipo_transacao = tipo_transacao.lower()
        if tipo_transacao in ('desdobramento', 'agrupamento'):
            # Buscar todas as transações anteriores (inclusive) ordenadas da mais recente para a mais antiga
            cursor.execute(
                """
                SELECT id, tipo_transacao FROM transacoes_acoes
                WHERE ticker = ? AND carteira_id = ? AND data_transacao <= ?
                ORDER BY data_transacao DESC, id DESC
                """,
                (ticker, carteira_id, data_transacao)
            )
            transacoes = cursor.fetchall()
            ids_para_reativar = []
            for t_id, t_tipo in transacoes:
                if t_id == transacao_id:
                    continue  # não reativa o próprio evento
                if t_tipo.lower() in ('desdobramento', 'agrupamento'):
                    break  # encontrou outro evento, para aqui
                ids_para_reativar.append(t_id)
            # Reativa apenas se houver transações elegíveis
            if ids_para_reativar:
                cursor.execute(
                    f"UPDATE transacoes_acoes SET ativo = 1 WHERE id IN ({','.join(['?']*len(ids_para_reativar))})",
                    ids_para_reativar
                )
        # Após reativar (se necessário), deleta a transação de desdobramento/agrupamento
        cursor.execute(
            "DELETE FROM transacoes_acoes WHERE id = ? AND carteira_id = ?",
            (transacao_id, carteira_id)
        )
        conn.commit()
        return {"mensagem": "Transação deletada com sucesso"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

@router.delete("/fii/deletar/{transacao_id}")
def deletar_transacao_fii(
    transacao_id: int,
    carteira_id: int = Query(..., description="ID da carteira")
):
    """
    Deleta uma transação de FII específica.
    Se for desdobramento/agrupamento, reativa apenas as transações inativadas por esse evento.
    """
    conn = sqlite3.connect('sqlite/radar_ativos.db')
    try:
        cursor = conn.cursor()
        # Buscar a transação alvo
        cursor.execute(
            "SELECT id, ticker, data_transacao, tipo_transacao FROM transacoes_fii WHERE id = ? AND carteira_id = ?",
            (transacao_id, carteira_id)
        )
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Transação não encontrada ou não pertence à carteira especificada")
        _, ticker, data_transacao, tipo_transacao = row
        tipo_transacao = tipo_transacao.lower()
        if tipo_transacao in ('desdobramento', 'agrupamento'):
            # Buscar todas as transações anteriores (inclusive) ordenadas da mais recente para a mais antiga
            cursor.execute(
                """
                SELECT id, tipo_transacao FROM transacoes_fii
                WHERE ticker = ? AND carteira_id = ? AND data_transacao <= ?
                ORDER BY data_transacao DESC, id DESC
                """,
                (ticker, carteira_id, data_transacao)
            )
            transacoes = cursor.fetchall()
            ids_para_reativar = []
            for t_id, t_tipo in transacoes:
                if t_id == transacao_id:
                    continue  # não reativa o próprio evento
                if t_tipo.lower() in ('desdobramento', 'agrupamento'):
                    break  # encontrou outro evento, para aqui
                ids_para_reativar.append(t_id)
            # Reativa apenas se houver transações elegíveis
            if ids_para_reativar:
                cursor.execute(
                    f"UPDATE transacoes_fii SET ativo = 1 WHERE id IN ({','.join(['?']*len(ids_para_reativar))})",
                    ids_para_reativar
                )
        # Após reativar (se necessário), deleta a transação de desdobramento/agrupamento
        cursor.execute(
            "DELETE FROM transacoes_fii WHERE id = ? AND carteira_id = ?",
            (transacao_id, carteira_id)
        )
        conn.commit()
        return {"mensagem": "Transação deletada com sucesso"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

@router.put("/acoes/atualizar/{transacao_id}")
def atualizar_transacao_acao(
    transacao_id: int,
    carteira_id: int = Query(..., description="ID da carteira"),
    ticker: str = Query(..., description="Código da ação (ex: PETR4)"),
    quantidade: int = Query(..., gt=0, description="Quantidade de ações"),
    preco: float = Query(..., gt=0, description="Preço unitário da ação"),
    tipo: str = Query(..., description="Tipo da transação (COMPRA ou VENDA)"),
    data: str = Query(..., description="Data da transação (dd/mm/yyyy)")
):
    """
    Atualiza uma transação de ação existente.
    """
    # Validação da data
    try:
        data_obj = datetime.strptime(data, "%d/%m/%Y")
        data_formatada = data_obj.strftime("%Y-%m-%d")
    except ValueError:
        raise HTTPException(status_code=400, detail="Data deve estar no formato dd/mm/yyyy")

    # Normalização do ticker
    ticker = ticker.upper()
    if not ticker.endswith('.SA'):
        ticker += '.SA'

    # Normalização do tipo
    tipo = tipo.upper()
    if tipo not in ['COMPRA', 'VENDA']:
        raise HTTPException(status_code=400, detail="Tipo deve ser COMPRA ou VENDA")

    conn = sqlite3.connect('sqlite/radar_ativos.db')
    try:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE transacoes_acoes 
            SET ticker = ?,
                data_transacao = ?,
                tipo_transacao = ?,
                preco = ?,
                quantidade = ?
            WHERE id = ? AND carteira_id = ?
        """, (ticker, data_formatada, tipo, preco, quantidade, transacao_id, carteira_id))
        conn.commit()
        
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Transação não encontrada ou não pertence à carteira especificada")
            
        return {"mensagem": "Transação atualizada com sucesso"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

@router.put("/fii/atualizar/{transacao_id}")
def atualizar_transacao_fii(
    transacao_id: int,
    carteira_id: int = Query(..., description="ID da carteira"),
    ticker: str = Query(..., description="Código do FII (ex: HGLG11)"),
    quantidade: int = Query(..., gt=0, description="Quantidade de cotas"),
    preco: float = Query(..., gt=0, description="Preço unitário da cota"),
    tipo: str = Query(..., description="Tipo da transação (COMPRA ou VENDA)"),
    data: str = Query(..., description="Data da transação (dd/mm/yyyy)")
):
    """
    Atualiza uma transação de FII existente.
    """
    # Validação da data
    try:
        data_obj = datetime.strptime(data, "%d/%m/%Y")
        data_formatada = data_obj.strftime("%Y-%m-%d")
    except ValueError:
        raise HTTPException(status_code=400, detail="Data deve estar no formato dd/mm/yyyy")

    # Normalização do ticker
    ticker = ticker.upper()
    if not ticker.endswith('.SA'):
        ticker += '.SA'
    fii = FII(ticker)
    # DEBUG: print info for investigation
    if not fii.cotacao or fii.cotacao <= 0:
        raise HTTPException(status_code=400, detail="FII não encontrado ou ticker inválido")


    # Normalização do tipo
    tipo = tipo.upper()
    if tipo not in ['COMPRA', 'VENDA']:
        raise HTTPException(status_code=400, detail="Tipo deve ser COMPRA ou VENDA")

    conn = sqlite3.connect('sqlite/radar_ativos.db')
    try:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE transacoes_fii 
            SET ticker = ?,
                data_transacao = ?,
                tipo_transacao = ?,
                preco = ?,
                quantidade = ?
            WHERE id = ? AND carteira_id = ?
        """, (ticker, data_formatada, tipo, preco, quantidade, transacao_id, carteira_id))
        conn.commit()
        
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Transação não encontrada ou não pertence à carteira especificada")
            
        return {"mensagem": "Transação atualizada com sucesso"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

@router.post("/acoes/desdobramento")
async def aplicar_desdobramento(
    ticker: str = Query(..., description="Código da ação (ex: PETR4)"),
    data_desdobramento: str = Query(..., description="Data do desdobramento (dd/mm/yyyy)"),
    proporcao_antes: int = Query(..., description="Proporção antes (ex: 1)"),
    proporcao_depois: int = Query(..., description="Proporção depois (ex: 10)"),
    carteira_id: int = Query(..., description="ID da carteira")
):
    """
    Aplica um desdobramento em todas as transações de uma ação até a data especificada.
    Exemplo: desdobramento 10:1 (proporcao_antes=1, proporcao_depois=10)
    """
    # Validações básicas
    if proporcao_antes <= 0 or proporcao_depois <= 0:
        raise HTTPException(status_code=400, detail="Proporções devem ser maiores que zero")
    
    if proporcao_depois <= proporcao_antes:
        raise HTTPException(status_code=400, detail="Proporção depois deve ser maior que proporção antes")
    
    # Normaliza o ticker
    ticker = ticker.upper()
    if not ticker.endswith('.SA'):
        ticker += '.SA'
    
    # Valida e converte a data
    try:
        data_obj = datetime.strptime(data_desdobramento, '%d/%m/%Y')
        data_desdobramento = data_obj.strftime('%Y-%m-%d')
    except ValueError:
        raise HTTPException(status_code=400, detail="Data deve estar no formato dd/mm/yyyy")
    
    try:
        # Conecta ao banco
        conn = sqlite3.connect('sqlite/radar_ativos.db')
        cursor = conn.cursor()
        
        # Busca todas as transações ativas do ticker até a data do desdobramento
        cursor.execute("""
            SELECT id, quantidade, preco
            FROM transacoes_acoes
            WHERE ticker = ? 
            AND carteira_id = ?
            AND data_transacao <= ?
            AND ativo = 1
            ORDER BY data_transacao DESC
        """, (ticker, carteira_id, data_desdobramento))
        
        transacoes = cursor.fetchall()
        if not transacoes:
            raise HTTPException(status_code=404, detail="Nenhuma transação encontrada para este ticker até a data especificada")
        
        # Calcula o fator de ajuste
        fator_ajuste = proporcao_depois / proporcao_antes

        # Soma todas as quantidades ativas
        quantidade_total = sum(transacao[1] for transacao in transacoes)

        # Calcula o preço médio ponderado das transações ativas
        soma_valor = sum(transacao[1] * transacao[2] for transacao in transacoes)
        preco_medio = soma_valor / quantidade_total if quantidade_total > 0 else 0

        # Calcula a nova quantidade (multiplicando para desdobramento)
        nova_quantidade = int(quantidade_total * fator_ajuste)

        # Calcula o novo preço (preço médio dividido pelo fator de ajuste)
        novo_preco = preco_medio / fator_ajuste if fator_ajuste > 0 else 0

        # Marca todas as transações anteriores como inativas
        cursor.execute("""
            UPDATE transacoes_acoes
            SET ativo = 0
            WHERE ticker = ? 
            AND carteira_id = ?
            AND data_transacao <= ?
            AND ativo = 1
        """, (ticker, carteira_id, data_desdobramento))
        
        # Cria uma nova transação de desdobramento
        cursor.execute("""
            INSERT INTO transacoes_acoes (
                ticker, data_transacao, tipo_transacao, preco, quantidade, carteira_id, ativo
            ) VALUES (?, ?, 'DESDOBRAMENTO', ?, ?, ?, 1)
        """, (ticker, data_desdobramento, novo_preco, nova_quantidade, carteira_id))
        
        conn.commit()
        return {"mensagem": "Desdobramento aplicado com sucesso"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao aplicar desdobramento: {str(e)}")
        
    finally:
        if 'conn' in locals():
            conn.close()

@router.post("/acoes/agrupamento")
async def aplicar_agrupamento(
    ticker: str = Query(..., description="Código da ação (ex: PETR4)"),
    data_agrupamento: str = Query(..., description="Data do agrupamento (dd/mm/yyyy)"),
    proporcao_antes: int = Query(..., description="Proporção antes (ex: 10)"),
    proporcao_depois: int = Query(..., description="Proporção depois (ex: 1)"),
    carteira_id: int = Query(..., description="ID da carteira")
):
    """
    Aplica um agrupamento em todas as transações de uma ação até a data especificada.
    Exemplo: agrupamento 10:1 (proporcao_antes=10, proporcao_depois=1)
    """
    # Validações básicas
    if proporcao_antes <= 0 or proporcao_depois <= 0:
        raise HTTPException(status_code=400, detail="Proporções devem ser maiores que zero")
    
    if proporcao_antes <= proporcao_depois:
        raise HTTPException(status_code=400, detail="Proporção antes deve ser maior que proporção depois")
    
    # Normaliza o ticker
    ticker = ticker.upper()
    if not ticker.endswith('.SA'):
        ticker += '.SA'
    
    # Valida e converte a data
    try:
        data_obj = datetime.strptime(data_agrupamento, '%d/%m/%Y')
        data_agrupamento = data_obj.strftime('%Y-%m-%d')
    except ValueError:
        raise HTTPException(status_code=400, detail="Data deve estar no formato dd/mm/yyyy")
    
    try:
        # Conecta ao banco
        conn = sqlite3.connect('sqlite/radar_ativos.db')
        cursor = conn.cursor()
        
        # Busca todas as transações ativas do ticker até a data do agrupamento
        cursor.execute("""
            SELECT id, quantidade, preco
            FROM transacoes_acoes
            WHERE ticker = ? 
            AND carteira_id = ?
            AND data_transacao <= ?
            AND ativo = 1
            ORDER BY data_transacao DESC
        """, (ticker, carteira_id, data_agrupamento))
        
        transacoes = cursor.fetchall()
        if not transacoes:
            raise HTTPException(status_code=404, detail="Nenhuma transação encontrada para este ticker até a data especificada")
        
        # Calcula o fator de ajuste
        fator_ajuste = proporcao_depois / proporcao_antes

        # Soma todas as quantidades ativas
        quantidade_total = sum(transacao[1] for transacao in transacoes)

        # Calcula o preço médio ponderado das transações ativas
        soma_valor = sum(transacao[1] * transacao[2] for transacao in transacoes)
        preco_medio = soma_valor / quantidade_total if quantidade_total > 0 else 0

        # Calcula a nova quantidade (dividindo para agrupamento)
        nova_quantidade = int(quantidade_total * fator_ajuste)

        # Calcula o novo preço (preço médio multiplicado pelo inverso do fator de ajuste)
        novo_preco = preco_medio * (proporcao_antes / proporcao_depois) if proporcao_depois > 0 else 0

        # Marca todas as transações anteriores como inativas
        cursor.execute("""
            UPDATE transacoes_acoes
            SET ativo = 0
            WHERE ticker = ? 
            AND carteira_id = ?
            AND data_transacao <= ?
            AND ativo = 1
        """, (ticker, carteira_id, data_agrupamento))
        
        # Cria uma nova transação de agrupamento
        cursor.execute("""
            INSERT INTO transacoes_acoes (
                ticker, data_transacao, tipo_transacao, preco, quantidade, carteira_id, ativo
            ) VALUES (?, ?, 'AGRUPAMENTO', ?, ?, ?, 1)
        """, (ticker, data_agrupamento, novo_preco, nova_quantidade, carteira_id))
        
        conn.commit()
        return {"mensagem": "Agrupamento aplicado com sucesso"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao aplicar agrupamento: {str(e)}")
        
    finally:
        if 'conn' in locals():
            conn.close()

@router.post("/fii/desdobramento")
async def aplicar_desdobramento_fii(
    ticker: str = Query(..., description="Código do FII (ex: HGLG11)"),
    data_desdobramento: str = Query(..., description="Data do desdobramento (dd/mm/yyyy)"),
    proporcao_antes: int = Query(..., description="Proporção antes (ex: 1)"),
    proporcao_depois: int = Query(..., description="Proporção depois (ex: 10)"),
    carteira_id: int = Query(..., description="ID da carteira")
):
    """
    Aplica um desdobramento em todas as transações de um FII até a data especificada.
    Exemplo: desdobramento 10:1 (proporcao_antes=1, proporcao_depois=10)
    """
    # Validações básicas
    if proporcao_antes <= 0 or proporcao_depois <= 0:
        raise HTTPException(status_code=400, detail="Proporções devem ser maiores que zero")
    
    if proporcao_depois <= proporcao_antes:
        raise HTTPException(status_code=400, detail="Proporção depois deve ser maior que proporção antes")
    
    # Normaliza o ticker
    ticker = ticker.upper()
    if not ticker.endswith('.SA'):
        ticker += '.SA'
    
    # Valida e converte a data
    try:
        data_obj = datetime.strptime(data_desdobramento, '%d/%m/%Y')
        data_desdobramento = data_obj.strftime('%Y-%m-%d')
    except ValueError:
        raise HTTPException(status_code=400, detail="Data deve estar no formato dd/mm/yyyy")
    
    try:
        # Conecta ao banco
        conn = sqlite3.connect('sqlite/radar_ativos.db')
        cursor = conn.cursor()
        
        # Busca todas as transações ativas do FII até a data do desdobramento
        cursor.execute("""
            SELECT id, quantidade, preco
            FROM transacoes_fii
            WHERE ticker = ? 
            AND carteira_id = ?
            AND data_transacao <= ?
            AND ativo = 1
            ORDER BY data_transacao DESC
        """, (ticker, carteira_id, data_desdobramento))
        
        transacoes = cursor.fetchall()
        if not transacoes:
            raise HTTPException(status_code=404, detail="Nenhuma transação encontrada para este FII até a data especificada")
        
        # Calcula o fator de ajuste
        fator_ajuste = proporcao_depois / proporcao_antes

        # Soma todas as quantidades ativas
        quantidade_total = sum(transacao[1] for transacao in transacoes)

        # Calcula o preço médio ponderado das transações ativas
        soma_valor = sum(transacao[1] * transacao[2] for transacao in transacoes)
        preco_medio = soma_valor / quantidade_total if quantidade_total > 0 else 0

        # Calcula a nova quantidade (multiplicando para desdobramento)
        nova_quantidade = int(quantidade_total * fator_ajuste)

        # Calcula o novo preço (preço médio dividido pelo fator de ajuste)
        novo_preco = preco_medio / fator_ajuste if fator_ajuste > 0 else 0

        # Marca todas as transações anteriores como inativas
        cursor.execute("""
            UPDATE transacoes_fii
            SET ativo = 0
            WHERE ticker = ? 
            AND carteira_id = ?
            AND data_transacao <= ?
            AND ativo = 1
        """, (ticker, carteira_id, data_desdobramento))
        
        # Cria uma nova transação de desdobramento
        cursor.execute("""
            INSERT INTO transacoes_fii (
                ticker, data_transacao, tipo_transacao, preco, quantidade, carteira_id, ativo
            ) VALUES (?, ?, 'DESDOBRAMENTO', ?, ?, ?, 1)
        """, (ticker, data_desdobramento, novo_preco, nova_quantidade, carteira_id))
        
        conn.commit()
        return {"mensagem": "Desdobramento aplicado com sucesso"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao aplicar desdobramento: {str(e)}")
        
    finally:
        if 'conn' in locals():
            conn.close()

@router.post("/fii/agrupamento")
async def aplicar_agrupamento_fii(
    ticker: str = Query(..., description="Código do FII (ex: HGLG11)"),
    data_agrupamento: str = Query(..., description="Data do agrupamento (dd/mm/yyyy)"),
    proporcao_antes: int = Query(..., description="Proporção antes (ex: 10)"),
    proporcao_depois: int = Query(..., description="Proporção depois (ex: 1)"),
    carteira_id: int = Query(..., description="ID da carteira")
):
    """
    Aplica um agrupamento em todas as transações de um FII até a data especificada.
    Exemplo: agrupamento 10:1 (proporcao_antes=10, proporcao_depois=1)
    """
    # Validações básicas
    if proporcao_antes <= 0 or proporcao_depois <= 0:
        raise HTTPException(status_code=400, detail="Proporções devem ser maiores que zero")
    
    if proporcao_antes <= proporcao_depois:
        raise HTTPException(status_code=400, detail="Proporção antes deve ser maior que proporção depois")
    
    # Normaliza o ticker
    ticker = ticker.upper()
    if not ticker.endswith('.SA'):
        ticker += '.SA'
    
    # Valida e converte a data
    try:
        data_obj = datetime.strptime(data_agrupamento, '%d/%m/%Y')
        data_agrupamento = data_obj.strftime('%Y-%m-%d')
    except ValueError:
        raise HTTPException(status_code=400, detail="Data deve estar no formato dd/mm/yyyy")
    
    try:
        # Conecta ao banco
        conn = sqlite3.connect('sqlite/radar_ativos.db')
        cursor = conn.cursor()
        
        # Busca todas as transações ativas do FII até a data do agrupamento
        cursor.execute("""
            SELECT id, quantidade, preco
            FROM transacoes_fii
            WHERE ticker = ? 
            AND carteira_id = ?
            AND data_transacao <= ?
            AND ativo = 1
            ORDER BY data_transacao DESC
        """, (ticker, carteira_id, data_agrupamento))
        
        transacoes = cursor.fetchall()
        if not transacoes:
            raise HTTPException(status_code=404, detail="Nenhuma transação encontrada para este FII até a data especificada")
        
        # Calcula o fator de ajuste
        fator_ajuste = proporcao_depois / proporcao_antes

        # Soma todas as quantidades ativas
        quantidade_total = sum(transacao[1] for transacao in transacoes)

        # Calcula o preço médio ponderado das transações ativas
        soma_valor = sum(transacao[1] * transacao[2] for transacao in transacoes)
        preco_medio = soma_valor / quantidade_total if quantidade_total > 0 else 0

        # Calcula a nova quantidade (dividindo para agrupamento)
        nova_quantidade = int(quantidade_total * fator_ajuste)

        # Calcula o novo preço (preço médio multiplicado pelo inverso do fator de ajuste)
        novo_preco = preco_medio * (proporcao_antes / proporcao_depois) if proporcao_depois > 0 else 0

        # Marca todas as transações anteriores como inativas
        cursor.execute("""
            UPDATE transacoes_fii
            SET ativo = 0
            WHERE ticker = ? 
            AND carteira_id = ?
            AND data_transacao <= ?
            AND ativo = 1
        """, (ticker, carteira_id, data_agrupamento))
        
        # Cria uma nova transação de agrupamento
        cursor.execute("""
            INSERT INTO transacoes_fii (
                ticker, data_transacao, tipo_transacao, preco, quantidade, carteira_id, ativo
            ) VALUES (?, ?, 'AGRUPAMENTO', ?, ?, ?, 1)
        """, (ticker, data_agrupamento, novo_preco, nova_quantidade, carteira_id))
        
        conn.commit()
        return {"mensagem": "Agrupamento aplicado com sucesso"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao aplicar agrupamento: {str(e)}")
        
    finally:
        if 'conn' in locals():
            conn.close()

def resumo_alunos(conexao):
    linha = conexao.execute(
        """
        SELECT
            COUNT(*) AS total,
            SUM(
                CASE
                    WHEN situacao = 'ativo'
                    THEN 1
                    ELSE 0
                END
            ) AS ativos,
            SUM(
                CASE
                    WHEN situacao = 'inadimplente'
                    THEN 1
                    ELSE 0
                END
            ) AS inadimplentes,
            SUM(
                CASE
                    WHEN situacao = 'congelado'
                    THEN 1
                    ELSE 0
                END
            ) AS congelados,
            SUM(
                CASE
                    WHEN situacao = 'inativo'
                    THEN 1
                    ELSE 0
                END
            ) AS inativos
        FROM aluno
        """
    ).fetchone()

    return {
        "total": linha["total"] or 0,
        "ativos": linha["ativos"] or 0,
        "inadimplentes": (
            linha["inadimplentes"] or 0
        ),
        "congelados": (
            linha["congelados"] or 0
        ),
        "inativos": linha["inativos"] or 0,
    }


def resumo_financeiro_mes(
    conexao,
    competencia,
    inicio_mes,
    inicio_proximo_mes,
):
    linha = conexao.execute(
        """
        SELECT
            (
                SELECT COALESCE(
                    SUM(pag.valor),
                    0
                )
                FROM pagamento pag
                WHERE datetime(
                    pag.data_pagamento
                ) >= datetime(?)
                  AND datetime(
                    pag.data_pagamento
                  ) < datetime(?)
            ) AS receita_mes,

            (
                SELECT COALESCE(
                    SUM(men.valor),
                    0
                )
                FROM mensalidade men
                WHERE men.competencia = ?
                  AND men.situacao IN (
                      'pendente',
                      'atrasada'
                  )
            ) AS pendente_mes,

            (
                SELECT COUNT(*)
                FROM mensalidade
                WHERE situacao = 'pendente'
            ) AS mensalidades_pendentes,

            (
                SELECT COUNT(*)
                FROM mensalidade
                WHERE situacao = 'atrasada'
            ) AS mensalidades_atrasadas
        """,
        (
            inicio_mes,
            inicio_proximo_mes,
            competencia,
        ),
    ).fetchone()

    return {
        "receita_mes": (
            linha["receita_mes"] or 0
        ),
        "pendente_mes": (
            linha["pendente_mes"] or 0
        ),
        "mensalidades_pendentes": (
            linha["mensalidades_pendentes"]
            or 0
        ),
        "mensalidades_atrasadas": (
            linha["mensalidades_atrasadas"]
            or 0
        ),
    }


def listar_proximos_vencimentos(
    conexao,
    hoje,
    limite=8,
):
    return conexao.execute(
        """
        SELECT
            men.id,
            alu.nome AS aluno,
            pla.nome AS plano,
            men.data_vencimento,
            men.valor,
            men.situacao
        FROM mensalidade men
        JOIN matricula mat
            ON mat.id = men.matricula_id
        JOIN aluno alu
            ON alu.id = mat.aluno_id
        JOIN plano pla
            ON pla.id = mat.plano_id
        WHERE men.situacao IN (
            'pendente',
            'atrasada'
        )
          AND mat.situacao NOT IN (
              'congelada',
              'encerrada'
          )
        ORDER BY
            CASE
                WHEN date(men.data_vencimento)
                     < date(?)
                THEN 0
                ELSE 1
            END,
            date(men.data_vencimento),
            alu.nome COLLATE NOCASE
        LIMIT ?
        """,
        (
            hoje,
            limite,
        ),
    ).fetchall()


def listar_planos_mais_vendidos(
    conexao,
    limite=5,
):
    return conexao.execute(
        """
        SELECT
            pla.id,
            pla.nome AS plano,
            COUNT(mat.id) AS vendas,
            COALESCE(
                SUM(mat.valor_contratado),
                0
            ) AS valor_contratado
        FROM plano pla
        LEFT JOIN matricula mat
            ON mat.plano_id = pla.id
        GROUP BY
            pla.id,
            pla.nome
        ORDER BY
            vendas DESC,
            pla.nome COLLATE NOCASE
        LIMIT ?
        """,
        (limite,),
    ).fetchall()


def contar_matriculas_por_situacao(
    conexao,
):
    linhas = conexao.execute(
        """
        SELECT
            situacao,
            COUNT(*) AS quantidade
        FROM matricula
        GROUP BY situacao
        """
    ).fetchall()

    resultado = {
        "ativa": 0,
        "vencida": 0,
        "congelada": 0,
        "encerrada": 0,
    }

    for linha in linhas:
        resultado[linha["situacao"]] = (
            linha["quantidade"]
        )

    return resultado

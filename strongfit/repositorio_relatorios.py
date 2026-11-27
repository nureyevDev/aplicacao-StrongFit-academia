def listar_alunos_ativos(
    conexao,
    pesquisa="",
):
    termo = f"%{pesquisa.strip()}%"

    return conexao.execute(
        """
        SELECT
            a.id,
            a.nome,
            a.cpf,
            a.telefone,
            a.email,
            a.situacao,
            p.nome AS plano,
            m.data_inicio,
            m.data_vencimento
        FROM aluno a
        LEFT JOIN matricula m
            ON m.aluno_id = a.id
           AND m.situacao = 'ativa'
        LEFT JOIN plano p
            ON p.id = m.plano_id
        WHERE a.situacao = 'ativo'
          AND (
                a.nome LIKE ? COLLATE NOCASE
                OR a.cpf LIKE ?
                OR a.telefone LIKE ?
          )
        ORDER BY a.nome COLLATE NOCASE
        """,
        (
            termo,
            termo,
            termo,
        ),
    ).fetchall()


def listar_alunos_inadimplentes(
    conexao,
    pesquisa="",
):
    termo = f"%{pesquisa.strip()}%"

    return conexao.execute(
        """
        SELECT
            a.id,
            a.nome,
            a.cpf,
            a.telefone,
            p.nome AS plano,
            COUNT(men.id) AS mensalidades_atrasadas,
            MIN(
                men.data_vencimento
            ) AS vencimento_mais_antigo,
            COALESCE(
                SUM(men.valor),
                0
            ) AS total_pendente
        FROM aluno a
        JOIN matricula m
            ON m.aluno_id = a.id
        JOIN plano p
            ON p.id = m.plano_id
        JOIN mensalidade men
            ON men.matricula_id = m.id
        WHERE a.situacao = 'inadimplente'
          AND men.situacao = 'atrasada'
          AND (
                a.nome LIKE ? COLLATE NOCASE
                OR a.cpf LIKE ?
                OR p.nome LIKE ? COLLATE NOCASE
          )
        GROUP BY
            a.id,
            a.nome,
            a.cpf,
            a.telefone,
            p.nome
        ORDER BY
            vencimento_mais_antigo,
            a.nome COLLATE NOCASE
        """,
        (
            termo,
            termo,
            termo,
        ),
    ).fetchall()


def listar_matriculas_periodo(
    conexao,
    data_inicial,
    data_final,
    situacao=None,
):
    sql = """
        SELECT
            m.id,
            a.nome AS aluno,
            a.cpf,
            p.nome AS plano,
            m.data_inicio,
            m.data_vencimento,
            m.valor_contratado,
            m.situacao
        FROM matricula m
        JOIN aluno a
            ON a.id = m.aluno_id
        JOIN plano p
            ON p.id = m.plano_id
        WHERE date(m.data_inicio)
              BETWEEN date(?) AND date(?)
    """

    parametros = [
        data_inicial,
        data_final,
    ]

    if situacao:
        sql += " AND m.situacao = ?"
        parametros.append(situacao)

    sql += """
        ORDER BY
            m.data_inicio DESC,
            a.nome COLLATE NOCASE
    """

    return conexao.execute(
        sql,
        parametros,
    ).fetchall()


def listar_planos_mais_vendidos(
    conexao,
    data_inicial,
    data_final,
):
    return conexao.execute(
        """
        SELECT
            p.id,
            p.nome AS plano,
            p.duracao_meses,
            COUNT(m.id) AS quantidade_vendida,
            COALESCE(
                SUM(m.valor_contratado),
                0
            ) AS valor_contratado
        FROM plano p
        LEFT JOIN matricula m
            ON m.plano_id = p.id
           AND date(m.data_inicio)
               BETWEEN date(?) AND date(?)
        GROUP BY
            p.id,
            p.nome,
            p.duracao_meses
        ORDER BY
            quantidade_vendida DESC,
            p.nome COLLATE NOCASE
        """,
        (
            data_inicial,
            data_final,
        ),
    ).fetchall()


def listar_financeiro_periodo(
    conexao,
    data_inicial,
    data_final,
    forma_pagamento=None,
):
    sql = """
        SELECT
            pag.id,
            pag.data_pagamento,
            a.nome AS aluno,
            a.cpf,
            p.nome AS plano,
            men.competencia,
            pag.valor,
            pag.forma_pagamento,
            pag.observacao
        FROM pagamento pag
        JOIN mensalidade men
            ON men.id = pag.mensalidade_id
        JOIN matricula m
            ON m.id = men.matricula_id
        JOIN aluno a
            ON a.id = m.aluno_id
        JOIN plano p
            ON p.id = m.plano_id
        WHERE date(pag.data_pagamento)
              BETWEEN date(?) AND date(?)
    """

    parametros = [
        data_inicial,
        data_final,
    ]

    if forma_pagamento:
        sql += " AND pag.forma_pagamento = ?"
        parametros.append(forma_pagamento)

    sql += """
        ORDER BY pag.data_pagamento DESC
    """

    return conexao.execute(
        sql,
        parametros,
    ).fetchall()


def resumo_financeiro_periodo(
    conexao,
    data_inicial,
    data_final,
):
    linha = conexao.execute(
        """
        SELECT
            COALESCE(
                SUM(pag.valor),
                0
            ) AS total_recebido,

            COUNT(pag.id) AS quantidade_pagamentos,

            COALESCE(
                SUM(
                    CASE
                        WHEN pag.forma_pagamento = 'pix'
                        THEN pag.valor
                        ELSE 0
                    END
                ),
                0
            ) AS total_pix,

            COALESCE(
                SUM(
                    CASE
                        WHEN pag.forma_pagamento = 'dinheiro'
                        THEN pag.valor
                        ELSE 0
                    END
                ),
                0
            ) AS total_dinheiro
        FROM pagamento pag
        WHERE date(pag.data_pagamento)
              BETWEEN date(?) AND date(?)
        """,
        (
            data_inicial,
            data_final,
        ),
    ).fetchone()

    return {
        "total_recebido": (
            linha["total_recebido"] or 0
        ),
        "quantidade_pagamentos": (
            linha["quantidade_pagamentos"] or 0
        ),
        "total_pix": (
            linha["total_pix"] or 0
        ),
        "total_dinheiro": (
            linha["total_dinheiro"] or 0
        ),
    }

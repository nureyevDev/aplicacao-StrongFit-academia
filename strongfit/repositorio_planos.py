def inserir_plano(
    conexao,
    nome,
    duracao_meses,
    valor,
    ativo=True,
):
    cursor = conexao.execute(
        """
        INSERT INTO plano (
            nome,
            duracao_meses,
            valor,
            ativo
        )
        VALUES (?, ?, ?, ?)
        """,
        (
            nome,
            duracao_meses,
            valor,
            int(ativo),
        ),
    )

    return cursor.lastrowid


def atualizar_plano(
    conexao,
    plano_id,
    nome,
    duracao_meses,
    valor,
    ativo,
):
    conexao.execute(
        """
        UPDATE plano
        SET
            nome = ?,
            duracao_meses = ?,
            valor = ?,
            ativo = ?
        WHERE id = ?
        """,
        (
            nome,
            duracao_meses,
            valor,
            int(ativo),
            plano_id,
        ),
    )


def obter_plano(
    conexao,
    plano_id,
):
    return conexao.execute(
        """
        SELECT
            id,
            nome,
            duracao_meses,
            valor,
            ativo,
            criado_em
        FROM plano
        WHERE id = ?
        """,
        (plano_id,),
    ).fetchone()


def buscar_plano_por_nome(
    conexao,
    nome,
):
    return conexao.execute(
        """
        SELECT
            id,
            nome,
            duracao_meses,
            valor,
            ativo
        FROM plano
        WHERE nome = ? COLLATE NOCASE
        """,
        (nome,),
    ).fetchone()


def listar_planos(
    conexao,
    pesquisa="",
    somente_ativos=False,
):
    termo = f"%{pesquisa.strip()}%"

    sql = """
        SELECT
            p.id,
            p.nome,
            p.duracao_meses,
            p.valor,
            p.ativo,
            p.criado_em,
            (
                SELECT COUNT(*)
                FROM matricula m
                WHERE m.plano_id = p.id
            ) AS total_matriculas
        FROM plano p
        WHERE p.nome LIKE ? COLLATE NOCASE
    """

    parametros = [termo]

    if somente_ativos:
        sql += " AND p.ativo = 1"

    sql += " ORDER BY p.nome COLLATE NOCASE"

    return conexao.execute(
        sql,
        parametros,
    ).fetchall()


def alterar_situacao_plano(
    conexao,
    plano_id,
    ativo,
):
    conexao.execute(
        """
        UPDATE plano
        SET ativo = ?
        WHERE id = ?
        """,
        (
            int(ativo),
            plano_id,
        ),
    )


def contar_matriculas_do_plano(
    conexao,
    plano_id,
):
    linha = conexao.execute(
        """
        SELECT COUNT(*) AS quantidade
        FROM matricula
        WHERE plano_id = ?
        """,
        (plano_id,),
    ).fetchone()

    return linha["quantidade"]
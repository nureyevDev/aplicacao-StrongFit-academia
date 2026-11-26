def inserir_observacao(
    conexao,
    aluno_id,
    texto,
    usuario_id=None,
):
    cursor = conexao.execute(
        """
        INSERT INTO observacao_aluno (
            aluno_id,
            usuario_id,
            texto
        )
        VALUES (?, ?, ?)
        """,
        (
            aluno_id,
            usuario_id,
            texto,
        ),
    )

    return cursor.lastrowid


def obter_observacao(
    conexao,
    observacao_id,
):
    return conexao.execute(
        """
        SELECT
            obs.id,
            obs.aluno_id,
            obs.usuario_id,
            obs.texto,
            obs.criado_em,
            alu.nome AS aluno,
            usu.nome AS usuario
        FROM observacao_aluno obs
        JOIN aluno alu
            ON alu.id = obs.aluno_id
        LEFT JOIN usuario usu
            ON usu.id = obs.usuario_id
        WHERE obs.id = ?
        """,
        (observacao_id,),
    ).fetchone()


def listar_observacoes_do_aluno(
    conexao,
    aluno_id,
    pesquisa="",
):
    termo = f"%{pesquisa.strip()}%"

    return conexao.execute(
        """
        SELECT
            obs.id,
            obs.aluno_id,
            obs.texto,
            obs.criado_em,
            COALESCE(
                usu.nome,
                'Sistema'
            ) AS usuario
        FROM observacao_aluno obs
        LEFT JOIN usuario usu
            ON usu.id = obs.usuario_id
        WHERE obs.aluno_id = ?
          AND obs.texto
              LIKE ? COLLATE NOCASE
        ORDER BY
            obs.criado_em DESC,
            obs.id DESC
        """,
        (
            aluno_id,
            termo,
        ),
    ).fetchall()


def contar_observacoes_do_aluno(
    conexao,
    aluno_id,
):
    linha = conexao.execute(
        """
        SELECT COUNT(*) AS quantidade
        FROM observacao_aluno
        WHERE aluno_id = ?
        """,
        (aluno_id,),
    ).fetchone()

    return linha["quantidade"]


def excluir_observacao(
    conexao,
    observacao_id,
):
    conexao.execute(
        """
        DELETE FROM observacao_aluno
        WHERE id = ?
        """,
        (observacao_id,),
    )
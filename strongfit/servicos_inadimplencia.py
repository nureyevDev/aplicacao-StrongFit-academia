from datetime import date

from strongfit import repositorio_financeiro as repo


def atualizar_inadimplencia(
    conexao,
    hoje=None,
):
    """
    Atualiza mensalidades vencidas e a situação
    financeira dos alunos.

    Retorna a quantidade de mensalidades que
    passaram para atrasada.
    """

    hoje = hoje or date.today()

    if isinstance(hoje, date):
        hoje = hoje.isoformat()

    with conexao:
        mensalidades_atualizadas = (
            repo.marcar_mensalidades_atrasadas(
                conexao,
                hoje,
            )
        )

        repo.atualizar_alunos_inadimplentes(
            conexao,
            hoje,
        )

        repo.regularizar_alunos_sem_pendencias(
            conexao,
        )

    return mensalidades_atualizadas


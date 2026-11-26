from strongfit import (
    repositorio_alunos as repo_alunos,
)
from strongfit import (
    repositorio_observacoes as repo,
)
from strongfit.erros import RegraNegocioErro


LIMITE_OBSERVACAO = 1000


def normalizar_texto(valor):
    return " ".join(
        (valor or "").split()
    )


def registrar_observacao(
    conexao,
    aluno_id,
    texto,
    usuario_id=None,
):
    if aluno_id is None:
        raise RegraNegocioErro(
            "Selecione um aluno antes de "
            "registrar a observação."
        )

    aluno = repo_alunos.obter_aluno(
        conexao,
        aluno_id,
    )

    if aluno is None:
        raise RegraNegocioErro(
            "O aluno selecionado não existe."
        )

    texto = normalizar_texto(texto)

    if not texto:
        raise RegraNegocioErro(
            "Informe o texto da observação."
        )

    if len(texto) > LIMITE_OBSERVACAO:
        raise RegraNegocioErro(
            "A observação não pode ultrapassar "
            f"{LIMITE_OBSERVACAO} caracteres."
        )

    with conexao:
        return repo.inserir_observacao(
            conexao,
            aluno_id,
            texto,
            usuario_id,
        )


def remover_observacao(
    conexao,
    observacao_id,
):
    observacao = repo.obter_observacao(
        conexao,
        observacao_id,
    )

    if observacao is None:
        raise RegraNegocioErro(
            "A observação selecionada não existe."
        )

    with conexao:
        repo.excluir_observacao(
            conexao,
            observacao_id,
        )
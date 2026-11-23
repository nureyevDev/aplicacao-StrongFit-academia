import re
import sqlite3

from strongfit import repositorio_alunos as repo
from strongfit.erros import RegraNegocioErro


SITUACOES = {
    "ativo",
    "inadimplente",
    "congelado",
    "inativo",
}


def normalizar_texto(valor):
    return " ".join(
        (valor or "").split()
    )


def normalizar_cpf(valor):
    return re.sub(
        r"\D",
        "",
        valor or "",
    )


def validar_email(email):
    if not email:
        return

    padrao = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"

    if not re.match(padrao, email):
        raise RegraNegocioErro(
            "Informe um e-mail válido."
        )


def validar_dados(
    nome,
    cpf,
    data_nascimento,
    telefone,
    email,
    endereco,
    situacao,
):
    nome = normalizar_texto(nome)
    cpf = normalizar_cpf(cpf)
    telefone = normalizar_texto(telefone)
    email = (email or "").strip().lower()
    endereco = normalizar_texto(endereco)

    if not nome:
        raise RegraNegocioErro(
            "Informe o nome do aluno."
        )

    if cpf and len(cpf) != 11:
        raise RegraNegocioErro(
            "O CPF deve possuir 11 dígitos."
        )

    validar_email(email)

    if situacao not in SITUACOES:
        raise RegraNegocioErro(
            "Selecione uma situação válida."
        )

    return (
        nome,
        cpf or None,
        data_nascimento or None,
        telefone,
        email,
        endereco,
        situacao,
    )


def cadastrar_aluno(
    conexao,
    nome,
    cpf,
    data_nascimento,
    telefone,
    email,
    endereco,
    situacao="ativo",
):
    dados = validar_dados(
        nome,
        cpf,
        data_nascimento,
        telefone,
        email,
        endereco,
        situacao,
    )

    cpf_normalizado = dados[1]

    if (
        cpf_normalizado
        and repo.buscar_aluno_por_cpf(
            conexao,
            cpf_normalizado,
        )
    ):
        raise RegraNegocioErro(
            "Já existe um aluno com esse CPF."
        )

    try:
        with conexao:
            return repo.inserir_aluno(
                conexao,
                *dados,
            )

    except sqlite3.IntegrityError as erro:
        raise RegraNegocioErro(
            "Não foi possível cadastrar o aluno."
        ) from erro


def editar_aluno(
    conexao,
    aluno_id,
    nome,
    cpf,
    data_nascimento,
    telefone,
    email,
    endereco,
    situacao,
):
    if repo.obter_aluno(
        conexao,
        aluno_id,
    ) is None:
        raise RegraNegocioErro(
            "O aluno selecionado não existe."
        )

    dados = validar_dados(
        nome,
        cpf,
        data_nascimento,
        telefone,
        email,
        endereco,
        situacao,
    )

    existente = None

    if dadosexistente = repo.buscar_aluno_por_cpf(
            conexao,
            dados[1],
        )

    if (
        existente
        and existente["id"] != aluno_id
    ):
        raise RegraNegocioErro(
            "Já existe outro aluno com esse CPF."
        )

    with conexao:
        repo.atualizar_aluno(
            conexao,
            aluno_id,
            *dados,
        )
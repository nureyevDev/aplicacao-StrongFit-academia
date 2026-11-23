from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QLabel,
    QVBoxLayout,
    QWidget,
)

from strongfit import repositorio_alunos as repo


class CartaoIndicador(QFrame):
    def __init__(
        self,
        titulo,
        cor,
    ):
        super().__init__()

        self.setObjectName("cartaoIndicador")
        self.setProperty("cor", cor)

        layout = QVBoxLayout(self)

        self.valor = QLabel("0")
        self.valor.setObjectName(
            "valorIndicador"
        )
        self.valor.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        rotulo = QLabel(titulo)
        rotulo.setObjectName(
            "rotuloIndicador"
        )
        rotulo.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        layout.addWidget(self.valor)
        layout.addWidget(rotulo)


class PaginaInicio(QWidget):
    def __init__(self, conexao):
        super().__init__()

        self.conexao = conexao

        layout = QVBoxLayout(self)
        layout.setContentsMargins(
            24,
            24,
            24,
            24,
        )
        layout.setSpacing(18)

        titulo = QLabel(
            "Visão geral da StrongFit"
        )
        titulo.setObjectName(
            "tituloPagina"
        )

        subtitulo = QLabel(
            "Acompanhe rapidamente a situação "
            "dos alunos da academia."
        )
        subtitulo.setObjectName(
            "subtituloPagina"
        )

        layout.addWidget(titulo)
        layout.addWidget(subtitulo)

        grade = QGridLayout()
        grade.setSpacing(16)

        self.cartao_total = CartaoIndicador(
            "Alunos cadastrados",
            "neutro",
        )

        self.cartao_ativos = CartaoIndicador(
            "Alunos ativos",
            "sucesso",
        )

        self.cartao_inadimplentes = (
            CartaoIndicador(
                "Inadimplentes",
                "perigo",
            )
        )

        self.cartao_congelados = (
            CartaoIndicador(
                "Planos congelados",
                "aviso",
            )
        )

        grade.addWidget(
            self.cartao_total,
            0,
            0,
        )
        grade.addWidget(
            self.cartao_ativos,
            0,
            1,
        )
        grade.addWidget(
            self.cartao_inadimplentes,
            1,
            0,
        )
        grade.addWidget(
            self.cartao_congelados,
            1,
            1,
        )

        layout.addLayout(grade)
        layout.addStretch()

    def atualizar(self):
        quantidades = (
            repo.contar_alunos_por_situacao(
                self.conexao
            )
        )

        total = sum(
            quantidades.values()
        )

        self.cartao_total.valor.setText(
            str(total)
        )

        self.cartao_ativos.valor.setText(
            str(
                quantidades.get(
                    "ativo",
                    0,
                )
            )
        )

        self.cartao_inadimplentes.valor.setText(
            str(
                quantidades.get(
                    "inadimplente",
                    0,
                )
            )
        )

        self.cartao_congelados.valor.setText(
            str(
                quantidades.get(
                    "congelado",
                    0,
                )
            )
        )
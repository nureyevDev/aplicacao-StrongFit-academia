from datetime import date

from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (
    QAbstractItemView,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from strongfit import (
    repositorio_dashboard as repo,
)
from strongfit.servicos_inadimplencia import (
    atualizar_inadimplencia,
)


class CartaoIndicador(QFrame):
    def __init__(
        self,
        titulo,
        destaque="padrao",
    ):
        super().__init__()

        self.setObjectName(
            "cartaoIndicador"
        )
        self.setProperty(
            "destaque",
            destaque,
        )
        self.setMinimumHeight(120)

        self.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Fixed,
        )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(
            18,
            16,
            18,
            16,
        )
        layout.setSpacing(6)

        self.valor = QLabel("0")
        self.valor.setObjectName(
            "valorIndicador"
        )

        self.rotulo = QLabel(titulo)
        self.rotulo.setObjectName(
            "rotuloIndicador"
        )
        self.rotulo.setWordWrap(True)

        layout.addWidget(self.valor)
        layout.addWidget(self.rotulo)
        layout.addStretch()


class PaginaInicio(QWidget):
    def __init__(self, conexao):
        super().__init__()

        self.conexao = conexao

        self.montar_interface()

        QTimer.singleShot(
            0,
            self.atualizar,
        )

    def montar_interface(self):
        layout_externo = QVBoxLayout(self)
        layout_externo.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        area_rolagem = QScrollArea()
        area_rolagem.setObjectName(
            "areaDashboard"
        )
        area_rolagem.setWidgetResizable(True)
        area_rolagem.setFrameShape(
            QFrame.Shape.NoFrame
        )
        area_rolagem.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        area_rolagem.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded
        )

        conteudo = QWidget()
        conteudo.setObjectName(
            "conteudoDashboard"
        )
        conteudo.setMinimumWidth(900)

        layout = QVBoxLayout(conteudo)
        layout.setContentsMargins(
            24,
            24,
            24,
            24,
        )
        layout.setSpacing(18)

        cabecalho = QHBoxLayout()
        textos = QVBoxLayout()

        titulo = QLabel(
            "Visão geral da StrongFit"
        )
        titulo.setObjectName(
            "tituloPagina"
        )

        self.subtitulo = QLabel(
            "Acompanhe alunos, mensalidades "
            "e resultados financeiros."
        )
        self.subtitulo.setObjectName(
            "subtituloPagina"
        )

        textos.addWidget(titulo)
        textos.addWidget(self.subtitulo)

        self.botao_atualizar = QPushButton(
            "Atualizar painel"
        )
        self.botao_atualizar.setObjectName(
            "botaoPrimario"
        )
        self.botao_atualizar.setMinimumWidth(
            150
        )
        self.botao_atualizar.clicked.connect(
            self.atualizar
        )

        cabecalho.addLayout(textos)
        cabecalho.addStretch()
        cabecalho.addWidget(
            self.botao_atualizar
        )

        layout.addLayout(cabecalho)

        self.criar_cartoes_alunos(layout)
        self.criar_cartoes_financeiros(layout)
        self.criar_tabelas(layout)

        self.mensagem = QLabel(
            "Painel aguardando atualização."
        )
        self.mensagem.setObjectName(
            "mensagem"
        )
        self.mensagem.setWordWrap(True)

        layout.addWidget(self.mensagem)

        area_rolagem.setWidget(conteudo)
        layout_externo.addWidget(
            area_rolagem
        )

    def criar_cartoes_alunos(self, layout):
        titulo = QLabel(
            "Alunos e matrículas"
        )
        titulo.setObjectName(
            "tituloSecao"
        )
        layout.addWidget(titulo)

        grade = QGridLayout()
        grade.setSpacing(14)

        self.cartao_total = CartaoIndicador(
            "Alunos cadastrados",
        )

        self.cartao_ativos = CartaoIndicador(
            "Alunos ativos",
            "sucesso",
        )

        self.cartao_inadimplentes = CartaoIndicador(
            "Alunos inadimplentes",
            "perigo",
        )

        self.cartao_congelados = CartaoIndicador(
            "Alunos congelados",
            "aviso",
        )

        self.cartao_matriculas = CartaoIndicador(
            "Matrículas ativas",
            "destaque",
        )

        self.cartao_inativos = CartaoIndicador(
            "Alunos inativos",
            "neutro",
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
            0,
            2,
        )
        grade.addWidget(
            self.cartao_congelados,
            1,
            0,
        )
        grade.addWidget(
            self.cartao_matriculas,
            1,
            1,
        )
        grade.addWidget(
            self.cartao_inativos,
            1,
            2,
        )

        for coluna in range(3):
            grade.setColumnStretch(
                coluna,
                1,
            )

        layout.addLayout(grade)

    def criar_cartoes_financeiros(
        self,
        layout,
    ):
        titulo = QLabel(
            "Resumo financeiro"
        )
        titulo.setObjectName(
            "tituloSecao"
        )
        layout.addWidget(titulo)

        grade = QGridLayout()
        grade.setSpacing(14)

        self.cartao_receita = CartaoIndicador(
            "Receita recebida no mês",
            "sucesso",
        )

        self.cartao_pendente = CartaoIndicador(
            "Valor pendente da competência",
            "aviso",
        )

        self.cartao_mensalidades_pendentes = (
            CartaoIndicador(
                "Mensalidades pendentes",
                "destaque",
            )
        )

        self.cartao_mensalidades_atrasadas = (
            CartaoIndicador(
                "Mensalidades atrasadas",
                "perigo",
            )
        )

        grade.addWidget(
            self.cartao_receita,
            0,
            0,
        )
        grade.addWidget(
            self.cartao_pendente,
            0,
            1,
        )
        grade.addWidget(
            self.cartao_mensalidades_pendentes,
            0,
            2,
        )
        grade.addWidget(
            self.cartao_mensalidades_atrasadas,
            0,
            3,
        )

        for coluna in range(4):
            grade.setColumnStretch(
                coluna,
                1,
            )

        layout.addLayout(grade)

    def criar_tabelas(self, layout):
        area_tabelas = QHBoxLayout()
        area_tabelas.setSpacing(16)

        area_tabelas.addWidget(
            self.criar_tabela_vencimentos(),
            3,
        )

        area_tabelas.addWidget(
            self.criar_tabela_planos(),
            2,
        )

        layout.addLayout(area_tabelas)

    def criar_tabela_vencimentos(self):
        frame = QFrame()
        frame.setObjectName("cartao")
        frame.setMinimumHeight(300)

        layout = QVBoxLayout(frame)

        titulo = QLabel(
            "Próximos vencimentos e atrasos"
        )
        titulo.setObjectName(
            "tituloSecao"
        )

        self.tabela_vencimentos = QTableWidget(
            0,
            5,
        )

        self.tabela_vencimentos.setHorizontalHeaderLabels(
            [
                "Aluno",
                "Plano",
                "Vencimento",
                "Valor",
                "Situação",
            ]
        )

        self.configurar_tabela(
            self.tabela_vencimentos
        )

        cabecalho = (
            self.tabela_vencimentos
            .horizontalHeader()
        )

        cabecalho.setSectionResizeMode(
            0,
            QHeaderView.ResizeMode.Stretch,
        )
        cabecalho.setSectionResizeMode(
            1,
            QHeaderView.ResizeMode.Stretch,
        )

        for coluna in range(2, 5):
            cabecalho.setSectionResizeMode(
                coluna,
                QHeaderView
                .ResizeMode
                .ResizeToContents,
            )

        layout.addWidget(titulo)
        layout.addWidget(
            self.tabela_vencimentos
        )

        return frame

    def criar_tabela_planos(self):
        frame = QFrame()
        frame.setObjectName("cartao")
        frame.setMinimumHeight(300)

        layout = QVBoxLayout(frame)

        titulo = QLabel(
            "Planos mais vendidos"
        )
        titulo.setObjectName(
            "tituloSecao"
        )

        self.tabela_planos = QTableWidget(
            0,
            3,
        )

        self.tabela_planos.setHorizontalHeaderLabels(
            [
                "Plano",
                "Matrículas",
                "Valor contratado",
            ]
        )

        self.configurar_tabela(
            self.tabela_planos
        )

        cabecalho = (
            self.tabela_planos
            .horizontalHeader()
        )

        cabecalho.setSectionResizeMode(
            0,
            QHeaderView.ResizeMode.Stretch,
        )

        for coluna in (1, 2):
            cabecalho.setSectionResizeMode(
                coluna,
                QHeaderView
                .ResizeMode
                .ResizeToContents,
            )

        layout.addWidget(titulo)
        layout.addWidget(
            self.tabela_planos
        )

        return frame

    @staticmethod
    def configurar_tabela(tabela):
        tabela.setSelectionBehavior(
            QAbstractItemView
            .SelectionBehavior
            .SelectRows
        )
        tabela.setSelectionMode(
            QAbstractItemView
            .SelectionMode
            .SingleSelection
        )
        tabela.setEditTriggers(
            QAbstractItemView
            .EditTrigger
            .NoEditTriggers
        )
        tabela.setAlternatingRowColors(
            True
        )
        tabela.verticalHeader().setVisible(
            False
        )

    def atualizar(self):
        try:
            atualizar_inadimplencia(
                self.conexao
            )

            hoje = date.today()
            inicio_mes = hoje.replace(
                day=1
            )

            if hoje.month == 12:
                inicio_proximo_mes = date(
                    hoje.year + 1,
                    1,
                    1,
                )
            else:
                inicio_proximo_mes = date(
                    hoje.year,
                    hoje.month + 1,
                    1,
                )

            competencia = hoje.strftime(
                "%Y-%m"
            )

            alunos = repo.resumo_alunos(
                self.conexao
            )

            financeiro = (
                repo.resumo_financeiro_mes(
                    self.conexao,
                    competencia,
                    inicio_mes.isoformat(),
                    inicio_proximo_mes.isoformat(),
                )
            )

            matriculas = (
                repo.contar_matriculas_por_situacao(
                    self.conexao
                )
            )

            vencimentos = (
                repo.listar_proximos_vencimentos(
                    self.conexao,
                    hoje.isoformat(),
                )
            )

            planos = (
                repo.listar_planos_mais_vendidos(
                    self.conexao
                )
            )

        except Exception as erro:
            self.mensagem.setText(
                "Não foi possível atualizar o painel: "
                f"{erro}"
            )
            return

        self.cartao_total.valor.setText(
            str(alunos["total"])
        )
        self.cartao_ativos.valor.setText(
            str(alunos["ativos"])
        )
        self.cartao_inadimplentes.valor.setText(
            str(alunos["inadimplentes"])
        )
        self.cartao_congelados.valor.setText(
            str(alunos["congelados"])
        )
        self.cartao_inativos.valor.setText(
            str(alunos["inativos"])
        )
        self.cartao_matriculas.valor.setText(
            str(matriculas["ativa"])
        )

        self.cartao_receita.valor.setText(
            self.formatar_moeda(
                financeiro["receita_mes"]
            )
        )

        self.cartao_pendente.valor.setText(
            self.formatar_moeda(
                financeiro["pendente_mes"]
            )
        )

        self.cartao_mensalidades_pendentes.valor.setText(
            str(
                financeiro[
                    "mensalidades_pendentes"
                ]
            )
        )

        self.cartao_mensalidades_atrasadas.valor.setText(
            str(
                financeiro[
                    "mensalidades_atrasadas"
                ]
            )
        )

        self.preencher_vencimentos(
            vencimentos
        )
        self.preencher_planos(
            planos
        )

        self.subtitulo.setText(
            "Dados atualizados para "
            f"{hoje.strftime('%d/%m/%Y')}."
        )

        self.mensagem.setText(
            "Painel atualizado com sucesso."
        )

    def preencher_vencimentos(
        self,
        vencimentos,
    ):
        self.tabela_vencimentos.setRowCount(
            len(vencimentos)
        )

        for linha, vencimento in enumerate(
            vencimentos
        ):
            valores = [
                vencimento["aluno"],
                vencimento["plano"],
                self.formatar_data(
                    vencimento[
                        "data_vencimento"
                    ]
                ),
                self.formatar_moeda(
                    vencimento["valor"]
                ),
                vencimento["situacao"].title(),
            ]

            for coluna, valor in enumerate(
                valores
            ):
                self.tabela_vencimentos.setItem(
                    linha,
                    coluna,
                    QTableWidgetItem(
                        str(valor)
                    ),
                )

    def preencher_planos(self, planos):
        self.tabela_planos.setRowCount(
            len(planos)
        )

        for linha, plano in enumerate(planos):
            valores = [
                plano["plano"],
                plano["vendas"],
                self.formatar_moeda(
                    plano["valor_contratado"]
                ),
            ]

            for coluna, valor in enumerate(
                valores
            ):
                self.tabela_planos.setItem(
                    linha,
                    coluna,
                    QTableWidgetItem(
                        str(valor)
                    ),
                )

    @staticmethod
    def formatar_data(data_iso):
        if not data_iso:
            return ""

        partes = (
            str(data_iso)
            .split(" ")[0]
            .split("-")
        )

        if len(partes) != 3:
            return str(data_iso)

        return "/".join(
            reversed(partes)
        )

    @staticmethod
    def formatar_moeda(valor):
        numero = float(valor or 0)

        formatado = (
            f"{numero:,.2f}"
            .replace(",", "X")
            .replace(".", ",")
            .replace("X", ".")
        )

        return f"R$ {formatado}"
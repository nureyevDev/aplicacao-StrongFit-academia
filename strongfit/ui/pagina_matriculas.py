from PySide6.QtCore import QDate, Qt
from PySide6.QtWidgets import (
    QAbstractItemView,
    QComboBox,
    QDateEdit,
    QDoubleSpinBox,
    QFormLayout,
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from strongfit import repositorio_matriculas as repo
from strongfit import servicos_matriculas
from strongfit.erros import RegraNegocioErro


class PaginaMatriculas(QWidget):
    def __init__(self, conexao):
        super().__init__()

        self.conexao = conexao
        self.matricula_selecionada_id = None
        self.planos = {}

        self.montar_interface()
        self.atualizar_tudo()

    def montar_interface(self):
        layout_principal = QVBoxLayout(self)
        layout_principal.setContentsMargins(
            22,
            22,
            22,
            22,
        )
        layout_principal.setSpacing(14)

        titulo = QLabel(
            "Gestão de matrículas"
        )
        titulo.setObjectName(
            "tituloPagina"
        )

        subtitulo = QLabel(
            "Vincule um aluno a um plano e "
            "acompanhe seus vencimentos."
        )
        subtitulo.setObjectName(
            "subtituloPagina"
        )

        layout_principal.addWidget(titulo)
        layout_principal.addWidget(subtitulo)

        conteudo = QHBoxLayout()
        conteudo.setSpacing(16)

        conteudo.addWidget(
            self.criar_formulario(),
            2,
        )
        conteudo.addWidget(
            self.criar_lista(),
            3,
        )

        layout_principal.addLayout(
            conteudo,
            1,
        )

        self.mensagem = QLabel(
            "Selecione um aluno e um plano."
        )
        self.mensagem.setObjectName(
            "mensagem"
        )
        self.mensagem.setWordWrap(True)

        layout_principal.addWidget(
            self.mensagem
        )

    def criar_formulario(self):
        frame = QFrame()
        frame.setObjectName("cartao")

        layout = QVBoxLayout(frame)
        layout.setSpacing(12)

        titulo = QLabel(
            "Nova matrícula"
        )
        titulo.setObjectName(
            "tituloSecao"
        )
        layout.addWidget(titulo)

        formulario = QFormLayout()
        formulario.setSpacing(11)

        self.combo_aluno = QComboBox()
        self.combo_plano = QComboBox()

        self.data_inicio = QDateEdit(
            QDate.currentDate()
        )
        self.data_inicio.setCalendarPopup(
            True
        )
        self.data_inicio.setDisplayFormat(
            "dd/MM/yyyy"
        )

        self.campo_valor = QDoubleSpinBox()
        self.campo_valor.setRange(
            0,
            999999.99,
        )
        self.campo_valor.setDecimals(2)
        self.campo_valor.setPrefix(
            "R$ "
        )

        self.rotulo_vencimento = QLabel(
            "Selecione um plano"
        )
        self.rotulo_vencimento.setObjectName(
            "destaque"
        )

        formulario.addRow(
            "Aluno *",
            self.combo_aluno,
        )
        formulario.addRow(
            "Plano *",
            self.combo_plano,
        )
        formulario.addRow(
            "Data inicial *",
            self.data_inicio,
        )
        formulario.addRow(
            "Valor contratado *",
            self.campo_valor,
        )
        formulario.addRow(
            "Vencimento",
            self.rotulo_vencimento,
        )

        layout.addLayout(formulario)

        self.botao_matricular = QPushButton(
            "Criar matrícula"
        )
        self.botao_matricular.setObjectName(
            "botaoPrimario"
        )

        self.botao_matricular.clicked.connect(
            self.criar_matricula
        )

        self.combo_plano.currentIndexChanged.connect(
            self.plano_alterado
        )

        self.data_inicio.dateChanged.connect(
            self.atualizar_previsao
        )

        layout.addWidget(
            self.botao_matricular
        )
        layout.addStretch()

        return frame

    def criar_lista(self):
        frame = QFrame()
        frame.setObjectName("cartao")

        layout = QVBoxLayout(frame)
        layout.setSpacing(12)

        topo = QHBoxLayout()

        titulo = QLabel(
            "Matrículas registradas"
        )
        titulo.setObjectName(
            "tituloSecao"
        )

        self.campo_pesquisa = QLineEdit()
        self.campo_pesquisa.setPlaceholderText(
            "Pesquisar aluno ou plano"
        )

        self.filtro_situacao = QComboBox()
        self.filtro_situacao.addItem(
            "Todas",
            None,
        )
        self.filtro_situacao.addItem(
            "Ativas",
            "ativa",
        )
        self.filtro_situacao.addItem(
            "Congeladas",
            "congelada",
        )
        self.filtro_situacao.addItem(
            "Vencidas",
            "vencida",
        )
        self.filtro_situacao.addItem(
            "Encerradas",
            "encerrada",
        )

        topo.addWidget(titulo)
        topo.addStretch()
        topo.addWidget(
            self.campo_pesquisa
        )
        topo.addWidget(
            self.filtro_situacao
        )

        self.tabela = QTableWidget(
            0,
            8,
        )

        self.tabela.setHorizontalHeaderLabels(
            [
                "ID",
                "Aluno",
                "CPF",
                "Plano",
                "Início",
                "Vencimento",
                "Valor",
                "Situação",
            ]
        )

        self.tabela.setSelectionBehavior(
            QAbstractItemView
            .SelectionBehavior
            .SelectRows
        )

        self.tabela.setSelectionMode(
            QAbstractItemView
            .SelectionMode
            .SingleSelection
        )

        self.tabela.setEditTriggers(
            QAbstractItemView
            .EditTrigger
            .NoEditTriggers
        )

        self.tabela.setAlternatingRowColors(
            True
        )

        self.tabela.verticalHeader().setVisible(
            False
        )

        cabecalho = (
            self.tabela.horizontalHeader()
        )

        cabecalho.setSectionResizeMode(
            0,
            QHeaderView
            .ResizeMode
            .ResizeToContents,
        )
        cabecalho.setSectionResizeMode(
            1,
            QHeaderView.ResizeMode.Stretch,
        )

        for coluna in range(2, 8):
            cabecalho.setSectionResizeMode(
                coluna,
                QHeaderView
                .ResizeMode
                .ResizeToContents,
            )

        self.botao_encerrar = QPushButton(
            "Encerrar matrícula selecionada"
        )
        self.botao_encerrar.setObjectName(
            "botaoPerigo"
        )

        self.botao_encerrar.clicked.connect(
            self.encerrar_matricula
        )

        self.campo_pesquisa.textChanged.connect(
            self.atualizar_tabela
        )

        self.filtro_situacao.currentIndexChanged.connect(
            self.atualizar_tabela
        )

        self.tabela.itemSelectionChanged.connect(
            self.selecionar_matricula
        )

        acoes = QHBoxLayout()
        acoes.addStretch()
        acoes.addWidget(
            self.botao_encerrar
        )

        layout.addLayout(topo)
        layout.addWidget(self.tabela)
        layout.addLayout(acoes)

        return frame

    def carregar_alunos(self):
        alunos = repo.listar_alunos_disponiveis(
            self.conexao
        )

        atual = self.combo_aluno.currentData()

        self.combo_aluno.clear()
        self.combo_aluno.addItem(
            "Selecione um aluno",
            None,
        )

        for aluno in alunos:
            texto = aluno["nome"]

            if aluno["cpf"]:
                texto += (
                    f" | {aluno['cpf']}"
                )

            self.combo_aluno.addItem(
                texto,
                aluno["id"],
            )

        indice = self.combo_aluno.findData(
            atual
        )

        self.combo_aluno.setCurrentIndex(
            max(indice, 0)
        )

    def carregar_planos(self):
        planos = repo.listar_planos_ativos(
            self.conexao
        )

        atual = self.combo_plano.currentData()

        self.planos = {
            plano["id"]: plano
            for plano in planos
        }

        self.combo_plano.clear()
        self.combo_plano.addItem(
            "Selecione um plano",
            None,
        )

        for plano in planos:
            self.combo_plano.addItem(
                (
                    f"{plano['nome']} | "
                    f"{plano['duracao_meses']} mês(es)"
                ),
                plano["id"],
            )

        indice = self.combo_plano.findData(
            atual
        )

        self.combo_plano.setCurrentIndex(
            max(indice, 0)
        )

    def plano_alterado(self):
        plano_id = self.combo_plano.currentData()

        if plano_id is None:
            self.campo_valor.setValue(0)
            self.rotulo_vencimento.setText(
                "Selecione um plano"
            )
            return

        plano = self.planos.get(
            plano_id
        )

        if plano is None:
            return

        self.campo_valor.setValue(
            float(plano["valor"])
        )

        self.atualizar_previsao()

    def atualizar_previsao(self):
        plano_id = self.combo_plano.currentData()

        if plano_id is None:
            return

        plano = self.planos.get(
            plano_id
        )

        if plano is None:
            return

        data_python = (
            self.data_inicio.date().toPython()
        )

        vencimento = (
            servicos_matriculas.adicionar_meses(
                data_python,
                plano["duracao_meses"],
            )
        )

        self.rotulo_vencimento.setText(
            vencimento.strftime(
                "%d/%m/%Y"
            )
        )

    def criar_matricula(self):
        try:
            servicos_matriculas.criar_matricula(
                self.conexao,
                self.combo_aluno.currentData(),
                self.combo_plano.currentData(),
                self.data_inicio
                .date()
                .toPython(),
                self.campo_valor.value(),
            )

        except RegraNegocioErro as erro:
            QMessageBox.warning(
                self,
                "StrongFit Academia",
                str(erro),
            )
            return

        self.atualizar_tudo()

        self.mensagem.setText(
            "Matrícula criada com sucesso."
        )

    def atualizar_tabela(self):
        matriculas = repo.listar_matriculas(
            self.conexao,
            self.campo_pesquisa.text(),
            self.filtro_situacao.currentData(),
        )

        self.tabela.setRowCount(
            len(matriculas)
        )

        for linha, matricula in enumerate(
            matriculas
        ):
            valores = [
                matricula["id"],
                matricula["aluno"],
                matricula["cpf"] or "",
                matricula["plano"],
                self.formatar_data(
                    matricula["data_inicio"]
                ),
                self.formatar_data(
                    matricula["data_vencimento"]
                ),
                self.formatar_moeda(
                    matricula["valor_contratado"]
                ),
                matricula["situacao"].title(),
            ]

            for coluna, valor in enumerate(
                valores
            ):
                item = QTableWidgetItem(
                    str(valor)
                )

                if coluna in (
                    0,
                    4,
                    5,
                    6,
                    7,
                ):
                    item.setTextAlignment(
                        Qt.AlignmentFlag.AlignCenter
                    )

                self.tabela.setItem(
                    linha,
                    coluna,
                    item,
                )

        self.tabela.clearSelection()
        self.matricula_selecionada_id = None

    def selecionar_matricula(self):
        linha = self.tabela.currentRow()

        if linha < 0:
            self.matricula_selecionada_id = None
            return

        self.matricula_selecionada_id = int(
            self.tabela.item(
                linha,
                0,
            ).text()
        )

    def encerrar_matricula(self):
        if (
            self.matricula_selecionada_id
            is None
        ):
            QMessageBox.warning(
                self,
                "StrongFit Academia",
                "Selecione uma matrícula.",
            )
            return

        matricula = repo.obter_matricula(
            self.conexao,
            self.matricula_selecionada_id,
        )

        if matricula is None:
            return

        resposta = QMessageBox.question(
            self,
            "Confirmar encerramento",
            (
                f"Encerrar a matrícula de "
                f"{matricula['aluno']} no plano "
                f"{matricula['plano']}?"
            ),
            (
                QMessageBox.StandardButton.Yes
                | QMessageBox.StandardButton.No
            ),
            QMessageBox.StandardButton.No,
        )

        if (
            resposta
            != QMessageBox.StandardButton.Yes
        ):
            return

        try:
            servicos_matriculas.encerrar_matricula(
                self.conexao,
                self.matricula_selecionada_id,
            )

        except RegraNegocioErro as erro:
            QMessageBox.warning(
                self,
                "StrongFit Academia",
                str(erro),
            )
            return

        self.atualizar_tudo()
        self.mensagem.setText(
            "Matrícula encerrada com sucesso."
        )

    def atualizar_tudo(self):
        self.carregar_alunos()
        self.carregar_planos()
        self.atualizar_tabela()
        self.plano_alterado()

    @staticmethod
    def formatar_data(data_iso):
        if not data_iso:
            return ""

        return (
            QDate.fromString(
                str(data_iso),
                "yyyy-MM-dd",
            )
            .toString("dd/MM/yyyy")
        )

    @staticmethod
    def formatar_moeda(valor):
        numero = float(valor)

        formatado = (
            f"{numero:,.2f}"
            .replace(",", "X")
            .replace(".", ",")
            .replace("X", ".")
        )

        return f"R$ {formatado}"
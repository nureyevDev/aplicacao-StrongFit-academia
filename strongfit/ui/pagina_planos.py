from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QAbstractItemView,
    QCheckBox,
    QDoubleSpinBox,
    QFormLayout,
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from strongfit import repositorio_planos as repo
from strongfit import servicos_planos
from strongfit.erros import RegraNegocioErro


class PaginaPlanos(QWidget):
    def __init__(self, conexao):
        super().__init__()

        self.conexao = conexao
        self.plano_selecionado_id = None

        self.montar_interface()
        self.atualizar_tabela()

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
            "Gestão de planos"
        )
        titulo.setObjectName(
            "tituloPagina"
        )

        subtitulo = QLabel(
            "Cadastre e mantenha os planos "
            "oferecidos pela StrongFit."
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
            "Preencha os dados para cadastrar um plano."
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
            "Dados do plano"
        )
        titulo.setObjectName(
            "tituloSecao"
        )

        layout.addWidget(titulo)

        formulario = QFormLayout()
        formulario.setSpacing(11)

        self.campo_nome = QLineEdit()
        self.campo_nome.setPlaceholderText(
            "Ex.: Mensal Plus"
        )

        self.campo_duracao = QSpinBox()
        self.campo_duracao.setRange(
            1,
            120,
        )
        self.campo_duracao.setSuffix(
            " mês(es)"
        )
        self.campo_duracao.setValue(1)

        self.campo_valor = QDoubleSpinBox()
        self.campo_valor.setRange(
            0,
            99999.99,
        )
        self.campo_valor.setDecimals(2)
        self.campo_valor.setPrefix(
            "R$ "
        )
        self.campo_valor.setSingleStep(
            10.00
        )

        self.check_ativo = QCheckBox(
            "Plano disponível para novas matrículas"
        )
        self.check_ativo.setChecked(True)

        formulario.addRow(
            "Nome *",
            self.campo_nome,
        )
        formulario.addRow(
            "Duração *",
            self.campo_duracao,
        )
        formulario.addRow(
            "Valor *",
            self.campo_valor,
        )

        layout.addLayout(formulario)
        layout.addWidget(self.check_ativo)

        botoes = QHBoxLayout()

        self.botao_salvar = QPushButton(
            "Cadastrar"
        )
        self.botao_salvar.setObjectName(
            "botaoPrimario"
        )

        self.botao_limpar = QPushButton(
            "Limpar"
        )

        self.botao_salvar.clicked.connect(
            self.salvar_plano
        )

        self.botao_limpar.clicked.connect(
            self.limpar_formulario
        )

        botoes.addWidget(
            self.botao_salvar
        )
        botoes.addWidget(
            self.botao_limpar
        )

        layout.addLayout(botoes)
        layout.addStretch()

        return frame

    def criar_lista(self):
        frame = QFrame()
        frame.setObjectName("cartao")

        layout = QVBoxLayout(frame)
        layout.setSpacing(12)

        topo = QHBoxLayout()

        titulo = QLabel(
            "Planos cadastrados"
        )
        titulo.setObjectName(
            "tituloSecao"
        )

        self.campo_pesquisa = QLineEdit()
        self.campo_pesquisa.setPlaceholderText(
            "Pesquisar plano"
        )

        self.check_somente_ativos = QCheckBox(
            "Somente ativos"
        )

        topo.addWidget(titulo)
        topo.addStretch()
        topo.addWidget(
            self.campo_pesquisa
        )
        topo.addWidget(
            self.check_somente_ativos
        )

        self.tabela = QTableWidget(
            0,
            6,
        )

        self.tabela.setHorizontalHeaderLabels(
            [
                "ID",
                "Plano",
                "Duração",
                "Valor",
                "Situação",
                "Matrículas",
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

        for coluna in range(2, 6):
            cabecalho.setSectionResizeMode(
                coluna,
                QHeaderView
                .ResizeMode
                .ResizeToContents,
            )

        acoes = QHBoxLayout()

        self.botao_alternar = QPushButton(
            "Ativar ou inativar selecionado"
        )

        self.botao_alternar.clicked.connect(
            self.alternar_situacao_plano
        )

        acoes.addStretch()
        acoes.addWidget(
            self.botao_alternar
        )

        self.campo_pesquisa.textChanged.connect(
            self.atualizar_tabela
        )

        self.check_somente_ativos.toggled.connect(
            self.atualizar_tabela
        )

        self.tabela.itemSelectionChanged.connect(
            self.carregar_plano_selecionado
        )

        layout.addLayout(topo)
        layout.addWidget(self.tabela)
        layout.addLayout(acoes)

        return frame

    def dados_formulario(self):
        return (
            self.campo_nome.text(),
            self.campo_duracao.value(),
            self.campo_valor.value(),
            self.check_ativo.isChecked(),
        )

    def salvar_plano(self):
        try:
            if self.plano_selecionado_id is None:
                servicos_planos.cadastrar_plano(
                    self.conexao,
                    *self.dados_formulario(),
                )

                mensagem = (
                    "Plano cadastrado com sucesso."
                )

            else:
                servicos_planos.editar_plano(
                    self.conexao,
                    self.plano_selecionado_id,
                    *self.dados_formulario(),
                )

                mensagem = (
                    "Plano atualizado com sucesso."
                )

        except RegraNegocioErro as erro:
            QMessageBox.warning(
                self,
                "StrongFit Academia",
                str(erro),
            )
            return

        self.limpar_formulario()
        self.atualizar_tabela()
        self.mensagem.setText(mensagem)

    def atualizar_tabela(self):
        planos = repo.listar_planos(
            self.conexao,
            self.campo_pesquisa.text(),
            self.check_somente_ativos.isChecked(),
        )

        self.tabela.setRowCount(
            len(planos)
        )

        for linha, plano in enumerate(
            planos
        ):
            valores = [
                plano["id"],
                plano["nome"],
                (
                    f"{plano['duracao_meses']} "
                    f"mês(es)"
                ),
                self.formatar_moeda(
                    plano["valor"]
                ),
                (
                    "Ativo"
                    if plano["ativo"]
                    else "Inativo"
                ),
                plano["total_matriculas"],
            ]

            for coluna, valor in enumerate(
                valores
            ):
                item = QTableWidgetItem(
                    str(valor)
                )

                if coluna in (0, 2, 3, 4, 5):
                    item.setTextAlignment(
                        Qt.AlignmentFlag.AlignCenter
                    )

                self.tabela.setItem(
                    linha,
                    coluna,
                    item,
                )

        self.tabela.clearSelection()

    def carregar_plano_selecionado(self):
        linha = self.tabela.currentRow()

        if linha < 0:
            return

        plano_id = int(
            self.tabela.item(
                linha,
                0,
            ).text()
        )

        plano = repo.obter_plano(
            self.conexao,
            plano_id,
        )

        if plano is None:
            return

        self.plano_selecionado_id = plano_id

        self.campo_nome.setText(
            plano["nome"]
        )

        self.campo_duracao.setValue(
            plano["duracao_meses"]
        )

        self.campo_valor.setValue(
            float(plano["valor"])
        )

        self.check_ativo.setChecked(
            bool(plano["ativo"])
        )

        self.botao_salvar.setText(
            "Atualizar"
        )

        self.mensagem.setText(
            "Plano selecionado para edição."
        )

    def alternar_situacao_plano(self):
        linha = self.tabela.currentRow()

        if linha < 0:
            QMessageBox.warning(
                self,
                "StrongFit Academia",
                "Selecione um plano na tabela.",
            )
            return

        plano_id = int(
            self.tabela.item(
                linha,
                0,
            ).text()
        )

        plano = repo.obter_plano(
            self.conexao,
            plano_id,
        )

        if plano is None:
            return

        novo_estado = not bool(
            plano["ativo"]
        )

        acao = (
            "ativar"
            if novo_estado
            else "inativar"
        )

        resposta = QMessageBox.question(
            self,
            "Confirmar alteração",
            (
                f"Deseja {acao} o plano "
                f"{plano['nome']}?"
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
            servicos_planos.definir_plano_ativo(
                self.conexao,
                plano_id,
                novo_estado,
            )

        except RegraNegocioErro as erro:
            QMessageBox.warning(
                self,
                "StrongFit Academia",
                str(erro),
            )
            return

        self.limpar_formulario()
        self.atualizar_tabela()

        self.mensagem.setText(
            f"Plano {acao} com sucesso."
        )

    def limpar_formulario(self):
        self.plano_selecionado_id = None
        self.campo_nome.clear()
        self.campo_duracao.setValue(1)
        self.campo_valor.setValue(0)
        self.check_ativo.setChecked(True)
        self.tabela.clearSelection()
        self.botao_salvar.setText(
            "Cadastrar"
        )
        self.campo_nome.setFocus()

        self.mensagem.setText(
            "Formulário limpo."
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
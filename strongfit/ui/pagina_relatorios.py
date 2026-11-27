import csv
from datetime import date
from pathlib import Path

from PySide6.QtCore import QDate, Qt
from PySide6.QtWidgets import (
    QAbstractItemView,
    QComboBox,
    QDateEdit,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTabWidget,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from strongfit import (
    repositorio_relatorios as repo,
)
from strongfit.servicos_inadimplencia import (
    atualizar_inadimplencia,
)


class PaginaRelatorios(QWidget):
    def __init__(self, conexao):
        super().__init__()

        self.conexao = conexao

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
            "Relatórios gerenciais"
        )
        titulo.setObjectName(
            "tituloPagina"
        )

        subtitulo = QLabel(
            "Consulte e exporte informações "
            "operacionais e financeiras da StrongFit."
        )
        subtitulo.setObjectName(
            "subtituloPagina"
        )

        layout_principal.addWidget(titulo)
        layout_principal.addWidget(subtitulo)

        layout_principal.addWidget(
            self.criar_filtros()
        )

        self.abas = QTabWidget()

        self.abas.addTab(
            self.criar_aba_ativos(),
            "Alunos ativos",
        )

        self.abas.addTab(
            self.criar_aba_inadimplentes(),
            "Inadimplentes",
        )

        self.abas.addTab(
            self.criar_aba_matriculas(),
            "Matrículas",
        )

        self.abas.addTab(
            self.criar_aba_planos(),
            "Planos mais vendidos",
        )

        self.abas.addTab(
            self.criar_aba_financeiro(),
            "Financeiro",
        )

        self.abas.currentChanged.connect(
            lambda _indice: self.atualizar_aba_atual()
        )

        layout_principal.addWidget(
            self.abas,
            1,
        )

        rodape = QHBoxLayout()

        self.mensagem = QLabel(
            "Selecione os filtros e atualize o relatório."
        )
        self.mensagem.setObjectName(
            "mensagem"
        )
        self.mensagem.setWordWrap(True)

        self.botao_exportar = QPushButton(
            "Exportar aba atual para CSV"
        )
        self.botao_exportar.setObjectName(
            "botaoPrimario"
        )
        self.botao_exportar.clicked.connect(
            self.exportar_aba_atual
        )

        rodape.addWidget(
            self.mensagem,
            1,
        )
        rodape.addWidget(
            self.botao_exportar
        )

        layout_principal.addLayout(rodape)

    def criar_filtros(self):
        frame = QFrame()
        frame.setObjectName("cartao")

        layout = QHBoxLayout(frame)
        layout.setContentsMargins(
            16,
            14,
            16,
            14,
        )
        layout.setSpacing(10)

        hoje = QDate.currentDate()

        self.data_inicial = QDateEdit(
            QDate(
                hoje.year(),
                1,
                1,
            )
        )
        self.data_inicial.setCalendarPopup(
            True
        )
        self.data_inicial.setDisplayFormat(
            "dd/MM/yyyy"
        )

        self.data_final = QDateEdit(hoje)
        self.data_final.setCalendarPopup(
            True
        )
        self.data_final.setDisplayFormat(
            "dd/MM/yyyy"
        )

        self.botao_atualizar = QPushButton(
            "Atualizar relatório"
        )
        self.botao_atualizar.setObjectName(
            "botaoPrimario"
        )
        self.botao_atualizar.clicked.connect(
            self.atualizar_aba_atual
        )

        layout.addWidget(
            QLabel("Período:")
        )
        layout.addWidget(
            QLabel("De")
        )
        layout.addWidget(
            self.data_inicial
        )
        layout.addWidget(
            QLabel("Até")
        )
        layout.addWidget(
            self.data_final
        )
        layout.addStretch()
        layout.addWidget(
            self.botao_atualizar
        )

        return frame

    def criar_aba_ativos(self):
        aba = QWidget()
        layout = QVBoxLayout(aba)
        layout.setContentsMargins(
            10,
            10,
            10,
            10,
        )

        topo = QHBoxLayout()

        titulo = QLabel(
            "Alunos ativos"
        )
        titulo.setObjectName(
            "tituloSecao"
        )

        self.pesquisa_ativos = QLineEdit()
        self.pesquisa_ativos.setPlaceholderText(
            "Pesquisar nome, CPF ou telefone"
        )
        self.pesquisa_ativos.returnPressed.connect(
            self.atualizar_ativos
        )

        self.resumo_ativos = QLabel(
            "0 aluno(s)"
        )
        self.resumo_ativos.setObjectName(
            "destaque"
        )

        topo.addWidget(titulo)
        topo.addStretch()
        topo.addWidget(
            self.pesquisa_ativos
        )
        topo.addWidget(
            self.resumo_ativos
        )

        self.tabela_ativos = self.criar_tabela(
            [
                "ID",
                "Nome",
                "CPF",
                "Telefone",
                "E-mail",
                "Plano",
                "Início",
                "Vencimento",
            ]
        )

        self.tabela_ativos.horizontalHeader().setSectionResizeMode(
            1,
            QHeaderView.ResizeMode.Stretch,
        )

        layout.addLayout(topo)
        layout.addWidget(
            self.tabela_ativos
        )

        return aba

    def criar_aba_inadimplentes(self):
        aba = QWidget()
        layout = QVBoxLayout(aba)
        layout.setContentsMargins(
            10,
            10,
            10,
            10,
        )

        topo = QHBoxLayout()

        titulo = QLabel(
            "Alunos inadimplentes"
        )
        titulo.setObjectName(
            "tituloSecao"
        )

        self.pesquisa_inadimplentes = QLineEdit()
        self.pesquisa_inadimplentes.setPlaceholderText(
            "Pesquisar nome, CPF ou plano"
        )
        self.pesquisa_inadimplentes.returnPressed.connect(
            self.atualizar_inadimplentes
        )

        self.resumo_inadimplentes = QLabel(
            "0 aluno(s) | R$ 0,00"
        )
        self.resumo_inadimplentes.setObjectName(
            "destaque"
        )

        topo.addWidget(titulo)
        topo.addStretch()
        topo.addWidget(
            self.pesquisa_inadimplentes
        )
        topo.addWidget(
            self.resumo_inadimplentes
        )

        self.tabela_inadimplentes = self.criar_tabela(
            [
                "ID",
                "Aluno",
                "CPF",
                "Telefone",
                "Plano",
                "Parcelas",
                "Vencimento mais antigo",
                "Total pendente",
            ]
        )

        self.tabela_inadimplentes.horizontalHeader().setSectionResizeMode(
            1,
            QHeaderView.ResizeMode.Stretch,
        )

        layout.addLayout(topo)
        layout.addWidget(
            self.tabela_inadimplentes
        )

        return aba

    def criar_aba_matriculas(self):
        aba = QWidget()
        layout = QVBoxLayout(aba)
        layout.setContentsMargins(
            10,
            10,
            10,
            10,
        )

        topo = QHBoxLayout()

        titulo = QLabel(
            "Matrículas por período"
        )
        titulo.setObjectName(
            "tituloSecao"
        )

        self.filtro_matricula = QComboBox()
        self.filtro_matricula.addItem(
            "Todas as situações",
            None,
        )
        self.filtro_matricula.addItem(
            "Ativas",
            "ativa",
        )
        self.filtro_matricula.addItem(
            "Vencidas",
            "vencida",
        )
        self.filtro_matricula.addItem(
            "Congeladas",
            "congelada",
        )
        self.filtro_matricula.addItem(
            "Encerradas",
            "encerrada",
        )
        self.filtro_matricula.currentIndexChanged.connect(
            self.atualizar_matriculas
        )

        self.resumo_matriculas = QLabel(
            "0 matrícula(s)"
        )
        self.resumo_matriculas.setObjectName(
            "destaque"
        )

        topo.addWidget(titulo)
        topo.addStretch()
        topo.addWidget(
            self.filtro_matricula
        )
        topo.addWidget(
            self.resumo_matriculas
        )

        self.tabela_matriculas = self.criar_tabela(
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

        self.tabela_matriculas.horizontalHeader().setSectionResizeMode(
            1,
            QHeaderView.ResizeMode.Stretch,
        )

        layout.addLayout(topo)
        layout.addWidget(
            self.tabela_matriculas
        )

        return aba

    def criar_aba_planos(self):
        aba = QWidget()
        layout = QVBoxLayout(aba)
        layout.setContentsMargins(
            10,
            10,
            10,
            10,
        )

        topo = QHBoxLayout()

        titulo = QLabel(
            "Planos mais vendidos no período"
        )
        titulo.setObjectName(
            "tituloSecao"
        )

        self.resumo_planos = QLabel(
            "0 matrícula(s)"
        )
        self.resumo_planos.setObjectName(
            "destaque"
        )

        topo.addWidget(titulo)
        topo.addStretch()
        topo.addWidget(
            self.resumo_planos
        )

        self.tabela_planos = self.criar_tabela(
            [
                "ID",
                "Plano",
                "Duração",
                "Quantidade vendida",
                "Valor contratado",
            ]
        )

        self.tabela_planos.horizontalHeader().setSectionResizeMode(
            1,
            QHeaderView.ResizeMode.Stretch,
        )

        layout.addLayout(topo)
        layout.addWidget(
            self.tabela_planos
        )

        return aba

    def criar_aba_financeiro(self):
        aba = QWidget()
        layout = QVBoxLayout(aba)
        layout.setContentsMargins(
            10,
            10,
            10,
            10,
        )

        resumo = QHBoxLayout()

        self.cartao_total = QLabel(
            "Total recebido\nR$ 0,00"
        )
        self.cartao_total.setObjectName(
            "destaque"
        )

        self.cartao_pix = QLabel(
            "Pix\nR$ 0,00"
        )
        self.cartao_pix.setObjectName(
            "destaque"
        )

        self.cartao_dinheiro = QLabel(
            "Dinheiro\nR$ 0,00"
        )
        self.cartao_dinheiro.setObjectName(
            "destaque"
        )

        self.cartao_quantidade = QLabel(
            "Pagamentos\n0"
        )
        self.cartao_quantidade.setObjectName(
            "destaque"
        )

        for cartao in (
            self.cartao_total,
            self.cartao_pix,
            self.cartao_dinheiro,
            self.cartao_quantidade,
        ):
            cartao.setAlignment(
                Qt.AlignmentFlag.AlignCenter
            )
            cartao.setMinimumHeight(65)
            resumo.addWidget(cartao)

        filtros = QHBoxLayout()

        self.filtro_forma_pagamento = QComboBox()
        self.filtro_forma_pagamento.addItem(
            "Todas as formas",
            None,
        )
        self.filtro_forma_pagamento.addItem(
            "Pix",
            "pix",
        )
        self.filtro_forma_pagamento.addItem(
            "Dinheiro",
            "dinheiro",
        )
        self.filtro_forma_pagamento.currentIndexChanged.connect(
            self.atualizar_financeiro
        )

        filtros.addStretch()
        filtros.addWidget(
            QLabel("Forma:")
        )
        filtros.addWidget(
            self.filtro_forma_pagamento
        )

        self.tabela_financeiro = self.criar_tabela(
            [
                "ID",
                "Data",
                "Aluno",
                "CPF",
                "Plano",
                "Competência",
                "Valor",
                "Forma",
                "Observação",
            ]
        )

        self.tabela_financeiro.horizontalHeader().setSectionResizeMode(
            2,
            QHeaderView.ResizeMode.Stretch,
        )
        self.tabela_financeiro.horizontalHeader().setSectionResizeMode(
            8,
            QHeaderView.ResizeMode.Stretch,
        )

        layout.addLayout(resumo)
        layout.addLayout(filtros)
        layout.addWidget(
            self.tabela_financeiro
        )

        return aba

    @staticmethod
    def criar_tabela(colunas):
        tabela = QTableWidget(
            0,
            len(colunas),
        )
        tabela.setHorizontalHeaderLabels(
            colunas
        )
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

        cabecalho = tabela.horizontalHeader()

        for indice in range(
            len(colunas)
        ):
            cabecalho.setSectionResizeMode(
                indice,
                QHeaderView
                .ResizeMode
                .ResizeToContents,
            )

        return tabela
    
    def periodo(self):
        inicio = (
            self.data_inicial
            .date()
            .toString("yyyy-MM-dd")
        )

        fim = (
            self.data_final
            .date()
            .toString("yyyy-MM-dd")
        )

        if inicio > fim:
            QMessageBox.warning(
                self,
                "StrongFit Academia",
                "A data inicial não pode ser "
                "posterior à data final.",
            )
            return None

        return inicio, fim

    def atualizar_tudo(self):
        atualizar_inadimplencia(
            self.conexao
        )

        self.atualizar_ativos()
        self.atualizar_inadimplentes()
        self.atualizar_matriculas()
        self.atualizar_planos()
        self.atualizar_financeiro()

    def atualizar_aba_atual(self):
        atualizar_inadimplencia(
            self.conexao
        )

        indice = self.abas.currentIndex()

        atualizadores = {
            0: self.atualizar_ativos,
            1: self.atualizar_inadimplentes,
            2: self.atualizar_matriculas,
            3: self.atualizar_planos,
            4: self.atualizar_financeiro,
        }

        atualizador = atualizadores.get(
            indice
        )

        if atualizador:
            atualizador()

    def atualizar_ativos(self):
        linhas = repo.listar_alunos_ativos(
            self.conexao,
            self.pesquisa_ativos.text(),
        )

        valores = []

        for aluno in linhas:
            valores.append(
                [
                    aluno["id"],
                    aluno["nome"],
                    aluno["cpf"] or "",
                    aluno["telefone"] or "",
                    aluno["email"] or "",
                    aluno["plano"] or "Sem plano",
                    self.formatar_data(
                        aluno["data_inicio"]
                    ),
                    self.formatar_data(
                        aluno["data_vencimento"]
                    ),
                ]
            )

        self.preencher_tabela(
            self.tabela_ativos,
            valores,
        )

        self.resumo_ativos.setText(
            f"{len(linhas)} aluno(s)"
        )

        self.mensagem.setText(
            "Relatório de alunos ativos atualizado."
        )

    def atualizar_inadimplentes(self):
        linhas = (
            repo.listar_alunos_inadimplentes(
                self.conexao,
                self.pesquisa_inadimplentes
                .text(),
            )
        )

        valores = []
        total = 0

        for aluno in linhas:
            total += float(
                aluno["total_pendente"] or 0
            )

            valores.append(
                [
                    aluno["id"],
                    aluno["nome"],
                    aluno["cpf"] or "",
                    aluno["telefone"] or "",
                    aluno["plano"],
                    aluno[
                        "mensalidades_atrasadas"
                    ],
                    self.formatar_data(
                        aluno[
                            "vencimento_mais_antigo"
                        ]
                    ),
                    self.formatar_moeda(
                        aluno["total_pendente"]
                    ),
                ]
            )

        self.preencher_tabela(
            self.tabela_inadimplentes,
            valores,
        )

        self.resumo_inadimplentes.setText(
            (
                f"{len(linhas)} aluno(s) | "
                f"{self.formatar_moeda(total)}"
            )
        )

        self.mensagem.setText(
            "Relatório de inadimplentes atualizado."
        )

    def atualizar_matriculas(self):
        periodo = self.periodo()

        if periodo is None:
            return

        inicio, fim = periodo

        linhas = repo.listar_matriculas_periodo(
            self.conexao,
            inicio,
            fim,
            self.filtro_matricula.currentData(),
        )

        valores = []

        for matricula in linhas:
            valores.append(
                [
                    matricula["id"],
                    matricula["aluno"],
                    matricula["cpf"] or "",
                    matricula["plano"],
                    self.formatar_data(
                        matricula["data_inicio"]
                    ),
                    self.formatar_data(
                        matricula[
                            "data_vencimento"
                        ]
                    ),
                    self.formatar_moeda(
                        matricula[
                            "valor_contratado"
                        ]
                    ),
                    matricula[
                        "situacao"
                    ].title(),
                ]
            )

        self.preencher_tabela(
            self.tabela_matriculas,
            valores,
        )

        self.resumo_matriculas.setText(
            f"{len(linhas)} matrícula(s)"
        )

        self.mensagem.setText(
            "Relatório de matrículas atualizado."
        )

    def atualizar_planos(self):
        periodo = self.periodo()

        if periodo is None:
            return

        inicio, fim = periodo

        linhas = repo.listar_planos_mais_vendidos(
            self.conexao,
            inicio,
            fim,
        )

        valores = []
        quantidade = 0

        for plano in linhas:
            quantidade += int(
                plano["quantidade_vendida"]
            )

            valores.append(
                [
                    plano["id"],
                    plano["plano"],
                    (
                        f"{plano['duracao_meses']} "
                        f"mês(es)"
                    ),
                    plano[
                        "quantidade_vendida"
                    ],
                    self.formatar_moeda(
                        plano["valor_contratado"]
                    ),
                ]
            )

        self.preencher_tabela(
            self.tabela_planos,
            valores,
        )

        self.resumo_planos.setText(
            f"{quantidade} matrícula(s)"
        )

        self.mensagem.setText(
            "Relatório de planos atualizado."
        )

    def atualizar_financeiro(self):
        periodo = self.periodo()

        if periodo is None:
            return

        inicio, fim = periodo

        linhas = repo.listar_financeiro_periodo(
            self.conexao,
            inicio,
            fim,
            self.filtro_forma_pagamento
            .currentData(),
        )

        resumo = repo.resumo_financeiro_periodo(
            self.conexao,
            inicio,
            fim,
        )

        valores = []

        for pagamento in linhas:
            valores.append(
                [
                    pagamento["id"],
                    self.formatar_data_hora(
                        pagamento[
                            "data_pagamento"
                        ]
                    ),
                    pagamento["aluno"],
                    pagamento["cpf"] or "",
                    pagamento["plano"],
                    pagamento["competencia"],
                    self.formatar_moeda(
                        pagamento["valor"]
                    ),
                    pagamento[
                        "forma_pagamento"
                    ].title(),
                    pagamento["observacao"] or "",
                ]
            )

        self.preencher_tabela(
            self.tabela_financeiro,
            valores,
        )

        self.cartao_total.setText(
            "Total recebido\n"
            + self.formatar_moeda(
                resumo["total_recebido"]
            )
        )

        self.cartao_pix.setText(
            "Pix\n"
            + self.formatar_moeda(
                resumo["total_pix"]
            )
        )

        self.cartao_dinheiro.setText(
            "Dinheiro\n"
            + self.formatar_moeda(
                resumo["total_dinheiro"]
            )
        )

        self.cartao_quantidade.setText(
            "Pagamentos\n"
            + str(
                resumo[
                    "quantidade_pagamentos"
                ]
            )
        )

        self.mensagem.setText(
            "Relatório financeiro atualizado."
        )

    @staticmethod
    def preencher_tabela(
        tabela,
        linhas,
    ):
        tabela.setRowCount(
            len(linhas)
        )

        for numero_linha, valores in enumerate(
            linhas
        ):
            for coluna, valor in enumerate(
                valores
            ):
                tabela.setItem(
                    numero_linha,
                    coluna,
                    QTableWidgetItem(
                        str(valor)
                    ),
                )

        tabela.clearSelection()
    
    
    def tabela_atual(self):
        tabelas = {
            0: (
                self.tabela_ativos,
                "alunos_ativos",
            ),
            1: (
                self.tabela_inadimplentes,
                "alunos_inadimplentes",
            ),
            2: (
                self.tabela_matriculas,
                "matriculas",
            ),
            3: (
                self.tabela_planos,
                "planos_mais_vendidos",
            ),
            4: (
                self.tabela_financeiro,
                "financeiro",
            ),
        }

        return tabelas.get(
            self.abas.currentIndex()
        )

    def exportar_aba_atual(self):
        resultado = self.tabela_atual()

        if resultado is None:
            return

        tabela, nome_base = resultado

        if tabela.rowCount() == 0:
            QMessageBox.warning(
                self,
                "StrongFit Academia",
                "Não existem dados para exportar.",
            )
            return

        periodo = self.periodo()

        if periodo is None:
            return

        inicio, fim = periodo

        nome_sugerido = (
            f"{nome_base}_{inicio}_{fim}.csv"
        )

        caminho, _ = QFileDialog.getSaveFileName(
            self,
            "Exportar relatório",
            nome_sugerido,
            "Arquivo CSV (*.csv)",
        )

        if not caminho:
            return

        if not caminho.lower().endswith(
            ".csv"
        ):
            caminho += ".csv"

        try:
            with open(
                caminho,
                "w",
                newline="",
                encoding="utf-8-sig",
            ) as arquivo:
                escritor = csv.writer(
                    arquivo,
                    delimiter=";",
                )

                cabecalhos = []

                for coluna in range(
                    tabela.columnCount()
                ):
                    item = (
                        tabela.horizontalHeaderItem(
                            coluna
                        )
                    )

                    cabecalhos.append(
                        item.text()
                        if item
                        else ""
                    )

                escritor.writerow(
                    cabecalhos
                )

                for linha in range(
                    tabela.rowCount()
                ):
                    valores = []

                    for coluna in range(
                        tabela.columnCount()
                    ):
                        item = tabela.item(
                            linha,
                            coluna,
                        )

                        valores.append(
                            item.text()
                            if item
                            else ""
                        )

                    escritor.writerow(
                        valores
                    )

        except OSError as erro:
            QMessageBox.critical(
                self,
                "StrongFit Academia",
                (
                    "Não foi possível exportar "
                    f"o relatório:\n{erro}"
                ),
            )
            return

        self.mensagem.setText(
            f"Relatório exportado para {caminho}"
        )

        QMessageBox.information(
            self,
            "Exportação concluída",
            (
                "O relatório foi exportado "
                "com sucesso."
            ),
        )

    @staticmethod
    def formatar_data(valor):
        if not valor:
            return ""

        partes = (
            str(valor)
            .split(" ")[0]
            .split("-")
        )

        if len(partes) != 3:
            return str(valor)

        return "/".join(
            reversed(partes)
        )

    @staticmethod
    def formatar_data_hora(valor):
        if not valor:
            return ""

        texto = str(valor)
        data, _, hora = texto.partition(
            " "
        )

        partes = data.split("-")

        if len(partes) == 3:
            data = "/".join(
                reversed(partes)
            )

        return (
            f"{data} {hora[:5]}"
            .strip()
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
import sys

from PySide6.QtWidgets import QApplication

from strongfit.db import (
    conectar,
    preparar_banco,
)
from strongfit.ui.janela_principal import (
    JanelaPrincipal,
)


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    conexao = conectar()
    preparar_banco(conexao)

    janela = JanelaPrincipal(conexao)
    janela.show()

    codigo = app.exec()

    conexao.close()

    return codigo


if __name__ == "__main__":
    sys.exit(main())
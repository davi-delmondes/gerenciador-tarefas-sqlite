from app import utils, config, interface, database

import os
import csv

# Fluxo de exportação do relatório CSV.
def exportar_relatorio_csv() -> bool:
    interface.mostrar_cabecalho("EXPORTAR RELATÓRIO CSV")

    tarefas = database.buscar_todas_tarefas()

    if tarefas is None:
        print("[ERRO] Não foi possível carregar as tarefas para exportação.")
        utils.pausar_e_limpar()
        return False
    
    if not tarefas:
        print("[AVISO] Nenhuma tarefa cadastrada para exportar.")
        utils.pausar_e_limpar()
        return False

    try:
        caminho_pasta = config.PASTA_EXPORTS
        nome_arquivo = config.NOME_RELATORIO
        caminho_completo = os.path.join(caminho_pasta, nome_arquivo)

        if not os.path.exists(caminho_pasta):
            os.makedirs(caminho_pasta)

        with open(caminho_completo, "w", newline="", encoding="utf-8-sig") as arquivo:
            escritor = csv.writer(arquivo, delimiter=";")
            escritor.writerow(["ID", "Título", "Descrição", "Status", "Data de criação"])
            escritor.writerows(tarefas)
    
    except (OSError, csv.Error) as ex:
        print(f"\n[ERRO] Não foi possível gerar o relatório CSV: {ex}")
        utils.pausar_e_limpar()
        return False
    
    print("[OK] Relatório exportado com sucesso!")
    print(f"\nArquivo gerado: {caminho_completo}")
    print(f"Total de tarefas exportadas: {len(tarefas)}")
    utils.pausar_e_limpar()
    return True
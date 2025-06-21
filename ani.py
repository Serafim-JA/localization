# ani.py / monitora de serviços.

import os  
import sys
import subprocess
import argparse # argumentos referente a linha de comandos.
import logging # logs do próprio script
import requests
import psycopg2

# ===================================================================================================
# Configurações Globais.
# ===================================================================================================

LOG_FILE = "monitor_serviços.log"
DATABASE_CONNECTION_STRING = "..." # Ex: "dbname=logs user=admin password=admin host=localhost port=5432"
GITHUB_API_URL = "https://api.github.com"
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "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") # Pegar sempre da variável de ambiente.
GITHUB_REPO_OWNER = "Serafim-JA"
GITHUB_REPO_NAME = "ANI"

# Configurar logging (para o mesmo script)
logging.basicConfig(filemode=LOG_FILE, level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# ===================================================================================================
# Funções de Interação com Base de Dados/Logs.
# ===================================================================================================

def consultar_logs_area_vpn(area, vpn):
    """Consulta logs específicos da base de dados ou arquivos."""
    try:
        # Exemplo para PostgreSQL
        # conn = psycopg2.connect(DATABASE_CONNECTION_STRING)
        # return conn
        logging.info(f"Consultando logs para Área: {area}, VPN: {vpn}")
        # Simulação: Retorna algumas linhas de log de exemplo.
        simulated_logs = [
            "2025-06-21 10:00:00 INFO - VPN-X: Conexão estabelecida.",
            "2025-06-21 10:05:15 ERROR - VPN-Y: Falha na autenticação do usuário Z.",
            "2025-06-21 10:10:30 WARNING - AREA-A: Sistema de pagamentos com latência."
        ]
        # Aqui iria a lógica real de consulta ao DB ou leitura de arquivos.
        return simulated_logs
def identificar_falhas_em_logs(logs):
    """Analisa logs e identifica padrões de falha."""
    falhas_enconstradas = []
    for line in logs:
        if "ERROR" in line or "Falha" in line:
            falhas_enconstradas.append(f"FALHA DETECTADA: {line.strip()}")
    return falhas_enconstradas

# ===================================================================================================
# Funções de Monitoramento e Controle de Serviços (Windowns).
# ===================================================================================================

def verificar_status_servico(nome_servico):
    """Verifica o status de um serviço Windowns"""
    try:
        # Comando PowerShell para obter status de serviço
        command = ['powershell.exe', '-command', f'Get-Service -Name "{nome_servico}" | Select-Object Status']
        result = subprocess.run(command, capture_output=True, text=True, check=True, encoding='utf-8')
        output = result.stdout.strip().lower()
        if "running" in output:
            return "Em execução"
        elif "stopped" in output:
            return "Parado"
        else:
            return "Desconhecido"
    except subprocess.CalledProcessError as e:
        logging.error(f"Erro ao verificar status do serviço '{nome_servico}': {e.stderr}")
        return "Erro ao verificar serviço"
    except FileNotFoundError:
        logging.error("PowerShell não localizado. Certifique-se de que o script está sendo executado no Windowns.")
        return "Erro (PowerShell)"
    except Exception as e:
        logging.error(f"Erro inesperado ao verificar serviço '{nome_servico}': {e}")
        return "Erro inesperado"
    
def reiniciar_servico(nome_servico):
    """Reinicia um serviço Windowns (Necessita de privilégios de administrador)"""
    logging.info(f"Tentando reiniciar o serviço: {nome_servico}")
    try:
        # Comando PowerShell para reiniciar serviço
        command = ['powershell.exe', '-command', f'Restart-Service -Name "{nome_servico}" -Force']
        # 'check=True' levantará uma exceção se o comando retornar um código de erro
        result = subprocess.run(command, capture_output=True, text=True, check=True, encoding='utf-8')
        logging.info(f"Serviço '{nome_servico}' reiniciado com sucesso: {result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError as e:
        logging.error(f"Erro ao reiniciar o serviço '{nome_servico}': {e.stderr}")
        print(f"ERRO: Não foi possível reiniciar o serviço '{nome_servico}'. Verifique as permissões de administrador.")
        return False
    except FileNotFoundError:
        logging.error("PowerShell não localizado. Certifique-se de que o script está sendo executado no Windowns.")
        print("ERRO: PowerShell não localizado. Este script precisa do PowerShell para gerenciar serviços.")
        return False
    except Exception as e:
        logging.error(f"Erro inesperado ao reiniciar serviço '{nome_servico}': {e}")
        print("ERRO: Erro inesperado ao reiniciar serviço '{nome_servico}'.")
        return False

# ===================================================================================================
# Funções de Integração com Github.
# ===================================================================================================

def criar_github_issue(titulo, corpo):
    """Cria uma nova issue no GitHub."""
    if not GITHUB_TOKEN:
        logging.error("GITHUB_TOKEN não configurado. Não é possível criar issues no GitHub.")
        print("Aviso: Variável de ambiente GITHUB_TOKEN não configurada. Não é possível criar issues.")
        return False
    url = f"{GITHUB_API_URL}/repos/{GITHUB_REPO_OWNER}/{GITHUB_REPO_NAME}/issues"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    data = {
        "title": titulo,
        "body": corpo
    }
    try:
        # response = requests.post(url, headers=headers, json=data)
        # response.raise_for_status() # Lança exceção para códigos de status HTTP 4xx/5xx
        logging.info(f"Issue '{titulo}' criada no GitHub com sucesso.")
        # print(f"Issue criado com sucesso: {response.json()['html_url']}")
        print(f"Issue criado com sucesso: '{titulo}'")
        return True
    except Exception as e: # requests.exceptions.RequestException as e:
        logging.error(f"Erro ao criar issue no GitHub: {e}")
        print(f"Erro ao criar issue no GitHub: {e}")
        return False
    
# ===================================================================================================
# Funções de Integração com Github.
# ===================================================================================================

def exibir_menu():
    """Exibe o menu principal do programa."""
    print("\n" + "+"*50)
    print("           Monitor de Serviços       ")
    print("+"*50)
    print("1. Consultar Logs por Área/VPN")
    print("2. Verificar Status de Serviço")
    print("3. Reiniciar Serviço")
    print("4. Relatar Falha no GitHub")
    print("5 Sair")
    print("+"*50)
    
def main():
    """Função principal do programa."""
    logging.info("Programa iniciado.")
    
    # Exemplo de uso de argumentos de linha de comando para automação
    parser = argparse.ArgumentParser(description="Ferramenta de monitoramente e gerenciamentos de serviços.")
    parser.add_argument("--action", help= "Ação a executar (consultar_logs, verificar_servico, reiniciar_servico, relatar_falha)", choices=['consultar_logs', 'verificar_servicos', 'reiniciar_servco', 'relatar_falha'])
    parser.add_argument("--area", help="Área para consulta de logs")
    parser.add_argument("--vpn", help="VPN para consulta de logs")
    parser.add_argument("--service", help="Nome do serviço para verificar/reiniciar")
    parser.add_argument("--issue_title", help="Título da issue para o GitHub")
    parser.add_argument("--issue_body", help="Corpo da issue para o GitHub")
    
    args = parser.parse_args()
    
    # Se uma ação for especificada na linha de comando, execute e sai
    if args.action:
        if args.action == "consultar_logs" and args.area and args.vpn:
            logs = consultar_logs_area_vpn(args.area, args.vpn)
            if logs:
                falhas = identificar_falhas_em_logs(logs)
                if falhas:
                    for f in falhas:
                        print(f)
                else:
                    print("Nenhuma falha detectada nos logs consultados.")
            else:
                print("Nenhum log para analisar.")
        elif args.action == "verificar_servico" and args.service:
            status = vericar_status_servico(args.service)
            print(f"Status do serviço '{args.service}': {status}")
        elif args.action == "reiniciar_servico" and args.service:
            if reiniciar_servico(args.service):
                print(f"Comando de reinício para '{args.service}' enviado.")
        elif args.action == "relatar_falha" and args.issue_title and args.issue_body:
            criar_github_issue(args.issue_title, args.issue_body)
        else:
            print("Argumentos insuficientes ou inválidos para a ação especificada.")
        sys.exit(0) # Sai após a execução da ação da linha de comando
        
# Se nenhuma ação for especificado, exibe o menu interativo
while True:
    exibir_menu()
    choice = input("Digite sua opção: ")
    
    if choice == '1':
        area = input("Digite a área (ex: Pagamentos): ")
        vpn = input("Digite a VPN (ex: Rede_Interna): ")
        logs = consultar_logs_area_vpn(area, vpn)
        if logs:
            print("\n--- Logs Consultados ---")
            for log in logs:
                print(log)
            falhas = identificar_falhas_em_logs(logs)
            if falhas:
                print("\n--- Falhas Identificadas ---")
                for f in falhas:
                    print(f)
            else:
                print("Nehuma falha detectada.")
        else:
            print("Nenhum log retornado.")
    elif choice == '1':
        service_name = input("Digite o nome do serviço (ex: Spooler): ")
        status = verificar_status_servico(service_name)
        print(f"Status do serviço '{service_name}': {status}")
    elif choice == '3':
        service_name = input("Digite o nome do serviço a reiniciar (ex: Spooler). ATENÇÃO: Requer privilégios de administrador: ")
        reiniciar_servico(service_name)
    elif choice == '4':
        issue_title = input("Digite o título da Issue no GitHub: ")
        issue_body = input("Digite o corpo da Issue: ")
        criar_github_issue(issue_title, issue_body)
    elif choice == '5':
        print("Saindo do programa. Até breve!")
        logging.info("Programa finalizado.")
        break
    else:
        print("Opção inválida. Por favor, tente novamente.")
    input("Pressione Enter para continuar...") # Pausa
    
if __name__ == "__main__":
    main()

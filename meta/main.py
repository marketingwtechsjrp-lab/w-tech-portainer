"""
Interface de linha de comando para o agente Meta Ads multi-conta.
Uso: python main.py
"""
import os
import sys
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.table import Table
from rich.markdown import Markdown
from rich import print as rprint

import accounts as acc
from meta_api import MetaAdsAPI
from agent import MetaAdsAgent

load_dotenv()
console = Console()


# ─── GERENCIAMENTO DE CONTAS ──────────────────────────────────────────────────

def cmd_add_account():
    """Cadastra uma nova conta de cliente."""
    console.print("\n[bold cyan]Cadastrar nova conta de cliente[/bold cyan]\n")
    slug = Prompt.ask("Identificador único (ex: empresa-abc)").strip().lower().replace(" ", "-")
    name = Prompt.ask("Nome do cliente/empresa")
    
    import business_profiles
    profiles = business_profiles.list_profiles()
    console.print("\n[bold]Selecione o nicho da empresa:[/bold]")
    niche_keys = list(profiles.keys())
    for i, key in enumerate(niche_keys, 1):
        p = profiles[key]
        console.print(f"  {i}. {p['icon']} [cyan]{p['name']}[/cyan] - {p['description']}")
    niche_idx = Prompt.ask("Número do nicho", default=str(len(niche_keys)))
    try:
        niche = niche_keys[int(niche_idx)-1]
    except:
        niche = "custom"
        
    ad_account_id = Prompt.ask("Ad Account ID (ex: act_123456789 ou apenas 123456789)")
    access_token = Prompt.ask("Access Token da Meta API", password=True)
    notes = Prompt.ask("Observações (opcional)", default="")

    acc.add_account(slug, name, access_token, ad_account_id, notes, niche)
    console.print(f"\n[green]✓ Conta '[bold]{name}[/bold]' cadastrada como '[bold]{slug}[/bold]' no nicho {profiles[niche]['name']}[/green]\n")


def cmd_list_accounts():
    """Lista todas as contas cadastradas."""
    all_accounts = acc.list_accounts()
    if not all_accounts:
        console.print("\n[yellow]Nenhuma conta cadastrada ainda.[/yellow]")
        console.print("Use [bold]accounts[/bold] → [bold]Adicionar conta[/bold] para começar.\n")
        return

    table = Table(title="Contas de Clientes", show_lines=True)
    table.add_column("Slug", style="cyan", no_wrap=True)
    table.add_column("Nome", style="bold")
    table.add_column("Nicho", style="magenta")
    table.add_column("Ad Account ID", style="dim")
    table.add_column("Observações")

    import business_profiles
    profiles = business_profiles.list_profiles()

    for slug, data in all_accounts.items():
        niche_key = data.get("niche", "custom")
        niche_name = profiles.get(niche_key, {}).get("name", "Desconhecido")
        
        table.add_row(
            slug,
            data["name"],
            niche_name,
            data["ad_account_id"],
            data.get("notes", ""),
        )
    console.print(table)


def cmd_remove_account():
    """Remove uma conta."""
    all_accounts = acc.list_accounts()
    if not all_accounts:
        console.print("[yellow]Nenhuma conta cadastrada.[/yellow]")
        return

    slugs = list(all_accounts.keys())
    console.print("\nContas disponíveis:", ", ".join(slugs))
    slug = Prompt.ask("Slug da conta a remover")
    if slug not in all_accounts:
        console.print(f"[red]Conta '{slug}' não encontrada.[/red]")
        return
    if Confirm.ask(f"Confirma remoção de '{all_accounts[slug]['name']}'?"):
        acc.remove_account(slug)
        console.print(f"[green]✓ Conta '{slug}' removida.[/green]")


def select_account() -> tuple[str, dict] | None:
    """Exibe menu de seleção de conta e retorna (slug, credentials)."""
    all_accounts = acc.list_accounts()
    if not all_accounts:
        console.print(
            "\n[yellow]Nenhuma conta cadastrada. "
            "Use o menu de contas para adicionar uma.[/yellow]\n"
        )
        return None

    console.print("\n[bold]Selecione a conta do cliente:[/bold]\n")
    slugs = list(all_accounts.keys())
    for i, (slug, data) in enumerate(all_accounts.items(), 1):
        console.print(f"  [cyan]{i}.[/cyan] [bold]{data['name']}[/bold] ({slug})")

    console.print()
    choice = Prompt.ask("Número ou slug", default="1")

    # Aceita número ou slug direto
    if choice.isdigit():
        idx = int(choice) - 1
        if 0 <= idx < len(slugs):
            slug = slugs[idx]
        else:
            console.print("[red]Opção inválida.[/red]")
            return None
    elif choice in all_accounts:
        slug = choice
    else:
        console.print(f"[red]Conta '{choice}' não encontrada.[/red]")
        return None

    creds = acc.get_account_credentials(slug)
    return slug, creds


# ─── SESSÃO DE CHAT ───────────────────────────────────────────────────────────

def run_chat_session(agent: MetaAdsAgent, account_name: str):
    """Loop principal de conversa com o agente."""
    console.print(Panel(
        f"[bold green]Agente Meta Ads ativo[/bold green]\n"
        f"Conta: [bold]{account_name}[/bold]\n\n"
        "[dim]Comandos especiais:\n"
        "  /novo    — Nova conversa (limpa histórico)\n"
        "  /conta   — Trocar de conta\n"
        "  /sair    — Sair[/dim]",
        title="Meta Ads AI",
        border_style="green",
    ))

    while True:
        try:
            user_input = Prompt.ask("\n[bold blue]Você[/bold blue]").strip()
        except (KeyboardInterrupt, EOFError):
            console.print("\n[dim]Saindo...[/dim]")
            break

        if not user_input:
            continue

        if user_input.lower() in ("/sair", "/exit", "/quit"):
            console.print("[dim]Até logo![/dim]")
            break
        elif user_input.lower() in ("/novo", "/new", "/reset"):
            agent.reset_conversation()
            console.print("[dim]Histórico limpo. Nova conversa iniciada.[/dim]")
            continue
        elif user_input.lower() in ("/conta", "/account"):
            return "SWITCH_ACCOUNT"

        console.print("\n[bold green]Agente[/bold green] [dim]pensando...[/dim]")
        try:
            response = agent.chat(user_input)
            console.print()
            console.print(Markdown(response))
        except Exception as e:
            console.print(f"\n[red]Erro: {e}[/red]")

    return "EXIT"


# ─── MENU DE CONTAS ───────────────────────────────────────────────────────────

def accounts_menu():
    """Menu de gerenciamento de contas."""
    while True:
        console.print("\n[bold cyan]Gerenciamento de Contas[/bold cyan]\n")
        console.print("  1. Listar contas")
        console.print("  2. Adicionar conta")
        console.print("  3. Remover conta")
        console.print("  4. Voltar\n")

        choice = Prompt.ask("Opção", default="4")
        if choice == "1":
            cmd_list_accounts()
        elif choice == "2":
            cmd_add_account()
        elif choice == "3":
            cmd_remove_account()
        else:
            break


# ─── MAIN ─────────────────────────────────────────────────────────────────────

def main():
    # Verifica ANTHROPIC_API_KEY
    if not os.getenv("ANTHROPIC_API_KEY"):
        console.print("[red]ANTHROPIC_API_KEY não configurada.[/red]")
        console.print("Crie um arquivo .env com sua chave Anthropic.")
        sys.exit(1)

    console.print(Panel(
        "[bold]Meta Ads AI[/bold] — Agente inteligente para gestão de anúncios\n"
        "[dim]Sistema multi-conta para agências de marketing[/dim]",
        border_style="blue",
    ))

    while True:
        console.print("\n[bold]Menu Principal[/bold]\n")
        console.print("  1. Iniciar sessão (escolher conta)")
        console.print("  2. Gerenciar contas")
        console.print("  3. Sair\n")

        choice = Prompt.ask("Opção", default="1")

        if choice == "3":
            console.print("[dim]Até logo![/dim]")
            break
        elif choice == "2":
            accounts_menu()
            continue
        elif choice == "1":
            result = select_account()
            if not result:
                continue
            slug, creds = result

            # Inicializa API e agente
            with console.status(f"Conectando à conta [bold]{creds['name']}[/bold]..."):
                try:
                    api = MetaAdsAPI(
                        access_token=creds["access_token"],
                        ad_account_id=creds["ad_account_id"],
                    )
                    # Testa a conexão
                    api.get_account_overview()
                except Exception as e:
                    console.print(f"\n[red]Erro ao conectar: {e}[/red]")
                    console.print("[dim]Verifique o token de acesso e o Ad Account ID.[/dim]")
                    continue

            agent = MetaAdsAgent(api, creds["name"], creds.get("niche", "custom"))
            action = run_chat_session(agent, creds["name"])

            if action == "EXIT":
                break
            # Se SWITCH_ACCOUNT, volta ao menu principal para selecionar nova conta


if __name__ == "__main__":
    main()

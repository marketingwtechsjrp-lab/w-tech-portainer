import json
import os
from pathlib import Path
from typing import Optional
from openai import OpenAI

from meta_api import MetaAdsAPI
import business_profiles
import settings

MEMORY_DIR = Path(__file__).parent / "memory"

# Converte as defines de ferramentas de Anthropic para o formato OpenAI
def build_tools(api: MetaAdsAPI) -> list[dict]:
    # Definição original
    anthropic_tools = [
        {
            "name": "get_account_overview",
            "description": "Retorna um resumo geral da conta de anúncios: status, moeda, timezone, gasto total e saldo.",
            "input_schema": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
        {
            "name": "get_campaigns",
            "description": "Lista campanhas da conta com informações de orçamento e status.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "status_filter": {
                        "type": "string",
                        "enum": ["ACTIVE", "PAUSED", "DELETED", "ARCHIVED", "ALL"],
                        "description": "Filtro de status das campanhas. Padrão: ACTIVE.",
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Máximo de campanhas a retornar (1-100). Padrão: 25.",
                    },
                },
                "required": [],
            },
        },
        {
            "name": "get_adsets",
            "description": "Lista adsets (conjuntos de anúncios). Pode filtrar por campanha.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "campaign_id": {
                        "type": "string",
                        "description": "ID da campanha para filtrar adsets. Opcional.",
                    },
                    "status_filter": {
                        "type": "string",
                        "enum": ["ACTIVE", "PAUSED", "DELETED", "ARCHIVED", "ALL"],
                    },
                    "limit": {"type": "integer"},
                },
                "required": [],
            },
        },
        {
            "name": "get_ads",
            "description": "Lista anúncios individuais. Pode filtrar por adset ou campanha.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "adset_id": {"type": "string", "description": "Filtrar por adset."},
                    "campaign_id": {"type": "string", "description": "Filtrar por campanha."},
                    "status_filter": {
                        "type": "string",
                        "enum": ["ACTIVE", "PAUSED", "DELETED", "ARCHIVED", "ALL"],
                    },
                    "limit": {"type": "integer"},
                },
                "required": [],
            },
        },
        {
            "name": "get_insights",
            "description": (
                "Busca métricas de performance: impressões, alcance, cliques, CTR, CPM, CPC, "
                "gasto, ROAS, conversões e métricas de vídeo. Essencial para análises e relatórios."
            ),
            "input_schema": {
                "type": "object",
                "properties": {
                    "object_id": {
                        "type": "string",
                        "description": "ID específico (campanha, adset ou ad). Se omitido, puxa dados de toda a conta.",
                    },
                    "level": {
                        "type": "string",
                        "enum": ["account", "campaign", "adset", "ad"],
                        "description": "Nível de agregação.",
                    },
                    "date_preset": {
                        "type": "string",
                        "enum": ["today", "yesterday", "last_7d", "last_14d", "last_30d", "last_month", "this_month", "last_quarter", "this_year"],
                        "description": "Período predefinido.",
                    },
                },
                "required": [],
            },
        },
        {
            "name": "create_campaign",
            "description": "Cria uma nova campanha. Sempre inicia com status PAUSED por segurança.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "objective": {
                        "type": "string",
                        "enum": [
                            "OUTCOME_AWARENESS", "OUTCOME_TRAFFIC", "OUTCOME_ENGAGEMENT",
                            "OUTCOME_LEADS", "OUTCOME_APP_PROMOTION", "OUTCOME_SALES",
                        ],
                    },
                    "daily_budget": {"type": "integer", "description": "Centavos da moeda local. Ex 30 euros/dia -> 3000"},
                    "start_time": {"type": "string", "description": "Formato UTC ISO"},
                },
                "required": ["name", "objective"],
            },
        },
        {
            "name": "create_adset",
            "description": "Cria um adset (conjunto de anúncios).",
            "input_schema": {
                "type": "object",
                "properties": {
                    "campaign_id": {"type": "string", "description": "ID da campanha pai."},
                    "name": {"type": "string"},
                    "optimization_goal": {
                        "type": "string",
                        "enum": [
                            "LINK_CLICKS", "IMPRESSIONS", "REACH", "LEAD_GENERATION",
                            "OFFSITE_CONVERSIONS", "LANDING_PAGE_VIEWS", "VIDEO_VIEWS",
                            "ENGAGED_USERS", "APP_INSTALLS", "QUALITY_LEAD",
                        ],
                    },
                    "billing_event": {
                        "type": "string",
                        "enum": ["IMPRESSIONS", "LINK_CLICKS"],
                    },
                    "daily_budget": {
                        "type": "integer",
                        "description": "Orçamento diário em centavos. OBRIGATÓRIO se não houver lifetime_budget. Ex: R$30/dia = 3000, R$50/dia = 5000.",
                    },
                    "lifetime_budget": {"type": "integer", "description": "Orçamento total do período em centavos. Use daily_budget OU lifetime_budget."},
                    "targeting": {
                        "type": "object",
                        "description": (
                            "Segmentação geográfica, idade. Ex: {"
                            '"geo_locations": {"countries": ["BR"]}, '
                            '"age_min": 25, "age_max": 55}'
                        ),
                    },
                    "status": {
                        "type": "string",
                        "enum": ["PAUSED", "ACTIVE"],
                    },
                },
                "required": ["campaign_id", "name", "optimization_goal", "billing_event"],
            },
        },
        {
            "name": "create_ad",
            "description": "Cria um anúncio. Requer um creative_id existente ou um creative_spec completo.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "adset_id": {"type": "string", "description": "Adset pai"},
                    "name": {"type": "string"},
                    "creative_id": {"type": "string", "description": "Usar criativo existente"},
                    "creative_spec": {"type": "object", "description": "Criar novo"},
                    "status": {"type": "string", "enum": ["PAUSED", "ACTIVE"]}
                },
                "required": ["adset_id", "name"]
            }
        },
        {
            "name": "update_campaign_status",
            "description": "Ativa, pausa, arquiva ou deleta uma campanha.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "campaign_id": {"type": "string"},
                    "status": {
                        "type": "string",
                        "enum": ["ACTIVE", "PAUSED", "ARCHIVED", "DELETED"],
                    },
                },
                "required": ["campaign_id", "status"],
            },
        },
        {
            "name": "get_pages",
            "description": "Lista todas as páginas do Facebook que você gerencia (necessário para AdSets/Ads).",
            "input_schema": {"type": "object", "properties": {}},
        },
        {
            "name": "get_lead_gen_forms",
            "description": "Lista os formulários de Leads de uma página específica.",
            "input_schema": {
                "type": "object",
                "properties": {"page_id": {"type": "string"}},
                "required": ["page_id"]
            },
        },
        {
            "name": "update_adset_status",
            "description": "Ativa ou pausa adset.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "adset_id": {"type": "string"},
                    "status": {"type": "string", "enum": ["ACTIVE", "PAUSED", "ARCHIVED", "DELETED"]}
                },
                "required": ["adset_id", "status"]
            }
        },
        {
            "name": "update_ad_status",
            "description": "Ativa ou pausa anúncio.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "ad_id": {"type": "string"},
                    "status": {"type": "string", "enum": ["ACTIVE", "PAUSED", "ARCHIVED", "DELETED"]}
                },
                "required": ["ad_id", "status"]
            }
        },
    ]

    # Convert to OpenAI tool format
    openai_tools = []
    for tool in anthropic_tools:
        openai_tools.append({
            "type": "function",
            "function": {
                "name": tool["name"],
                "description": tool["description"],
                "parameters": tool["input_schema"]
            }
        })
    return openai_tools


def execute_tool(tool_name: str, tool_input: dict, api: MetaAdsAPI) -> str:
    """Executa a ferramenta solicitada pelo LLM e retorna o resultado como string."""
    try:
        if tool_name == "get_account_overview":
            result = api.get_account_overview()
        elif tool_name == "get_campaigns":
            result = api.get_campaigns(**tool_input)
        elif tool_name == "get_adsets":
            result = api.get_adsets(**tool_input)
        elif tool_name == "get_ads":
            result = api.get_ads(**tool_input)
        elif tool_name == "get_insights":
            result = api.get_insights(**tool_input)
        elif tool_name == "create_campaign":
            result = api.create_campaign(**tool_input)
        elif tool_name == "create_adset":
            result = api.create_adset(**tool_input)
        elif tool_name == "create_ad":
            result = api.create_ad(**tool_input)
        elif tool_name == "update_campaign_status":
            result = api.update_campaign_status(**tool_input)
        elif tool_name == "update_adset_status":
            result = api.update_adset_status(**tool_input)
        elif tool_name == "get_pages":
            result = api.get_pages()
        elif tool_name == "get_lead_gen_forms":
            result = api.get_lead_gen_forms(**tool_input)
        elif tool_name == "update_ad_status":
            result = api.update_ad_status(**tool_input)
        else:
            return f"Ferramenta desconhecida: {tool_name}"

        return json.dumps(result, ensure_ascii=False, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)


BASE_SYSTEM_PROMPT = """Você é um AGENTE EXECUTOR MESTRE em Meta Ads.
Seu objetivo é ser 100% autônomo. NUNCA diga que o usuário precisa criar algo manualmente se você tiver ferramentas para isso.

**REGRAS DE EXECUÇÃO SEQUENCIAL (OBRIGATÓRIO):**
1. Se o usuário pedir uma 'campanha completa', você deve:
   a) Chamar `create_campaign` e obter o ID.
   b) IMEDIATAMENTE chamar `create_adset` usando esse ID (pode chamar múltiplas vezes para vários conjuntos).
   c) IMEDIATAMENTE chamar `create_ad` para cada conjunto criado.
2. Não espere confirmação entre os passos. Faça tudo em uma única sequência de pensamento/ferramentas.
3. Para Lead Ads: Use `get_pages` e `get_lead_gen_forms` para achar o formulário correto antes de criar o Ad. Se não achar, crie o Ad assim mesmo com um placeholder ou avise após criar a estrutura.
4. Sempre crie tudo como 'PAUSED' por segurança.
5. Use Markdown para relatar o que foi construído com os IDs reais gerados.

**REGRAS DE ORÇAMENTO (CRÍTICO):**
- Ao criar um Adset com `create_adset`, SEMPRE informe `daily_budget` em centavos (ex: R$30/dia = 3000, R$50/dia = 5000).
- Se o usuário não especificar o orçamento, use 3000 (R$30/dia) como padrão seguro.
- Se a ferramenta retornar erro de orçamento, tente novamente com `daily_budget: 3000`.

**REGRAS DE CRIATIVO (CRÍTICO):**
- Para criar um anúncio (`create_ad`), você PRECISA de um `page_id` da página do Facebook do cliente.
- SEMPRE chame `get_pages` antes de criar o primeiro Ad para obter o `page_id` correto.
- O `creative_spec` deve conter: `{"name": "...", "object_story_spec": {"page_id": "ID_DA_PAGINA", "link_data": {"link": "URL", "message": "Texto", "name": "Título"}}}`
- Se não houver imagem disponível, crie o anúncio sem `image_hash` (criativo de texto/link simples)."""

class MetaAdsAgent:
    def __init__(self, api: MetaAdsAPI, account_name: str, niche: str = "custom", slug: str = ""):
        self.api = api
        self.account_name = account_name
        self.niche = niche
        self.slug = slug
        
        provider = settings.get_setting("ai_provider", "openrouter")
        api_key = settings.get_setting("api_key", "")
        self.provider = provider
        self.api_key = api_key
        self.model = settings.get_setting("model", "anthropic/claude-3.5-sonnet:beta")
        
        if provider == "openrouter":
            base_url = "https://openrouter.ai/api/v1"
        else:
            base_url = "https://api.openai.com/v1"

        self.client = OpenAI(
            base_url=base_url,
            api_key=api_key or "sk-invalid", 
        )
        self.tools = build_tools(api)

        profile = business_profiles.get_profile(self.niche)
        self.profile_name = profile["name"]
        
        custom_prompt = settings.get_setting("custom_prompt", "")
        knowledge_base = settings.get_setting("knowledge_base", "")
        
        addon = business_profiles.get_system_prompt_addon(self.niche)
        
        system = f"{custom_prompt}\n\n" if custom_prompt else f"{BASE_SYSTEM_PROMPT}\n\n"
        if addon:
            system += f"**Diretrizes de Nicho ({self.profile_name})**:\n{addon}\n\n"
            
        system += f"Conta ativa: **{self.account_name}** | Nicho: **{self.profile_name}**\n\n"
        
        if knowledge_base:
            system += f"**BASE DE CONHECIMENTO VINCULADA**:\n{knowledge_base}\n\n"

        self.system_message = {"role": "system", "content": system}
        self.messages: list[dict] = []
        self._load_memory()

    # ── MEMÓRIA PERSISTENTE ──────────────────────────────────────────────────

    def _memory_file(self) -> Path:
        MEMORY_DIR.mkdir(exist_ok=True)
        safe = self.slug or self.account_name.lower().replace(" ", "_")
        return MEMORY_DIR / f"{safe}_history.json"

    def _load_memory(self):
        """Carrega o histórico de conversas salvo em disco para este cliente."""
        path = self._memory_file()
        if path.exists():
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self.messages = data.get("messages", [])
            except Exception:
                self.messages = []

    def _save_memory(self):
        """Salva apenas as mensagens texto (user + assistant) — sem tool calls/results volumosos."""
        text_messages = []
        for msg in self.messages:
            role = msg.get("role")
            content = msg.get("content")
            if role in ("user", "assistant") and isinstance(content, str) and content.strip():
                text_messages.append({"role": role, "content": content})
        # Mantém apenas as últimas 40 mensagens para não sobrecarregar o contexto
        text_messages = text_messages[-40:]
        path = self._memory_file()
        with open(path, "w", encoding="utf-8") as f:
            json.dump({"slug": self.slug, "account": self.account_name, "messages": text_messages}, f, ensure_ascii=False, indent=2)

    def clear_memory(self):
        """Apaga a memória persistente deste cliente."""
        path = self._memory_file()
        if path.exists():
            path.unlink()
        self.messages = []

    def chat(self, user_message: str, log_callback=None) -> str:
        """Envia uma mensagem e retorna a resposta final do agente."""
        api_key = settings.get_setting("api_key", "")
        if not api_key:
            return "Erro: Chave de API não configurada. Vá em Configurações para definir a API Key."
            
        self.messages.append({"role": "user", "content": user_message})
        full_content = ""

        while True:
            full_messages = [self.system_message] + self.messages
            
            try:
                if self.provider == "anthropic":
                    import litellm
                    import os
                    os.environ["ANTHROPIC_API_KEY"] = self.api_key
                    # litellm requires the model name exactly, e.g. "claude-3-5-sonnet-20240620"
                    # But it will map OpenAI formatted tools automatically
                    response = litellm.completion(
                        model=self.model,
                        messages=full_messages,
                        tools=self.tools,
                        tool_choice="auto"
                    )
                else:
                    response = self.client.chat.completions.create(
                        model=self.model,
                        messages=full_messages,
                        tools=self.tools,
                        tool_choice="auto",
                    )
            except Exception as e:
                return f"Erro de API ({self.provider}): {str(e)}"
            
            # Extract usage
            if response.usage:
                settings.register_token_usage(
                    prompt_tokens=response.usage.prompt_tokens,
                    completion_tokens=response.usage.completion_tokens,
                    cost_per_1k_prompt=0.0, # openrouter usage can be retrieved via their dedicated endpoint instead if needed
                    cost_per_1k_comp=0.0
                )

            choice = response.choices[0]
            message = choice.message
            
            if message.content:
                full_content += message.content + "\n\n"

            # Append the assistant message correctly to history
            assistant_msg = {
                "role": "assistant",
                "content": message.content,
            }
            if message.tool_calls:
                assistant_msg["tool_calls"] = [{"id": tc.id, "type": "function", "function": {"name": tc.function.name, "arguments": tc.function.arguments}} for tc in message.tool_calls]
                
            self.messages.append(assistant_msg)

            if message.tool_calls:
                # Executar as ferramentas
                for tool_call in message.tool_calls:
                    function_name = tool_call.function.name
                    step_msg = f"🤖 [Ação] Executando {function_name}..."
                    try:
                        print(step_msg)
                    except UnicodeEncodeError:
                        print(f"[Acao] Executando {function_name}...")
                    if log_callback: log_callback(step_msg)

                    try:
                        arguments = json.loads(tool_call.function.arguments)
                    except:
                        arguments = {}

                    result = execute_tool(function_name, arguments, self.api)

                    done_msg = f"✅ [OK] {function_name} finalizado."
                    try:
                        print(done_msg)
                    except UnicodeEncodeError:
                        print(f"[OK] {function_name} finalizado.")
                    if log_callback: log_callback(done_msg)
                    
                    self.messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": function_name,
                        "content": result
                    })
            else:
                self._save_memory()
                return full_content or "Agente finalizou as ações solicitadas."

    def reset_conversation(self):
        self.clear_memory()

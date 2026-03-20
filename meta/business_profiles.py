"""
Perfis de empresa por nicho de mercado.
Cada perfil define estratégias padrão de IA para criação e otimização de campanhas.
"""

BUSINESS_PROFILES = {
    "ecommerce": {
        "name": "E-commerce",
        "icon": "🛒",
        "description": "Lojas virtuais, marketplaces e vendas online",
        "objectives": ["OUTCOME_SALES", "OUTCOME_TRAFFIC"],
        "optimization_goals": ["OFFSITE_CONVERSIONS", "LINK_CLICKS", "LANDING_PAGE_VIEWS"],
        "kpis": ["ROAS", "CPA", "Conversões", "Ticket Médio"],
        "targeting_tips": [
            "Use catálogo de produtos para anúncios dinâmicos",
            "Configure pixel de conversão para rastreamento de compras",
            "Crie públicos lookalike baseados em compradores",
            "Retarget visitantes do site nos últimos 7-30 dias",
            "Segmente por interesses relacionados aos produtos vendidos",
        ],
        "creative_tips": [
            "Use fotos de produto em alta qualidade",
            "Inclua preço e desconto no criativo",
            "Teste carrosséis de produtos vs. imagem única",
            "Use vídeos curtos de unboxing ou uso do produto",
            "Destaque frete grátis ou condições de pagamento",
        ],
        "budget_strategy": "Comece com R$30-50/dia por campanha. Escale após ROAS positivo.",
        "ab_test_suggestions": [
            "Criativo com preço vs. sem preço",
            "Catálogo dinâmico vs. imagem estática",
            "Público frio vs. retargeting",
            "Copy curta vs. copy com storytelling",
        ],
        "system_prompt_addon": (
            "Este cliente é um e-commerce. Foque em ROAS, conversões e CPA. "
            "Sugira sempre testes A/B de criativos com variações de preço e oferta. "
            "Priorize retargeting e públicos lookalike de compradores. "
            "Monitore crescimento do custo por conversão e frequência dos anúncios."
        ),
    },
    "services_local": {
        "name": "Serviços Locais",
        "icon": "📍",
        "description": "Serviços presenciais: encanador, elétricista, salão, etc.",
        "objectives": ["OUTCOME_LEADS", "OUTCOME_TRAFFIC"],
        "optimization_goals": ["LEAD_GENERATION", "LINK_CLICKS", "REACH"],
        "kpis": ["CPL", "Leads", "Alcance Local", "Agendamentos"],
        "targeting_tips": [
            "Segmente por raio geográfico (5-25km do ponto de atendimento)",
            "Use targeting por CEP ou bairro quando possível",
            "Inclua interesses relacionados ao tipo de serviço",
            "Alcance somente adultos na faixa etária relevante",
            "Use formulários de lead nativo do Facebook",
        ],
        "creative_tips": [
            "Mostre antes e depois do serviço",
            "Inclua depoimentos de clientes satisfeitos",
            "Destaque localização e telefone",
            "Use CTA de WhatsApp ou ligar agora",
            "Fotos reais do trabalho realizado",
        ],
        "budget_strategy": "R$20-40/dia por campanha. Foque em horário comercial e dias úteis.",
        "ab_test_suggestions": [
            "Formulário nativo vs. link para WhatsApp",
            "Foto do serviço vs. vídeo de depoimento",
            "Raio 5km vs. 15km",
            "Copy técnica vs. copy emocional",
        ],
        "system_prompt_addon": (
            "Este cliente oferece serviços locais. Foque em geração de leads e alcance local. "
            "Recomende sempre formulários nativos do Facebook para captura de leads. "
            "Priorize segmentação geográfica precisa e horários de pico de busca. "
            "Sugira criativos com antes/depois e depoimentos de clientes."
        ),
    },
    "infoproducts": {
        "name": "Infoprodutos",
        "icon": "📚",
        "description": "Cursos online, mentorias, ebooks, comunidades",
        "objectives": ["OUTCOME_SALES", "OUTCOME_LEADS", "OUTCOME_TRAFFIC"],
        "optimization_goals": ["OFFSITE_CONVERSIONS", "LEAD_GENERATION", "LANDING_PAGE_VIEWS"],
        "kpis": ["CPA", "ROAS", "Leads", "Taxa de Conversão"],
        "targeting_tips": [
            "Crie funil: awareness → captação → venda",
            "Use públicos de engajamento do Instagram/Facebook",
            "Lookalike de compradores/leads dos últimos 180 dias",
            "Segmente por interesses em educação e desenvolvimento",
            "Exclua compradores recentes da campanha de captação",
        ],
        "creative_tips": [
            "Vídeos de VSL (Video Sales Letter) de 1-3 minutos",
            "Criativos com prova social e resultados de alunos",
            "Use gatilhos de escassez e urgência",
            "Teste headlines diferentes no criativo",
            "Carrossel com módulos/conteúdo do curso",
        ],
        "budget_strategy": "R$50-100/dia por funil. Divida 30% captação, 70% venda.",
        "ab_test_suggestions": [
            "VSL vs. imagem com copy longa",
            "Headline de dor vs. headline de resultado",
            "Público frio por interesse vs. lookalike",
            "Landing page com vídeo vs. sem vídeo",
        ],
        "system_prompt_addon": (
            "Este cliente vende infoprodutos. Foque em funil de vendas com captação de leads e conversão. "
            "Sugira sempre estrutura de funil com campanhas separadas para awareness, captação e venda. "
            "Monitore taxa de conversão do lead para compra. "
            "Recomende criativos com prova social e VSL."
        ),
    },
    "saas": {
        "name": "SaaS / Software",
        "icon": "💻",
        "description": "Software como serviço, apps, plataformas digitais",
        "objectives": ["OUTCOME_LEADS", "OUTCOME_TRAFFIC", "OUTCOME_SALES"],
        "optimization_goals": ["LEAD_GENERATION", "OFFSITE_CONVERSIONS", "LANDING_PAGE_VIEWS"],
        "kpis": ["CPL", "CPA", "LTV", "Trial-to-Paid"],
        "targeting_tips": [
            "Segmente por cargo/indústria para B2B",
            "Use interesses em softwares e tecnologia concorrentes",
            "Alcance decisores e influenciadores de compra",
            "Retarget visitantes da página de pricing",
            "Lookalike de clientes pagantes",
        ],
        "creative_tips": [
            "Demonstrações rápidas do produto em vídeo",
            "Print screens da interface em uso",
            "Comparativos com concorrentes",
            "Depoimentos de empresas clientes",
            "Oferta de trial gratuito como CTA",
        ],
        "budget_strategy": "R$40-80/dia. Foque em qualificação de leads, não volume.",
        "ab_test_suggestions": [
            "Demo em vídeo vs. print de tela",
            "Trial gratuito vs. agendamento de demo",
            "Copy técnica vs. copy de benefícios",
            "Público por cargo vs. por interesse",
        ],
        "system_prompt_addon": (
            "Este cliente é um SaaS. Foque em geração de leads qualificados e CAC. "
            "Sugira funis com trial/demo como entrada. "
            "Monitore taxa de conversão trial-to-paid e LTV. "
            "Recomende segmentação por cargo e indústria para B2B."
        ),
    },
    "restaurant": {
        "name": "Restaurantes / Alimentação",
        "icon": "🍽️",
        "description": "Restaurantes, bares, delivery, food trucks",
        "objectives": ["OUTCOME_AWARENESS", "OUTCOME_ENGAGEMENT", "OUTCOME_TRAFFIC"],
        "optimization_goals": ["REACH", "ENGAGED_USERS", "LINK_CLICKS"],
        "kpis": ["Alcance", "Engajamento", "Pedidos", "Visitas ao Estabelecimento"],
        "targeting_tips": [
            "Raio geográfico de 3-10km do restaurante",
            "Segmente por faixa etária do público do estabelecimento",
            "Horários de refeição: almoço (10h-13h) e jantar (17h-20h)",
            "Interesses em gastronomia e delivery",
            "Use públicos de eventos para festas/promos",
        ],
        "creative_tips": [
            "Fotos profissionais dos pratos (food porn)",
            "Vídeos de preparo dos pratos",
            "Promoções com desconto e combos",
            "Cardápio em carrossel",
            "Stories com bastidores da cozinha",
        ],
        "budget_strategy": "R$15-30/dia. Foque em horários de pico e fins de semana.",
        "ab_test_suggestions": [
            "Foto de prato vs. vídeo de preparo",
            "Promoção vs. awareness da marca",
            "Horário de almoço vs. jantar",
            "Raio 5km vs. 10km",
        ],
        "system_prompt_addon": (
            "Este cliente é do ramo de alimentação. Foque em alcance local e engajamento. "
            "Sugira criativos visuais com fotos profissionais de comida. "
            "Programe anúncios para horários de pico (almoço e jantar). "
            "Monitore alcance local e engajamento."
        ),
    },
    "real_estate": {
        "name": "Imobiliárias",
        "icon": "🏠",
        "description": "Imobiliárias, construtoras, corretores",
        "objectives": ["OUTCOME_LEADS", "OUTCOME_TRAFFIC"],
        "optimization_goals": ["LEAD_GENERATION", "LINK_CLICKS", "LANDING_PAGE_VIEWS"],
        "kpis": ["CPL", "Leads Qualificados", "Agendamentos de Visita"],
        "targeting_tips": [
            "IMPORTANTE: Use special_ad_categories HOUSING",
            "Segmente por região desejada de moradia/investimento",
            "Faixa de renda compatível com os imóveis",
            "Lookalike de compradores anteriores",
            "Retarget visitantes de imóveis específicos",
        ],
        "creative_tips": [
            "Tours virtuais em vídeo dos imóveis",
            "Fotos profissionais com todas as dependências",
            "Planta baixa e mapa de localização",
            "Destaque metragem, quartos e diferenciais",
            "CTA de agendar visita ou simular financiamento",
        ],
        "budget_strategy": "R$40-80/dia. Leads imobiliários têm custo mais alto mas ticket elevado.",
        "ab_test_suggestions": [
            "Vídeo tour vs. carrossel de fotos",
            "Lead form vs. landing page de simulação",
            "Público por renda vs. por região",
            "Copy técnica vs. copy aspiracional",
        ],
        "system_prompt_addon": (
            "Este cliente é do ramo imobiliário. SEMPRE inclua HOUSING em special_ad_categories. "
            "Foque em geração de leads qualificados com formulários de contato. "
            "Sugira criativos com tours virtuais e fotos profissionais. "
            "Monitore CPL e taxa de agendamento de visitas."
        ),
    },
    "health": {
        "name": "Saúde / Clínicas",
        "icon": "🏥",
        "description": "Clínicas, consultórios, academias, bem-estar",
        "objectives": ["OUTCOME_LEADS", "OUTCOME_AWARENESS", "OUTCOME_TRAFFIC"],
        "optimization_goals": ["LEAD_GENERATION", "REACH", "LINK_CLICKS"],
        "kpis": ["CPL", "Agendamentos", "Alcance Local"],
        "targeting_tips": [
            "Geolocalização: raio de 10-20km da clínica",
            "Faixa etária relevante para o serviço médico",
            "Interesses em saúde e bem-estar",
            "Exclua menores de idade para procedimentos estéticos",
            "Cuidado com políticas de compliance de saúde do Meta",
        ],
        "creative_tips": [
            "Antes e depois (dentro das políticas do Meta)",
            "Depoimentos de pacientes (com autorização)",
            "Equipe médica e estrutura da clínica",
            "Explique procedimentos de forma educativa",
            "CTA de agendar consulta ou avaliação gratuita",
        ],
        "budget_strategy": "R$25-50/dia. Leads de saúde convertem bem em consultório.",
        "ab_test_suggestions": [
            "Antes/depois vs. depoimento",
            "Agendamento online vs. WhatsApp",
            "Público amplo vs. interesse em saúde",
            "Vídeo do profissional vs. foto da estrutura",
        ],
        "system_prompt_addon": (
            "Este cliente é da área de saúde. Respeite SEMPRE as políticas de anúncio do Meta sobre saúde. "
            "Evite promessas de resultado ou claims médicos nos criativos. "
            "Foque em geração de leads para agendamento de consultas. "
            "Sugira conteúdo educativo como estratégia de awareness."
        ),
    },
    "education": {
        "name": "Educação",
        "icon": "🎓",
        "description": "Escolas, faculdades, cursos presenciais",
        "objectives": ["OUTCOME_LEADS", "OUTCOME_AWARENESS", "OUTCOME_TRAFFIC"],
        "optimization_goals": ["LEAD_GENERATION", "REACH", "LINK_CLICKS"],
        "kpis": ["CPL", "Matrículas", "Inscrições"],
        "targeting_tips": [
            "Segmente pais para ensino fundamental/médio",
            "Segmente jovens 17-25 para graduação",
            "Interesses em educação e carreira",
            "Geolocalização da área de captação",
            "Épocas de matrícula: intensifique jan-mar e jul-ago",
        ],
        "creative_tips": [
            "Infraestrutura e diferenciais da instituição",
            "Cases de sucesso de ex-alunos",
            "Vídeos de aulas e atividades",
            "Destaque bolsas e condições de pagamento",
            "Evento de visitação como CTA",
        ],
        "budget_strategy": "R$30-60/dia. Intensifique em períodos de matrícula.",
        "ab_test_suggestions": [
            "Vídeo institucional vs. depoimento de aluno",
            "Bolsa vs. desconto na matrícula",
            "Formulário nativo vs. landing page",
            "Público por idade vs. por interesse",
        ],
        "system_prompt_addon": (
            "Este cliente é do setor educacional. Foque em captação de leads para matrículas. "
            "Adapte a comunicação para o público específico (pais ou alunos). "
            "Intensifique investimento em períodos de matrícula. "
            "Sugira eventos e visitações como estratégia de conversão."
        ),
    },
    "fashion_beauty": {
        "name": "Moda / Beleza",
        "icon": "👗",
        "description": "Lojas de roupas, cosméticos, salões de beleza",
        "objectives": ["OUTCOME_SALES", "OUTCOME_TRAFFIC", "OUTCOME_ENGAGEMENT"],
        "optimization_goals": ["OFFSITE_CONVERSIONS", "LINK_CLICKS", "ENGAGED_USERS"],
        "kpis": ["ROAS", "CPA", "Engajamento", "Ticket Médio"],
        "targeting_tips": [
            "Interesses em moda, beleza e tendências",
            "Segmente por gênero quando relevante",
            "Faixa etária alinhada ao público da marca",
            "Lookalike de compradoras frequentes",
            "Retarget de visitantes do site/Instagram",
        ],
        "creative_tips": [
            "Fotos lifestyle com modelos usando os produtos",
            "Vídeos de looks do dia e tutoriais",
            "Carrossel de coleção/tendências",
            "Reels e conteúdo UGC (user generated content)",
            "Promoções sazonais e drops exclusivos",
        ],
        "budget_strategy": "R$30-60/dia. Intensifique em datas comemorativas e drops.",
        "ab_test_suggestions": [
            "Foto lifestyle vs. foto de produto",
            "Vídeo tutorial vs. carrossel",
            "Desconto percentual vs. valor fixo",
            "Público amplo vs. interesse em moda",
        ],
        "system_prompt_addon": (
            "Este cliente é do segmento de moda/beleza. Foque em ROAS e engajamento visual. "
            "Sugira criativos com forte apelo visual e tendências atuais. "
            "Recomende catálogo dinâmico quando possível. "
            "Intensifique investimento em datas comemorativas."
        ),
    },
    "custom": {
        "name": "Personalizado",
        "icon": "⚙️",
        "description": "Configuração manual para nichos específicos",
        "objectives": [
            "OUTCOME_AWARENESS", "OUTCOME_TRAFFIC", "OUTCOME_ENGAGEMENT",
            "OUTCOME_LEADS", "OUTCOME_APP_PROMOTION", "OUTCOME_SALES",
        ],
        "optimization_goals": [
            "LINK_CLICKS", "IMPRESSIONS", "REACH", "LEAD_GENERATION",
            "OFFSITE_CONVERSIONS", "LANDING_PAGE_VIEWS", "VIDEO_VIEWS",
            "ENGAGED_USERS", "APP_INSTALLS", "QUALITY_LEAD",
        ],
        "kpis": ["Definir manualmente"],
        "targeting_tips": ["Analise o público do cliente para definir segmentação"],
        "creative_tips": ["Analise o produto/serviço para definir criativos"],
        "budget_strategy": "Defina conforme o ticket médio e margem do negócio.",
        "ab_test_suggestions": ["Teste diferentes abordagens conforme o nicho"],
        "system_prompt_addon": (
            "Este cliente tem um perfil personalizado. "
            "Analise as informações disponíveis e recomende a melhor estratégia "
            "baseada no objetivo informado e nos dados de performance."
        ),
    },
}


def get_profile(profile_key: str) -> dict:
    """Retorna um perfil de empresa pelo key."""
    return BUSINESS_PROFILES.get(profile_key, BUSINESS_PROFILES["custom"])


def list_profiles() -> dict:
    """Retorna todos os perfis disponíveis com nome e ícone."""
    return {
        key: {"name": p["name"], "icon": p["icon"], "description": p["description"]}
        for key, p in BUSINESS_PROFILES.items()
    }


def get_system_prompt_addon(profile_key: str) -> str:
    """Retorna o addon de system prompt para o agente IA baseado no perfil."""
    profile = get_profile(profile_key)
    return profile.get("system_prompt_addon", "")

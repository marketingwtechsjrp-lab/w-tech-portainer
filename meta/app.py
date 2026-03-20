import os
import json
from functools import wraps
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_cors import CORS
from dotenv import load_dotenv

import accounts as acc
import business_profiles
import settings
from meta_api import MetaAdsAPI
from agent import MetaAdsAgent

load_dotenv()

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*", "allow_headers": "*", "methods": "*"}})
# Keep secret key persistent so it doesn't disconnect users on server restart
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'default-secret-key-for-meta-ads-ai-123')

# Armazena os agentes em memória (em produção usaria algo mais robusto)
active_agents = {}

def get_agent(slug):
    """Instancia ou obtém do cache o agente para a conta atual"""
    if slug not in active_agents:
        creds = acc.get_account_credentials(slug)
        if not creds:
            return None
        try:
            api = MetaAdsAPI(
                access_token=creds["access_token"],
                ad_account_id=creds["ad_account_id"]
            )
            niche = creds.get("niche", "custom")
            active_agents[slug] = MetaAdsAgent(api, creds["name"], niche, slug=slug)
        except Exception as e:
            print(f"Erro ao inicializar agente para {slug}: {e}")
            return None
    return active_agents[slug]

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'active_account' not in session and request.endpoint not in ['select_account', 'api_accounts', 'settings_page', 'api_settings']:
            return redirect(url_for('select_account'))
        return f(*args, **kwargs)
    return decorated_function

# --- ROTAS DE VIEWS ---

@app.route('/')
def index():
    if 'active_account' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('select_account'))

@app.route('/select')
def select_account():
    return render_template('accounts.html')

@app.route('/settings')
def settings_page():
    return render_template('settings.html')

@app.route('/dashboard')
@login_required
def dashboard():
    slug = session.get('active_account')
    creds = acc.get_account_credentials(slug)
    profile = business_profiles.get_profile(creds.get('niche', 'custom'))
    return render_template('dashboard.html', account_name=creds['name'], slug=slug, profile=profile)

@app.route('/campaigns')
@login_required
def campaigns():
    slug = session.get('active_account')
    creds = acc.get_account_credentials(slug)
    profile = business_profiles.get_profile(creds.get('niche', 'custom'))
    return render_template('campaigns.html', account_name=creds['name'], slug=slug, profile=profile)

@app.route('/chat')
@login_required
def chat():
    slug = session.get('active_account')
    creds = acc.get_account_credentials(slug)
    profile = business_profiles.get_profile(creds.get('niche', 'custom'))
    return render_template('chat.html', account_name=creds['name'], slug=slug, profile=profile)

# --- ROTAS DE API ---

@app.route('/api/settings', methods=['GET'])
def api_settings_get():
    return jsonify(settings.load_settings())

@app.route('/api/settings', methods=['POST'])
def api_settings_post():
    data = request.json
    for key, val in data.items():
        settings.update_setting(key, val)
    
    # Reset all agents so they pick up new config
    global active_agents
    active_agents = {}
    return jsonify({"success": True})

@app.route('/api/settings/upload', methods=['POST'])
def api_settings_upload():
    if 'file' not in request.files:
        return jsonify({"success": False, "error": "Nenhum arquivo enviado"}), 400
    
    file = request.files['file']
    filename = file.filename.lower()
    
    try:
        text = ""
        if filename.endswith(".pdf"):
            import PyPDF2
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                text += page.extract_text() + "\n"
        elif filename.endswith(".txt"):
            text = file.read().decode('utf-8')
        else:
            return jsonify({"success": False, "error": "Formato não suportado (.pdf e .txt)"}), 400
            
        return jsonify({"success": True, "text": text.strip()})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400

@app.route('/api/accounts', methods=['GET'])
def api_accounts():
    accounts_dict = acc.list_accounts()
    profiles = business_profiles.list_profiles()
    
    # Adicionar o nome do nicho aos dados
    for slug, data in accounts_dict.items():
        niche_key = data.get('niche', 'custom')
        data['niche_name'] = profiles.get(niche_key, {}).get('name', 'Custom')
        data['niche_icon'] = profiles.get(niche_key, {}).get('icon', '⚙️')
        
    return jsonify(accounts_dict)

@app.route('/api/accounts', methods=['POST'])
def api_add_account():
    data = request.json
    try:
        acc.add_account(
            slug=data['slug'],
            name=data['name'],
            access_token=data['access_token'],
            ad_account_id=data['ad_account_id'],
            notes=data.get('notes', ''),
            niche=data.get('niche', 'custom')
        )
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400

@app.route('/api/accounts/<slug>', methods=['PUT'])
def api_update_account(slug):
    data = request.json
    success = acc.update_account(
        slug,
        name=data.get('name'),
        access_token=data.get('access_token') or None,
        ad_account_id=data.get('ad_account_id'),
        notes=data.get('notes'),
        niche=data.get('niche'),
    )
    if success:
        # Reinicia o agente para usar novas credenciais
        active_agents.pop(slug, None)
        return jsonify({"success": True})
    return jsonify({"success": False, "error": "Conta não encontrada"}), 404

@app.route('/api/accounts/<slug>', methods=['DELETE'])
def api_delete_account(slug):
    success = acc.remove_account(slug)
    if success:
        if session.get('active_account') == slug:
            session.pop('active_account', None)
        active_agents.pop(slug, None)
        return jsonify({"success": True})
    return jsonify({"success": False, "error": "Conta não encontrada"}), 404

@app.route('/api/auth/<slug>', methods=['POST'])
def api_auth(slug):
    creds = acc.get_account_credentials(slug)
    if not creds:
        return jsonify({"success": False, "error": "Conta não encontrada"}), 404
        
    agent = get_agent(slug)
    if not agent:
        return jsonify({"success": False, "error": "Erro de conexão com a API da Meta. Verifique o Access Token e o Ad Account ID."}), 400
        
    session['active_account'] = slug
    return jsonify({"success": True})

@app.route('/api/profiles', methods=['GET'])
def api_profiles():
    return jsonify(business_profiles.list_profiles())

# --- API DA CONTA ATIVA (META ADS) ---

@app.route('/api/meta/overview', methods=['GET'])
@login_required
def api_overview():
    slug = session['active_account']
    agent = get_agent(slug)
    try:
        data = agent.api.get_account_overview()
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/api/meta/campaigns', methods=['GET'])
@login_required
def api_campaigns():
    slug = session['active_account']
    agent = get_agent(slug)
    status = request.args.get('status', 'ACTIVE')
    try:
        data = agent.api.get_campaigns(status_filter=status)
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/api/meta/insights', methods=['GET'])
@login_required
def api_insights():
    slug = session['active_account']
    agent = get_agent(slug)
    level = request.args.get('level', 'campaign')
    preset = request.args.get('preset', 'last_30d')
    try:
        data = agent.api.get_insights(level=level, date_preset=preset)
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/campaigns/<campaign_id>')
@login_required
def campaign_details(campaign_id):
    slug = session.get('active_account')
    creds = acc.get_account_credentials(slug)
    profile = business_profiles.get_profile(creds.get('niche', 'custom'))
    return render_template('campaign_details.html', account_name=creds['name'], slug=slug, profile=profile, campaign_id=campaign_id)

@app.route('/api/meta/campaigns/<campaign_id>/insights', methods=['GET'])
@login_required
def api_campaign_insights(campaign_id):
    slug = session['active_account']
    agent = get_agent(slug)
    try:
        # Get overall metrics for the campaign
        overall = agent.api.get_insights(object_id=campaign_id, level="campaign", date_preset="last_30d")
        
        # Get daily metrics for charts
        daily = agent.api.get_insights(object_id=campaign_id, level="campaign", date_preset="last_30d", time_increment=1)
        
        # Get adsets inside campaign
        adsets = agent.api.get_adsets(campaign_id=campaign_id)
        
        # Get ads inside campaign
        ads = agent.api.get_ads(campaign_id=campaign_id)
        
        return jsonify({
            "overall": overall[0] if overall else None,
            "daily": daily,
            "adsets": adsets,
            "ads": ads
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/api/meta/auto_optimize', methods=['POST'])
@login_required
def api_auto_optimize():
    slug = session['active_account']
    agent = get_agent(slug)
    
    prompt = (
        "Analise ativamente o desempenho da conta e das campanhas atuais. "
        "Baseado nisso e nas diretrizes do meu nicho de mercado, aja automaticamente: "
        "1) Crie uma nova campanha recomendada (com status PAUSED, claro), OU "
        "2) Crie Testes A/B, OU "
        "3) Aplique as melhorias que você achar necessário nas campanhas existentes. "
        "Responda ao final resumindo detalhadamente tudo o que você fez nesta rotina de auto-otimização."
    )
    
    try:
        response = agent.chat(prompt)
        return jsonify({"success": True, "report": response})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --- API DO CHAT IA ---

# Armazena os logs da execução em tempo real para o frontend
current_logs = []

def add_agent_log(msg):
    global current_logs
    current_logs.append(msg)
    if len(current_logs) > 50:
        current_logs.pop(0)

@app.route('/api/chat', methods=['POST'])
@login_required
def api_chat():
    global current_logs
    current_logs = [] # Limpa ao iniciar novo chat
    
    slug = session['active_account']
    agent = get_agent(slug)
    data = request.json
    user_message = data.get('message', '')
    
    if not user_message:
        return jsonify({"error": "Mensagem vazia"}), 400
        
    try:
        response = agent.chat(user_message, log_callback=add_agent_log)
        return jsonify({"response": response})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/chat/logs', methods=['GET'])
@login_required
def api_chat_logs():
    return jsonify({"logs": current_logs})

@app.route('/api/chat/reset', methods=['POST'])
@login_required
def api_chat_reset():
    global current_logs
    current_logs = []
    slug = session['active_account']
    agent = get_agent(slug)
    agent.reset_conversation()  # também limpa memória persistente
    return jsonify({"success": True})

@app.route('/api/memory/<slug>', methods=['GET'])
@login_required
def api_memory_info(slug):
    """Retorna info sobre a memória persistente de uma conta."""
    from pathlib import Path
    memory_file = Path(__file__).parent / "memory" / f"{slug}_history.json"
    if not memory_file.exists():
        return jsonify({"exists": False, "message_count": 0})
    try:
        import json as _json
        data = _json.loads(memory_file.read_text(encoding="utf-8"))
        return jsonify({"exists": True, "message_count": len(data.get("messages", []))})
    except Exception:
        return jsonify({"exists": False, "message_count": 0})

@app.route('/api/chat/history', methods=['GET'])
@login_required
def api_chat_history():
    slug = session['active_account']
    agent = get_agent(slug)
    
    # Filtra as mensagens para enviar ao frontend
    history = []
    for msg in agent.messages:
        if msg['role'] == 'user':
            content = msg.get('content')
            if content and isinstance(content, str):
                history.append({"role": "user", "content": content})
        elif msg['role'] == 'assistant':
            content = msg.get('content')
            if content and isinstance(content, str):
                history.append({"role": "assistant", "content": content})
                    
    return jsonify({"history": history})

if __name__ == '__main__':
    # Em produção, ouça em 0.0.0.0 para o Docker conseguir acessar
    app.run(host='0.0.0.0', port=5000)

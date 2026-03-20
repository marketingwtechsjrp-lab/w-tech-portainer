import React, { useState, useEffect } from 'react';
import { 
    LayoutDashboard, 
    Megaphone, 
    MessageSquare, 
    RefreshCcw, 
    Settings, 
    AlertCircle,
    ChevronRight,
    Search,
    Filter
} from 'lucide-react';
import MetaDashboard from './MetaDashboard.tsx';
import MetaCampaigns from './MetaCampaigns.tsx';
import MetaAIChat from './MetaAIChat.tsx';

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:5000/api';

const MetaAdsView = () => {
    const [accounts, setAccounts] = useState<any>({});
    const [activeAccount, setActiveAccount] = useState<string | null>(null);
    const [activeSubTab, setActiveSubTab] = useState<'dashboard' | 'campaigns' | 'chat'>('dashboard');
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        fetchAccounts();
    }, []);

    const fetchAccounts = async () => {
        try {
            setLoading(true);
            const response = await fetch(`${API_BASE}/accounts`);
            if (!response.ok) throw new Error('Falha ao carregar contas do Meta');
            const data = await response.json();
            setAccounts(data);
            
            // Auto-select first account if none selected
            const slugs = Object.keys(data);
            if (slugs.length > 0 && !activeAccount) {
                handleSelectAccount(slugs[0]);
            }
        } catch (err: any) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    const handleSelectAccount = async (slug: string) => {
        try {
            const response = await fetch(`${API_BASE}/auth/${slug}`, { method: 'POST' });
            if (!response.ok) throw new Error('Falha ao autenticar conta');
            setActiveAccount(slug);
        } catch (err: any) {
            setError(err.message);
        }
    };

    if (loading && !Object.keys(accounts).length) {
        return (
            <div className="flex flex-col items-center justify-center h-[500px] gap-4">
                <RefreshCcw className="animate-spin text-wtech-gold" size={32} />
                <p className="text-gray-500 font-medium">Conectando ao Gerenciador Meta...</p>
            </div>
        );
    }

    if (error && !Object.keys(accounts).length) {
        return (
            <div className="flex flex-col items-center justify-center h-[500px] p-8 text-center">
                <div className="bg-red-50 dark:bg-red-900/10 p-4 rounded-full text-red-600 mb-4">
                    <AlertCircle size={48} />
                </div>
                <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-2">Erro de Conexão</h3>
                <p className="text-gray-500 max-w-md mb-6">
                    Não foi possível conectar ao serviço de Meta Ads. Certifique-se de que o backend Python está rodando na porta 5000.
                </p>
                <button 
                    onClick={fetchAccounts}
                    className="px-6 py-2 bg-black dark:bg-white dark:text-black text-white rounded-xl font-bold flex items-center gap-2 hover:opacity-80 transition-all"
                >
                    <RefreshCcw size={18} /> Tentar Novamente
                </button>
            </div>
        );
    }

    const currentAccountData = activeAccount ? accounts[activeAccount] : null;

    return (
        <div className="flex flex-col h-full bg-gray-50/50 dark:bg-transparent">
            {/* Meta Header / Account Selector */}
            <div className="bg-white dark:bg-[#1A1A1A] border-b border-gray-100 dark:border-gray-800 p-4 sticky top-0 z-10">
                <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
                    <div className="flex items-center gap-4">
                        <div className="p-3 bg-blue-600 rounded-2xl text-white shadow-lg shadow-blue-500/20">
                            <Megaphone size={24} />
                        </div>
                        <div>
                            <div className="flex items-center gap-2">
                                <h3 className="text-lg font-black text-gray-900 dark:text-white uppercase tracking-tight">
                                    Meta Traffic AI
                                </h3>
                                <span className="px-2 py-0.5 bg-green-100 dark:bg-green-900/30 text-green-600 dark:text-green-400 text-[10px] font-bold rounded-full border border-green-200 dark:border-green-800/50">
                                    CONECTADO
                                </span>
                            </div>
                            <div className="flex items-center gap-2 mt-0.5">
                                <select 
                                    value={activeAccount || ''} 
                                    onChange={(e) => handleSelectAccount(e.target.value)}
                                    className="bg-transparent border-none text-sm font-bold text-gray-500 dark:text-gray-400 focus:ring-0 p-0 cursor-pointer hover:text-gray-900 dark:hover:text-white transition-colors"
                                >
                                    {Object.entries(accounts).map(([slug, acc]: [string, any]) => (
                                        <option key={slug} value={slug} className="dark:bg-[#1A1A1A]">
                                            {acc.name} ({acc.niche_name})
                                        </option>
                                    ))}
                                </select>
                                <ChevronRight size={14} className="text-gray-300" />
                                <span className="text-xs text-gray-400 font-medium">ID: {currentAccountData?.ad_account_id}</span>
                            </div>
                        </div>
                    </div>

                    <div className="flex bg-gray-100 dark:bg-[#111] p-1 rounded-xl w-full md:w-auto">
                        <button
                            onClick={() => setActiveSubTab('dashboard')}
                            className={`flex-1 md:flex-none flex items-center justify-center gap-2 px-6 py-2 rounded-lg text-xs font-bold transition-all ${
                                activeSubTab === 'dashboard' 
                                ? 'bg-white dark:bg-[#222] text-black dark:text-white shadow-sm' 
                                : 'text-gray-500 hover:text-gray-900'
                            }`}
                        >
                            <LayoutDashboard size={14} /> Dashboard
                        </button>
                        <button
                            onClick={() => setActiveSubTab('campaigns')}
                            className={`flex-1 md:flex-none flex items-center justify-center gap-2 px-6 py-2 rounded-lg text-xs font-bold transition-all ${
                                activeSubTab === 'campaigns' 
                                ? 'bg-white dark:bg-[#222] text-black dark:text-white shadow-sm' 
                                : 'text-gray-500 hover:text-gray-900'
                            }`}
                        >
                            <Megaphone size={14} /> Campanhas
                        </button>
                        <button
                            onClick={() => setActiveSubTab('chat')}
                            className={`flex-1 md:flex-none flex items-center justify-center gap-2 px-6 py-2 rounded-lg text-xs font-bold transition-all ${
                                activeSubTab === 'chat' 
                                ? 'bg-white dark:bg-[#222] text-black dark:text-white shadow-sm' 
                                : 'text-gray-500 hover:text-gray-900'
                            }`}
                        >
                            <MessageSquare size={14} /> IA Gestor
                        </button>
                    </div>
                </div>
            </div>

            {/* Content Area */}
            <div className="flex-1 overflow-y-auto custom-scrollbar">
                {activeSubTab === 'dashboard' && <MetaDashboard slug={activeAccount} />}
                {activeSubTab === 'campaigns' && <MetaCampaigns slug={activeAccount} />}
                {activeSubTab === 'chat' && <MetaAIChat slug={activeAccount} />}
            </div>
        </div>
    );
};

export default MetaAdsView;

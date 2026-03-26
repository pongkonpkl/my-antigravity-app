import React, { useState, useEffect, useMemo, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Activity, Target, Satellite, Maximize2, MessageSquare, LayoutDashboard, Send, Trash2, ShieldAlert } from 'lucide-react';

const calculate_rsi = (prices, periods = 14) => {
  if (!prices || prices.length < periods + 1) return 50.0;
  let deltas = [];
  for (let i = 1; i < prices.length; i++) deltas.push(prices[i] - prices[i - 1]);
  let gains = deltas.map(d => d > 0 ? d : 0);
  let losses = deltas.map(d => d < 0 ? -d : 0);
  
  let sum_gain = 0; let sum_loss = 0;
  for(let i=0; i<periods; i++) { sum_gain += gains[i]; sum_loss += losses[i]; }
  
  let avg_gain = sum_gain / periods;
  let avg_loss = sum_loss / periods;
  
  for (let i = periods; i < gains.length; i++) {
      avg_gain = (avg_gain * (periods - 1) + gains[i]) / periods;
      avg_loss = (avg_loss * (periods - 1) + losses[i]) / periods;
  }
  if (avg_loss === 0) return 100.0;
  const rs = avg_gain / avg_loss;
  return 100.0 - (100.0 / (1.0 + rs));
};

const calculate_ma_cross = (prices) => {
  if (!prices || prices.length < 168) return { text: "➖ NEUTRAL TREND", color: "#888", border: "#444" };
  const start_idx = prices.length - 24;
  let short_sum = 0, long_sum = 0;
  for(let i=0; i<prices.length; i++) {
     if(i >= start_idx) short_sum += prices[i];
     long_sum += prices[i];
  }
  const diff = (((short_sum / 24) - (long_sum / prices.length)) / (long_sum / prices.length)) * 100.0;
  if(diff > 5.0) return { text: "⚡ GOLDEN CROSS", color: "#D4AF37", border: "rgba(212,175,55,0.4)" };
  if(diff < -5.0) return { text: "💀 DEATH CROSS", color: "#f87171", border: "rgba(248,113,113,0.4)" };
  return { text: "➖ NEUTRAL TREND", color: "#888", border: "#444" };
};

const formatPrice = (p) => {
    if (p === 0) return "0.00";
    if (p >= 1) return p.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 });
    if (p >= 0.01) return p.toLocaleString(undefined, { minimumFractionDigits: 4, maximumFractionDigits: 4 });
    return p.toLocaleString(undefined, { minimumFractionDigits: 7, maximumFractionDigits: 7 });
};

const formatCompact = (num) => {
    if (num >= 1e12) return (num / 1e12).toFixed(2) + "T";
    if (num >= 1e9) return (num / 1e9).toFixed(2) + "B";
    if (num >= 1e6) return (num / 1e6).toFixed(2) + "M";
    return num.toLocaleString();
};

const SparklineSVG = ({ prices, isPos }) => {
    if (!prices || prices.length < 2) return null;
    const sliced = prices.slice(Math.max(0, prices.length - 24));
    const minP = Math.min(...sliced);
    let maxP = Math.max(...sliced);
    if(maxP === minP) maxP += 1e-8;
    
    const w = 130, h = 45;
    const pts = sliced.map((p, i) => {
        const x = (i / (sliced.length - 1)) * w;
        const y = h - ((p - minP) / (maxP - minP)) * h * 0.8 - (h * 0.1);
        return `${x},${y}`;
    });
    
    const colorHex = isPos ? "4ade80" : "f87171";
    const color = `#${colorHex}`;
    const linePts = pts.join(" ");
    const polyPts = `0,${h} ${linePts} ${w},${h}`;
    
    return (
        <svg width={w} height={h} viewBox={`0 0 ${w} ${h}`} style={{overflow:'visible', filter:'drop-shadow(0 2px 5px rgba(0,0,0,0.5))'}} title="24H Sub-Trend">
            <defs>
                <linearGradient id={`grad_${colorHex}`} x1="0%" y1="0%" x2="0%" y2="100%">
                    <stop offset="0%" stopColor={color} stopOpacity="0.3"/>
                    <stop offset="100%" stopColor={color} stopOpacity="0.0"/>
                </linearGradient>
            </defs>
            <polygon points={polyPts} fill={`url(#grad_${colorHex})`} />
            <polyline points={linePts} fill="none" stroke={color} strokeWidth="2.5" strokeLinejoin="round" strokeLinecap="round"/>
        </svg>
    )
};

const SocialFeed = ({ isAdmin }) => {
    const [posts, setPosts] = useState([]);
    const [nickname, setNickname] = useState('TRADER_X');
    const [content, setContent] = useState('');
    const [captcha, setCaptcha] = useState({ q: '', a: 0 });
    const [captchaInput, setCaptchaInput] = useState('');
    const [honeypot, setHoneypot] = useState('');
    const [loading, setLoading] = useState(false);

    const generateCaptcha = () => {
        const a = Math.floor(Math.random() * 10) + 1;
        const b = Math.floor(Math.random() * 10) + 1;
        setCaptcha({ q: `${a} + ${b}`, a: a + b });
    }

    const fetchPosts = async () => {
        try {
            const r = await fetch('http://127.0.0.1:8001/api/social');
            if(r.ok) setPosts(await r.json());
        } catch(e) {}
    }

    useEffect(() => {
        fetchPosts();
        generateCaptcha();
        const interval = setInterval(fetchPosts, 10000);
        return () => clearInterval(interval);
    }, []);

    const handleBroadcast = async () => {
        if (!content.trim()) return alert('Content required');
        if (parseInt(captchaInput) !== captcha.a) return alert('Human verification failed');
        if (honeypot) return; // Silent block

        setLoading(true);
        try {
            const r = await fetch('http://127.0.0.1:8001/api/social', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ nickname, content, image_data: null, honeypot })
            });
            if (r.ok) {
                setContent('');
                setCaptchaInput('');
                generateCaptcha();
                fetchPosts();
            } else {
                const err = await r.json();
                alert(err.detail || 'Broadcast failed');
            }
        } catch(e) { alert('Social uplink offline'); }
        setLoading(false);
    }

    const handleDelete = async (id) => {
        if(!confirm('Delete this signal?')) return;
        try {
            const r = await fetch(`http://127.0.0.1:8001/api/social/${id}`, { method: 'DELETE' });
            if(r.ok) fetchPosts();
        } catch(e) {}
    }

    return (
        <div className="max-w-4xl mx-auto py-8">
            <motion.div initial={{opacity:0, scale:0.95}} animate={{opacity:1, scale:1}} className="glass-card p-6 mb-8 border-l-2 border-l-[#D4AF37]">
                <h3 className="text-[#D4AF37] font-black text-xs tracking-widest mb-4">🚀 NEW SIGNAL BROADCAST</h3>
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-4">
                    <input value={nickname} onChange={e=>setNickname(e.target.value)} placeholder="NICKNAME" className="bg-white/5 border border-white/10 rounded p-2 text-sm outline-none focus:border-[#D4AF37]"/>
                    <textarea value={content} onChange={e=>setContent(e.target.value)} placeholder="Market intelligence, alpha, or trader thoughts..." className="md:col-span-3 bg-white/5 border border-white/10 rounded p-2 text-sm outline-none focus:border-[#D4AF37] h-20"/>
                </div>
                <div className="flex flex-wrap items-center gap-4">
                    <div className="flex items-center gap-2 bg-white/5 border border-white/10 px-3 py-1 rounded">
                       <span className="text-[10px] font-bold text-[#AAA]">HUMAN? {captcha.q} =</span>
                       <input value={captchaInput} onChange={e=>setCaptchaInput(e.target.value)} className="w-10 bg-transparent outline-none text-[#D4AF37] font-bold"/>
                    </div>
                    <input value={honeypot} onChange={e=>setHoneypot(e.target.value)} style={{display:'none'}}/>
                    <button onClick={handleBroadcast} disabled={loading} className="ml-auto bg-[#D4AF37] text-black font-black text-xs px-6 py-2 rounded hover:bg-[#FCF6BA] transition-all flex items-center gap-2">
                        {loading ? "SENDING..." : <><Send size={14}/> BROADCAST</>}
                    </button>
                </div>
            </motion.div>

            <div className="space-y-4">
                <AnimatePresence mode="popLayout">
                    {posts.map(p => (
                        <motion.div key={p.id} layout initial={{opacity:0, x:-20}} animate={{opacity:1, x:0}} exit={{opacity:0, scale:0.95}} className="glass-card p-5 relative group overflow-hidden">
                            <div className="flex justify-between items-center mb-2 border-b border-white/5 pb-2">
                                <span className="font-fira font-black text-[#D4AF37] text-xs">/// {p.nickname.toUpperCase()}</span>
                                <span className="text-[9px] text-[#555] font-fira">{p.timestamp}</span>
                            </div>
                            <div className="text-sm text-[#EEE] leading-relaxed whitespace-pre-wrap">{p.content}</div>
                            {isAdmin && (
                                <button onClick={()=>handleDelete(p.id)} className="absolute top-4 right-4 text-red-500/50 hover:text-red-500 transition-all">
                                    <Trash2 size={14}/>
                                </button>
                            )}
                            <div className="absolute inset-0 bg-gradient-to-r from-transparent via-[#D4AF37]/5 to-transparent -translate-x-full group-hover:animate-[shimmer_2s_infinite]"></div>
                        </motion.div>
                    ))}
                </AnimatePresence>
            </div>
        </div>
    )
}

export default function App() {
  const [coins, setCoins] = useState([]);
  const [search, setSearch] = useState("");
  const [sortMode, setSortMode] = useState("Market Cap");
  const [activeTab, setActiveTab] = useState("DASHBOARD");
  const [adminKey, setAdminKey] = useState("");
  const isAdmin = adminKey === "admin123";

  useEffect(() => {
    const fetchData = async () => {
        try {
            const res = await fetch("http://127.0.0.1:8001/api/crypto");
            if(res.ok) {
                const data = await res.json();
                setCoins(data);
            }
        } catch(e) { console.error("Oracle fetch failed", e); }
    };
    fetchData();
    const interval = setInterval(fetchData, 60000);
    return () => clearInterval(interval);
  }, []);

  const processedCoins = useMemo(() => {
      let data = coins.map(c => {
          const prices = c.sparkline_in_7d?.price || [];
          const mcap = c.market_cap || 1;
          const vol = c.total_volume || 0;
          return {
              ...c,
              _rsi: calculate_rsi(prices),
              _change: c.price_change_percentage_24h || 0,
              _turnover: (vol / mcap) * 100,
              _prices: prices,
              _ma: calculate_ma_cross(prices)
          };
      });

      if (search) {
          data = data.filter(c => 
              c.name.toLowerCase().includes(search.toLowerCase()) || 
              c.symbol.toLowerCase().includes(search.toLowerCase())
          );
      }

      data.sort((a, b) => {
          if (sortMode === "Gainers") return b._change - a._change;
          if (sortMode === "RSI Overbought") return b._rsi - a._rsi;
          if (sortMode === "RSI Oversold") return a._rsi - b._rsi;
          if (sortMode === "Volume") return b._turnover - a._turnover;
          return (a.market_cap_rank || 999) - (b.market_cap_rank || 999);
      });

      return data.slice(0, 50);
  }, [coins, search, sortMode]);

  const handleTearOut = () => {
      try { if(navigator.vibrate) navigator.vibrate([100,50,100]); } catch(e) {}
      new Audio('https://assets.mixkit.co/active_storage/sfx/2573/2573-preview.mp3').play().catch(e=>{});
  };

  return (
    <div className="min-h-screen p-8" style={{ background: 'radial-gradient(circle at top center, #0a0a0a 0%, #000000 100%)' }}>
      {/* Header Matrix Layer */}
      <div className="fixed inset-0 pointer-events-none z-[-1]" style={{
          backgroundImage: 'linear-gradient(rgba(212, 175, 55, 0.03) 1px, transparent 1px), linear-gradient(90deg, rgba(212, 175, 55, 0.03) 1px, transparent 1px)',
          backgroundSize: '30px 30px', animation: 'gridMove 20s linear infinite'
      }}/>

      <div className="max-w-7xl mx-auto">
        <div className="flex flex-col md:flex-row md:items-center mb-6 border-b border-[rgba(212,175,55,0.2)] pb-6 gap-6">
            <div className="flex items-center">
                <svg width="32" height="32" viewBox="0 0 24 24" fill="none" style={{ filter: 'drop-shadow(0 0 10px rgba(212,175,55,0.6))', marginRight: '15px' }}>
                    <path d="M12 2L2 7L12 12L22 7L12 2Z" fill="url(#goldGrad)" />
                    <path d="M2 17L12 22L22 17" stroke="url(#goldGrad)" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                    <path d="M2 12L12 17L22 12" stroke="url(#goldGrad)" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                    <defs><linearGradient id="goldGrad" x1="0" y1="0" x2="24" y2="24"><stop stopColor="#BF953F"/><stop offset="0.5" stopColor="#FCF6BA"/><stop offset="1" stopColor="#B38728"/></linearGradient></defs>
                </svg>
                <h1 className="text-3xl font-black tracking-tight font-inter">COIN<span className="gold-gradient-text px-1">PT</span> 
                   <span className="ml-3 text-[10px] px-2 py-1 border border-[#D4AF37] text-[#D4AF37] rounded font-bold">TERMINAL PRO [VITE]</span>
                </h1>
            </div>
            
            {/* TABS */}
            <div className="flex bg-white/5 p-1 rounded-lg border border-white/10">
                <button onClick={()=>setActiveTab('DASHBOARD')} className={`flex items-center gap-2 px-6 py-1.5 rounded-md text-xs font-bold transition-all ${activeTab==='DASHBOARD' ? 'bg-[#D4AF37] text-black shadow-lg shadow-[#D4AF37]/20' : 'text-[#AAA] hover:text-white'}`}>
                    <LayoutDashboard size={14}/> DASHBOARD
                </button>
                <button onClick={()=>setActiveTab('SOCIAL')} className={`flex items-center gap-2 px-6 py-1.5 rounded-md text-xs font-bold transition-all ${activeTab==='SOCIAL' ? 'bg-[#D4AF37] text-black shadow-lg shadow-[#D4AF37]/20' : 'text-[#AAA] hover:text-white'}`}>
                    <Satellite size={14}/> GLOBAL FEED
                </button>
            </div>

            <div className="md:ml-auto flex items-center gap-4">
                <ShieldAlert size={14} className={isAdmin ? "text-[#D4AF37]" : "text-[#333]"} />
                <input type="password" value={adminKey} onChange={e=>setAdminKey(e.target.value)} placeholder="0000" className="w-12 bg-transparent border-b border-white/10 text-[10px] text-center focus:border-[#D4AF37] outline-none text-[#555]"/>
                
                {activeTab === 'DASHBOARD' && (
                    <>
                        <input 
                        type="text" 
                        placeholder="SCAN PROTOCOLS..." 
                        value={search} 
                        onChange={e => setSearch(e.target.value)}
                        className="bg-black/50 border border-white/10 text-white px-4 py-2 rounded-lg outline-none focus:border-[#D4AF37] transition-all font-fira text-xs w-48"
                        />
                        <select 
                        value={sortMode} 
                        onChange={e => setSortMode(e.target.value)}
                        className="bg-black/50 border border-white/10 text-[#D4AF37] px-4 py-2 rounded-lg outline-none font-bold text-sm cursor-pointer"
                        >
                        <option>Market Cap</option>
                        <option>Gainers</option>
                        <option>Volume</option>
                        <option>RSI Overbought</option>
                        <option>RSI Oversold</option>
                        </select>
                    </>
                )}
            </div>
        </div>

        <motion.div initial={{opacity:0, y:10}} animate={{opacity:1, y:0}} transition={{duration:0.4}}>
            {activeTab === 'DASHBOARD' ? (
                <div className="grid gap-4">
                <AnimatePresence mode="popLayout">
                    {processedCoins.map((coin, index) => {
                        const isPos = coin._change >= 0;
                        let rank = coin.market_cap_rank === 1 ? "🥇" : coin.market_cap_rank === 2 ? "🥈" : coin.market_cap_rank === 3 ? "🥉" : coin.market_cap_rank;
                        if(!rank) rank = "-";

                        const rsiColor = coin._rsi > 70 ? "#f87171" : (coin._rsi < 30 ? "#4ade80" : "#AAA");
                        const iconGlow = isPos ? "rgba(74, 222, 128, 0.4)" : "rgba(248, 113, 113, 0.4)";
                        const iconBorder = isPos ? "#4ade80" : "#f87171";

                        const tvSym = coin.symbol.toUpperCase() === 'USDT' || coin.symbol.toUpperCase() === 'USDC' ? `${coin.symbol.toUpperCase()}USD` : (coin.symbol.toUpperCase() !== 'BTC' && coin.symbol.toUpperCase() !== 'ETH' ? `${coin.symbol.toUpperCase()}USDT` : coin.symbol.toUpperCase());
                        
                        return (
                        <motion.div 
                            layout
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            exit={{ opacity: 0, scale: 0.95 }}
                            transition={{ duration: 0.3 }}
                            key={coin.id} 
                            className="glass-card p-5 hover:border-l-4 hover:border-l-[#D4AF37] transition-all duration-300 hover:-translate-y-1 hover:shadow-2xl hover:shadow-[#D4AF37]/10"
                        >
                            <div className="grid grid-cols-1 md:grid-cols-[2fr_2fr_2fr_1.5fr] gap-6 items-center">
                                <div className="flex items-center">
                                    <span className="w-10 text-[#AAA] font-fira font-bold text-sm">{rank}</span>
                                    <img src={coin.image} alt={coin.name} className="w-12 h-12 rounded-full mr-4 bg-[#111] p-[2px] object-cover" style={{ boxShadow: `0 0 15px ${iconGlow}`, border: `1.5px solid ${iconBorder}` }} />
                                    <div className="flex flex-col">
                                        <span className="font-bold text-lg">{coin.name} <span className="text-[#888] text-xs ml-1">{coin.symbol.toUpperCase()}</span></span>
                                        <span className="text-xs font-bold text-[#b38728] mt-1">{coin.market_cap > 50e9 ? "👑 Blue Chip" : "🛡️ Core Asset"}</span>
                                    </div>
                                </div>

                                <div className="flex flex-col gap-1">
                                    <div className="font-fira text-xs text-[#AAA]">
                                        <span style={{color: rsiColor, fontWeight: '800'}}>RSI {coin._rsi.toFixed(1)}</span>
                                    </div>
                                    <div className="text-[10px] text-[#888] font-inter">
                                        Vol: ${formatCompact(coin.total_volume)} ({coin._turnover.toFixed(1)}% TR)
                                    </div>
                                </div>

                                <div className="flex flex-col md:ml-4">
                                    <div className="flex items-center gap-2 mb-2 text-[10px] font-black tracking-wider px-2 py-1 rounded" style={{border: `1px solid ${coin._ma.border}`, color: coin._ma.color, width: 'fit-content'}}>
                                        {coin._ma.text}
                                    </div>
                                    <SparklineSVG prices={coin._prices} isPos={isPos} />
                                </div>

                                <div className="flex flex-col items-end pr-4">
                                    <div className="font-fira text-2xl font-black">${formatPrice(coin.current_price)}</div>
                                    <div className={`font-bold text-sm ${isPos ? "text-[#4ade80]" : "text-[#f87171]"}`}>
                                        {isPos ? "+" : ""}{coin._change.toFixed(2)}%
                                    </div>
                                    <a href={`https://www.tradingview.com/chart/?symbol=${tvSym}`} target="_blank" onClick={handleTearOut} className="mt-3 flex items-center justify-center gap-2 w-full max-w-[120px] py-[6px] border border-white/10 rounded font-fira text-[9px] text-[#AAA] hover:bg-[#D4AF37]/10 hover:border-[#D4AF37] hover:text-white transition-all cursor-pointer relative overflow-hidden group">
                                    <Maximize2 size={10} /> TEAR-OUT
                                    <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/10 to-transparent -translate-x-full group-hover:animate-[shimmer_1.5s_infinite]"></div>
                                    </a>
                                </div>
                            </div>
                        </motion.div>
                        )
                    })}
                </AnimatePresence>
                </div>
            ) : (
                <SocialFeed isAdmin={isAdmin} />
            )}
        </motion.div>
      </div>
      <style dangerouslySetInnerHTML={{__html: `
        @keyframes shimmer { 100% { transform: translateX(100%); } }
        @keyframes gridMove { 0% { background-position: 0 0; } 100% { background-position: 30px 30px; } }
      `}}/>
    </div>
  );
}

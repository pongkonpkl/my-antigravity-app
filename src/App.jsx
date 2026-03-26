import React, { useState, useEffect, useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Activity, Target, Satellite, Maximize2 } from 'lucide-react';

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

export default function App() {
  const [coins, setCoins] = useState([]);
  const [search, setSearch] = useState("");
  const [sortMode, setSortMode] = useState("Market Cap");

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
        <div className="flex items-center mb-10 border-b border-[rgba(212,175,55,0.2)] pb-6">
            <svg width="32" height="32" viewBox="0 0 24 24" fill="none" style={{ filter: 'drop-shadow(0 0 10px rgba(212,175,55,0.6))', marginRight: '15px' }}>
                <path d="M12 2L2 7L12 12L22 7L12 2Z" fill="url(#goldGrad)" />
                <path d="M2 17L12 22L22 17" stroke="url(#goldGrad)" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                <path d="M2 12L12 17L22 12" stroke="url(#goldGrad)" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                <defs><linearGradient id="goldGrad" x1="0" y1="0" x2="24" y2="24"><stop stopColor="#BF953F"/><stop offset="0.5" stopColor="#FCF6BA"/><stop offset="1" stopColor="#B38728"/></linearGradient></defs>
            </svg>
            <h1 className="text-4xl font-black tracking-tight font-inter">COIN<span className="gold-gradient-text px-1">PT</span> 
               <span className="ml-4 text-sm px-2 py-1 border border-[#D4AF37] text-[#D4AF37] rounded-md font-bold">TERMINAL PRO [REACT NATIVE]</span>
            </h1>
            <div className="ml-auto flex gap-4">
                <input 
                   type="text" 
                   placeholder="SCAN PROTOCOLS..." 
                   value={search} 
                   onChange={e => setSearch(e.target.value)}
                   className="bg-black/50 border border-white/10 text-white px-4 py-2 rounded-lg outline-none focus:border-[#D4AF37] transition-all font-fira text-sm w-64"
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
            </div>
        </div>

        <div className="grid gap-4">
          <AnimatePresence>
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
                    <div className="grid grid-cols-[2fr_2fr_2fr_1fr] gap-6 items-center">
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

                        <div className="flex flex-col ml-4">
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
      </div>
      <style dangerouslySetInnerHTML={{__html: `
        @keyframes shimmer { 100% { transform: translateX(100%); } }
        @keyframes gridMove { 0% { background-position: 0 0; } 100% { background-position: 30px 30px; } }
      `}}/>
    </div>
  );
}

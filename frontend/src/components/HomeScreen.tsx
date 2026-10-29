'use client';
import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { ArrowRight, Check, Compass, BookOpen, Shield, Sparkles, Waves, Radio, Crown, Loader2 } from 'lucide-react';
import { usePlayerSession } from '@/hooks/usePlayerSession';
import { useGameContext } from '@/components/GameContext';

const worlds = [
  {title:'The Clockwork Tide', genre:'01 / Brass & betrayal', description:'A sinking city. A stolen engine. The one ally you cannot afford to lose.', world:'A clockwork city above a rising sea. A stolen heart-engine is sinking the harbor; Sinbad must choose between his promise to pilot Mara and the city council that betrayed her.', tag:'Rescue · Loyalty · Sabotage', icon:Waves},
  {title:'The Ninth Signal', genre:'02 / Beyond the known', description:'An abandoned station is broadcasting your voice. The message is tomorrow’s.', world:'An abandoned orbital station broadcasts Sinbad’s voice describing a catastrophe tomorrow. Engineer Imani wants to save the sleeping colonists; the station commander wants to erase the signal and everyone who heard it.', tag:'Infiltration · Mystery · Sacrifice', icon:Radio},
  {title:'The Ashen Crown', genre:'03 / A kingdom divided', description:'Your sister leads the rebellion. The crown has just chosen you.', world:'A kingdom of ash and living oaths. Sinbad is named heir by a sentient crown while his sister leads the rebellion. Their childhood friend guards the prison holding the only witness to the old king’s murder.', tag:'Combat · Family · Allegiance', icon:Crown},
];
export default function HomeScreen() {
  const sessionId = usePlayerSession();
  const router = useRouter();
  const {setGameData} = useGameContext();
  const [world,setWorld] = useState(worlds[0].world);
  const [selected,setSelected] = useState(0);
  const [turns,setTurns] = useState(30);
  const [custom,setCustom] = useState(false);
  const [saved,setSaved] = useState<GameMemory | null>(null);
  const [starting,setStarting] = useState(false);
  const [error,setError] = useState('');
  useEffect(()=>{
    if (!sessionId) return;
    let cancelled = false;
    fetch('/api/init',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({session_id:sessionId,action:'load'})})
      .then(res=>res.ok ? res.json() : null).then(data=>{if(!cancelled && data?.status==='loaded')setSaved(data.latest_memory_data);}).catch(()=>{});
    return ()=>{cancelled=true;};
  },[sessionId]);
  async function start() {
    if (starting || !sessionId || !world.trim() || turns < 5 || turns > 60) return;
    setStarting(true);setError('');
    try {
      const res = await fetch('/api/init',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({session_id:sessionId,action:'new',world:world.trim(),total_turns:turns})});
      const data = await res.json();
      if(!res.ok) throw new Error(data.detail || 'Your adventure could not start. Please retry.');
      localStorage.removeItem('loadedMemory');
      setGameData({worldName:world.trim(),totalTurns:turns});router.push('/game');
    } catch(e){setError(e instanceof Error ? e.message : 'Please retry.');setStarting(false);}
  }
  function resume(){if(!saved)return;localStorage.setItem('loadedMemory',JSON.stringify(saved));setGameData({loaded:saved});router.push('/game');}
  return <div className="sb-home">
    <div className="sb-home-topline"><span className="sb-eyebrow"><Sparkles size={12}/>An adventure shaped by you</span><span>GENERATIVE WORLDS. HUMAN CHOICES.</span></div>
    <section className="sb-home-hero">
      <div><h1>Every choice leaves<br/>a <em>different world.</em></h1><p className="sb-home-lede">Step into a story with people worth caring about. Take on missions, outthink your opponents, and decide what you are willing to lose.</p><div className="sb-home-proof"><span><Compass size={13}/>Your world</span><span><Shield size={13}/>Playable encounters</span><span><BookOpen size={13}/>A real ending</span></div></div>
      <div className="sb-launch-card"><div className="sb-launch-heading"><span className="sb-eyebrow">The first page is yours</span><span>↗</span></div><h2>Where does your story begin?</h2><label className="sb-field-label" htmlFor="world-description">Your world & its conflict</label><textarea id="world-description" rows={3} maxLength={1200} value={world} onChange={e=>{setWorld(e.target.value);setSelected(-1);}} placeholder="A world, a conflict, someone worth saving…"/>
        <label className="sb-field-label">How long is the adventure?</label><div className="sb-lengths">{[10,20,30].map(n=><button key={n} aria-pressed={!custom && turns===n} className={!custom && turns===n?'is-active':''} onClick={()=>{setTurns(n);setCustom(false);}}>{n} beats<small>{n===10?'A short story':n===20?'A deeper journey':'The full adventure'}</small></button>)}<button aria-pressed={custom} className={custom?'is-active':''} onClick={()=>setCustom(true)}>Custom<small>Your own pace</small></button></div>{custom && <label className="sb-custom-length">Story beats (5–60)<input aria-label="Custom story length" type="number" min={5} max={60} value={turns} onChange={e=>setTurns(Number(e.target.value))}/></label>}
        <button className="sb-primary" onClick={start} disabled={starting || !sessionId || !world.trim() || turns<5 || turns>60}>{starting?<><Loader2 size={16} className="sb-spin"/>Opening your adventure</>:<>Begin your adventure <ArrowRight size={17}/></>}</button><p className="sb-launch-note">Play as a guest or sign in with Google. Each committed approach shapes the story.</p>{error && <p className="sb-home-error" role="alert">{error}</p>}
        {saved && <div className="sb-resume"><BookOpen size={18}/><div><strong>{saved.game_state.story_flags.is_complete?'Revisit your finished story':'Your last story is waiting'}</strong><small>Beat {saved.scenes_completed} / {saved.game_state.story_flags.total_turns || 30} · {saved.location.replaceAll('_',' ')}</small></div><button onClick={resume}>Resume ↗</button></div>}
      </div>
    </section>
    <section className="sb-worlds"><div className="sb-worlds-heading"><span className="sb-eyebrow">Three doors. Entirely different stories.</span><span>Choose a starting point, or write your own above.</span></div><div className="sb-world-grid">{worlds.map((w,i)=><button key={w.title} aria-pressed={selected===i} onClick={()=>{setSelected(i);setWorld(w.world);}} className={`sb-world-card ${selected===i?'is-active':''}`}><small>{w.genre}</small>{selected===i?<Check size={17}/>:<w.icon size={18}/>}<h3>{w.title}</h3><p>{w.description}</p><span>{w.tag}</span></button>)}</div></section>
    <footer className="sb-home-footer"><span>SINBAD AI / A story worth finishing.</span><span>Planned arcs. Persistent consequences. A path only you could take.</span></footer>
  </div>;
}

'use client';
import React, { useState } from 'react';
import AccountButton from './AccountButton';
import { useGameLogic } from '@/hooks/useGameLogic';
import { ArrowUpRight, ArrowLeft, ArrowRight, Swords, Shield, Crosshair, Package, BookOpen, Users, Target, Sparkles, Check, X, Flag, ChevronRight, Compass, Loader2, Gem, Heart, Eye } from 'lucide-react';

const initials = name => (name || '?').split(' ').map(n => n[0]).slice(0,2).join('');

export default function SinbadGame() {
  const { scene, loading, error, gameProgress, initialized, handleChoice, playEncounter, retry, journal, lore } = useGameLogic();
  const [approach, setApproach] = useState('');
  const [tab, setTab] = useState('story');
  const [selectedCharacter, setSelectedCharacter] = useState(null);
  const [selectedItem, setSelectedItem] = useState(null);
  const [selectedObject, setSelectedObject] = useState(null);
  const flags = scene?.game_state?.story_flags || {};
  const presentation = flags.presentation || {};
  const encounter = flags.encounter;
  const activeEncounter = encounter?.status === 'active';
  const complete = Boolean(flags.is_complete);
  const total = flags.total_turns || 30;
  const turn = Number(flags.turn || gameProgress.scenes_completed || 0);
  const mission = presentation.mission;
  const cast = Object.values(flags.cast || {}).length ? Object.values(flags.cast) : scene?.characters || [];
  const inventory = scene?.current_inventory || [];
  const artifacts = inventory.filter(item => !['consumable','food','potion','medical'].includes(item.item_type.toLowerCase()));
  const actionable = !loading && !complete;

  return <div className="sb-app">
    <header className="sb-game-header">
      <a className="sb-brand" href="/"><span className="sb-monogram">S</span><span>SINBAD<span className="sb-brand-ai"> / AI</span></span></a>
      <div className="sb-header-world"><Compass size={14}/><span>{scene?.world?.length > 80 ? (presentation.chapter_title || 'Your world') : scene?.world || 'A new world is taking shape'}</span></div>
      <AccountButton/><a href="/" className="sb-text-link"><ArrowLeft size={14}/><span>Adventures</span></a>
    </header>
    <div className="sb-campaign-bar"><span><i className="sb-live-dot"/>{complete ? 'Adventure complete' : loading ? 'The world is responding' : 'Adventure in progress'}</span><div className="sb-campaign-track"><span style={{width:`${turn / total * 100}%`}}/></div><span className="sb-mono">{String(turn).padStart(2,'0')} <span className="sb-dim">/ {total} story turns</span></span></div>

    {error && <div className="sb-alert" role="alert"><span>{error}</span><button onClick={retry} disabled={loading}>Retry action <ArrowRight size={14}/></button><a href="/">Return home</a></div>}
    {!scene ? <div className="sb-loading"><div className="sb-orbit"><Compass size={38}/></div><span className="sb-eyebrow">{initialized ? 'Writing the opening chapter' : 'Opening your journal'}</span><h1>A world worth getting lost in.</h1><p>Establishing the cast, the conflict, and where this story might end.</p><p className="sb-dim">Your opening scene will appear here. Model rate limits can take a moment.</p></div> :
    <div className="sb-game-grid">
      <aside className="sb-left-rail">
        <div className="sb-rail-label"><span className="sb-eyebrow">Your adventure</span><span className="sb-small-index">01</span></div>
        <nav className="sb-view-nav" aria-label="Adventure views">
          <button className={tab === 'story' ? 'is-active' : ''} onClick={()=>setTab('story')}><Compass size={17}/>The story<ChevronRight size={14}/></button>
          <button className={tab === 'journal' ? 'is-active' : ''} onClick={()=>setTab('journal')}><BookOpen size={17}/>Journal<span>{journal.length}</span></button>
          <button className={tab === 'collection' ? 'is-active' : ''} onClick={()=>setTab('collection')}><Gem size={17}/>Collectibles<span>{artifacts.length + lore.length}</span></button>
        </nav>
        <section className="sb-rail-section"><div className="sb-section-label"><Package size={14}/><h2>Your satchel</h2><span>{inventory.reduce((n,i)=>n+i.quantity,0)}</span></div>
          {inventory.length ? <div className="sb-item-grid">{inventory.map(item=><button key={item.name} className="sb-item" onClick={()=>setSelectedItem(item)} title={item.description}><span className="sb-item-icon">{/artifact|relic|collectible|quest|key|evidence|token|clue/i.test(item.item_type)?<Gem size={20}/>:<Package size={20}/>}</span><span>{item.name}</span><small>×{item.quantity}</small></button>)}</div> : <div className="sb-empty"><Package size={22}/><p>Travel light, for now.</p><small>Useful objects and earned artifacts will appear here.</small></div>}
        </section>
        <div className="sb-rail-note"><BookOpen size={16}/><div><strong>You decide. The world responds.</strong><p>Choose an approach or describe your own. Allies, objects, and earlier decisions shape what happens next.</p></div></div>
        <div className="sb-save-note"><Check size={13}/>{loading ? 'Resolving your action…' : 'Progress saved in this browser'}</div>
      </aside>

      <main className="sb-story-column">
        <div className="sb-chapter-heading"><span className="sb-eyebrow">{complete ? 'Epilogue' : `Chapter ${String(Math.ceil(turn / Math.max(1,total/3))).padStart(2,'0')} / ${flags.story_phase || 'setup'}`}</span><span className="sb-location"><span/> {scene.location === 'starting_area' ? 'Opening scene' : scene.location?.replaceAll('_',' ')}</span></div>
        {tab === 'story' ? <>
          <div className="sb-story-title"><h1>{presentation.scene_title || 'The next turning point'}</h1><p>{presentation.chapter_title || scene.mood_atmosphere}</p>{activeEncounter && <a className="sb-jump-to-mission" href="#active-encounter"><Swords size={13}/>An obstacle stands in your way <ArrowRight size={13}/></a>}</div>
          {loading && <div className="sb-thinking" role="status"><Loader2 size={15} className="sb-spin"/>{activeEncounter ? 'Resolving your move…' : 'Following the consequences of your decision…'}</div>}
          <article className={`sb-prose ${loading ? 'is-pending' : ''}`} key={scene.scene_tag}><span className="sb-story-rule"/>{scene.narration_text.split(/\n+/).filter(Boolean).map((paragraph,i)=><p key={i}>{paragraph}</p>)}</article>
          {scene.dialogue?.filter(line=>!line.is_internal_thought).slice(0,3).map((line,i)=><div className="sb-dialogue" key={`${scene.scene_tag}-${i}`}><span className="sb-avatar sb-avatar-small">{initials(line.speaker)}</span><div><span className="sb-dialogue-name">{line.speaker}<small>{line.emotion}</small></span><p>“{line.text}”</p></div></div>)}

          {encounter && <section id="active-encounter" className="sb-encounter" aria-label="Scene challenge"><span className="sb-eyebrow"><Swords size={13}/>The challenge · {encounter.kind}</span><h2>{encounter.title}</h2><p className="sb-encounter-description">{encounter.description}</p><p className="sb-dim">Your approach below determines how this plays out. You can also use the surroundings or ask an ally for help.</p></section>}

          {!complete && scene.interactive_elements?.length > 0 && <section className="sb-scene-objects"><div className="sb-section-label"><Crosshair size={14}/><h2>Within reach</h2><small>Inspect freely</small></div><div>{scene.interactive_elements.map(object=><button key={object.id} onClick={()=>setSelectedObject(object)}><span className="sb-object-glyph">◇</span><span>{object.name}<small>Inspect object</small></span><ArrowUpRight size={14}/></button>)}</div></section>}
          {complete ? <section className="sb-ending"><Flag size={24}/><span className="sb-eyebrow">Your story, concluded</span><h2>Some journeys change everything.</h2><p>{presentation.ending_summary || 'Your adventure has reached its final chapter. Its consequences live in your journal.'}</p><div className="sb-ending-stats"><span>{turn} story turns</span><span>{scene.game_state.completed_objectives?.length || 0} objectives completed</span><span>{artifacts.length} artifacts collected</span></div><a className="sb-primary" href="/">Begin another story <ArrowRight size={16}/></a></section> : <section className="sb-decisions"><div className="sb-decision-label"><span className="sb-eyebrow">A decision that matters</span><span>Advances the story · 1 story turn</span></div>{scene.options?.map((option,i)=><button key={i} onClick={()=>handleChoice(option,'narrative_choice',undefined,undefined,i)} disabled={!actionable}><span className="sb-choice-index">0{i+1}</span><span><strong>{option}</strong>{presentation.choice_stakes?.[i] && <small>{presentation.choice_stakes[i]}</small>}</span><ArrowUpRight size={19}/></button>)}<form className="sb-custom-approach" onSubmit={e=>{e.preventDefault();if(approach.trim()){handleChoice(approach.trim(),'narrative_choice');setApproach('');}}}><label htmlFor="custom-approach">Or take your own approach</label><textarea id="custom-approach" value={approach} onChange={e=>setApproach(e.target.value)} maxLength={1200} placeholder="Describe what you attempt, who you involve, or which object you use…" disabled={!actionable}/><button type="submit" disabled={!actionable || !approach.trim()}><span>Commit to your approach · 1 story turn</span><ArrowRight size={16}/></button></form></section>}
        </> : tab === 'journal' ? <section className="sb-journal"><span className="sb-eyebrow">The record of your choices</span><h1>What you leave behind.</h1>{journal.map((entry,i)=><div key={i}><span>{String(i+1).padStart(2,'0')}</span><p>{entry}</p></div>)}{!journal.length && <p>Your first chapter is still being written.</p>}</section> : <section className="sb-collection"><span className="sb-eyebrow">Objects & discoveries</span><h1>Things with a story.</h1><p>Objects you earned. Secrets you uncovered. Each belongs to this world.</p>{artifacts.map(item=><button key={item.name} onClick={()=>setSelectedItem(item)}><Gem/><h2>{item.name}</h2><p>{item.description}</p></button>)}{lore.map((entry,i)=><article key={entry.id || i}><span className="sb-eyebrow">{entry.category}</span><h2>{entry.title}</h2><p>{entry.content}</p></article>)}{!artifacts.length && !lore.length && <div className="sb-empty"><Gem size={28}/><p>No trophies without a journey.</p><small>Complete missions and inspect the world to uncover meaningful collectibles.</small></div>}</section>}
      </main>

      <aside className="sb-right-rail"><section className="sb-mission-card"><div className="sb-section-label"><Target size={15}/><h2>{complete ? 'The final chapter' : 'Current mission'}</h2></div><span className="sb-mission-mark">{complete ? '✓' : '↗'}</span><h3>{mission?.title || scene.game_state.active_objectives?.[0]?.description || 'Find your place in this world'}</h3><p>{mission?.objective || 'Your next decision will reveal the way forward.'}</p>{mission?.stakes && <div className="sb-mission-stakes"><span className="sb-eyebrow">What is at stake</span><p>{mission.stakes}</p></div>}<div className="sb-mission-state"><i/>{complete ? 'Campaign concluded' : activeEncounter ? 'Encounter in progress' : encounter?.status === 'won' ? 'Encounter secured · Choose your next move' : 'Your approach will shape the outcome'}</div></section>
        <section className="sb-rail-section"><div className="sb-section-label"><Users size={14}/><h2>The cast</h2><span>{cast.length}</span></div><p className="sb-rail-caption">Allies have their own reasons.</p><div className="sb-cast">{cast.map(character=><button key={character.id} onClick={()=>setSelectedCharacter(character)}><span className="sb-avatar">{initials(character.name)}</span><span><strong>{character.name}</strong><small>{character.faction || character.current_mood || 'A story of their own'}</small><span className="sb-relationship"><i style={{width:`${(Number(scene.game_state.relationships?.[character.id] ?? character.relationship_level ?? 0)+10)*5}%`}}/></span></span><ArrowUpRight size={13}/></button>)}</div>{!cast.length && <p className="sb-muted-copy">The important people in your story will appear here.</p>}</section>
        <div className="sb-chapter-note"><Sparkles size={15}/><p>A planned destination.<br/><em>Your way of getting there.</em></p></div>
      </aside>
    </div>}

    {(selectedCharacter || selectedItem || selectedObject) && <div className="sb-modal-backdrop" onClick={()=>{setSelectedCharacter(null);setSelectedItem(null);setSelectedObject(null);}}><section className="sb-modal" role="dialog" aria-modal="true" aria-label="Inspect detail" onClick={e=>e.stopPropagation()}><button className="sb-modal-close" aria-label="Close details" onClick={()=>{setSelectedCharacter(null);setSelectedItem(null);setSelectedObject(null);}}><X size={19}/></button>
      {selectedCharacter && <><span className="sb-eyebrow">Character dossier · Inspection is free</span><div className="sb-avatar sb-avatar-large">{initials(selectedCharacter.name)}</div><h2>{selectedCharacter.name}</h2><p>{selectedCharacter.backstory || selectedCharacter.current_mood}</p><span className="sb-eyebrow">What they want</span>{selectedCharacter.personal_objectives?.map((objective,i)=><p key={i}>{objective}</p>)}<span className="sb-eyebrow">What they remember</span>{selectedCharacter.memories?.length ? selectedCharacter.memories.map((memory,i)=><p key={i}>{memory}</p>) : <p>Your history with them is still unfolding.</p>}<p className="sb-dim">Their priorities and your relationship influence the director's next story beat.</p></>}
      {selectedItem && <><span className="sb-eyebrow">{selectedItem.item_type} · In your possession</span><Gem className="sb-detail-icon" size={36}/><h2>{selectedItem.name}</h2><p>{selectedItem.description}</p><div className="sb-detail-facts"><span>Quantity <strong>{selectedItem.quantity}</strong></span><span>Durability <strong>{selectedItem.durability}%</strong></span></div>{!complete && <><p className="sb-dim">Use this item's established abilities in the scene. The next passage explains its effect and any consumption or wear.</p><button className="sb-primary" disabled={!actionable || selectedItem.durability === 0} onClick={()=>{handleChoice(`Use ${selectedItem.name} in a way consistent with its description to address the current obstacle`, 'item_interaction',selectedItem.name,'inventory_item');setSelectedItem(null);}}>Use in this scene · 1 story turn <ArrowRight size={16}/></button></>}</>}
      {selectedObject && <><span className="sb-eyebrow">Scene object · Inspection is free</span><Crosshair className="sb-detail-icon" size={36}/><h2>{selectedObject.name}</h2><p>{selectedObject.description}</p>{selectedObject.requires_items?.length > 0 && <p className="sb-dim">Requires: {selectedObject.requires_items.join(', ')}</p>}<button className="sb-primary" disabled={!actionable || selectedObject.requires_items?.some(name=>!inventory.some(item=>item.name.toLowerCase()===name.toLowerCase() && item.durability > 0))} onClick={()=>{handleChoice(selectedObject.options?.[0] || `Commit to using ${selectedObject.name} to advance the mission`, 'item_interaction',selectedObject.id,'interactive_element');setSelectedObject(null);}}>Commit to this approach · 1 story turn <ArrowRight size={16}/></button></>}
    </section></div>}
  </div>;
}

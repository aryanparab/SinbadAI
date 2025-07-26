'use client';
import React, { useState, useEffect } from 'react';
import { useGameLogic } from '@/hooks/useGameLogic';
import { getThemeClasses, getThreatColor, getResourceColor, getWeatherIcon } from '@/themes/themes';
import { 
  Heart, 
  Shield, 
  Sword, 
  Package, 
  Users, 
  MapPin, 
  Clock, 
  AlertTriangle, 
  Eye,
  Thermometer,
  Cloud,
  Target,
  Book,
  Zap,
  ChevronRight,
  MessageCircle,
  Sparkles,
  Crown,
  Skull,
  Palette
} from 'lucide-react';

const SurvivalRPGGame = () => {
  const { scene, loading, error, gameProgress, initialized, handleChoice } = useGameLogic();
  const [selectedOption, setSelectedOption] = useState(null);
  const [showInventory, setShowInventory] = useState(false);
  const [showLore, setShowLore] = useState(false);
  const [animatingText, setAnimatingText] = useState('');
  const [currentTheme, setCurrentTheme] = useState('default');
  const [showThemeSelector, setShowThemeSelector] = useState(false);

  // Get theme classes
  const theme = getThemeClasses(currentTheme);

  // Available themes list
  const availableThemes = [
    { key: 'default', name: 'Mystic Purple' },
    { key: 'cyberpunk', name: 'Neon Cyberpunk' },
    { key: 'forest', name: 'Dark Forest' },
    { key: 'volcanic', name: 'Volcanic Fire' },
    { key: 'arctic', name: 'Arctic Ice' },
    { key: 'desert', name: 'Desert Sands' }
  ];

  // Text animation effect
  useEffect(() => {
    if (scene?.narration_text) {
      setAnimatingText('');
      let i = 0;
      const text = scene.narration_text;
      const timer = setInterval(() => {
        if (i < text.length) {
          setAnimatingText(text.slice(0, i + 1));
          i++;
        } else {
          clearInterval(timer);
        }
      }, 30);
      return () => clearInterval(timer);
    }
  }, [scene?.narration_text]);

  const handleOptionClick = (option, index) => {
    setSelectedOption(index);
    setTimeout(() => {
      handleChoice(option, 'narrative_choice', undefined, undefined, index);
      setSelectedOption(null);
    }, 300);
  };

  const handleInteractiveElement = (element) => {
    handleChoice(
      `Interact with ${element.name}`,
      'item_interaction',
      element.id,
      'interactive_element'
    );
  };

  if (!initialized) {
    return (
      <div className={`min-h-screen ${theme.backgrounds.main} flex items-center justify-center`}>
        <div className="text-center">
          <div className={`animate-spin rounded-full h-32 w-32 border-t-2 border-b-2 ${theme.borders.accent.replace('border-', 'border-t-').replace('/30', '').replace('/50', '')} mb-4`}></div>
          <p className={`${theme.text.accent} text-xl`}>Initializing your adventure...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-red-900 to-black flex items-center justify-center p-4">
        <div className="bg-red-900/50 border border-red-500 rounded-lg p-6 max-w-md">
          <AlertTriangle className="h-8 w-8 text-red-400 mb-2" />
          <h2 className="text-red-300 text-xl font-bold mb-2">Error</h2>
          <p className="text-red-200">{error}</p>
        </div>
      </div>
    );
  }

  if (!scene) {
    return (
      <div className={`min-h-screen ${theme.backgrounds.main} flex items-center justify-center`}>
        <div className="text-center">
          <Sparkles className={`h-16 w-16 ${theme.text.accent} mx-auto mb-4 animate-pulse`} />
          <p className={`${theme.text.accent} text-xl`}>Loading your world...</p>
        </div>
      </div>
    );
  }

  return (
    <div className={`min-h-screen ${theme.backgrounds.main} ${theme.text.primary} overflow-hidden`}>
      {/* Header Bar */}
      <div className={`${theme.backgrounds.header} backdrop-blur-sm border-b ${theme.borders.primary} p-4 relative z-40`}>
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <MapPin className={`h-5 w-5 ${theme.text.accent}`} />
            <span className={`${theme.text.accent} font-semibold`}>{scene.location}</span>
            <span className={theme.text.accent}>•</span>
            <span className={theme.text.accent}>{scene.world}</span>
          </div>
          <div className="flex items-center space-x-6">
            {/* Theme Selector */}
            <div className="relative">
              <button
                onClick={() => setShowThemeSelector(!showThemeSelector)}
                className={`flex items-center space-x-2 ${theme.buttons.primary} rounded-lg px-3 py-2 transition-colors`}
              >
                <Palette className="h-4 w-4" />
                <span className="text-sm">Theme</span>
              </button>
              
              {showThemeSelector && (
                <div 
                  className={`absolute right-0 top-full mt-2 ${theme.backgrounds.card} backdrop-blur-sm border ${theme.borders.primary} rounded-lg p-2 min-w-48 shadow-2xl`}
                  style={{ zIndex: 9999 }}
                >
                  {availableThemes.map((themeOption) => (
                    <button
                      key={themeOption.key}
                      onClick={() => {
                        setCurrentTheme(themeOption.key);
                        setShowThemeSelector(false);
                      }}
                      className={`w-full text-left px-3 py-2 rounded text-sm transition-colors ${
                        currentTheme === themeOption.key 
                          ? `${theme.buttons.selected}` 
                          : `hover:${theme.backgrounds.cardAlt}`
                      }`}
                    >
                      {themeOption.name}
                    </button>
                  ))}
                </div>
              )}
            </div>
            
            <div className="flex items-center space-x-2">
              <Clock className={`h-4 w-4 ${theme.text.accent}`} />
              <span className={`${theme.text.accent} text-sm`}>{Math.floor(gameProgress.play_time_minutes / 60)}h {gameProgress.play_time_minutes % 60}m</span>
            </div>
            <div className="flex items-center space-x-2">
              <Target className={`h-4 w-4 ${theme.text.accent}`} />
              <span className={`${theme.text.accent} text-sm`}>Scene {gameProgress.scenes_completed}</span>
            </div>
          </div>
        </div>
      </div>

      <div className="flex h-screen">
        {/* Left Sidebar - Game Stats */}
        <div className={`w-80 ${theme.backgrounds.sidebar} backdrop-blur-sm border-r ${theme.borders.primary} p-4 overflow-y-auto`}>
          {/* Environmental Conditions */}
          <div className="mb-6">
            <h3 className={`${theme.text.accent} font-semibold mb-3 flex items-center`}>
              <Cloud className="h-4 w-4 mr-2" />
              Environment
            </h3>
            <div className="space-y-2 text-sm">
              <div className="flex items-center justify-between">
                <span className={theme.text.tertiary}>Weather</span>
                <span className={theme.text.accent}>{getWeatherIcon(scene.game_state?.environmental_conditions?.weather)} {scene.game_state?.environmental_conditions?.weather}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className={theme.text.tertiary}>Visibility</span>
                <span className={theme.text.accent}>{scene.game_state?.environmental_conditions?.visibility}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className={theme.text.tertiary}>Hazard Level</span>
                <span className={getThreatColor(scene.game_state?.environmental_conditions?.hazard_level || 0)}>
                  {scene.game_state?.environmental_conditions?.hazard_level || 0}/10
                </span>
              </div>
            </div>
          </div>

          {/* Resources */}
          <div className="mb-6">
            <h3 className={`${theme.text.accent} font-semibold mb-3 flex items-center`}>
              <Package className="h-4 w-4 mr-2" />
              Resources
            </h3>
            <div className="space-y-2 text-sm">
              {Object.entries(scene.game_state?.resource_availability || {}).map(([resource, status]) => (
                <div key={resource} className="flex items-center justify-between">
                  <span className={`${theme.text.tertiary} capitalize`}>{resource.replace('_', ' ')}</span>
                  <span className={getResourceColor(status)}>{status}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Inventory Button */}
          <button
            onClick={() => setShowInventory(!showInventory)}
            className={`w-full ${theme.elements.inventory} rounded-lg p-3 mb-4 transition-colors`}
          >
            <div className="flex items-center justify-between">
              <span className="flex items-center">
                <Package className="h-4 w-4 mr-2" />
                Inventory ({scene.current_inventory?.length || 0})
              </span>
              <ChevronRight className={`h-4 w-4 transition-transform ${showInventory ? 'rotate-90' : ''}`} />
            </div>
          </button>

          {/* Inventory Dropdown */}
          {showInventory && (
            <div className={`mb-4 ${theme.backgrounds.card} rounded-lg p-3 border ${theme.borders.subtle}`}>
              {scene.current_inventory?.length > 0 ? (
                <div className="space-y-2">
                  {scene.current_inventory.map((item, index) => (
                    <div key={index} className="flex items-center justify-between text-sm">
                      <span className={theme.text.tertiary}>{item.name}</span>
                      <span className={theme.text.accent}>×{item.quantity}</span>
                    </div>
                  ))}
                </div>
              ) : (
                <p className={`${theme.text.muted} text-sm`}>No items</p>
              )}
            </div>
          )}

          {/* Characters Present */}
          {scene.characters && scene.characters.length > 0 && (
            <div className="mb-6">
              <h3 className={`${theme.text.accent} font-semibold mb-3 flex items-center`}>
                <Users className="h-4 w-4 mr-2" />
                Characters Present
              </h3>
              <div className="space-y-2">
                {scene.characters.map((character, index) => (
                  <div key={index} className={`${theme.elements.character} rounded-lg p-3 border`}>
                    <div className="flex items-center justify-between">
                      <span className={`${theme.text.highlight} font-medium`}>{character.name}</span>
                      <span className={`text-sm ${theme.text.muted}`}>{character.current_mood}</span>
                    </div>
                    <div className={`text-xs ${theme.text.muted} mt-1`}>
                      Relationship: {character.relationship_level}/10
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Active Threats */}
          {scene.threat_updates && scene.threat_updates.length > 0 && (
            <div className="mb-6">
              <h3 className="text-red-300 font-semibold mb-3 flex items-center">
                <AlertTriangle className="h-4 w-4 mr-2" />
                Active Threats
              </h3>
              <div className="space-y-2">
                {scene.threat_updates.map((threat, index) => (
                  <div key={index} className={`${theme.elements.threat} rounded-lg p-3 border`}>
                    <div className="flex items-center justify-between">
                      <span className="text-red-300 font-medium">{threat.threat_name}</span>
                      <span className={getThreatColor(threat.escalation_level)}>
                        {threat.escalation_level}/10
                      </span>
                    </div>
                    {threat.immediate_danger && (
                      <div className="text-red-400 text-xs mt-1 flex items-center">
                        <Skull className="h-3 w-3 mr-1" />
                        Immediate Danger!
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Main Game Area */}
        <div className="flex-1 flex flex-col">
          {/* Narration Area */}
          <div className={`flex-1 ${theme.backgrounds.overlay} backdrop-blur-sm p-6 overflow-y-auto`}>
            {/* Mood/Atmosphere Bar */}
            <div className="mb-6 flex items-center justify-center">
              <div className={`${theme.backgrounds.card} rounded-full px-4 py-2 border ${theme.borders.subtle}`}>
                <span className={`${theme.text.accent} text-sm font-medium`}>
                  {scene.mood_atmosphere}
                </span>
              </div>
            </div>

            {/* Main Narration */}
            <div className="max-w-4xl mx-auto">
              <div className={`${theme.backgrounds.narration} backdrop-blur-sm rounded-lg p-6 border ${theme.borders.primary} mb-6`}>
                <p className={`text-lg leading-relaxed ${theme.text.secondary}`}>
                  {animatingText}
                </p>
              </div>

              {/* Dialogue */}
              {scene.dialogue && scene.dialogue.length > 0 && (
                <div className="mb-6">
                  <h3 className={`${theme.text.accent} font-semibold mb-3 flex items-center`}>
                    <MessageCircle className="h-4 w-4 mr-2" />
                    Dialogue
                  </h3>
                  <div className="space-y-3">
                    {scene.dialogue.map((line, index) => (
                      <div key={index} className={`${theme.elements.dialogue} rounded-lg p-4 border`}>
                        <div className="flex items-center justify-between mb-2">
                          <span className={`${theme.text.highlight} font-medium`}>{line.speaker}</span>
                          <span className={`text-xs ${theme.text.muted}`}>{line.emotion}</span>
                        </div>
                        <p className={theme.text.secondary}>{line.text}</p>
                        {line.is_internal_thought && (
                          <div className={`text-xs ${theme.text.accent} mt-1 italic`}>
                            *Internal thought*
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Interactive Elements */}
              {scene.interactive_elements && scene.interactive_elements.length > 0 && (
                <div className="mb-6">
                  <h3 className={`${theme.text.accent} font-semibold mb-3 flex items-center`}>
                    <Eye className="h-4 w-4 mr-2" />
                    Interactive Elements
                  </h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                    {scene.interactive_elements.map((element, index) => (
                      <button
                        key={index}
                        onClick={() => handleInteractiveElement(element)}
                        className={`${theme.buttons.interactive} rounded-lg p-4 border transition-colors text-left`}
                      >
                        <div className={`font-medium ${theme.text.highlight}`}>{element.name}</div>
                        <div className={`text-sm ${theme.text.muted} mt-1`}>{element.description}</div>
                      </button>
                    ))}
                  </div>
                </div>
              )}

              {/* Environmental Discoveries */}
              {scene.environmental_discoveries && scene.environmental_discoveries.length > 0 && (
                <div className="mb-6">
                  <h3 className={`${theme.text.accent} font-semibold mb-3 flex items-center`}>
                    <Sparkles className="h-4 w-4 mr-2" />
                    Discoveries
                  </h3>
                  <div className="space-y-3">
                    {scene.environmental_discoveries.map((discovery, index) => (
                      <div key={index} className={`${theme.elements.discovery} rounded-lg p-4 border`}>
                        <div className="font-medium text-yellow-300">{discovery.name}</div>
                        <div className={`text-sm ${theme.text.secondary} mt-1`}>{discovery.description}</div>
                        <div className="text-xs text-yellow-400 mt-2">
                          Significance: {discovery.significance}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Options/Choices Area */}
          <div className={`${theme.backgrounds.card} backdrop-blur-sm border-t ${theme.borders.primary} p-6`}>
            <div className="max-w-4xl mx-auto">
              <h3 className={`${theme.text.accent} font-semibold mb-4 flex items-center`}>
                <Crown className="h-4 w-4 mr-2" />
                Your Choices
              </h3>
              
              {loading ? (
                <div className="text-center py-8">
                  <div className={`animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 ${theme.borders.accent.replace('border-', 'border-t-').replace('/30', '').replace('/50', '')} mx-auto mb-2`}></div>
                  <p className={theme.text.accent}>Processing your choice...</p>
                </div>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {scene.options?.map((option, index) => (
                    <button
                      key={index}
                      onClick={() => handleOptionClick(option, index)}
                      disabled={selectedOption !== null}
                      className={`
                        relative overflow-hidden rounded-lg p-4 border-2 text-left transition-all duration-300 transform
                        ${selectedOption === index 
                          ? `${theme.buttons.selected} scale-105` 
                          : `${theme.buttons.secondary} hover:scale-105`
                        }
                        ${selectedOption !== null && selectedOption !== index ? 'opacity-50' : ''}
                      `}
                    >
                      <div className="flex items-center justify-between">
                        <span className={`${theme.text.secondary} font-medium`}>{option}</span>
                        <ChevronRight className={`h-4 w-4 ${theme.text.accent}`} />
                      </div>
                      
                      {selectedOption === index && (
                        <div className="absolute inset-0 bg-gradient-to-r from-purple-600/20 to-blue-600/20 animate-pulse"></div>
                      )}
                    </button>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Right Sidebar - Lore & Objectives */}
        <div className={`w-80 ${theme.backgrounds.sidebar} backdrop-blur-sm border-l ${theme.borders.primary} p-4 overflow-y-auto`}>
          {/* Active Objectives */}
          {scene.game_state?.active_objectives && scene.game_state.active_objectives.length > 0 && (
            <div className="mb-6">
              <h3 className={`${theme.text.accent} font-semibold mb-3 flex items-center`}>
                <Target className="h-4 w-4 mr-2" />
                Active Objectives
              </h3>
              <div className="space-y-2">
                {scene.game_state.active_objectives.map((objective, index) => (
                  <div key={index} className={`${theme.backgrounds.cardAlt} rounded-lg p-3 border ${theme.borders.subtle}`}>
                    <div className={`${theme.text.accent} font-medium text-sm`}>{objective.description}</div>
                    <div className="flex items-center justify-between mt-2">
                      <div className={`text-xs ${theme.text.muted}`}>{objective.quest_type}</div>
                      <div className={`text-xs ${theme.text.highlight}`}>{objective.progress}%</div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Discovered Lore */}
          <button
            onClick={() => setShowLore(!showLore)}
            className={`w-full ${theme.elements.lore} rounded-lg p-3 mb-4 transition-colors`}
          >
            <div className="flex items-center justify-between">
              <span className="flex items-center">
                <Book className="h-4 w-4 mr-2" />
                Lore ({scene.discovered_lore?.length || 0})
              </span>
              <ChevronRight className={`h-4 w-4 transition-transform ${showLore ? 'rotate-90' : ''}`} />
            </div>
          </button>

          {showLore && scene.discovered_lore && scene.discovered_lore.length > 0 && (
            <div className={`mb-6 ${theme.backgrounds.card} rounded-lg p-3 border ${theme.borders.subtle}`}>
              <div className="space-y-3">
                {scene.discovered_lore.map((lore, index) => (
                  <div key={index} className="border-b border-amber-500/20 pb-3 last:border-b-0">
                    <div className="text-amber-300 font-medium text-sm">{lore.title}</div>
                    <div className={`text-xs ${theme.text.muted} mt-1`}>{lore.category}</div>
                    <div className={`text-xs ${theme.text.tertiary} mt-2`}>{lore.content}</div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Recent Changes */}
          {(scene.relationship_changes && Object.keys(scene.relationship_changes).length > 0) ||
           (scene.new_secrets && scene.new_secrets.length > 0) ? (
            <div className="mb-6">
              <h3 className={`${theme.text.accent} font-semibold mb-3 flex items-center`}>
                <Zap className="h-4 w-4 mr-2" />
                Recent Changes
              </h3>
              
              {scene.relationship_changes && Object.keys(scene.relationship_changes).length > 0 && (
                <div className="mb-3">
                  <div className={`text-sm ${theme.text.muted} mb-2`}>Relationships</div>
                  {Object.entries(scene.relationship_changes).map(([character, change]) => (
                    <div key={character} className="flex items-center justify-between text-sm">
                      <span className={theme.text.highlight}>{character}</span>
                      <span className={change > 0 ? 'text-green-400' : 'text-red-400'}>
                        {change > 0 ? '+' : ''}{change}
                      </span>
                    </div>
                  ))}
                </div>
              )}
              
              {scene.new_secrets && scene.new_secrets.length > 0 && (
                <div>
                  <div className={`text-sm ${theme.text.muted} mb-2`}>New Secrets</div>
                  {scene.new_secrets.map((secret, index) => (
                    <div key={index} className={`text-sm ${theme.text.accent} mb-1`}>
                      • {secret}
                    </div>
                  ))}
                </div>
              )}
            </div>
          ) : null}
        </div>
      </div>
    </div>
  );
};

export default SurvivalRPGGame;
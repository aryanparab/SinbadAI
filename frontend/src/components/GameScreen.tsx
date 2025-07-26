'use client';

import { useGameLogic } from "@/hooks/useGameLogic"

export default function GameScreenUI() {
  const { scene, loading, gameProgress, initialized, handleChoice } = useGameLogic();

  if (!initialized) {
    return (
      <div className="p-4 flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading game...</p>
        </div>
      </div>
    );
  }
  
  return (
    <div className="p-6 max-w-4xl mx-auto">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-3xl font-bold mb-2 text-center">{scene?.world} Survival</h1>
        <div className="flex justify-center space-x-4 text-sm text-gray-600">
          <span>Scenes: {gameProgress.scenes_completed}</span>
          <span>Play Time: {Math.floor(gameProgress.play_time_minutes / 60)}h {gameProgress.play_time_minutes % 60}m</span>
          <span>Tension: {gameProgress.tension_level}/10</span>
        </div>
      </div>

      {/* Loading State */}
      {loading && (
        <div className="text-center p-8">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading next scene...</p>
        </div>
      )}

      {/* Main Game Content */}
      {!loading && scene && (
        <div className="space-y-6">
          {/* Main Scene Content */}
          <div className="bg-gray-100 p-6 rounded-lg shadow">
            <h2 className="text-xl font-semibold mb-3">Scene: {scene.scene_tag}</h2>
            <p className="text-gray-800 mb-4 leading-relaxed">{scene.narration_text}</p>
            <div className="flex justify-between text-sm text-gray-500">
              <span>Location: {scene.location}</span>
              <span>Mood: {scene.mood_atmosphere}</span>
            </div>
          </div>

          {/* Dialogue Section */}
          {scene.dialogue && scene.dialogue.length > 0 && (
            <div className="bg-white p-4 rounded-lg shadow">
              <h3 className="font-semibold mb-3">Dialogue:</h3>
              <div className="space-y-2">
                {scene.dialogue.map((line, idx) => (
                  <div key={idx} className="border-l-4 border-blue-300 pl-3">
                    <div className="flex items-center gap-2">
                      <strong className="text-blue-700">{line.speaker}:</strong>
                      {line.emotion && (
                        <span className="text-xs bg-blue-100 px-2 py-1 rounded">{line.emotion}</span>
                      )}
                    </div>
                    <p className="text-gray-700">{line.text}</p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Characters Section */}
          {scene.characters && scene.characters.length > 0 && (
            <div className="bg-white p-4 rounded-lg shadow">
              <h3 className="font-semibold mb-3">Characters Present:</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {scene.characters.map((char) => (
                  <div
                    key={char.id}
                    className={`p-3 border rounded-lg cursor-pointer transition-colors ${
                      char.interactable ? 'hover:bg-blue-50 border-blue-200' : 'bg-gray-50'
                    }`}
                    onClick={() => char.interactable && handleChoice(`Talk to ${char.name}`, 'character_interaction', char.id, 'npc')}
                  >
                    <h4 className="font-bold text-lg">{char.name}</h4>
                    <div className="text-sm text-gray-600 space-y-1">
                      <p>Relationship: {char.relationship_level > 0 ? '+' : ''}{char.relationship_level}</p>
                      <p>Trust: {char.trust_level > 0 ? '+' : ''}{char.trust_level}</p>
                      <p>Mood: {char.current_mood}</p>
                    </div>
                    {char.interactable && (
                      <div className="mt-2 text-xs text-blue-600">Click to interact</div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Interactive Elements */}
          {scene.interactive_elements && scene.interactive_elements.length > 0 && (
            <div className="bg-white p-4 rounded-lg shadow">
              <h3 className="font-semibold mb-3">Interactive Elements:</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {scene.interactive_elements.map((element) => (
                  <div
                    key={element.id}
                    className="p-3 border rounded-lg cursor-pointer hover:bg-green-50 border-green-200"
                  >
                    <h4 className="font-bold">{element.name}</h4>
                    <p className="text-sm text-gray-600 mb-2">{element.description}</p>
                    <div className="flex flex-wrap gap-1">
                      {element.interaction_types.map((type, idx) => (
                        <button
                          key={idx}
                          onClick={() => handleChoice(`${type} ${element.name}`, 'environmental_interaction', element.id, 'interactive_element')}
                          className="text-xs bg-green-100 hover:bg-green-200 px-2 py-1 rounded"
                        >
                          {type}
                        </button>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Inventory Changes */}
          {scene.inventory_changes && 
           (scene.inventory_changes.added_items.length > 0 || 
            scene.inventory_changes.removed_items.length > 0 ||
            scene.inventory_changes.modified_items.length > 0) && (
            <div className="bg-yellow-50 p-4 rounded-lg shadow">
              <h3 className="font-semibold mb-3">Inventory Changes:</h3>
              {scene.inventory_changes.added_items.length > 0 && (
                <div className="mb-2">
                  <p className="text-green-700 font-medium">Added Items:</p>
                  {scene.inventory_changes.added_items.map((item, idx) => (
                    <div key={idx} className="ml-4 text-sm">
                      <span className="font-medium">{item.name}</span> x{item.quantity}
                      {item.description && <span className="text-gray-600"> - {item.description}</span>}
                    </div>
                  ))}
                </div>
              )}
              {scene.inventory_changes.removed_items.length > 0 && (
                <div className="mb-2">
                  <p className="text-red-700 font-medium">Removed Items:</p>
                  {scene.inventory_changes.removed_items.map((item, idx) => (
                    <div key={idx} className="ml-4 text-sm">
                      <span className="font-medium">{item.name}</span> x{item.quantity}
                    </div>
                  ))}
                </div>
              )}
              <div className="mt-3 pt-3 border-t">
                <p className="text-sm text-gray-600">Current Inventory:</p>
                <div className="flex flex-wrap gap-2 mt-1">
                  {scene.current_inventory.map((item, idx) => (
                    <span
                      key={idx}
                      className="text-xs bg-gray-100 px-2 py-1 rounded cursor-pointer hover:bg-gray-200"
                      onClick={() => handleChoice(`Examine ${item.name}`, 'item_interaction', item.name, 'inventory_item')}
                    >
                      {item.name} x{item.quantity}
                    </span>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* Threats and Events */}
          {scene.threat_updates && scene.threat_updates.length > 0 && (
            <div className="bg-red-50 p-4 rounded-lg shadow">
              <h3 className="font-semibold mb-3 text-red-800">Threat Updates:</h3>
              {scene.threat_updates.map((threat, idx) => (
                <div key={idx} className="mb-3 p-3 bg-white rounded border-l-4 border-red-400">
                  <div className="flex justify-between items-start">
                    <h4 className="font-bold text-red-700">{threat.threat_name}</h4>
                    <span className="text-xs bg-red-100 px-2 py-1 rounded">Level {threat.escalation_level}</span>
                  </div>
                  {threat.immediate_danger && (
                    <p className="text-sm text-red-600 font-medium mt-1">⚠️ Immediate Danger!</p>
                  )}
                  <div className="text-sm text-gray-600 mt-2">
                    Possible solutions: {threat.resolution_methods.join(', ')}
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* Active Objectives */}
          {scene.game_state?.active_objectives?.length > 0 && (
            <div className="bg-blue-50 p-4 rounded-lg shadow">
              <h3 className="font-semibold mb-3 text-blue-800">Active Objectives:</h3>
              <div className="space-y-2">
                {scene.game_state.active_objectives.map((objective, idx) => (
                  <div key={idx} className="bg-white p-3 rounded border-l-4 border-blue-400">
                    <div className="flex justify-between items-start">
                      <h4 className="font-medium">{objective.description}</h4>
                      <span className="text-xs bg-blue-100 px-2 py-1 rounded">{objective.progress}%</span>
                    </div>
                    {objective.involves_npcs.length > 0 && (
                      <p className="text-sm text-gray-600 mt-1">
                        Involves: {objective.involves_npcs.join(', ')}
                      </p>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Main Choice Options */}
          {scene.options && scene.options.length > 0 && (
            <div className="bg-white p-4 rounded-lg shadow">
              <h3 className="font-semibold mb-3">What do you do?</h3>
              <div className="space-y-2">
                {scene.options.map((option, idx) => (
                  <button
                    key={idx}
                    onClick={() => handleChoice(option, 'narrative_choice', undefined, undefined, idx)}
                    className="w-full text-left px-4 py-3 bg-gradient-to-r from-blue-600 to-blue-700 text-white rounded-lg hover:from-blue-700 hover:to-blue-800 transition-all duration-200 shadow-sm"
                  >
                    {option}
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
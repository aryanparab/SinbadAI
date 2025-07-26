// themes.js
export const themes = {
  // Default purple/dark theme (current)
  default: {
    name: 'Mystic Purple',
    backgrounds: {
      main: 'bg-gradient-to-br from-gray-900 via-purple-900 to-black',
      sidebar: 'bg-black/30',
      header: 'bg-black/50',
      card: 'bg-black/40',
      cardAlt: 'bg-black/30',
      narration: 'bg-black/40',
      overlay: 'bg-black/20'
    },
    borders: {
      primary: 'border-purple-500/30',
      secondary: 'border-purple-500/50',
      accent: 'border-purple-400',
      subtle: 'border-purple-500/20'
    },
    text: {
      primary: 'text-white',
      secondary: 'text-gray-200',
      tertiary: 'text-gray-300',
      muted: 'text-gray-400',
      accent: 'text-purple-300',
      highlight: 'text-purple-400'
    },
    buttons: {
      primary: 'bg-purple-600/50 hover:bg-purple-600/70 border-purple-500/50',
      secondary: 'bg-purple-900/30 hover:bg-purple-900/50 border-purple-500/50',
      selected: 'bg-purple-600/50 border-purple-400',
      interactive: 'bg-green-900/30 hover:bg-green-900/50 border-green-500/30'
    },
    status: {
      health: 'text-red-400',
      mana: 'text-blue-400',
      stamina: 'text-yellow-400',
      success: 'text-green-400',
      warning: 'text-orange-400',
      danger: 'text-red-400'
    },
    elements: {
      inventory: 'bg-purple-600/50 hover:bg-purple-600/70 border-purple-500/50',
      lore: 'bg-amber-600/50 hover:bg-amber-600/70 border-amber-500/50',
      threat: 'bg-red-900/30 border-red-500/30',
      discovery: 'bg-yellow-900/30 border-yellow-500/30',
      dialogue: 'bg-black/30 border-blue-500/30',
      character: 'bg-black/30 border-purple-500/30'
    }
  },

  // Cyberpunk theme
  cyberpunk: {
    name: 'Neon Cyberpunk',
    backgrounds: {
      main: 'bg-gradient-to-br from-black via-cyan-900 to-purple-900',
      sidebar: 'bg-black/40',
      header: 'bg-black/60',
      card: 'bg-black/50',
      cardAlt: 'bg-black/40',
      narration: 'bg-black/50',
      overlay: 'bg-black/30'
    },
    borders: {
      primary: 'border-cyan-500/40',
      secondary: 'border-cyan-500/60',
      accent: 'border-cyan-400',
      subtle: 'border-cyan-500/20'
    },
    text: {
      primary: 'text-cyan-100',
      secondary: 'text-cyan-200',
      tertiary: 'text-cyan-300',
      muted: 'text-gray-400',
      accent: 'text-cyan-400',
      highlight: 'text-pink-400'
    },
    buttons: {
      primary: 'bg-cyan-600/50 hover:bg-cyan-600/70 border-cyan-500/50',
      secondary: 'bg-cyan-900/30 hover:bg-cyan-900/50 border-cyan-500/50',
      selected: 'bg-cyan-600/50 border-cyan-400',
      interactive: 'bg-pink-900/30 hover:bg-pink-900/50 border-pink-500/30'
    },
    status: {
      health: 'text-red-400',
      mana: 'text-cyan-400',
      stamina: 'text-yellow-400',
      success: 'text-green-400',
      warning: 'text-orange-400',
      danger: 'text-red-400'
    },
    elements: {
      inventory: 'bg-cyan-600/50 hover:bg-cyan-600/70 border-cyan-500/50',
      lore: 'bg-pink-600/50 hover:bg-pink-600/70 border-pink-500/50',
      threat: 'bg-red-900/30 border-red-500/30',
      discovery: 'bg-yellow-900/30 border-yellow-500/30',
      dialogue: 'bg-black/40 border-cyan-500/30',
      character: 'bg-black/40 border-cyan-500/30'
    }
  },

  // Dark forest theme
  forest: {
    name: 'Dark Forest',
    backgrounds: {
      main: 'bg-gradient-to-br from-gray-900 via-green-900 to-black',
      sidebar: 'bg-black/30',
      header: 'bg-black/50',
      card: 'bg-black/40',
      cardAlt: 'bg-black/30',
      narration: 'bg-black/40',
      overlay: 'bg-black/20'
    },
    borders: {
      primary: 'border-green-500/30',
      secondary: 'border-green-500/50',
      accent: 'border-green-400',
      subtle: 'border-green-500/20'
    },
    text: {
      primary: 'text-green-100',
      secondary: 'text-green-200',
      tertiary: 'text-green-300',
      muted: 'text-gray-400',
      accent: 'text-green-400',
      highlight: 'text-emerald-400'
    },
    buttons: {
      primary: 'bg-green-600/50 hover:bg-green-600/70 border-green-500/50',
      secondary: 'bg-green-900/30 hover:bg-green-900/50 border-green-500/50',
      selected: 'bg-green-600/50 border-green-400',
      interactive: 'bg-emerald-900/30 hover:bg-emerald-900/50 border-emerald-500/30'
    },
    status: {
      health: 'text-red-400',
      mana: 'text-blue-400',
      stamina: 'text-yellow-400',
      success: 'text-green-400',
      warning: 'text-orange-400',
      danger: 'text-red-400'
    },
    elements: {
      inventory: 'bg-green-600/50 hover:bg-green-600/70 border-green-500/50',
      lore: 'bg-amber-600/50 hover:bg-amber-600/70 border-amber-500/50',
      threat: 'bg-red-900/30 border-red-500/30',
      discovery: 'bg-yellow-900/30 border-yellow-500/30',
      dialogue: 'bg-black/30 border-emerald-500/30',
      character: 'bg-black/30 border-green-500/30'
    }
  },

  // Volcanic/Fire theme
  volcanic: {
    name: 'Volcanic Fire',
    backgrounds: {
      main: 'bg-gradient-to-br from-black via-red-900 to-orange-900',
      sidebar: 'bg-black/40',
      header: 'bg-black/60',
      card: 'bg-black/50',
      cardAlt: 'bg-black/40',
      narration: 'bg-black/50',
      overlay: 'bg-black/30'
    },
    borders: {
      primary: 'border-red-500/40',
      secondary: 'border-red-500/60',
      accent: 'border-orange-400',
      subtle: 'border-red-500/20'
    },
    text: {
      primary: 'text-orange-100',
      secondary: 'text-orange-200',
      tertiary: 'text-orange-300',
      muted: 'text-gray-400',
      accent: 'text-orange-400',
      highlight: 'text-red-400'
    },
    buttons: {
      primary: 'bg-red-600/50 hover:bg-red-600/70 border-red-500/50',
      secondary: 'bg-red-900/30 hover:bg-red-900/50 border-red-500/50',
      selected: 'bg-red-600/50 border-orange-400',
      interactive: 'bg-orange-900/30 hover:bg-orange-900/50 border-orange-500/30'
    },
    status: {
      health: 'text-red-400',
      mana: 'text-blue-400',
      stamina: 'text-yellow-400',
      success: 'text-green-400',
      warning: 'text-orange-400',
      danger: 'text-red-400'
    },
    elements: {
      inventory: 'bg-red-600/50 hover:bg-red-600/70 border-red-500/50',
      lore: 'bg-orange-600/50 hover:bg-orange-600/70 border-orange-500/50',
      threat: 'bg-red-900/30 border-red-500/30',
      discovery: 'bg-yellow-900/30 border-yellow-500/30',
      dialogue: 'bg-black/40 border-red-500/30',
      character: 'bg-black/40 border-red-500/30'
    }
  },

  // Ice/Arctic theme
  arctic: {
    name: 'Arctic Ice',
    backgrounds: {
      main: 'bg-gradient-to-br from-slate-900 via-blue-900 to-cyan-900',
      sidebar: 'bg-black/30',
      header: 'bg-black/50',
      card: 'bg-black/40',
      cardAlt: 'bg-black/30',
      narration: 'bg-black/40',
      overlay: 'bg-black/20'
    },
    borders: {
      primary: 'border-blue-500/30',
      secondary: 'border-blue-500/50',
      accent: 'border-cyan-400',
      subtle: 'border-blue-500/20'
    },
    text: {
      primary: 'text-blue-100',
      secondary: 'text-blue-200',
      tertiary: 'text-blue-300',
      muted: 'text-gray-400',
      accent: 'text-blue-400',
      highlight: 'text-cyan-400'
    },
    buttons: {
      primary: 'bg-blue-600/50 hover:bg-blue-600/70 border-blue-500/50',
      secondary: 'bg-blue-900/30 hover:bg-blue-900/50 border-blue-500/50',
      selected: 'bg-blue-600/50 border-cyan-400',
      interactive: 'bg-cyan-900/30 hover:bg-cyan-900/50 border-cyan-500/30'
    },
    status: {
      health: 'text-red-400',
      mana: 'text-blue-400',
      stamina: 'text-yellow-400',
      success: 'text-green-400',
      warning: 'text-orange-400',
      danger: 'text-red-400'
    },
    elements: {
      inventory: 'bg-blue-600/50 hover:bg-blue-600/70 border-blue-500/50',
      lore: 'bg-cyan-600/50 hover:bg-cyan-600/70 border-cyan-500/50',
      threat: 'bg-red-900/30 border-red-500/30',
      discovery: 'bg-yellow-900/30 border-yellow-500/30',
      dialogue: 'bg-black/30 border-blue-500/30',
      character: 'bg-black/30 border-blue-500/30'
    }
  },

  // Desert/Sand theme
  desert: {
    name: 'Desert Sands',
    backgrounds: {
      main: 'bg-gradient-to-br from-yellow-900 via-orange-900 to-red-900',
      sidebar: 'bg-black/30',
      header: 'bg-black/50',
      card: 'bg-black/40',
      cardAlt: 'bg-black/30',
      narration: 'bg-black/40',
      overlay: 'bg-black/20'
    },
    borders: {
      primary: 'border-yellow-600/30',
      secondary: 'border-yellow-600/50',
      accent: 'border-orange-400',
      subtle: 'border-yellow-600/20'
    },
    text: {
      primary: 'text-yellow-100',
      secondary: 'text-yellow-200',
      tertiary: 'text-yellow-300',
      muted: 'text-gray-400',
      accent: 'text-yellow-400',
      highlight: 'text-orange-400'
    },
    buttons: {
      primary: 'bg-yellow-600/50 hover:bg-yellow-600/70 border-yellow-600/50',
      secondary: 'bg-yellow-900/30 hover:bg-yellow-900/50 border-yellow-600/50',
      selected: 'bg-yellow-600/50 border-orange-400',
      interactive: 'bg-orange-900/30 hover:bg-orange-900/50 border-orange-500/30'
    },
    status: {
      health: 'text-red-400',
      mana: 'text-blue-400',
      stamina: 'text-yellow-400',
      success: 'text-green-400',
      warning: 'text-orange-400',
      danger: 'text-red-400'
    },
    elements: {
      inventory: 'bg-yellow-600/50 hover:bg-yellow-600/70 border-yellow-600/50',
      lore: 'bg-orange-600/50 hover:bg-orange-600/70 border-orange-500/50',
      threat: 'bg-red-900/30 border-red-500/30',
      discovery: 'bg-yellow-900/30 border-yellow-500/30',
      dialogue: 'bg-black/30 border-yellow-600/30',
      character: 'bg-black/30 border-yellow-600/30'
    }
  }
};

// Theme context and hook
export const getThemeClasses = (themeName = 'default') => {
  const theme = themes[themeName] || themes.default;
  return theme;
};

// Utility function to get threat level colors (theme-independent)
export const getThreatColor = (level) => {
  if (level >= 8) return 'text-red-400';
  if (level >= 5) return 'text-orange-400';
  return 'text-yellow-400';
};

// Utility function to get resource status colors (theme-independent)
export const getResourceColor = (resource) => {
  switch (resource?.toLowerCase()) {
    case 'critical': return 'text-red-400';
    case 'low': return 'text-orange-400';
    case 'moderate': return 'text-yellow-400';
    case 'abundant': return 'text-green-400';
    default: return 'text-gray-400';
  }
};

// Weather icons (theme-independent)
export const getWeatherIcon = (weather) => {
  switch (weather?.toLowerCase()) {
    case 'rain': return '🌧️';
    case 'storm': return '⛈️';
    case 'snow': return '❄️';
    case 'fog': return '🌫️';
    default: return '☀️';
  }
};

// Theme-aware component helper
export const createThemeClasses = (themeName, customClasses = {}) => {
  const theme = getThemeClasses(themeName);
  
  return {
    // Main layout
    container: `min-h-screen ${theme.backgrounds.main} text-white overflow-hidden`,
    header: `${theme.backgrounds.header} backdrop-blur-sm border-b ${theme.borders.primary} p-4`,
    sidebar: `${theme.backgrounds.sidebar} backdrop-blur-sm border-r ${theme.borders.primary} p-4 overflow-y-auto`,
    sidebarRight: `${theme.backgrounds.sidebar} backdrop-blur-sm border-l ${theme.borders.primary} p-4 overflow-y-auto`,
    mainArea: `${theme.backgrounds.overlay} backdrop-blur-sm p-6 overflow-y-auto`,
    
    // Cards and containers
    card: `${theme.backgrounds.card} backdrop-blur-sm rounded-lg p-6 border ${theme.borders.primary}`,
    cardAlt: `${theme.backgrounds.cardAlt} rounded-lg p-3 border ${theme.borders.primary}`,
    
    // Buttons
    buttonPrimary: `${theme.buttons.primary} rounded-lg p-3 transition-colors`,
    buttonSecondary: `${theme.buttons.secondary} rounded-lg p-4 border-2 text-left transition-all duration-300 transform hover:scale-105`,
    buttonSelected: `${theme.buttons.selected} scale-105`,
    buttonInteractive: `${theme.buttons.interactive} rounded-lg p-4 border transition-colors text-left`,
    
    // Text
    textPrimary: theme.text.primary,
    textSecondary: theme.text.secondary,
    textTertiary: theme.text.tertiary,
    textMuted: theme.text.muted,
    textAccent: theme.text.accent,
    textHighlight: theme.text.highlight,
    
    // Special elements
    inventory: `${theme.elements.inventory} rounded-lg p-3 transition-colors`,
    lore: `${theme.elements.lore} rounded-lg p-3 transition-colors`,
    threat: `${theme.elements.threat} rounded-lg p-3 border`,
    discovery: `${theme.elements.discovery} rounded-lg p-4 border`,
    dialogue: `${theme.elements.dialogue} rounded-lg p-4 border`,
    character: `${theme.elements.character} rounded-lg p-3 border`,
    
    // Override with custom classes
    ...customClasses
  };
};

// Example usage:
// const theme = createThemeClasses('cyberpunk');
// <div className={theme.container}>
//   <div className={theme.header}>Header content</div>
//   <div className={theme.card}>Card content</div>
// </div>
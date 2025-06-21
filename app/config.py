"""
Configuration constants for the MKV muxer.
"""

# Language configurations
LANGUAGE_CONFIGS = {
    'spanish_latin': {
        'codes': ['es-419', 'es-MX'],
        'fallback_code': 'es-419',
        'name': 'Spanish (Latin America)',
        'keywords': ['lat']
    },
    'spanish_spain': {
        'codes': ['es-ES', 'es-724'],
        'fallback_code': 'es-ES', 
        'name': 'Spanish (Spain)',
        'keywords': ['europ']
    },
    'japanese': {
        'codes': ['jpn'],
        'name': 'Japanese'
    },
    'chinese': {
        'codes': ['chi'],
        'fallback_code': 'zh-CN',
        'name': 'Chinese'
    },
    'korean': {
        'codes': ['kor'],
        'name': 'Korean'
    },
    'english': {
        'codes': ['eng'],
        'name': 'English'
    }
}

# Track processing patterns
SUBTITLE_PATTERNS = {
    'forced': ['forced'],
    'sdh': ['sdh'],
    'cc': ['cc'],
    'dubtitle': ['dub'],
    'ao': ['ao']
}

# Processing priorities (order matters)
AUDIO_PRIORITY = ['spanish_latin', 'spanish_spain', 'japanese', 'chinese', 'korean', 'english']
SUBTITLE_PRIORITY = ['spanish_latin', 'spanish_spain', 'english'] 
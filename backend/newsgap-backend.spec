# -*- mode: python ; coding: utf-8 -*-
"""
NewsGap Backend PyInstaller 配置文件
用于将 FastAPI 后端打包为独立可执行文件
"""

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('config.yaml', '.'),
        ('config/', 'config/'),
        ('prompts/', 'prompts/'),
        ('database/schema.sql', 'database/'),
    ],
    hiddenimports=[
        # Uvicorn 相关
        'uvicorn.logging',
        'uvicorn.loops',
        'uvicorn.loops.auto',
        'uvicorn.protocols',
        'uvicorn.protocols.http',
        'uvicorn.protocols.http.auto',
        'uvicorn.protocols.websockets',
        'uvicorn.protocols.websockets.auto',
        'uvicorn.lifespan',
        'uvicorn.lifespan.on',
        
        # 数据库
        'aiosqlite',
        'sqlite3',
        
        # LLM SDK
        'google.generativeai',
        'google.ai.generativelanguage_v1beta',
        'google.api_core',
        'openai',
        'tiktoken',
        
        # HTTP 客户端
        'httpx',
        'httpcore',
        
        # 数据验证
        'pydantic',
        'pydantic_core',
        
        # 爬虫相关
        'feedparser',
        'beautifulsoup4',
        'bs4',
        'lxml',
        'lxml.html',
        'readability',
        
        # FastAPI 相关
        'fastapi',
        'starlette',
        'starlette.routing',
        'starlette.middleware',
        'starlette.middleware.cors',
        
        # 其他
        'yaml',
        'dotenv',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # 排除不必要的库以减小体积
        'matplotlib',
        'PIL',
        'tkinter',
        'numpy',
        'scipy',
        'pandas',
        'pytest',
        'IPython',
        'jupyter',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='newsgap-backend',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,  # 使用 UPX 压缩
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # 无控制台窗口（macOS/Linux）
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

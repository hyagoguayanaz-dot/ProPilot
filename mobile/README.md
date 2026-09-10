# ProPilot Mobile — Android APK

Versão mobile do ProPilot (mesma base do desktop) em **Kivy 2.3 + KivyMD 2.0**, pronta para gerar `.apk` e rodar em qualquer celular Android 7+.

## 📁 Estrutura

```
ProPilot/mobile/
  main.py              → App KivyMD com 6 telas (Dashboard, Missões, Estudos, QRH, SOP, Ajustes)
  database.py          → Persistência Android (app_storage_path) + cache mtime + escrita atômica
  data/                → missions.json (36 missões), manuals.json, sop.json, sop_exercises.json
  assets/icon.png      → Ícone do app (PP-HPA)
  assets/logo.png      → Presplash
  buildozer.spec       → Config de build (package org.guayanaz.propilot, api 33)
  README.md            → Este arquivo
```

## ✨ Funcionalidades (paridade 100% com desktop)

- **Dashboard** — Saudação `Bom dia/tarde/noite, <nome>` + relógio, fase atual, horas de voo, progresso 36 missões, acesso rápido
- **Missões** — Busca + filtros `Todas/PS/AP/NV/NOT`, cards com badge `M/C/A/E/X` colorido, detalhe em dialog com **nível clicável → popup** (cobrança oficial), SOP por exercício + erros comuns/dica, botão marcar concluída (persiste)
- **Central de Estudos** — Busca + filtros `Todas/Básico/Navegação`, 15 manobras com passos
- **QRH / Manuais** — 4 aeronaves (C152, C172S, P-56, PA-28) com overview, specs, limitações, procedimentos e QRH memory items
- **SOP** — 74 seções do SOP ACP 2023, busca + split lista/detalhe
- **Ajustes** — Perfil editável (nome/escola), tema dark/light, 8 cores accent (`spotify`, `ocean` etc), persistência imediata

Persistência em `app_storage_path()/ProPilot/user_progress.json` (Android) ou `ProPilot/data` (desktop). Cache mtime + `RLock` + escrita `.tmp → replace` — zero lag.

## 🧪 Testar no Windows (sem celular)

```bash
pip install kivy==2.3.0 kivymd==2.0.0 Pillow
python mobile/main.py
# A janela Kivy abre com a UI mobile (bottom nav). Use o mouse como toque.
```

## 📦 Gerar APK — 3 formas

### 1. GitHub Actions (mais fácil — 1 clique, sem instalar nada)
1. Faça push do repositório para GitHub (já tem `.github/workflows/build-apk.yml`)
2. Vá em **Actions → Build APK → Run workflow**
3. Aguarde ~12 min (instala SDK/NDK + compila)
4. Baixe o artefato `ProPilot-debug-apk` → `pro-pilot-2.0-debug.apk`
5. Envie o APK para o celular e instale (permitir fontes desconhecidas)

### 2. Local via WSL Ubuntu (Windows)
```powershell
wsl --install -d Ubuntu   # só na 1ª vez, reinicie
wsl
sudo apt update && sudo apt install -y openjdk-17-jdk unzip wget python3-pip
pip install buildozer cython==0.29.36
cd /mnt/c/Users/hyago/ProPilot/mobile
buildozer android debug
# APK em: mobile/bin/propilot-2.0-debug.apk
```

### 3. Local via Docker
```bash
docker run --rm -v "%cd%/mobile":/home/user/app kivy/buildozer android debug
```

## 📲 Instalar no celular

1. Copie o `.apk` para o celular (WhatsApp, Drive, USB)
2. Toque no arquivo → **Permitir instalar de fontes desconhecidas** (Android 8+ pede na hora)
3. Instale → ícone **ProPilot** (PP-HPA vermelho) aparece na gaveta
4. Abra: já vem com 36 missões, SOP e manuais offline

> Dica: `Iniciar via Python.bat` continua funcionando no PC. O APK é para celular.

## 🔧 buildozer.spec — chaves principais

- `title = Pro Pilot`, `package.name = propilot`, `package.domain = org.guayanaz` → `org.guayanaz.propilot`
- `version = 2.0`, `icon.filename = assets/icon.png`, `presplash.filename = assets/logo.png`
- `requirements = python3,kivy==2.3.0,kivymd==2.0.0,Pillow`
- `orientation = portrait`, `fullscreen = 0`, `android.api = 33`, `minapi = 21`
- `permissions = INTERNET`

## 🐛 Troubleshooting

- `ModuleNotFoundError: kivymd` → `pip install kivymd==2.0.0`
- `SDK not found` no buildozer → primeira build baixa ~1 GB, aguarde
- `AIDL not found` → instale `build-tools 33.0.2` via sdkmanager
- Tela preta no celular → limpe `mobile/.buildozer` e recompile

---
Guayanaz Systems © 2026 — ProPilot Mobile v2.0

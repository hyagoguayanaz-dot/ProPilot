#!/bin/bash
set -e
cd /home/user/hostcwd
export PATH=$HOME/.local/bin:$PATH
echo "=== Buildozer fix: aceitando licenças SDK ==="
echo "[fix] Instalando python3-dev e libgl para corrigir NOTNONE..." 
sudo apt update -qq 2>&1 | tail -3 || true
sudo apt install -y python3-dev libgl1-mesa-dev libgles2-mesa-dev 2>&1 | tail -5 || true
# Tenta buildozer uma vez para baixar SDK (pode falhar na licença)
buildozer android debug 2>&1 | tee /tmp/build1.log || true
# Se falhou por licença, aceita manualmente
if grep -q "License.*not accepted\|Aidl not found" /tmp/build1.log; then
  echo "=== Licença não aceita detectada, aceitando via sdkmanager ==="
  # Tenta ambos /root e /home/user (Docker roda como root)
  for CANDIDATE in "/root/.buildozer/android/platform/android-sdk" "/home/user/.buildozer/android/platform/android-sdk"; do
    if [ -d "$CANDIDATE" ]; then
      SDK_ROOT="$CANDIDATE"
      break
    fi
  done
  SDK_ROOT=${SDK_ROOT:-/root/.buildozer/android/platform/android-sdk}
  # Localiza sdkmanager
  SDKMGR=""
  if [ -f "$SDK_ROOT/cmdline-tools/latest/bin/sdkmanager" ]; then
    SDKMGR="$SDK_ROOT/cmdline-tools/latest/bin/sdkmanager"
  elif [ -f "$SDK_ROOT/cmdline-tools/bin/sdkmanager" ]; then
    SDKMGR="$SDK_ROOT/cmdline-tools/bin/sdkmanager"
  elif [ -f "$SDK_ROOT/tools/bin/sdkmanager" ]; then
    SDKMGR="$SDK_ROOT/tools/bin/sdkmanager"
  fi
  if [ -n "$SDKMGR" ]; then
    echo "SDKMGR=$SDKMGR"
    yes | $SDKMGR --sdk_root=$SDK_ROOT --licenses 2>&1 | tail -20 || true
    # Aceita também build-tools explicitamente
    yes | $SDKMGR --sdk_root=$SDK_ROOT "build-tools;37.0.0" 2>&1 | tail -20 || true
  else
    echo "sdkmanager não encontrado, tentando sdkmanager do sistema"
    yes | sdkmanager --licenses 2>&1 | tail -20 || true
  fi
  echo "=== Re-tentando buildozer ==="
  buildozer android debug 2>&1 | tee /tmp/build2.log
else
  echo "=== Primeira tentativa não falhou por licença, verificando APK ==="
  cat /tmp/build1.log | tail -30
fi
ls -lh bin/*.apk 2>&1 | head -5
echo "=== FIM ==="

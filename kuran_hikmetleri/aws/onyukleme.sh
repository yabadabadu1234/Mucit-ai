#!/bin/bash
exec > /var/log/mucit-boot.log 2>&1
set -x
KOVA=mucit-vllm-088976930189
KOK=${MUCIT_KOK:-شدد}
shutdown -P +300
bitir() {
  mkdir -p /opt/sonuc
  cp /var/log/mucit-boot.log /opt/sonuc/boot.log 2>/dev/null
  cp /opt/vllm.log /opt/sonuc/vllm.log 2>/dev/null
  nvidia-smi > /opt/sonuc/nvidia-smi.txt 2>&1
  aws s3 cp --recursive /opt/sonuc s3://$KOVA/sonuc/$(date +%Y%m%d-%H%M%S)/ 
  shutdown -h now
}
trap bitir EXIT
aws s3 cp s3://$KOVA/paket/mucit_paket.tgz /tmp/p.tgz
tar -C / -xzf /tmp/p.tgz
python3 -m venv /opt/venv
. /opt/venv/bin/activate
pip install -q -U pip
pip install -q beautifulsoup4 "huggingface_hub[hf_transfer]"
pip install -q -U vllm --extra-index-url https://wheels.vllm.ai/nightly
export HF_HUB_ENABLE_HF_TRANSFER=1
mkdir -p /opt/sonuc
date +%s > /opt/sonuc/t_indirme_basla
hf download Qwen/Qwen3.8-27B-FP8 --local-dir /opt/model
date +%s > /opt/sonuc/t_indirme_bitis
nohup vllm serve /opt/model --served-model-name qwen --max-model-len 65536 --max-num-seqs 8 \
  --gpu-memory-utilization 0.92 --enable-prefix-caching --kv-cache-dtype fp8 \
  --enable-auto-tool-choice --tool-call-parser qwen3_coder --reasoning-parser qwen3 > /opt/vllm.log 2>&1 &
for i in $(seq 1 360); do
  curl -s localhost:8000/health && break
  sleep 10
done
date +%s > /opt/sonuc/t_sunucu_hazir
export LLM_URL=http://localhost:8000/v1/chat/completions LLM_MODEL=qwen LLM_BAGLAM=65536
PY=$(head -1 $(which vllm) | sed "s/^#!//")
echo "PY=$PY" >> /opt/sonuc/py.txt
$PY -m pip install -q beautifulsoup4 >> /opt/sonuc/pip2.log 2>&1
$PY /opt/harness/tek_madde.py "$KOK" > /opt/sonuc/tek_madde.log 2>&1
date +%s > /opt/sonuc/t_madde_bitis

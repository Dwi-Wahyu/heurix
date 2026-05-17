REPOS=("dwi-wahyu/heurix")

for REPO in "${REPOS[@]}"; do
   echo "🚀 Mengirim secrets Production ke $REPO..."
   gh secret set -f .env -R $REPO
done
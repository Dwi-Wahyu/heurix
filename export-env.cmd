while IFS= read -r line; do
  # Skip baris kosong dan komentar
  [[ -z "$line" || "$line" == \#* ]] && continue
  key="${line%%=*}"
  value="${line#*=}"
  gh secret set "$key" --body "$value"
done < .env
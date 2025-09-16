# Profile Comparator

## Install
python3 -m venv venv && . venv/bin/activate
pip install matplotlib

## Run
python compare_profiles.py profile1.json profile2.json \
  --name-a "Composite groupby" --name-b "Date histogram" \
  --title "Why A is slower than B" --out compare.png

## Output
- compare.png: side-by-side charts (time, drivers, counts)
- Stdout: concise summary and diagnosis

## Notes
- Works with OpenSearch/Elasticsearch profile responses.
- Robust to missing counters; zeros are assumed if absent.
- Fast-path detection: collect_count==0 and optimized_segments>0.
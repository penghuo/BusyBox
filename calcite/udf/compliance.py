import os
import sys
import glob
import json
import csv
import requests
import re
from collections import Counter
from opensearchpy import OpenSearch, helpers

def index_from_files(input_dir, host='localhost', port=9200):
    client = OpenSearch(
        hosts=[{'host': host, 'port': port}],
        http_compress=True,
        use_ssl=False,
        verify_certs=False
    )

    for mapping_path in glob.glob(os.path.join(input_dir, '*.mapping.json')):
        index_name = os.path.basename(mapping_path).rsplit('.mapping.json', 1)[0]
        data_path  = os.path.join(input_dir, f'{index_name}.json')

        # Read mapping
        with open(mapping_path, 'r') as mf:
            mapping_body = json.load(mf).get('mappings', {})

        # Create index if needed
        if not client.indices.exists(index=index_name):
            client.indices.create(index=index_name, body={'mappings': mapping_body})
            print(f'➜ Created index: {index_name}')
        else:
            print(f'➜ Index already exists: {index_name}')

        # ** New existence check **
        if not os.path.isfile(data_path):
            print(f'➜ No data file for "{index_name}" → skipping data indexing')
            continue

        # Read data file and build bulk actions
        actions = []
        with open(data_path, 'r') as df:
            lines = df.readlines()
            for _, doc_line in zip(lines[::2], lines[1::2]):
                doc = json.loads(doc_line)
                actions.append({
                    '_index':  index_name,
                    '_source': doc
                })

        # Bulk-index
        if actions:
            helpers.bulk(client, actions)
            print(f'➜ Indexed {len(actions)} docs into {index_name}')
        else:
            print(f'➜ Found no documents in {data_path}')

def write_html_report(report, report_path='report.html'):
    # calculate summary
    total  = len(report)
    passed = sum(1 for r in report if r['status'] == 'pass')
    failed = total - passed

    # build rows with a CSS class based on status
    rows = []
    for r in report:
        cls = 'pass' if r['status'] == 'pass' else 'failed'
        rows.append(f"""
        <tr class="{cls}">
          <td>{r['query_id']}</td>
          <td>{r['status']}</td>
          <td>{r['reason'] or '&ndash;'}</td>
          <td>
            <pre style="white-space: pre-wrap; word-wrap: break-word;
                        max-height:200px; overflow:auto; margin:0;">
{r['raw_response']}
            </pre>
          </td>
        </tr>""")

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>PPL Compliance Report</title>
  <style>
    table {{
      width: 100%;
      table-layout: fixed;
      border-collapse: collapse;
    }}
    colgroup col {{ border: none; }}
    th, td {{
      border: 1px solid #ccc;
      padding: 8px;
      vertical-align: top;
      overflow: hidden;
      text-overflow: ellipsis;
    }}
    th {{ background: #f0f0f0; }}
    pre {{ margin: 0; font-size: 0.9em; }}

    /* row highlighting */
    tr.pass   {{ background-color: #d4edda; }}
    tr.failed {{ background-color: #f8d7da; }}
  </style>
</head>
<body>
  <h1>PPL Compliance Report</h1>
  <p><strong>Total:</strong> {total} &nbsp;&nbsp; 
     <strong>Pass:</strong> {passed} &nbsp;&nbsp; 
     <strong>Fail:</strong> {failed}</p>
  <table>
    <colgroup>
      <col style="width: 10%;">
      <col style="width: 10%;">
      <col style="width: 20%;">
      <col style="width: 60%;">
    </colgroup>
    <thead>
      <tr>
        <th>Query ID</th>
        <th>Status</th>
        <th>Reason</th>
        <th>Raw Response</th>
      </tr>
    </thead>
    <tbody>
      {''.join(rows)}
    </tbody>
  </table>
</body>
</html>"""

    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f'Report written to {report_path}')

def unify_rows(schema, rows):
    names = [col['name'] for col in schema]
    return [
        { names[i]: row[i] for i in range(len(names)) }
        for row in rows
    ]

def test_ppl_queries(query_dir, max_query_id,
                     report_path='report.html',
                     host='localhost', port=9200):
    """
    Run query_###.ppl → compare actual vs expected CSV (###.results)
    All actual values are stringified to match expected strings.
    Outputs an HTML report with pass/fail and diffs.
    """
    endpoint = f'http://{host}:{port}/_plugins/_ppl'
    report = []

    for i in range(1, int(max_query_id) + 1):
        qid        = f'{i:03d}'
        qfile      = os.path.join(query_dir, f'query_{qid}.ppl')
        expfile    = os.path.join(query_dir, f'query_{qid}.results')

        if not os.path.isfile(qfile):
            report.append({'query_id': qid, 'status':'failed',
                           'reason':'missing .ppl file','raw_response':''})
            continue

        raw_q = open(qfile).read()
        query = re.sub(r'\b\w+\.default\.', '', raw_q).strip()

        try:
            resp     = requests.post(endpoint, json={'query': query})
            raw_resp = resp.text
            data     = resp.json()
        except Exception as e:
            report.append({'query_id': qid, 'status':'failed',
                           'reason':f'HTTP error: {e}','raw_response':''})
            continue

        if 'datarows' not in data:
            report.append({'query_id': qid, 'status':'failed',
                           'reason':'no datarows in response',
                           'raw_response':raw_resp})
            continue

        # unify and stringify actual rows
        actual_dicts = []
        for row in unify_rows(data['schema'], data['datarows']):
            actual_dicts.append({k: str(v) for k, v in row.items()})

        # read expected CSV rows (strings only)
        if not os.path.isfile(expfile):
            report.append({'query_id': qid, 'status':'failed',
                           'reason':'missing expected-results file',
                           'raw_response':raw_resp})
            continue

        expected_dicts = []
        with open(expfile, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for raw_row in reader:
                # drop None-key columns and skip blank rows
                row = {k:v for k,v in raw_row.items() if k is not None}
                if not row or all(v.strip()=='' for v in row.values()):
                    continue
                expected_dicts.append(row)

        # compare ignoring order
        act_cnt = Counter(json.dumps(r, sort_keys=True) for r in actual_dicts)
        exp_cnt = Counter(json.dumps(r, sort_keys=True) for r in expected_dicts)

        if act_cnt == exp_cnt:
            report.append({'query_id': qid, 'status':'pass',
                           'reason':'','raw_response':raw_resp})
        else:
            missing    = [json.loads(s) for s in (exp_cnt-act_cnt).elements()]
            unexpected = [json.loads(s) for s in (act_cnt-exp_cnt).elements()]
            diff = json.dumps({'missing':missing,'unexpected':unexpected}, indent=2)
            report.append({'query_id': qid, 'status':'failed',
                           'reason':diff,'raw_response':raw_resp})

    write_html_report(report, report_path)

if __name__ == '__main__':
    if len(sys.argv) != 4:
        print("Usage: python indexer.py /path/to/indices /path/to/queries maxQueryId")
        sys.exit(1)

    # index_from_files(sys.argv[1])
    test_ppl_queries(sys.argv[2], int(sys.argv[3]))
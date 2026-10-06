#!/usr/bin/env python3
"""Extract the canonical F/E/G/no-go law surfaces with exact source locations."""
from __future__ import annotations

import csv
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAPERS = ROOT / "source" / "papers"
REG = ROOT / "registry"
REG.mkdir(exist_ok=True)

FILES = {
    "F": PAPERS / "Tsiokos_2026_Six_Birds_Foundations_IV_A_Catalog_of_Layer_Agnostic_Structural_Laws.tex",
    "E": PAPERS / "Tsiokos_2026_Six_Birds_Foundations_V_Endogenous_Closure_A_Catalog_of_Structural_Laws_for_Living_Cognitive_and_Social_Systems.tex",
    "G": PAPERS / "Tsiokos_2026_Six_Birds_Foundations_VI_A_Catalog_of_Dynamical_Structural_Laws.tex",
    "NG": PAPERS / "Tsiokos_2026_Six_Birds_No_Go_Theorems_for_Audited_Emergence.tex",
}

G_PAPER_GRADES = {
    "G1": "theorem (Part a) / schema (Part b)",
    "G2": "theorem",
    "G3": "theorem",
    "G4": "schema",
    "G5": "calibration-anchored schema",
    "G6": "schema",
    "G7": "calibration-anchored schema",
    "G8": "theorem",
    "G9": "calibration-anchored schema",
    "G10": "theorem",
    "G11": "theorem",
    "G12": "theorem",
    "G13": "schema",
}


def strip_comments(text: str) -> str:
    out=[]
    for line in text.splitlines():
        m=re.search(r'(?<!\\)%', line)
        out.append(line if not m else line[:m.start()])
    return '\n'.join(out)


def plain(s: str) -> str:
    s=s.replace('---','—').replace('--','–').replace('~',' ')
    for _ in range(6):
        s=re.sub(r'\\(?:textbf|textit|emph|mathrm|mathbf|mathsf|mathtt|operatorname|textrm|texttt|text|underline)\s*\{([^{}]*)\}',r'\1',s)
        s=re.sub(r'\\texorpdfstring\s*\{([^{}]*)\}\s*\{([^{}]*)\}',r'\1',s)
    s=re.sub(r'\\(?:label|cite\w*|ref|cref|Cref|eqref|footnote|url|href)\*?(?:\[[^\]]*\])?\s*\{[^{}]*\}',' ',s)
    s=re.sub(r'\\begin\{[^{}]+\}|\\end\{[^{}]+\}',' ',s)
    # retain common symbols as readable tokens
    symbol_map={r'\emptyset':'∅',r'\to':'→',r'\Rightarrow':'⇒',r'\Longrightarrow':'⇒',r'\neq':'≠',r'\le':'≤',r'\ge':'≥',r'\in':'∈',r'\notin':'∉',r'\subset':'⊂',r'\subseteq':'⊆',r'\cup':'∪',r'\cap':'∩',r'\times':'×',r'\infty':'∞'}
    for a,b in symbol_map.items(): s=s.replace(a,b)
    s=re.sub(r'\\[A-Za-z@]+\*?(?:\[[^\]]*\])?',' ',s)
    s=s.replace('{',' ').replace('}',' ').replace('$',' ')
    s=re.sub(r'\\[\[\]()]',' ',s)
    return re.sub(r'\s+',' ',s).strip()


def parse_newcommands(text: str) -> dict[str,str]:
    commands={}
    # Sufficient for the simple one-argument-free macros used for law names/statements.
    pat=re.compile(r'\\newcommand\s*\{\\([A-Za-z@]+)\}\s*\{')
    for m in pat.finditer(text):
        start=text.find('{', m.end()-1)
        depth=0; buf=[]; i=start
        while i<len(text):
            c=text[i]
            if c=='{' and (i==0 or text[i-1]!='\\'):
                depth+=1
                if depth>1: buf.append(c)
            elif c=='}' and (i==0 or text[i-1]!='\\'):
                depth-=1
                if depth==0: break
                buf.append(c)
            else: buf.append(c)
            i+=1
        commands[m.group(1)]=''.join(buf)
    return commands


def expand_macros(s: str, macros: dict[str,str]) -> str:
    for _ in range(5):
        old=s
        for name,val in macros.items():
            s=re.sub(r'\\'+re.escape(name)+r'\b(?:\{\})?', lambda _m: val, s)
        if s==old: break
    return s


def env_records(path: Path) -> list[dict]:
    text=strip_comments(path.read_text(encoding='utf-8',errors='replace'))
    macros=parse_newcommands(text)
    envs='theorem|lemma|proposition|corollary|definition'
    pat=re.compile(r'\\begin\{('+envs+r')\}(?:\[([^\]]*)\])?')
    records=[]
    for m in pat.finditer(text):
        env=m.group(1); end_marker='\\end{'+env+'}'
        end=text.find(end_marker,m.end())
        if end<0: continue
        body=text[m.end():end]
        label_m=re.search(r'\\label\{([^{}]+)\}',body[:600])
        label=label_m.group(1) if label_m else ''
        title_tex=expand_macros(m.group(2) or '',macros)
        body_expanded=expand_macros(body,macros)
        # remove label and proof-footnote detritus but retain the full theorem statement.
        body_expanded=re.sub(r'\\label\{[^{}]+\}',' ',body_expanded)
        records.append({
            'environment':env,
            'title_tex':title_tex.strip(),
            'title':plain(title_tex),
            'label':label,
            'statement_tex':body_expanded.strip(),
            'statement_plain':plain(body_expanded),
            'source_line':text.count('\n',0,m.start())+1,
        })
    return records


def f_axis(fid: str) -> str:
    if fid in {'F10','F11','F12','F13a','F13b','F24'}: return 'Access'
    if fid in {'F6','F7','F8','F9'}: return 'Stability'
    if fid in {'F2','F3','F4','F5'}: return 'Transport'
    if fid in {'F14','F15a','F15b','F40','F41'}: return 'Symmetry'
    n=int(re.match(r'F(\d+)',fid).group(1))
    if 17 <= n <= 31: return 'Status / Records / Coherence'
    if 33 <= n <= 52: return 'Self-reference / Limits'
    if fid=='F53': return 'Closure–Reality anchor'
    return 'Unclassified'


def f_status(fid: str) -> str:
    if fid in {'F6','F53'}: return 'substrate-delegated anchor'
    if fid in {'F13a','F14'}: return 'partial theorem wrapper'
    if fid in {'F13b','F15b'}: return 'obligation-guarded wrapper'
    return 'direct theorem row'


def cluster_for_g(gid: str) -> str:
    n=int(gid[1:])
    if n<=3:return 'A — Temporal Currencies'
    if n<=7:return 'B — Moving and Self-Generated Obstructions'
    if n<=10:return 'C — Defect Integration and Emergent Transport'
    return 'D — Productive Obstructions and Sparse Saturation'


def extract_f() -> list[dict]:
    out=[]
    for r in env_records(FILES['F']):
        m=re.search(r'(?:thm|lem|prop):(?P<id>F\d+[ab]?)$',r['label'])
        if not m: continue
        fid=m.group('id')
        out.append({
            'law_id':fid,'name':r['title'],'axis':f_axis(fid),'formal_status':f_status(fid),
            'environment':r['environment'],'source_paper':'P028','source_path':str(FILES['F'].relative_to(ROOT/'source')),
            'source_line':r['source_line'],'source_label':r['label'],'statement_plain':r['statement_plain'],'statement_tex':r['statement_tex'],
        })
    def key(x):
        m=re.match(r'F(\d+)([ab]?)',x['law_id']); return (int(m.group(1)),m.group(2))
    return sorted(out,key=key)


def extract_e() -> list[dict]:
    out=[]
    for r in env_records(FILES['E']):
        m=re.fullmatch(r'thm:e(\d+)',r['label'])
        if not m: continue
        eid='E'+m.group(1)
        n=int(m.group(1))
        cluster=('A — Laws of Endogeny' if n<=5 else 'B — Priced Access and Control' if n<=10 else 'C — Stack Rewrite, Individuation, and Repair Transport' if n<=13 else 'D — Carried Memory and Adaptive Capacity')
        out.append({
            'law_id':eid,'name':re.sub(r'^E\d+:\s*','',r['title']),'cluster':cluster,
            'paper_grade':'theorem','environment':r['environment'],'source_paper':'P030','source_path':str(FILES['E'].relative_to(ROOT/'source')),
            'source_line':r['source_line'],'source_label':r['label'],'statement_plain':r['statement_plain'],'statement_tex':r['statement_tex'],
        })
    return sorted(out,key=lambda x:int(x['law_id'][1:]))


def extract_g() -> list[dict]:
    out=[]
    seen=set()
    for r in env_records(FILES['G']):
        m=re.fullmatch(r'thm:G(\d+)(b)?',r['label'])
        if not m: continue
        gid='G'+m.group(1)
        if gid in seen:
            # G1 has a and b theorem surfaces; append part b to the canonical record.
            existing=next(x for x in out if x['law_id']==gid)
            existing['statement_plain'] += ' | Part (b): ' + r['statement_plain']
            existing['statement_tex'] += '\n\n% PART B\n' + r['statement_tex']
            existing['source_label'] += ';'+r['label']
            continue
        seen.add(gid)
        name=re.sub(r',\s*Part \(a\):.*$','',r['title'])
        out.append({
            'law_id':gid,'name':name,'cluster':cluster_for_g(gid),
            'paper_grade':G_PAPER_GRADES[gid],'environment':r['environment'],'source_paper':'P029','source_path':str(FILES['G'].relative_to(ROOT/'source')),
            'source_line':r['source_line'],'source_label':r['label'],'statement_plain':r['statement_plain'],'statement_tex':r['statement_tex'],
        })
    return sorted(out,key=lambda x:int(x['law_id'][1:]))


NG_SUMMARIES={
'NG_ARROW_DPI':'Deterministic observation cannot increase forward-versus-reversed path-space KL divergence.',
'NG_PROTOCOL_TRAP':'A stationary reversible autonomous lift has zero micro and observed arrow, even with hidden protocol coordinates.',
'NG_FORCE_FOREST':'Every antisymmetric edge field on a finite forest is a potential difference; forest support carries no cycle obstruction.',
'NG_FORCE_NULL':'An exact antisymmetric edge form has zero sum on every closed walk.',
'NG_MACRO_CLOSURE_DEFICIT':'Closure deficit equals the minimum weighted KL loss of any macro kernel and is positive when same-macro microstates have different packaged futures.',
'NG_OBJECT_CONTRACTIVE':'Under strict Dobrushin contraction, epsilon-stable distributions are mutually close; exact fixed distributions are unique.',
'NG_LADDER_IDEM':'Iterating an idempotent packaging map produces no ladder after the first application.',
'NG_LADDER_BOUNDED_INTERFACE':'A fixed finite interface defines only finitely many predicates and therefore cannot support an infinite strict definability ladder.',
}
NG_ESCAPE={
'NG_ARROW_DPI':'Leave deterministic honest pushforward; use stochastic observation or fitted/proxy macro models, or introduce genuine micro nonreversibility.',
'NG_PROTOCOL_TRAP':'Drop stationarity or reversibility, use external scheduling, or introduce genuinely driven lifted dynamics.',
'NG_FORCE_FOREST':'Use support with positive cycle rank or change the exact support notion; thresholded proxy graphs are outside scope.',
'NG_FORCE_NULL':'Break exactness or replace exact bidirected support with a thresholded/regularized proxy.',
'NG_MACRO_CLOSURE_DEFICIT':'Change package, lag, or dynamics, or accept a fitted macro kernel only as a diagnostic proxy.',
'NG_OBJECT_CONTRACTIVE':'Move to a noncontractive regime; clustering heuristics are outside theorem evidence.',
'NG_LADDER_IDEM':'Change operator class or package; non-idempotent updates and interface/theory growth are outside scope.',
'NG_LADDER_BOUNDED_INTERFACE':'Grow the lens, domain, or package; fixed finite interfaces must stabilize.',
}

def extract_ng() -> list[dict]:
    out=[]
    for r in env_records(FILES['NG']):
        m=re.fullmatch(r'thm:(NG_[A-Z_]+)',r['label'])
        if not m: continue
        nid=m.group(1)
        out.append({
            'law_id':nid,'name':nid,'summary':NG_SUMMARIES[nid],'escape_route':NG_ESCAPE[nid],
            'environment':r['environment'],'source_paper':'P032','source_path':str(FILES['NG'].relative_to(ROOT/'source')),
            'source_line':r['source_line'],'source_label':r['label'],'statement_plain':r['statement_plain'],'statement_tex':r['statement_tex'],
        })
    return out


def write_registry(name: str, rows: list[dict], expected: int) -> None:
    if len(rows)!=expected:
        raise RuntimeError(f'{name}: expected {expected}, found {len(rows)}')
    with (REG/f'{name}.jsonl').open('w',encoding='utf-8') as f:
        for r in rows:f.write(json.dumps(r,ensure_ascii=False)+'\n')
    csv_fields=[k for k in rows[0].keys() if k!='statement_tex']
    with (REG/f'{name}.csv').open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=csv_fields,lineterminator="\n");w.writeheader();w.writerows({k:r.get(k,'') for k in csv_fields} for r in rows)
    md=[f'# {name.replace("_"," ").title()}', '', f'Count: **{len(rows)}**', '']
    for r in rows:
        md.extend([f"## {r['law_id']} — {r.get('name','')}", '',
                   f"- Source: `{r['source_path']}:{r['source_line']}` (`{r['source_label']}`)"])
        for key,label in [('axis','Axis'),('cluster','Cluster'),('formal_status','Formal status'),('paper_grade','Paper grade'),('summary','Interpretive summary'),('escape_route','Escape route')]:
            if r.get(key): md.append(f"- {label}: {r[key]}")
        md.extend(['', r['statement_plain'], ''])
    (REG/f'{name}.md').write_text('\n'.join(md),encoding='utf-8')


def main():
    f=extract_f();e=extract_e();g=extract_g();ng=extract_ng()
    write_registry('F_laws',f,52)
    write_registry('E_laws',e,16)
    write_registry('G_laws',g,13)
    write_registry('no_go_theorems',ng,8)
    print(f'F={len(f)} E={len(e)} G={len(g)} NG={len(ng)}')

if __name__=='__main__':main()

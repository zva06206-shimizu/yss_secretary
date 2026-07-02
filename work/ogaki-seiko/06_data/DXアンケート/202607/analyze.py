# -*- coding: utf-8 -*-
"""DXアンケート集計。Zohoエクスポート(xlsx)のResponsesシートから
カテゴリ別・部門別・拠点別・全社DX成熟度スコアを算出する。
採点原則：各設問 5=成熟(良い)〜1=未成熟(悪い)。「該当なし/わからない」は除外(平均に含めない)。
Zoho内蔵のMeanは該当なしを6点として数えるため使わない(スコアを不当に押し上げる)。
"""
import zipfile, re, io, sys
from xml.etree import ElementTree as ET

XLSX = 'DX推進状況アンケート ご協力のお願い.xlsx'
NS = '{http://schemas.openxmlformats.org/spreadsheetml/2006/main}'

# 設問→(選択肢を score1..5 の順で。該当なしは除外)
SCALE = {
 'Q1':["ほぼ全てが紙","大半が紙","半分程度","一部のみ","ほぼ無い"],
 'Q2':["ほぼ全てが紙","大半が紙","半分程度","一部のみ","ほぼ無い"],
 'Q3':["6時間以上","4〜6時間","2〜4時間","1〜2時間","1時間未満"],
 'Q4':["ほぼ毎日ある","週に数回ある","月に数回ある","たまにある","ほぼ無い"],
 'Q5':["非常に多い","多い","一部ある","少ない","ほぼ無い"],
 'Q6':["ほぼ無い","少ない","半分程度","多い","ほぼ全て"],
 'Q7':["ほぼ全て","多い","半分程度","少ない","ほぼ無い"],
 'Q8':["月10回以上","月6〜10回","月3〜5回","月1〜2回","ほぼ無い"],
 'Q9':["40時間以上","20〜40時間","10〜20時間","5〜10時間","5時間未満"],
 'Q10':["ほぼ独立運用","手作業転記が多い","CSVで連携","一部自動連携","自動連携されている"],
 'Q11':["毎日ある","週に数回","月に数回","少ない","ほぼ無い"],
 'Q12':["ほぼ紙","一部のみ","半分程度","大部分電子化","ほぼ全て電子化"],
 'Q13':["非常に多い","多い","一部ある","少ない","ほぼ無い"],
 'Q14':["1週間以上","1週間程度","3〜5日","2日以内","即日"],
 'Q15':["1週間以上","1週間以内","3日以内","翌日","即日"],
}
CATEGORIES = [
 ("1.ペーパーレス化",       ["Q1","Q2","Q3"]),
 ("2.データ一元化",         ["Q4","Q5","Q6"]),
 ("3.集計・転記の自動化",   ["Q7","Q8","Q9"]),
 ("4.システム連携",         ["Q10","Q11"]),
 ("5.情報・ナレッジ共有",   ["Q12","Q13"]),
 ("6.承認・意思決定スピード",["Q14","Q15"]),
]
# Responsesシートの列: 7=拠点 8=部署 10..24=Q1..Q15
COL_SITE, COL_DEPT, COL_Q1 = 7, 8, 10

def score(q, ans):
    if ans is None: return None
    a = ans.strip()
    if a.startswith("該当なし") or a=="" or "わからない" in a: return None
    opts = SCALE[q]
    return (opts.index(a)+1) if a in opts else None

def colnum(ref):
    c=re.match(r'([A-Z]+)',ref).group(1); n=0
    for ch in c: n=n*26+(ord(ch)-64)
    return n

def load_responses():
    z=zipfile.ZipFile(XLSX)
    ss=[]
    root=ET.fromstring(z.read('xl/sharedStrings.xml'))
    for si in root.findall(NS+'si'):
        ss.append(''.join(t.text or '' for t in si.iter(NS+'t')))
    root=ET.fromstring(z.read('xl/worksheets/sheet1.xml'))
    rows=[]
    for row in root.iter(NS+'row'):
        cells={}
        for c in row.findall(NS+'c'):
            v=c.find(NS+'v'); t=c.get('t'); val=''
            if v is not None: val=ss[int(v.text)] if t=='s' else v.text
            else:
                isn=c.find(NS+'is')
                if isn is not None: val=''.join(x.text or '' for x in isn.iter(NS+'t'))
            if val not in ('',None): cells[colnum(c.get('r'))]=val
        rows.append((int(row.get('r')), cells))
    # データ行 = col1(連番)が数値の行。col2は英数字トークンなので使わない。
    data=[]
    for r,cells in rows:
        seq=cells.get(1,'')
        if re.match(r'^\d', str(seq)):
            data.append(cells)
    return data

def mean(xs):
    xs=[x for x in xs if x is not None]
    return round(sum(xs)/len(xs),2) if xs else None

def main():
    # 標準出力をUTF-8に(Windowsコンソールの文字化け回避)
    try: sys.stdout.reconfigure(encoding='utf-8')
    except Exception: pass
    data=load_responses()
    N=len(data)
    print(f"=== 回答数 N={N} （途中経過） ===\n")

    # 設問別平均(該当なし除外)＋有効回答数
    qmean={}; qn={}
    for q in SCALE:
        col=COL_Q1+int(q[1:])-1
        sc=[score(q,c.get(col)) for c in data]
        valid=[x for x in sc if x is not None]
        qmean[q]=mean(sc); qn[q]=len(valid)

    print("【設問別平均（5=成熟, 該当なし除外）】 ※nは有効回答数")
    for q in SCALE:
        print(f"  {q}: 平均 {qmean[q]}  (n={qn[q]}/{N})")

    print("\n【カテゴリ別平均】")
    cat_avgs={}
    for name,qs in CATEGORIES:
        ms=[qmean[q] for q in qs if qmean[q] is not None]
        cavg=round(sum(ms)/len(ms),2) if ms else None
        cat_avgs[name]=cavg
        state=""
        if cavg is not None:
            state = "要改善" if cavg<2.0 else "改善余地大" if cavg<3.0 else "概ね良好" if cavg<4.0 else "定着・活用"
        print(f"  {name}: {cavg}  [{state}]  (設問{','.join(qs)})")

    # 全社DX成熟度スコア(100点)= Σ (カテゴリ平均-1)/4*16.67
    pts=[]
    for name,qs in CATEGORIES:
        c=cat_avgs[name]
        if c is not None: pts.append((c-1)/4*16.67)
    total=round(sum(pts),1)
    band = "紙・属人化中心" if total<=25 else "電子化途上" if total<=50 else "業務改善定着" if total<=75 else "データ活用・自動化段階"
    print(f"\n【全社DX成熟度スコア】 {total}/100  [{band}]")

    # 拠点別・部署別（全設問の有効回答の平均＝総合成熟度の目安）
    def group_avg(colidx):
        g={}
        for c in data:
            key=c.get(colidx,'(未記入)')
            scores=[score(q, c.get(COL_Q1+int(q[1:])-1)) for q in SCALE]
            scores=[x for x in scores if x is not None]
            g.setdefault(key,{'sum':0,'cnt':0,'resp':0})
            g[key]['sum']+=sum(scores); g[key]['cnt']+=len(scores); g[key]['resp']+=1
        return g

    print("\n【拠点別 総合平均（全設問・該当なし除外）】")
    for k,v in sorted(group_avg(COL_SITE).items(), key=lambda kv:-(kv[1]['sum']/kv[1]['cnt'] if kv[1]['cnt'] else 0)):
        avg=round(v['sum']/v['cnt'],2) if v['cnt'] else None
        print(f"  {k}: {avg}  (回答{v['resp']}名, 有効{v['cnt']}件)")

    print("\n【部署別 総合平均（全設問・該当なし除外）】")
    for k,v in sorted(group_avg(COL_DEPT).items(), key=lambda kv:-(kv[1]['sum']/kv[1]['cnt'] if kv[1]['cnt'] else 0)):
        avg=round(v['sum']/v['cnt'],2) if v['cnt'] else None
        print(f"  {k}: {avg}  (回答{v['resp']}名, 有効{v['cnt']}件)")

if __name__=='__main__':
    main()

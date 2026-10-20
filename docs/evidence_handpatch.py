import pandas as pd, os, re, sys
os.chdir(r"D:\Research-Publishing\03-fx-data-artefact\bibliometrics")
e = pd.read_csv(r"data\clean\evidence-table.autogen.csv", keep_default_na=False)
drop_kw = ['Improving data quality : data consistency', 'Herd behaviour in the cryptocurrency', 'Sustainable Development of Digital Financial', 'Improving Data Quality for the Australian High Frequency', 'End-to-End Data Quality Assessment', 'XBRL and Data Standardization', 'Time-Related Factors of Data Quality']
mask = e.citation.apply(lambda c: any(k in c for k in drop_kw))
dropped = e[mask][['rank', 'citation']].copy()
dropped["reason"] = "off-topic after hand screen (not about FX or financial data errors)"
e = e[~mask].copy()
RN = "depth\\reading-notes\\"
notes = {'Krohn': 'krohn-2023-fixings.md', 'Ito, Yuko Hashimoto': 'ito-2006-ebs-seasonality.md', 'Sullivan': 'sullivan-1999-datasnooping.md', 'Pseudo-Mathematics': 'bailey-2014-pseudo-mathematics.md', 'Brooks': 'brooks-2006-periodicities.md', 'Anderson, Tim Bollerslev, Ashish': 'anderson-1998-microstructure-tests.md', 'Frömmel': 'frommel-2023-trading-hours.md', 'Chaboud': 'chaboud-2004-macro-releases.md', 'Fatum': 'fatum-2012-intervention-spread.md', 'Batten': 'batten-2005-hurst.md', 'Bradley': 'bradley-2013-timestamps.md', 'Filimonov': 'filimonov-2015-hawkes-bias.md', 'Noss': 'noss-2017-sterling-flash.md', 'Breedon': 'breedon-2012-intraday-patterns.md', 'Huang': 'huang-1999-spreads.md', 'Ince': 'ince-2006-datastream.md'}
full = {'Krohn', 'Sullivan', 'Pseudo-Mathematics', 'Brooks', 'Frömmel', 'Chaboud', 'Fatum', 'Batten', 'Bradley', 'Filimonov', 'Breedon', 'Ito, Yuko Hashimoto', 'Noss'}
e['depth_reading_note'] = ''
for i, r in e.iterrows():
    for k, v in notes.items():
        if k in r.citation:
            e.at[i, 'depth_reading_note'] = RN + v
            if k in full:
                e.at[i, 'read_status'] = 'full text read (working-paper or accepted-manuscript PDF; see note)'
            elif k.startswith('Anderson'):
                e.at[i, 'read_status'] = 'abstract read (PDF is an image scan, no text)'
            elif k in ('Huang', 'Ince'):
                e.at[i, 'read_status'] = 'abstract read'
e = e.reset_index(drop=True)
common = dict(oa_status='open web', pdf_in_folder='', local_citations='', global_citations_openalex='', openalex_id='', country_or_setting='')
extra = [
    dict(citation='radiusred (GitHub), "HistData timestamps are one hour late in summer: EST is not a fixed UTC-5", issue #82, 2026-10-09', year=2026, doi_or_link='https://github.com/radiusred/tradedesk-marketdata/issues/82', open_access_link='https://github.com/radiusred/tradedesk-marketdata/issues/82', sub_literature='c_data_quality (practitioner, not in corpus)', study_type='practitioner defect report', data='HistData M1 vs Dukascopy cache, 25 instruments, 2020-01 to 2026-02', method='minute-by-minute equality at shifted offsets; weekly-open timing', main_finding_from_abstract='Summer days match only at -60 min; two provider eras (New York local time with DST until 2018-12-16, then Europe/Zurich minus 6 h).', read_status='full text read (web page via GitHub API)', relation_to_seans_paper='direct prior art for the clock-convention finding', depth_reading_note=RN + 'radiusred-2026-histdata-clock.md', **common),
    dict(citation='jay79-boop (GitHub), pull request #87 "Add a cross-instrument backtest lab...", pwb-toolbox, 2026-08-22', year=2026, doi_or_link='https://github.com/jay79-boop/pwb-toolbox/pull/87', open_access_link='https://github.com/jay79-boop/pwb-toolbox/pull/87', sub_literature='c_data_quality (practitioner, not in corpus)', study_type='practitioner write-up', data='histdata ASCII M1, eight instruments, eight years', method='compare winter and summer month returns across vendors', main_finding_from_abstract='histdata stamps are New York local time with DST; a strategy measured +39 points on a flat offset and +7 on the right one.', read_status='full text read (PR description via GitHub API)', relation_to_seans_paper='earlier prior art for the clock finding; example of the consequence', depth_reading_note=RN + 'jay79boop-2026-backtest-lab.md', **common),
    dict(citation='HistData.com, F.A.Q. and Data Files - Detailed Specification (vendor documentation)', year=2026, doi_or_link='https://www.histdata.com/f-a-q/', open_access_link='https://www.histdata.com/f-a-q/', sub_literature='c_data_quality (vendor documentation)', study_type='vendor documentation', data='', method='', main_finding_from_abstract='Documents EST without DST and bar prices based on the tick bid price.', read_status='full text read (Wayback copy of 2019-03-14 checked for the quoted sentences)', relation_to_seans_paper='primary source for what the vendor says', depth_reading_note=RN + 'histdata-faq-2026.md', **common),
]
e = pd.concat([e, pd.DataFrame(extra)], ignore_index=True)
e['rank'] = range(1, len(e) + 1)
e.to_csv('evidence-table.csv', index=False, encoding='utf-8-sig')
dropped.to_csv(r'tables\evidence_hand_screen_removed.csv', index=False, encoding='utf-8-sig')
print(len(e), len(dropped)); print(e.read_status.value_counts().to_dict())

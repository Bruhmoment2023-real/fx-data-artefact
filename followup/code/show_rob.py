import pandas as pd
pd.set_option("display.width",250); pd.set_option("display.max_rows",300)
r1=pd.read_csv('tables/R1_profile_all_instruments.csv'); print(r1.to_string(index=False))
r2=pd.read_csv('tables/R2_size_by_year.csv')
print(r2.pivot(index='year',columns='inst',values='mean_1659_bp').round(2).to_string())
print(r2.pivot(index='year',columns='inst',values='t_1659').round(1).to_string())
r3=pd.read_csv('tables/R3_mask_grid_rule.csv'); x=r3[r3['sample']=='2015-2026']
print(x.pivot(index='inst',columns='mask_start_minutes_before_1700',values='sharpe').round(2).to_string())
print(x.pivot(index='inst',columns='mask_start_minutes_before_1700',values='t').round(1).to_string())
x=r3[r3['sample']=='2009-2014']; print(x.pivot(index='inst',columns='mask_start_minutes_before_1700',values='t').round(1).to_string())
r4=pd.read_csv('tables/R4_after_side_residual.csv'); x=r4[r4['sample']=='2015-2026']
print(x.pivot(index='inst',columns='after_mask_minutes',values='t').round(1).to_string())
print(x.pivot(index='inst',columns='after_mask_minutes',values='mean_bp').round(2).to_string())

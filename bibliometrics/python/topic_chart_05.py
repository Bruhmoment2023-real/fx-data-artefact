"""Paper 05 topic chart: yearly records on AI/ChatGPT, Wikipedia and Stack Overflow, with the ChatGPT release marked."""
import os, sys
import matplotlib.pyplot as plt
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import topic_util as T

B = os.path.abspath(sys.argv[1])
M, cfg = T.load(B)
M = M[(M.year >= 2005) & (M.year <= 2026)]
terms = {
    "Wikipedia": r"wikipedia",
    "Stack Overflow / Q&A communities": r"stack ?overflow|stack exchange|community question|q&a (site|communit|platform)",
    "ChatGPT / generative AI / LLM": r"chatgpt|generative ai|genai|large language model|\bllms?\b|gpt-?[34]|ai chatbot|ai search|ai overview",
    "Page views / traffic": r"page ?views?|web traffic|clickstream|pageview",
    "Students using AI for schoolwork": r"(student|pupil|learner|school)[^.]{0,80}(chatgpt|generative ai|ai tools?|large language)|(chatgpt|generative ai|ai tools?)[^.]{0,80}(student|pupil|learner|homework|assignment)",
}
yrs = list(range(2005, 2027))
fig, ax = plt.subplots(figsize=(11, 6))
rows = {}
for (k, p), c in zip(terms.items(), ["#457b9d", "#e76f51", "#2a9d8f", "#8d6a9f", "#e9c46a"]):
    s = M[M.txt.str.contains(p, regex=True)].groupby(M.year.astype(int)).size().reindex(yrs, fill_value=0)
    rows[k] = s
    ax.plot(yrs, s.values, marker="o", ms=4, label=f"{k} (n={int(s.sum())})", color=c)
ax.axvline(2022.92, color="k", ls="--", lw=1)
ax.text(2022.85, ax.get_ylim()[1] * 0.97, "ChatGPT released\n30 Nov 2022", ha="right", va="top", fontsize=8)
ax.set_xlabel("Publication year"); ax.set_ylabel("Corpus records mentioning the term in title/abstract")
ax.set_title(f"When did the literature start to cover AI, Wikipedia traffic and students' AI use?\nCorpus: {len(M)} records, 2005-2026 (OpenAlex metadata, {cfg['paper_id']})", loc="left", fontsize=11, fontweight="bold")
ax.legend(fontsize=8, loc="upper left"); ax.spines[["top", "right"]].set_visible(False); ax.grid(alpha=0.3)
import pandas as pd
pd.DataFrame(rows).to_csv(os.path.join(B, "tables", "py_topic_terms_by_year.csv"), encoding="utf-8-sig")
T.save(fig, B, "py_10_topic_terms_by_year")
T.caption(B, "py_10_topic_terms_by_year.png", "Topic terms by year against the ChatGPT release",
          "Number of corpus records per year whose title or abstract mentions Wikipedia, Stack Overflow/Q&A, ChatGPT/generative AI, page-view traffic, and students' AI use; the dashed line is the ChatGPT release.",
          "Case-insensitive regular expressions on title+abstract in master.csv (patterns in python/topic_chart_05.py); counts per publication year, a record can appear in several lines.",
          "The corpus was built from topic searches, so a rise after 2022 partly reflects my query terms and the 2025-26 records not yet indexed or cited, not the true size of the literature.")

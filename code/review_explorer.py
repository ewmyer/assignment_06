"""
review_explorer.py — what Salt City Coffee's customers are saying, at a glance.

The owner reads every review on the shop's website, but thirty reviews across
three locations is more than anyone can hold in their head. This page shows
what customers praise and complain about — by location and by subject — and
answers plain-English questions like "Do people like the mocha latte?" or "What
is the most popular product?" from the reviews themselves, with the evidence
underneath.

The page is assembly again: `analyze_reviews` does all the API work (from the
cache after the first run), and the Q&A box is three calls you have already
written — find the question's scope and evidence, build the messages, ask the
model.

Run it:  Run and Debug -> "Streamlit Run: Current File"
Test it: pytest tests/test_pipeline.py -k app
"""
# --- The page ---------------------------------------------------------------------
#
# No scaffolding. Every function this page needs exists in the reviews package,
# and every widget it needs you have used before. README Step 8 has the exact
# widgets, keys and labels; the tests in tests/test_pipeline.py -k app check them.
#
# The shape, in words:
#
#   reviews_file <- the REVIEWS_FILE environment variable if it is set, else
#                   REVIEWS_FILE from the package (the tests use the 5 test reviews)
#   title and a sentence of instructions
#   mentions <- analyze_reviews(reviews_file)          (from cache after the first run)
#   two st.selectbox filters side by side, keys "location" and "subject",
#       each "All" plus the sorted values in mentions
#   four st.metric cards: Reviews (unique review_id), Mentions, Positive, Negative
#   summary <- summarize_items(the filtered mentions)
#   three st.tabs, one st.dataframe in each:
#   "Most praised": rows with net > 0, highest net first, top 5
#   "Most complained about": rows with net < 0, lowest first, top 5
#   "What people said": the filtered mentions
#   "Ask the reviews": st.text_input key "question", st.button "Ask" key "ask"
#   when Ask is clicked and the question is not blank:
#       scope, evidence <- answer_question(question, mentions, load_aliases())
#       no evidence  -> st.warning, and do NOT call the model
#       otherwise    -> answer <- ask_llm(build_messages(question, evidence)),
#                       inside `with st.spinner(...)` (it takes a few seconds)
#                       show the answer, a caption with describe_scope(scope),
#                       and the evidence
#
# What the page does NOT do: call the API directly, group, or count by hand
# beyond the metrics. That logic lives in the package.

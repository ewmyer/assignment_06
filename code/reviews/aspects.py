"""
aspects.py — Step 3: from API output to "what are people saying about what".

The tables from Step 2 each know one thing. This step puts them together into
`mentions` — one row per thing a customer had an opinion about — and then asks
the questions the owner cares about.

Two sources of mentions, because each API catches what the other misses:

- **Opinion targets** (Azure opinion mining): "the mocha latte was overpriced" —
  a target, its own sentiment, and the words behind it. The best evidence.
- **Named entities** (Azure NER): "Otto always says hi" has no opinion words for
  opinion mining to latch onto, but the entity recognizer knows Otto is a
  Person. These mentions borrow their sentence's sentiment.

No walkthrough. The docstrings state what each function returns; `tests/` says
how it is checked.
"""

import pandas as pd

from .apicalls import get_entities
from .pipeline import (
    entities_step,
    entities_table,
    opinions_table,
    sentences_table,
    sentiment_step,
    subjects_step,
)
from .settings import (
    ALIASES_FILE,
    LOCATION_WORDS,
    MENTION_CATEGORIES,
    SUBJECT_WORDS,
    SYSTEM_PROMPT,
    cache_path,
)

MENTION_COLUMNS = ["review_id", "sentence_id", "mention", "mention_sentiment",
                   "assessments", "mention_offset", "source"]


def entity_mentions(entities: pd.DataFrame, sentences: pd.DataFrame,
                    opinions: pd.DataFrame) -> pd.DataFrame:
    """Entities that opinion mining missed, as mentions with their sentence's sentiment.

    Same seven columns as `opinions_table`. Each entity is placed in the sentence
    whose span contains it — `sentence_offset <= entity_offset <
    sentence_offset + sentence_length` — and takes that sentence's
    `sentence_id` and `sentence_sentiment` (as `mention_sentiment`).
    `assessments` is `""` and `source` is `"entity"`.

    Leave out an entity when an opinion target in the same review and sentence
    already covers it: their lowercased texts are equal, or one contains the
    other ("oat milk" inside "oat milk cortado"). Sorted by `review_id` then
    `mention_offset`, plain index.
    """
    # TODO: your code here
    pass


def load_aliases() -> dict:
    """data/aliases.csv as a dict: alternate spelling -> the item's one name."""
    aliases = pd.read_csv(ALIASES_FILE)
    return dict(zip(aliases["alias"].str.lower(), aliases["item"]))


def item_name(mention: str, aliases: dict) -> str:
    """The canonical name for a mention: lowercased, then looked up in the aliases.

        item_name("Parking downtown", aliases)  ->  "parking"
        item_name("Mocha Latte", aliases)        ->  "mocha latte"   # not an alias
    """
    # TODO: your code here
    pass


def build_mentions(reviews: pd.DataFrame, sentences: pd.DataFrame,
                   opinions: pd.DataFrame, entity_rows: pd.DataFrame,
                   subjects: pd.DataFrame, aliases: dict) -> pd.DataFrame:
    """Everything together: one row per mention, with its subject, sentence and review.

    Columns, in this order: `review_id`, `date`, `location`, `stars`, `item`,
    `mention`, `subject`, `mention_sentiment`, `assessments`, `sentence_text`,
    `source`, `subject_confidence`.

    `opinions` and `entity_rows` stacked (`pd.concat`), then merged with
    `subjects` on (`review_id`, `mention`), `sentences` on (`review_id`,
    `sentence_id`) and `reviews` on `review_id`. `item` is `item_name` of the
    mention. Rows whose subject is `"other"` are dropped, and so is a second
    mention of the same item in the same sentence ("oat milk" and "oat milk
    cortado" both becoming "oat milk cortado"). Sorted by `review_id` then
    `mention_offset`, plain index.
    """
    # TODO: your code here
    pass


def analyze_reviews(reviews_file: str) -> pd.DataFrame:
    """The whole pipeline for one reviews file: raw CSV in, `mentions` out.

    Reads the CSV, runs `sentiment_step` and `entities_step` (cached with
    `cache_path(reviews_file, "sentiment")` and `"entities"`), builds the three
    tables, `entity_mentions`, then `subjects_step` on the combined mentions
    (cached with `cache_path(reviews_file, "subjects", "csv")`), and finally
    `build_mentions` with `load_aliases()`. Call the functions; do not redo them.
    """
    # TODO: your code here
    pass


def summarize_items(mentions: pd.DataFrame) -> pd.DataFrame:
    """Most-discussed items: one row per (subject, item).

    Columns: `subject`, `item`, `mentions` (how many rows), `positive`,
    `negative` (how many of those rows have that `mention_sentiment`), and `net`
    (positive minus negative). Sorted by `mentions` descending, then `item`;
    plain index. Named aggregation, as in Assignment 05.
    """
    # TODO: your code here
    pass


# --- The Q&A box --------------------------------------------------------------------


def question_scope(question: str, entity_document: dict, mentions: pd.DataFrame,
                   aliases: dict) -> dict:
    """What a question is about: the items, locations and subjects it names.

    Returns a dict with three lists, any of which may be empty:

        {"items": [...], "locations": [...], "subjects": [...]}

    `entity_document` is `get_entities(question)["results"]["documents"][0]`.

    - **items**: its Person and Product entities, put through `item_name` —
      kept even when no review mentions them, so "chai latte" is in the scope
      of a question about it — then every item in `mentions["item"]` whose
      lowercased name appears in the lowercased question (entity recognition
      does not know that "wifi" or "parking" are things). No repeats,
      entities first.
    - **locations**: each location in `LOCATION_WORDS` with any of its words in
      the lowercased question, in `LOCATION_WORDS` order.
    - **subjects**: the same, with `SUBJECT_WORDS`.

        question_scope("Do people like the mocha latte?", ...)
            -> {"items": ["mocha latte"], "locations": [], "subjects": []}
        question_scope("How is the staff at Armory Square?", ...)
            -> {"items": [], "locations": ["Armory Square"],
                "subjects": ["customer service"]}
    """
    # TODO: your code here
    pass


SCOPE_COLUMNS = {"items": "item", "subjects": "subject", "locations": "location"}


def evidence_for(mentions: pd.DataFrame, scope: dict) -> pd.DataFrame:
    """The mentions inside a question's scope — the rows the answer is built from.

    Items and subjects say *what* the question is about, so a row matches when
    its item is one of the items **or** its subject is one of the subjects.
    Locations say *where*, and narrow that further. An empty list does not
    filter, so a question that names nothing gets every mention.
    """
    selected = mentions
    if scope["items"] or scope["subjects"]:
        what = (mentions["item"].isin(scope["items"])
                | mentions["subject"].isin(scope["subjects"]))
        selected = selected[what]
    if scope["locations"]:
        selected = selected[selected["location"].isin(scope["locations"])]
    return selected.reset_index(drop=True)


def describe_scope(scope: dict) -> str:
    """A scope in words, for the page: "mocha latte · Westcott", or "all reviews"."""
    parts = [", ".join(scope[key]) for key in SCOPE_COLUMNS if scope[key]]
    return " · ".join(parts) if parts else "all reviews"


def build_messages(question: str, evidence: pd.DataFrame, limit: int = 20) -> list:
    """The conversation for `ask_llm`: a system prompt, then question and evidence.

    Returns a list of two dicts:

        {"role": "system", "content": SYSTEM_PROMPT}
        {"role": "user",   "content": <the text below>}

    The user content is, line by line:

        Question: <question>
        Facts: <n> mentions — <p> positive, <q> negative, <r> neutral or mixed.
        Items, most mentioned first:
        - <item> (<subject>): <mentions> mentions, <pos> positive, <neg> negative
        - ...
        Review sentences:
        - (<location>, <date>, <item>, <mention_sentiment>) <sentence_text>
        - ...

    One item line per row of `summarize_items(evidence)`, in its order (`<pos>`
    and `<neg>` are its `positive` and `negative` columns); one
    sentence line per evidence row, at most `limit` of them. The counts cover
    every row, so "what is the most popular product?" is answered from the
    whole table, not from whichever sentences fit. pandas does the counting; the
    language model only writes the answer. Language models are bad at counting
    and good at prose — give each the job it is good at.
    """
    # TODO: your code here
    pass


def answer_question(question: str, mentions: pd.DataFrame, aliases: dict):
    """What a question is about and the evidence for it: (scope, evidence)."""
    document = get_entities(question)["results"]["documents"][0]
    scope = question_scope(question, document, mentions, aliases)
    return scope, evidence_for(mentions, scope)

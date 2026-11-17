---
license: cc-by-nc-sa-4.0
pretty_name: "islamlab — The Classical Arabic Lexicons"
language:
  - ar
task_categories:
  - text-retrieval
  - question-answering
  - text-generation
size_categories:
  - 100K<n<1M
tags:
  - arabic
  - lexicon
  - dictionary
  - classical-arabic
  - islam
  - lexicography
configs:
  - config_name: default
    data_files:
    - split: train
      path: train-*.parquet
---

# islamlab — The Classical Arabic Lexicons

**197,731 entries** from **136 lexical works** — the dictionaries,
the *gharīb* collections and the technical glossaries — cut so that the
headword is its own column and the article is its own text.

A dictionary sits in the corpus like any other book, but nobody reads one that
way. This is the same material arranged for the thing people actually do with
it: look a word up.

| work | author | entries |
|---|---|---:|
| شمس العلوم ودواء كلام العرب من الكلوم | نشوان الحميري | 58,637 |
| معجم تيمور الكبير في الألفاظ العامية | أحمد بن إسماعيل بن محمد تيمور | 13,298 |
| تاج العروس من جواهر القاموس | مرتضى الزبيدي | 12,051 |
| التكملة والذيل والصلة لكتاب تاج اللغة وصحاح العربية | الحسن بن محمد بن الحسن الصغاني | 8,833 |
| التكملة والذيل والصلة للصغاني | الصغاني | 8,825 |
| المحكم والمحيط الأعظم | ابن سيده المرسي | 6,323 |
| منتخب من صحاح الجوهري | أبو نصر إسماعيل بن حماد الجوهري ال | 6,180 |
| مجمع بحار الأنوار في غرائب التنزيل ولطائف الأخبار | جمال الدين، محمد طاهر بن علي الصدي | 6,177 |
| مجمع الآداب في معجم الألقاب | ابن الفوطي | 5,794 |
| تجديد الصحاح | أبو نصر الجوهري | 5,758 |
| الصحاح تاج اللغة وصحاح العربية | أبو نصر الجوهري | 5,661 |
| معجم مقاييس اللغة | ابن فارس | 4,882 |
| النهاية في غريب الحديث والأثر | ابن الأثير، مجد الدين أبو السعادات | 4,334 |
| مجمع الغرائب ومنبع الرغائب | عبد الغافر الفارسي | 3,779 |

## Columns

- `headword` — the entry as the work heads it, with any entry number split
  into `entry_no`.
- `root` — filled (69,517 rows) where the
  work is arranged by root and the heading states it: `مادة`, `باب`, `فصل`,
  `حرف`, or a bare tri-literal. Empty where the arrangement is alphabetical by
  word, or where the heading is a chapter rather than an article.
- `text` — the article, Arabic untouched.
- `work_id`, `title_ar`, `author_ar`, `death_year_ah`, `page_start` — join keys
  and citation.

Coverage is uneven by design: it follows what the source editions marked as a
heading. A work with few headings contributes few but long entries.

## Where this comes from

Derived from
[`islamlab/islamic-sciences`](https://huggingface.co/datasets/islamlab/islamic-sciences),
which is where the gate, the provenance and the credits live: scope is
**Ahl al-Sunnah wa'l-Jamāʿah**, and a work enters only if its author died by
1350 AH, so every text is in the public domain. The machine-readable
transcriptions carry **CC BY-NC-SA 4.0**, and so does this.

Corrections and removal requests are welcome on the **Community** tab.

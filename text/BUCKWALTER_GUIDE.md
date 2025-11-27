# Buckwalter Transliteration Guide

## What is Buckwalter?

**Buckwalter transliteration** is a way to represent Arabic text using only ASCII/Latin characters. It was developed by Tim Buckwalter for Arabic-to-English machine translation.

This TTS system uses Buckwalter because:
- ✅ Works with any keyboard (no Arabic keyboard needed)
- ✅ Easy to use in APIs and URLs
- ✅ Preserves all Arabic phonetic information
- ✅ One-to-one character mapping (reversible)

---

## Quick Conversion Tool

I've created a simple converter for you:

### Arabic → Buckwalter
```bash
python3 convert_arabic.py 'مرحبا'
# Output: mrHbA
```

### Buckwalter → Arabic
```bash
python3 convert_arabic.py --reverse 'mrHbA'
# Output: مرحبا
```

---

## Character Mapping Reference

### Consonants

| Arabic | Buckwalter | Name | Example |
|--------|------------|------|---------|
| ء | ' | hamza | ma' (ماء) |
| ا | A | alif | bAb (باب) |
| ب | b | ba | bnt (بنت) |
| ت | t | ta | ktb (كتب) |
| ث | v | tha | vlj (ثلج) |
| ج | j | jim | jml (جمل) |
| ح | H | ha | Hlm (حلم) |
| خ | x | kha | xbz (خبز) |
| د | d | dal | drs (درس) |
| ذ | * | dhal | *hb (*هب) |
| ر | r | ra | rjl (رجل) |
| ز | z | zay | zmn (زمن) |
| س | s | sin | shr (شهر) |
| ش | $ | shin | $ms ($مس) |
| ص | S | sad | Sbr (صبر) |
| ض | D | dad | Drb (ضرب) |
| ط | T | ta | Tyr (طير) |
| ظ | Z | za | Zhr (ظهر) |
| ع | E | ayn | Elm (علم) |
| غ | g | ghayn | grb (غرب) |
| ف | f | fa | fkr (فكر) |
| ق | q | qaf | qlb (قلب) |
| ك | k | kaf | ktAb (كتاب) |
| ل | l | lam | lbn (لبن) |
| م | m | mim | mAl (مال) |
| ن | n | nun | nwr (نور) |
| ه | h | ha | hnd (هند) |
| و | w | waw | wld (ولد) |
| ي | y | ya | yد (يد) |

### Special Characters

| Arabic | Buckwalter | Name |
|--------|------------|------|
| ة | p | ta marbuta |
| ى | Y | alif maqsura |
| أ | > | alif with hamza above |
| إ | < | alif with hamza below |
| آ | \| | alif with madda |
| ؤ | & | waw with hamza |
| ئ | } | ya with hamza |

### Vowels (Diacritics)

| Arabic | Buckwalter | Name | Sound |
|--------|------------|------|-------|
| َ | a | fatha | short 'a' |
| ُ | u | damma | short 'u' |
| ِ | i | kasra | short 'i' |
| ّ | ~ | shadda | doubled consonant |
| ْ | o | sukun | no vowel |
| ً | F | tanwin fath | -an |
| ٌ | N | tanwin damm | -un |
| ٍ | K | tanwin kasr | -in |

---

## Common Examples

### Greetings
```
مرحبا          → mrHbA
السلام عليكم   → AlslAm Elykm  
صباح الخير     → SbAH Alxyr
مساء الخير     → msA' Alxyr
```

### Common Phrases
```
شكرا           → $krA
من فضلك        → mn fDlk
كيف حالك       → kyf HAlk
ما اسمك        → mA Asmk
```

### Numbers
```
واحد           → wAHd
اثنان          → AvnAn
ثلاثة          → vlAvp
أربعة          → >arbEp
خمسة           → xmsp
```

### Days of the Week
```
الأحد          → Al>Hd
الإثنين        → Al<vnyn
الثلاثاء       → AlvlAvA'
الأربعاء       → Al>arbEA'
الخميس         → Alxmys
الجمعة         → Aljmp
السبت          → Alsbt
```

---

## Tips for Using Buckwalter

### 1. Case Sensitivity Matters
- Lowercase = light consonants (e.g., `s` = س)
- Uppercase = emphatic/special (e.g., `S` = ص, `A` = ا)

### 2. Special Symbol Keys
- `>` and `<` = different hamza positions
- `~` = shadda (doubled consonant)
- `'` = hamza standalone
- `*` = ذ (dhal)
- `$` = ش (shin)

### 3. Diacritics (Optional but Recommended)
While many systems work without diacritics, including them improves pronunciation:
```
كتب without diacritics: ktb
كَتَبَ with diacritics: kataba
```

### 4. Common Mistakes
❌ `mrHaba` → Should be `mrHabA` (final alif)
❌ `Salam` → Should be `slAm` (plain س not ص)
❌ `shams` → Should be `$ms` ($ for ش)

---

## Using in the TTS API

### Example API Call
```bash
curl -X POST "http://0.0.0.0:8000/api/tts" \
  -H "Content-Type: application/json" \
  -d '{
    "buckw": "mrHabA",
    "rate": 1.0,
    "denoise": 0.01
  }'
```

### Python Example with Converter
```python
from text.phonetise_buckwalter import arabic_to_buckwalter
import requests

# Convert Arabic to Buckwalter
arabic_text = "مرحبا بك في النظام"
buckw_text = arabic_to_buckwalter(arabic_text)

# Generate speech
response = requests.post('http://0.0.0.0:8000/api/tts', json={
    'buckw': buckw_text,
    'rate': 1.0,
    'denoise': 0.01
})
```

---

## Online Converters

If you need to convert large amounts of text, you can use online tools:
- **Yamli**: https://www.yamli.com/
- **Google Translate** (copy Arabic, then use converter tool)
- Or use our `convert_arabic.py` script!

---

## Advanced: Understanding the Phonetics

The Buckwalter system preserves all phonetic information:

### Emphatic vs. Plain Consonants
```
Plain: t (ت) → Emphatic: T (ط)
Plain: d (د) → Emphatic: D (ض)
Plain: s (س) → Emphatic: S (ص)
Plain: z (ذ) → Emphatic: Z (ظ)
```

### Different H Sounds
```
h (ه) = regular h sound
H (ح) = pharyngeal h sound (deeper)
x (خ) = velar fricative (like German "ch")
```

### Glottal Stop (Hamza)
```
' (ء) = standalone hamza
> (أ) = hamza above alif
< (إ) = hamza below alif
& (ؤ) = hamza on waw
} (ئ) = hamza on ya
```

---

## Quick Reference Card

Save this for quick lookup:

```
CONSONANTS:
b ت  t ت  v ث  j ج  H ح  x خ  d د  * ذ  r ر  z ز  
s س  $ ش  S ص  D ض  T ط  Z ظ  E ع  g غ  f ف  
q ق  k ك  l ل  m م  n ن  h ه  w و  y ي

SPECIAL:
' ء  > أ  < إ  | آ  & ؤ  } ئ  p ة  Y ى  A ا

VOWELS:
a َ  u ُ  i ِ  ~ ّ  o ْ  F ً  N ٌ  K ٍ
```

---

## Practice Exercises

Try converting these yourself, then check with `convert_arabic.py`:

1. كتاب (book)
2. مدرسة (school)
3. صديق (friend)
4. شمس (sun)
5. قمر (moon)

<details>
<summary>Click for answers</summary>

1. ktAb
2. mdrsp
3. Sdyq
4. $ms
5. qmr

</details>

---

For more information, see:
- Wikipedia: https://en.wikipedia.org/wiki/Buckwalter_transliteration
- API Guide: `API_GUIDE.md`

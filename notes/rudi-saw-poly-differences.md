> Research/design evidence with its original experimental scope. Historical blockers and next steps below are not current project instructions; see [current state](../docs/CURRENT_STATUS.md).

# Phase20B4 — seven serialized differences and DSP reach

2026-10-07. **VERIFIED fields / CALCULATED conditional material difference.**
Overall event qualification **PARTIAL**. Compare the exact authored340-byte
Phase20B2 patch to cached project0 bytes[158996,159336). Original files and
earlier exports are preserved. Canonical evidence:
`builds/phase20b-projectassoc/final-v2/`.

|Decimal offset (hex)|Authored→cached|Serialized field|Original descriptor ID|Class|
|---|---|---|---|---|
|35 (23)|63→64|settings.keyboardOctave, encoded−1→0|5|F: event/UI relevance not closed|
|221 (DD)|0→126|macroSlots[1].value, UI Macro2|BF|E: correction seed|
|238 (EE)|46→11|macroSlots[2].value, UI Macro3|D0|E: correction seed|
|255 (FF)|83→84|macroSlots[3].value, UI Macro4|E1|E: correction seed|
|272 (110)|0→51|macroSlots[4].value, UI Macro5|F2|E: correction seed|
|289 (121)|0→58|macroSlots[5].value, UI Macro6|103|E: correction seed|
|306 (132)|48→73|macroSlots[6].value, UI Macro7|114|E: correction seed|

**VERIFIED:** installed patch schema places settings at32 with keyboardOctave
at+3 signed, and macro records at204+17*m. Their first byte is `value`; four
subslots follow, each4 bytes(destination,start,end,signed depth). Original
805454C+8*ID descriptors independently match these offsets/types. The six
changed macro bytes are **values, not assignments or names**. All32 assignment
records are byte-identical. The keyboard field is not promoted to classA/B:
its selected event-source relevance still needs an original consumer proof.

## Original correction arithmetic

**VERIFIED:** 36192→3BE3E→bank parameter view→3BBD6→3BD00 reads raw
descriptor values. 35F84 reads one macro value and16 assignment bytes, returning
the next descriptor ID. 3602A invokes it eight times startingAE(hex), after
clearing140 bytes of work halfwords at20005B10+8C*bank.
36042→1A7E4 setsr2=0→1A93C zero-fill; this is an ARM correction workspace,
not DSP history initialization. 3608C..A6 compares/copies70 accumulated signed
halfwords to active correction array20005C28+8C*bank and notifies changed IDs.
360B2 adds the selected correction to the raw patch getter and clips0..127.

For the selected legal ascending assignment domains:

`span = abs(s8(end-start)), replacing0 by1`

`position = clamp(s8(value-start),0,span)`

`contribution = trunc_toward_zero(2*position*s8(depth-64)/span)`

Destination0 is skipped; other destinations accumulate atindex destination−1.
The original step model and independent rational model agree on4096 selected
assignment/value fixtures. **TESTED arithmetic**, not executed ARM/DSP.
No generic macro center is assumed. The app property default0 is separately
identified; no firmware default or event-time active value is inferred from it.

## Material consequences using stored values

**CONDITIONAL premise:** original3602A fully recomputes from either exact
340-byte patch view, with no intervening automation/override; corresponding
original callbacks publish controls. This premise is not a recovered event.

|Changed macro|Unchanged assignments affected|Authored→cached contribution|
|---|---|---|
|Macro2|Osc2Level destination18|0→121|
|Macro3|FilterEnv2ToFreq25; Env2Decay31; Env2Release33|18→4;28→0;2→0|
|Macro4|Env1Decay27; Env1Release29; Env2Release33|50→51;52→52;54→55|
|Macro5|FilterFrequency21|0→33|
|Macro6|FilterResonance22|0→42|
|Macro7|ChorusLevel46|37→56|

Destination29 illustrates integer convergence: macro value83→84 produces the
same truncated correction52. It does not make the entire macro immaterial;
its other destinations change. Destination33 combines Macro3+Macro4, so total
correction56→55. These names are installed schema labels corroborated by the
original destination→parameter-ID table805A2B0.

Eight corrected parameters differ (base bytes identical):

|Parameter ID|Source label|Corrected authored→cached|Original reach|
|---|---|---|---|
|19|Osc2Level|0→121|278D0→X3C5;1B89→X2E2;6BB; global mask remains material|
|22|FilterFrequency|13→46|2797E→X3E7;1B89→retainedX2E9;6DF|
|24|FilterResonance|2→44|27964→X2E8;6D8/6DE|
|26|FilterEnv2ToFreq|97→83|27998→X2EA;6E2/6E4|
|29|Env1Decay|72→73|per-slot envelope parameters→4D5|
|2E|Env2Decay|34→6|per-slot envelope parameters→4D5|
|30|Env2Release|68→67|per-slot envelope parameters→4D5|
|4F|ChorusLevel|37→56|27C52→X3F1 effect target; outside immediate P657 scalar inputs|

These are parameter-boundary differences, not a claim all downstream current
smoothed values or rendered samples differ at every invocation.

**CALCULATED conditional original upper24 ARM transfers:**

|Destination|Authored|Cached|Evidence|
|---|---|---|---|
|X2E7|0A0000|0A0000|ID1F10 unchanged,2794A shift|
|X2E8|020408|2C58B1|27964→3B8BA: multiply01020408|
|X2EA|1C0000|0CAAAA|27998→28314: encoded−64 lookup805A340, multiplierAAAAAB|
|X2EB|000000|000000|ID230 unchanged,279B2→3B8BA|
|X3E7 target|19B6AA|2FB6AA|2797E→282E4; immutable high-half addend590C|

**VERIFIED correction to Phase20B3:** 282F4 usesPC-relative literal28750,
value805BCD0; LDRH[IP+4] reads immutable805BCD4=`590C`. The high-half
addend previously described as runtime/unresolved is fixed flash data.
The source-backed target formula is
`upper24((AAAAAB*v+B7FFFFEC+(590C<<16)) mod2^32)`.
CurrentX2E9 still requires its prior value and smoothing update history.

Therefore the stored-macro load/recompute context is **MATERIALLY DIFFERENT**.
No conversion convergence exists forX2E8 orX2EA under the stated premise.
Event-time macro automation may replace these values; that timeline is not
qualified. The existential question whether some cached event becomes materially
equivalent therefore remains **INSUFFICIENT EVIDENCE**, not a universal NO.

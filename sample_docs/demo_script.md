# Pet Care Coach Demo Script — Three Levels of Context

This script demonstrates the evolution from basic AI chat to sophisticated agentic RAG systems. Follow along step-by-step to see how better context systems lead to better answers.

---

## Setup Instructions

Before starting the demo:

1. **Load Seed Data**: Click "Load Seed Data" in the sidebar to populate the diagnostics database
2. **Upload Transcript**: Upload `sample_docs/visit_transcript_daisy.md` to the document store
3. **Verify Setup**: 
   - Check that diagnostics database shows 1 visit for Daisy
   - Check that document store shows chunks indexed (should be ~10 chunks)

---

## Part 1: Model-Only (No RAG) — "Guessing in the Dark"

**Narrative**: *Before the clinic visit, a pet owner notices symptoms and turns to a general AI chat for help. Without any specific context about their pet or access to medical records, the AI can only provide general information.*

**Mode**: Select **"Model-only (No RAG)"** in the sidebar

### Question 1: Initial Symptom Inquiry
**Ask**: 
> "My dog has been vomiting for the past two days, seems lethargic, and isn't eating much. What could be causing this?"

**Expected Response Characteristics**:
- Lists multiple possible causes (GI upset, infection, obstruction, etc.)
- Provides general advice
- Recommends seeking veterinary care
- Cannot reference specific pet history or test results
- Response is generic, not personalized

**Talking Points**:
- "Notice how the AI provides a broad range of possibilities"
- "Without context about the specific pet, visit, or test results, the answer is necessarily generic"
- "This is like asking a general medical question without any patient history"

---

### Question 2: Follow-up on Specific Concern
**Ask**:
> "Should I be worried about kidney problems?"

**Expected Response Characteristics**:
- Discusses general kidney disease symptoms and causes
- Cannot reference specific lab values or the pet's actual results
- Provides general guidance about when to seek care
- No connection to the vomiting/lethargy symptoms mentioned earlier

**Talking Points**:
- "The AI has no memory of our previous conversation in this session"
- "It can't access any specific diagnostic information about this pet"
- "This demonstrates the limitation of context-free AI"

---

## Part 2: Classic RAG (Transcript) — "Remembering What Was Said"

**Narrative**: *After the clinic visit, the visit transcript has been uploaded to the system. Now the assistant can search and recall what was discussed during the visit.*

**Mode**: Select **"Classic RAG (Transcript)"** in the sidebar

### Question 3: Recall Visit Discussion
**Ask**:
> "What did the vet recommend we do at home after the visit?"

**Expected Response Characteristics**:
- References specific recommendations from the transcript
- Mentions hydration, bland diet, monitoring, follow-up
- Cites the source document
- Shows retrieved chunks in "Show retrieved sources"
- More specific and actionable than model-only

**Talking Points**:
- "Now the AI can search the visit transcript and find specific recommendations"
- "Notice the citations showing which parts of the transcript were used"
- "This is much more useful than generic advice"

---

### Question 4: Symptom Summary
**Ask**:
> "What were Daisy's symptoms when she came to the clinic?"

**Expected Response Characteristics**:
- Lists specific symptoms from the transcript (vomiting, lethargy, decreased appetite)
- Mentions duration (2 days)
- References the physical exam findings (tacky gums, dehydration)
- Grounded in the actual visit record

**Talking Points**:
- "The AI can now recall the specific symptoms discussed during the visit"
- "This demonstrates how RAG enables the system to 'remember' conversations"

---

### Question 5: Treatment Plan Details
**Ask**:
> "What follow-up care did the vet recommend, and when should we come back?"

**Expected Response Characteristics**:
- Mentions the 3-5 day follow-up for rechecking kidney values
- Discusses what to watch for (vomiting, lethargy)
- References the specific treatment plan from the transcript
- Cannot provide actual lab values (not in transcript in detail)

**Talking Points**:
- "The AI can recall the treatment plan and follow-up instructions"
- "However, notice it can't provide the actual lab values - those are in the database, not the transcript"
- "This shows the limitation of text-only RAG"

---

### Question 6: Lab Results Discussion (Transcript Only)
**Ask**:
> "What did the vet say about Daisy's lab results?"

**Expected Response Characteristics**:
- Summarizes the vet's discussion of lab results from the transcript
- Mentions elevated BUN (32), Creatinine (1.8), elevated WBC, etc.
- Discusses the vet's interpretation (dehydration affecting kidneys)
- Cannot show the actual structured data or compare values to reference ranges
- Response is based on what was *said*, not the raw data

**Talking Points**:
- "The AI can tell us what the vet discussed about the lab results"
- "But it can't query the actual database to show us the structured data"
- "This is where we need to move to the next level"

---

## Part 3: Agentic Context (Transcript + Diagnostics) — "Reasoning Across Evidence"

**Narrative**: *Now the system has access to both the visit transcript AND the structured diagnostic database. The assistant can intelligently combine information from both sources to provide comprehensive, evidence-based answers.*

**Mode**: Select **"Agentic Context (Transcript + Diagnostics)"** in the sidebar

### Question 7: Query Diagnostic Data
**Ask**:
> "What are the most recent CBC test results for Daisy?"

**Expected Response Characteristics**:
- Executes SQL query against the diagnostics database
- Returns structured data showing WBC, RBC, HCT, HGB, PLT, NEU, LYM values
- Shows actual numeric values with flags (H, L, N)
- "How I answered" panel shows the SQL query executed
- Response is data-driven, not just narrative

**Talking Points**:
- "Now the AI can query the structured database directly"
- "Notice the SQL query in the 'How I answered' panel - this shows transparency"
- "We're getting actual data, not just what someone said about the data"

---

### Question 8: Identify Abnormal Values
**Ask**:
> "Which lab values were abnormal in Daisy's most recent visit?"

**Expected Response Characteristics**:
- Queries database for results with flags H (high) or L (low)
- Lists specific abnormal values: WBC (high), PLT (low), NEU (high), BUN (high), CREA (high), ALP (high)
- Shows actual values and reference ranges
- May also search transcript to see what vet said about these
- Combines structured data with narrative context

**Talking Points**:
- "The AI can now identify which specific values are abnormal"
- "It's working with the actual structured data, not just descriptions"
- "This enables precise, data-driven answers"

---

### Question 9: Correlate Transcript and Data
**Ask**:
> "Do the lab results support the vet's assessment that dehydration is affecting Daisy's kidneys?"

**Expected Response Characteristics**:
- **Uses BOTH tools**: Searches transcript for vet's assessment AND queries database for BUN/Creatinine values
- Shows actual BUN (32) and Creatinine (1.8) values from database
- References vet's interpretation from transcript
- Correlates the data with the assessment
- "How I answered" shows both retrieved chunks AND SQL queries
- Confidence level should be High (has both sources)

**Talking Points**:
- "This is the power of agentic RAG - combining multiple sources"
- "Notice in 'How I answered' it shows both transcript chunks AND SQL queries"
- "The AI is reasoning across evidence from different sources"
- "This demonstrates true context integration"

---

### Question 10: Evidence-Based Interpretation
**Ask**:
> "The vet mentioned elevated BUN and Creatinine for Daisy. What are the actual values, and do they support her concern about dehydration?"

**Expected Response Characteristics**:
- Retrieves BUN (32 mg/dL) and Creatinine (1.8 mg/dL) from database
- References vet's discussion from transcript
- Compares values to normal ranges
- Provides evidence-based interpretation
- Shows both transcript excerpts and database results

**Talking Points**:
- "The AI can now provide the exact values AND correlate them with the vet's assessment"
- "This combines narrative context with structured data"
- "Much more powerful than either source alone"

---

### Question 11: Comprehensive Analysis
**Ask**:
> "Based on the visit transcript and lab results for Daisy, what should I watch for at home, and which abnormal lab values are most concerning?"

**Expected Response Characteristics**:
- Searches transcript for home care instructions
- Queries database for all abnormal values
- Prioritizes which abnormalities are most significant (likely kidney values)
- Combines treatment recommendations with diagnostic context
- Provides comprehensive, evidence-based guidance

**Talking Points**:
- "This question requires synthesizing information from both sources"
- "The AI can prioritize concerns based on actual data"
- "Notice how it combines 'what to watch for' (from transcript) with 'which values are concerning' (from database)"

---

### Question 12: Follow-up Planning
**Ask**:
> "What follow-up tests for Daisy did the vet mention, and do the current lab results suggest urgency for that follow-up?"

**Expected Response Characteristics**:
- Retrieves follow-up plan from transcript (3-5 day recheck of kidney values)
- Queries current abnormal kidney values (BUN, Creatinine)
- Assesses urgency based on severity of abnormalities
- Provides evidence-based recommendation about follow-up timing

**Talking Points**:
- "The AI can now reason about urgency based on actual data"
- "It combines the treatment plan (from transcript) with diagnostic severity (from database)"
- "This demonstrates practical application of agentic RAG"

---

## Summary: The Progression

### Model-Only (Part 1)
- **Capability**: General knowledge only
- **Limitation**: No specific context, generic responses
- **Use Case**: Initial symptom inquiry before any medical interaction

### Classic RAG (Part 2)
- **Capability**: Can search and recall visit conversations
- **Limitation**: Only has narrative/text data, no structured diagnostic data
- **Use Case**: Recalling what was discussed, treatment plans, recommendations

### Agentic Context (Part 3)
- **Capability**: Can query structured data AND search transcripts, intelligently combining both
- **Advantage**: Evidence-based answers that correlate narrative with data
- **Use Case**: Comprehensive analysis, correlating assessments with actual results, evidence-based decision support

---

## Key Takeaways for Your Class

1. **Context Matters**: Each level adds more context, leading to better answers
2. **Structured + Unstructured**: Combining structured data (database) with unstructured text (transcripts) is powerful
3. **Transparency**: The "How I answered" panels show the reasoning process
4. **Tool Selection**: The agent intelligently chooses which tools to use
5. **Evidence-Based**: Answers are grounded in actual data, not just general knowledge

---

## Tips for Running the Demo

1. **Start Fresh**: Clear chat between sections to show clear progression
2. **Show "How I Answered"**: Expand these panels to show transparency, especially in Part 3
3. **Compare Responses**: You can ask similar questions in different modes to show the difference
4. **Highlight SQL Queries**: In Part 3, point out the actual SQL queries being generated
5. **Emphasize Correlation**: Questions 9-12 show the real power of combining sources

---

## Optional: Advanced Questions (If Time Permits)

### Question 13: Pattern Recognition
**Ask**:
> "Are there any patterns in Daisy's abnormal lab values that might indicate a specific condition?"

**Expected Response Characteristics**:
- Analyzes multiple abnormal values together
- May identify patterns (e.g., kidney values elevated together, inflammatory markers)
- Combines data analysis with clinical knowledge

### Question 14: Treatment Validation
**Ask**:
> "The vet recommended rehydration. Which of Daisy's lab values would be most likely to improve with proper hydration?"

**Expected Response Characteristics**:
- Identifies values most affected by hydration (BUN, Creatinine, possibly HCT)
- References vet's recommendation from transcript
- Provides evidence-based explanation

---

**Remember**: Better answers aren't just better prompts. They're better **context systems**.

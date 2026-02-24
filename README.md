# Discussion Guide Generator

Generate context-aware, ready-to-use cold calling scripts powered by OpenAI, modeled on your best-performing guides.

## Features

- **Context-Aware Generation**: Automatically detects prior relationships and adjusts tone/content
- **Reference-Based Styling**: Learns from your `master_reference.md` examples
- **Source Material Upload**: Upload PDF, DOCX, PPTX files as a "Deep Knowledge Base" for enriched pitches
- **Feedback Loop**: Refines objection handling based on real call feedback
- **Audience Segmentation**: Differentiates between new customers and upsells

## Setup

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Set your OpenAI API key**:
   Create a `.env` file in the project root:
   ```
   OPENAI_API_KEY=your_key_here
   ```

3. **Add reference guides** (optional but recommended):
   Edit `master_reference.md` with examples of your best cold calling scripts.

4. **Run the app**:
   ```bash
   streamlit run streamlit_app.py
   ```

## Usage

### Basic Flow
1. Fill in **Campaign Inputs**:
   - Product description
   - Goal (Leads/Meetings/Workshops)
   - Target Group
   - Personas

2. Optionally upload **Source Materials** (product decks, case studies, technical docs)

3. Click **Generate Script**

### Advanced Options

- **Additional Constraints & Notes**: Add mandatory rules like "Avoid corporate jargon" or "They already know our brand"
- **Recent Call Feedback**: Input objections heard live (e.g., "They're too busy") to refine handling
- **Tone of Voice**: Customize the conversational style

## File Upload Feature

Upload PDF, Word, or PowerPoint files containing:
- Product specifications
- Case studies
- Technical documentation
- Value propositions

The AI will **consult** these materials to:
- Find specific technical details
- Extract unique value props
- Identify pain points and solutions
- Pull relevant data/proof points

**Note**: Uploaded materials complement (not replace) your Product field. The AI uses them as a "Deep Knowledge Base" for enrichment.

## How It Works

1. **Reference Analysis**: Loads `master_reference.md` and analyzes style/tone/structure
2. **Context Detection**: Scans Target Group for prior relationship indicators
3. **Material Extraction**: Extracts text from uploaded files (if any)
4. **Prompt Assembly**: Combines all inputs into a structured prompt
5. **AI Generation**: OpenAI generates a tailored cold calling script
6. **Output**: Clean Markdown with 6 sections (Hook, Why Now, Discovery, Value Prop, CTA, Objection Handling)

## Project Structure

```
discussionguide-generator/
├── .env                    # API keys (gitignored)
├── .gitignore
├── requirements.txt
├── master_reference.md     # Your reference guides
├── streamlit_app.py       # Main application
└── README.md
```

## Troubleshooting

**Import errors for pdfplumber/docx/pptx?**
- Run `pip install -r requirements.txt` to install document parsing libraries

**"OPENAI_API_KEY is missing" error?**
- Ensure `.env` file exists with `OPENAI_API_KEY=your_key`
- Restart the Streamlit app after creating `.env`

**Files not extracting properly?**
- Check file format (PDF, DOCX, PPTX only)
- Some encrypted or scanned PDFs may not extract text
- Error messages will appear if extraction fails

## Tips for Best Results

1. **Quality over quantity**: 2-3 perfect reference examples > 10 mediocre ones
2. **Be specific**: Generic input = generic output. Add details to Target Group and Personas
3. **Use constraints**: Add notes like "Skip intro, they know us" for better targeting
4. **Upload relevant materials**: Product decks and case studies yield the best enrichment


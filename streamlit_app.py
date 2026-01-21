import os
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()


@st.cache_data(show_spinner=False)
def read_master_reference() -> str:
    """Read the entire reference library from master_reference.md (if present)."""
    path = Path(__file__).with_name("master_reference.md")
    if not path.exists():
        return ""
    content = path.read_text(encoding="utf-8")
    return content.strip()


def _trim_reference_for_prompt(reference_text: str, max_chars: int = 40_000) -> tuple[str, bool]:
    """
    Keep prompts reliable by trimming very large reference libraries to a manageable size.
    Returns (trimmed_text, was_trimmed).
    """
    if len(reference_text) <= max_chars:
        return reference_text, False
    return reference_text[-max_chars:], True


def _detect_prior_relationship(target_group: str) -> bool:
    """Detect if the target group indicates an existing relationship or brand awareness."""
    text = target_group.lower()
    relationship_signals = [
        "already",
        "existing",
        "current customer",
        "in contact",
        "familiar with",
        "know us",
        "working with",
        "using our",
        "past customer",
    ]
    return any(signal in text for signal in relationship_signals)


def _build_prompt(
    product: str,
    goal: str,
    target_group: str,
    personas: str,
    tone_of_voice: str,
    reference_examples: str,
    audience_mode: str,
    feedback: str,
    additional_reference: str,
) -> str:
    audience_instruction = (
        "New Customer: lead with trust-building, highlight the status-quo problem, and why change now."
        if audience_mode == "New Customer"
        else "Upsell: lean on the existing relationship, show how this is the natural next step for their size/revenue, and reflect established familiarity."
    )
    
    # Detect prior relationship
    has_prior_relationship = _detect_prior_relationship(target_group)
    relationship_instruction = ""
    if has_prior_relationship:
        relationship_instruction = (
            "\n⚠️ CRITICAL: The Target Group indicates a prior relationship or brand awareness. "
            "SKIP all brand introductions and 'what is [company]' explanations. "
            "Start the conversation from relevance, not from zero. "
            "Assume they know who you are—focus on WHY THIS MATTERS NOW for their specific context."
        )
    
    # Elevate feedback and additional notes to hard constraints
    hard_constraints = []
    if feedback.strip():
        hard_constraints.append(f"Recent call feedback (HIGH PRIORITY CONSTRAINT): {feedback.strip()}")
    if additional_reference.strip():
        hard_constraints.append(f"Additional constraint notes (MANDATORY): {additional_reference.strip()}")
    
    constraints_block = ""
    if hard_constraints:
        constraints_block = "\n\n🚨 MANDATORY CONSTRAINTS (failure to follow = script rejected):\n" + "\n".join(
            f"- {constraint}" for constraint in hard_constraints
        )
    
    rewrite_objection = ""
    feedback_lower = feedback.lower()
    if any(keyword in feedback_lower for keyword in ["busy", "time", "no time", "too busy", "calendar"]):
        rewrite_objection = (
            "\n- Objection Handling MUST directly address 'I don't have time' for this persona. "
            "Make it concise, respectful of time, and offer a frictionless next step."
        )
    
    return f"""
You are crafting a COLD OUTREACH calling script for a sales campaign.

THIS IS NOT MARKETING COPY. THIS IS NOT A WEBSITE. THIS IS A REAL PHONE CALL.
Be punchy, direct, and conversational. Eliminate copywriter fluff and corporate bullshit.

Tone of Voice:
{tone_of_voice.strip() or 'Professional yet conversational. Confident, concise, and helpful.'}

Reference Examples (analyze style/tone/structure, then mimic formatting + the "painless" approach used):
{reference_examples.strip() or 'N/A'}

Context Inputs (STRICTLY FOLLOW THESE):
- Product: {product.strip() or 'N/A'}
- Goal: {goal}
- Target Group: {target_group.strip() or 'N/A'}
- Personas: {personas.strip() or 'N/A'}
- Audience Focus: {audience_mode} ({audience_instruction})
{relationship_instruction}
{constraints_block}

Output Structure (cold call script, not a summary):
1) Hook / Permission: brief opener that respects time (e.g., "Do you have 30 seconds to see if this is relevant?")
2) Why Now (Relevance): tie the target group's industry/persona to a specific pain point
3) Discovery Questions: 2-3 open-ended questions that get them talking about current challenges
4) Value Prop (The Tease): short snippet of how we solve it, no feature-dumps
5) Close (CTA): clear ask for a 15-minute meeting
6) Objection Handling: 3 examples in "If they say X, say Y" format, tailored to likely persona objections (e.g., "We already have a solution", "Send me an email")

CRITICAL CONSTRAINTS:
- This is COLD OUTREACH, not a brochure. Be direct, punchy, human.
- STRICTLY follow the Target Group, Personas, and any Additional Reference Notes.
- If the Target Group indicates prior relationship/brand awareness, START FROM RELEVANCE, not introductions.
- Be SPECIFIC to the inputs above. Generic scripts will be rejected.
- NO copywriter fluff. NO corporate jargon unless the reference examples use it.
- Match the reference formatting conventions (pacing, phrasing, bulleting, "borrow X minutes" style).
- Lean into a "painless" next step: low commitment, minimal effort for the prospect.
- Output as clean Markdown with these exact section headers:
  ## Hook / Permission
  ## Why Now (Relevance)
  ## Discovery Questions
  ## Value Prop (The Tease)
  ## Close (CTA)
  ## Objection Handling
{rewrite_objection}
""".strip()


def _audience_mode(personas: str) -> str:
    text = personas.lower()
    upsell_keywords = ["upsell", "expand", "expansion", "existing", "customer base", "current customer"]
    if any(keyword in text for keyword in upsell_keywords):
        return "Upsell"
    return "New Customer"


def generate_guide(
    product: str,
    goal: str,
    target_group: str,
    personas: str,
    tone_of_voice: str,
    additional_reference: str,
    feedback: str,
) -> str:
    master_reference = read_master_reference()
    trimmed_master_reference, _ = _trim_reference_for_prompt(master_reference)
    reference_examples = trimmed_master_reference
    if additional_reference.strip():
        reference_examples = (
            (
                trimmed_master_reference + "\n\n---\n\nAdditional reference notes:\n" + additional_reference
            ).strip()
            if trimmed_master_reference
            else additional_reference.strip()
        )

    audience_mode = _audience_mode(personas)
    prompt = _build_prompt(
        product=product,
        goal=goal,
        target_group=target_group,
        personas=personas,
        tone_of_voice=tone_of_voice,
        reference_examples=reference_examples,
        audience_mode=audience_mode,
        feedback=feedback,
        additional_reference=additional_reference,
    )

    try:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            # UI should handle this before calling generation, but keep a safe guard here.
            raise ValueError("Missing OPENAI_API_KEY")

        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            temperature=0.7,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You create sharp, context-aware, ready-to-use COLD OUTREACH calling scripts. "
                        "You are NOT writing marketing copy or website content—this is a REAL phone conversation. "
                        "Analyze provided reference examples and mimic their style, tone, and structure, "
                        'especially the "painless" low-friction approach. '
                        "STRICTLY follow user-provided context (Target Group, Personas, Additional Notes, Feedback). "
                        "If context indicates prior relationship or brand awareness, SKIP introductions and start from relevance. "
                        "Be punchy, direct, conversational. Eliminate corporate fluff and generic messaging. "
                        "Treat user feedback and additional reference notes as MANDATORY constraints."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
        )
        return (response.choices[0].message.content or "").strip()
    except Exception as exc:  # pragma: no cover - surfaced to UI
        return f"Error generating guide: {exc}"


def main() -> None:
    st.set_page_config(page_title="Discussion Guide Generator", layout="wide")

    st.title("Discussion Guide Generator")
    st.caption("Generate a ready-to-use cold calling script, modeled on your best-performing guides.")

    with st.sidebar:
        st.header("Campaign Inputs")
        product = st.text_area("Product", height=120, placeholder="Describe the product or offer...")
        goal = st.selectbox("Goal", options=["Leads", "Meetings", "Workshops"], index=0)
        target_group = st.text_area(
            "Target Group",
            height=120,
            placeholder="Industries, company size, revenue, employees...",
        )
        personas = st.text_area(
            "Personas",
            height=120,
            placeholder="Titles, new customers vs. upsell, decision makers...",
        )
        tone_of_voice = st.text_input(
            "Tone of Voice",
            value="Professional, conversational, confident; concise and value-led.",
        )

        master_reference = read_master_reference()
        if master_reference:
            trimmed_reference, was_trimmed = _trim_reference_for_prompt(master_reference)
            st.caption(f"Loaded `master_reference.md` ({len(master_reference):,} characters).")
            if was_trimmed:
                st.info(
                    f"Note: references are long, so the last {len(trimmed_reference):,} characters will be used per request."
                )
        else:
            st.warning("`master_reference.md` not found or empty — generation will be less consistent.")

        additional_reference = st.text_area(
            "Additional Constraints & Notes (optional)",
            height=90,
            placeholder="E.g., 'Avoid corporate jargon', 'They already know our brand', 'Skip introductions'...",
            help="These will be treated as MANDATORY constraints by the AI.",
        )
        feedback = st.text_area(
            "Recent Call Feedback (optional)",
            height=100,
            placeholder="E.g., 'They keep saying they are too busy' or other objections heard live.",
            help="High-priority feedback that will adjust the script generation.",
        )
        generate_clicked = st.button("Generate Script", use_container_width=True)

    st.subheader("Cold Calling Script")
    if generate_clicked:
        if not os.getenv("OPENAI_API_KEY"):
            st.error(
                "OPENAI_API_KEY is missing. Add it to your `.env` file (or your environment) and restart the app."
            )
            return

        with st.spinner("Generating guide with OpenAI..."):
            guide_text = generate_guide(
                product=product,
                goal=goal,
                target_group=target_group,
                personas=personas,
                tone_of_voice=tone_of_voice,
                additional_reference=additional_reference,
                feedback=feedback,
            )
        st.markdown(guide_text or "")
        with st.expander("Copyable text"):
            st.text_area("Script (raw)", guide_text, height=320)
    else:
        st.info("Fill out the inputs and click Generate Script to generate a cold calling script.")


if __name__ == "__main__":
    main()


import os
from typing import Optional

import streamlit as st

from utils.facade import PortfolioFacade
from utils.insights import InsightsFacade

_DISABLED_MSG = """
<div style="background:#EEF2F7;border:1px solid #B0C4D8;border-radius:8px;padding:16px 20px;margin-bottom:16px;">
<strong>🔒 AI Insights are disabled</strong><br><br>
To enable, add your Anthropic API key to <code>.streamlit/secrets.toml</code>:<br>
<code style="background:#dde6f0;padding:2px 6px;border-radius:4px;">ANTHROPIC_API_KEY = "sk-ant-..."</code><br><br>
See <code>secrets.toml.example</code> in the project root for the template.
</div>
"""

_CARD_CSS = """
<style>
.insight-card {
    background: #FFFFFF;
    border: 1px solid #B0C4D8;
    border-radius: 10px;
    padding: 18px 22px;
    margin-bottom: 18px;
}
.insight-title { font-size: 15px; font-weight: 700; color: #1A1A2E; margin-bottom: 4px; }
.insight-desc  { font-size: 12px; color: #666; margin-bottom: 12px; }
</style>
"""


def _get_api_key() -> Optional[str]:
    try:
        key = st.secrets.get("ANTHROPIC_API_KEY")
        if key:
            return key
    except Exception:
        pass
    return os.environ.get("ANTHROPIC_API_KEY")


def _build_llm(api_key: str):
    from langchain_anthropic import ChatAnthropic
    from langchain_core.caches import InMemoryCache
    from langchain_core.globals import set_llm_cache
    set_llm_cache(InMemoryCache())
    return ChatAnthropic(model="claude-sonnet-4-6", api_key=api_key, max_tokens=600)


def render(facade: PortfolioFacade, targets: Optional[dict], **kwargs) -> None:
    st.header("AI Insights")
    st.caption("Powered by claude-sonnet-4-6 via LangChain")

    st.markdown(_CARD_CSS, unsafe_allow_html=True)

    api_key = _get_api_key()

    if not api_key:
        st.markdown(_DISABLED_MSG, unsafe_allow_html=True)

    _render_card(
        key="rebalancing_rationale",
        title="Rebalancing Rationale",
        description="Why are these BUY / SELL / HOLD actions being recommended?",
        facade=facade,
        targets=targets,
        api_key=api_key,
        requires_targets=True,
    )

    _render_card(
        key="sector_concentration",
        title="Sector Concentration",
        description="Are you over-exposed to any sector? What's missing?",
        facade=facade,
        targets=targets,
        api_key=api_key,
        requires_targets=False,
    )


def _render_card(
    key: str,
    title: str,
    description: str,
    facade: PortfolioFacade,
    targets: Optional[dict],
    api_key: Optional[str],
    requires_targets: bool,
) -> None:
    session_key = f"insight_{key}"

    st.markdown(
        f"<div class='insight-card'>"
        f"<div class='insight-title'>{title}</div>"
        f"<div class='insight-desc'>{description}</div>"
        f"</div>",
        unsafe_allow_html=True,
    )

    missing_targets = requires_targets and targets is None
    button_disabled = (not api_key) or missing_targets

    col_btn, col_clear = st.columns([2, 1])

    with col_btn:
        if missing_targets:
            st.caption("Set your targets in the Allocation Dashboard first.")
        generate = st.button(
            "Generate" if session_key not in st.session_state else "Regenerate",
            key=f"btn_{key}",
            disabled=button_disabled,
        )

    with col_clear:
        if session_key in st.session_state:
            if st.button("Clear", key=f"clear_{key}"):
                del st.session_state[session_key]
                st.rerun()

    if generate and api_key and not missing_targets:
        llm = _build_llm(api_key)
        insights_facade = InsightsFacade(facade, targets, llm)
        with st.spinner("Analyzing portfolio..."):
            response = st.write_stream(insights_facade.stream_insight(key))
        st.session_state[session_key] = response
    elif session_key in st.session_state:
        st.markdown(st.session_state[session_key])

    st.divider()

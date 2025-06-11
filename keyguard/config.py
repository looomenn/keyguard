"""Global constants."""

APP_TITLE: str = "KeyGuard"
APP_SIZE: tuple[int, int] = (1400, 740)
PHRASE: str = "щука бомба флюгер язик джміль щодня озеро грані"
# PHRASE_TEST = "doom doom doom doom"

FG_PRIMARY: str = "#FFFFFF"
FG_SECONDARY: str = "#888888"
BORDER_PRIMARY: str = "#333333"
FONT_FAMILY: str = "IBM Plex Mono"
MAX_TRAINING_RUNS: int = 15
MAX_AUTH_ATTEMPTS: int = 3

FONT_SIZE: dict[str, int] = {
    "xs": 12,  # extra-small (legal fine print)
    "sm": 14,  # small (fine prin1t, secondary text)
    "base": 16,  # base/body text
    "lg": 18,  # lead text, small labels
    "xl": 20,  # subheadings
    "2xl": 24,  # section headings
    "3xl": 30,  # page headings
    "4xl": 36,  # large display
    "5xl": 48,  # hero/title
}

GLOBAL_STYLESHEET = f"""
QWidget, QLineEdit, QPushButton, QLabel, QComboBox, QTextEdit {{
    font-family: {FONT_FAMILY};
}}

QLabel {{
    background-color: transparent;
}}

.header-title{{
    font-size: 24px;
    font-weight: 700;
    color: {FG_PRIMARY};
}}

.header-frame{{
    border: 1px solid {BORDER_PRIMARY};
    border-bottom: 0px;
}}


#app {{
    background-color: #000000;
}}

.copyright-label{{
    color: {FG_SECONDARY};
    font-weight: 400;
    font-size: 14px;
}}

.blank_state-emoji{{
    font-size: 32px;
    color: {FG_SECONDARY};
    padding-bottom: 24px;
}}

.blank_state-heading{{
    font-size: {FONT_SIZE["base"]}pt;
    font-weight: 600;
    color: {FG_PRIMARY};
}}

.blank_state-description{{
    font-size: {FONT_SIZE["sm"]}pt;
    font-weight: 400;
    color: {FG_SECONDARY};
}}

.blank_state-action{{
    margin-top: 32px;
}}

.profile-panel_title{{
    font-size: {FONT_SIZE["sm"]}pt;
    font-weight: 600;
    color: {FG_PRIMARY};
}}

.label-value_label--medium{{
    font-size: {FONT_SIZE["xs"]}pt;
    font-weight: 400;
    color: {FG_SECONDARY};
}}

.label-value_value--medium{{
    font-size: {FONT_SIZE["xs"]}pt;
    font-weight: 500;
    color: {FG_PRIMARY};
}}

.label-value_label--large{{
    font-size: {FONT_SIZE["sm"]}pt;
    font-weight: 400;
    color: {FG_SECONDARY};
}}

.label-value_value--large{{
    font-size: {FONT_SIZE["base"]}pt;
    font-weight: 500;
    color: {FG_PRIMARY};
}}


.profile-panel{{
    border: 1px solid {BORDER_PRIMARY};
    border-right: 0px;
    border-bottom: 0px;
    border-top: 0px;
}}

.phrase-char{{
    color: #666;
    font-size: 24px;
    padding: 0 2px;
}}

correct{{
    color: #4CAF50;
}}
.incorrect{{
    color: #f44336;
}}
"""

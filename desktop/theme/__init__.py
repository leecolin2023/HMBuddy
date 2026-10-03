"""Phase 2.2 Desktop Theme（规格第 31 节：Calm Enterprise Agent）。

只包含 Presentation 常量与 QSS；Controller / Runtime 不得 import 本包。
"""
from __future__ import annotations

# Layout tokens（规格第 9 节）
SIDEBAR_DEFAULT_WIDTH = 248
SIDEBAR_MIN_WIDTH = 220
SIDEBAR_MAX_WIDTH = 320
PREVIEW_DEFAULT_WIDTH = 400
PREVIEW_MIN_WIDTH = 320

SPACING = 8  # 8px rhythm
SPACING_SM = 4
SPACING_LG = 16

FONT_FAMILY = '"Microsoft YaHei UI", "Segoe UI", system-ui'

COLORS = {
    "bg": "#f7f7f8",
    "surface": "#ffffff",
    "sidebar_bg": "#ececee",
    "border": "#dcdce0",
    "text": "#26262b",
    "muted": "#7a7a82",
    "accent": "#3564d3",
    "accent_soft": "#e6edfb",
    "ok": "#2e8b57",
    "warn": "#c47f17",
    "error": "#b3403a",
    "user_bubble": "#e6edfb",
    "assistant_bubble": "#ffffff",
}


def build_qss() -> str:
    c = COLORS
    return f"""
QWidget {{
    background: {c['bg']};
    color: {c['text']};
    font-family: {FONT_FAMILY};
    font-size: 13px;
}}
QMainWindow, #Root {{ background: {c['bg']}; }}

/* ---- Sidebar ---- */
#Sidebar {{
    background: {c['sidebar_bg']};
    border-right: 1px solid {c['border']};
}}
#BrandLabel {{
    font-size: 17px; font-weight: 600; color: {c['text']}; background: transparent;
}}
#SidebarButton {{
    background: transparent; border: none; border-radius: 6px;
    padding: 8px 10px; text-align: left; color: {c['text']};
}}
#SidebarButton:hover {{ background: {c['accent_soft']}; }}
#SidebarSectionLabel {{
    color: {c['muted']}; font-size: 11px; background: transparent;
    padding: 6px 10px 2px 10px;
}}
#StatusDotLabel {{ color: {c['muted']}; background: transparent; }}

/* ---- Conversation ---- */
#ConversationHeader {{
    background: {c['surface']}; border-bottom: 1px solid {c['border']};
}}
#ConversationTitle {{ font-size: 15px; font-weight: 600; background: transparent; }}
#ConversationSubtitle {{ color: {c['muted']}; font-size: 11px; background: transparent; }}
#MessageStream, #ZeroState {{
    background: {c['bg']}; border: none;
}}
#UserBubble {{
    background: {c['user_bubble']}; border-radius: 8px; padding: 10px 12px;
}}
#AssistantBubble {{
    background: {c['assistant_bubble']}; border: 1px solid {c['border']};
    border-radius: 8px; padding: 10px 12px;
}}
#StatusNotice {{
    color: {c['muted']}; background: transparent; padding: 2px 4px;
}}
#ErrorNotice {{ color: {c['error']}; background: transparent; padding: 2px 4px; }}

/* ---- File Card ---- */
#FileCard {{
    background: {c['surface']}; border: 1px solid {c['border']};
    border-radius: 8px; padding: 8px 10px;
}}
#FileCard:hover {{ border-color: {c['accent']}; }}
#FileCardName {{ font-weight: 600; background: transparent; border: none; }}
#FileCardMeta {{ color: {c['muted']}; font-size: 11px; background: transparent; border: none; }}

/* ---- Composer ---- */
#Composer {{
    background: {c['surface']}; border-top: 1px solid {c['border']};
}}
#ComposerInput {{
    background: {c['surface']}; border: 1px solid {c['border']};
    border-radius: 8px; padding: 8px 10px;
}}
#ComposerInput:focus {{ border-color: {c['accent']}; }}
#SendButton {{
    background: {c['accent']}; color: #ffffff; border: none;
    border-radius: 8px; padding: 8px 16px; font-weight: 600;
}}
#SendButton:disabled {{ background: {c['border']}; }}

/* ---- Preview ---- */
#PreviewPane {{
    background: {c['surface']}; border-left: 1px solid {c['border']};
}}
#PreviewHeader {{
    background: {c['surface']}; border-bottom: 1px solid {c['border']};
}}
#PreviewContent {{ background: {c['surface']}; border: none; }}

/* ---- Cards / Pages ---- */
#PageContainer {{ background: {c['bg']}; }}
#PageHeader {{ background: transparent; }}
#Card {{
    background: {c['surface']}; border: 1px solid {c['border']};
    border-radius: 8px; padding: 10px 12px;
}}
#Card:hover {{ border-color: {c['accent']}; }}
#CardTitle {{ font-weight: 600; background: transparent; border: none; }}
#CardMeta {{ color: {c['muted']}; font-size: 11px; background: transparent; border: none; }}
#SectionTitle {{ font-size: 14px; font-weight: 600; background: transparent; }}
#SettingsCategory {{
    background: transparent; border: none; border-radius: 6px;
    padding: 8px 10px; text-align: left;
}}
#SettingsCategory:hover {{ background: {c['accent_soft']}; }}
#Badge {{
    border-radius: 8px; padding: 1px 8px; font-size: 11px;
    background: {c['accent_soft']}; color: {c['accent']}; border: none;
}}
#BadgeError {{
    border-radius: 8px; padding: 1px 8px; font-size: 11px;
    background: #fbe9e8; color: {c['error']}; border: none;
}}
QLineEdit, QComboBox, QSpinBox {{
    background: {c['surface']}; border: 1px solid {c['border']};
    border-radius: 6px; padding: 6px 8px;
}}
QLineEdit:focus {{ border-color: {c['accent']}; }}
QPushButton {{
    background: {c['surface']}; border: 1px solid {c['border']};
    border-radius: 6px; padding: 6px 12px;
}}
QPushButton:hover {{ border-color: {c['accent']}; }}
QScrollArea {{ border: none; background: transparent; }}
"""

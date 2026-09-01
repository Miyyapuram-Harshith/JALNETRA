"""
JALNETRA Internationalization
Template-based multilingual alert messages.
"""

from typing import Dict
from enum import Enum


class Language(str, Enum):
    EN = "en"
    HI = "hi"
    UR = "ur"  # Regional language option


# ---------------------------------------------------------------------------
# Alert Message Templates
# ---------------------------------------------------------------------------
# Placeholders: {risk_level}, {zone}, {region}, {impact_minutes},
#   {action}, {shelter}, {route}, {departure_window}, {confidence}
# ---------------------------------------------------------------------------

ALERT_TEMPLATES: Dict[str, Dict[str, str]] = {
    "AWARENESS": {
        "en": (
            "ℹ️ JALNETRA AWARENESS\n\n"
            "📍 {zone} — {region}\n\n"
            "Current conditions are being monitored.\n"
            "Risk Level: {risk_level}\n\n"
            "No immediate action required.\n"
            "Stay informed."
        ),
        "hi": (
            "ℹ️ जलनेत्र जागरूकता\n\n"
            "📍 {zone} — {region}\n\n"
            "वर्तमान स्थितियों की निगरानी की जा रही है।\n"
            "जोखिम स्तर: {risk_level}\n\n"
            "तत्काल कार्रवाई की आवश्यकता नहीं।\n"
            "जानकारी बनाए रखें।"
        ),
        "ur": (
            "ℹ️ جلنیترا آگاہی\n\n"
            "📍 {zone} — {region}\n\n"
            "موجودہ حالات کی نگرانی کی جا رہی ہے۔\n"
            "خطرے کی سطح: {risk_level}\n\n"
            "فوری کارروائی ضروری نہیں۔"
        ),
    },
    "WATCH": {
        "en": (
            "⚠️ JALNETRA FLOOD WATCH\n\n"
            "📍 {zone} — {region}\n\n"
            "Risk Level: {risk_level}\n"
            "Estimated impact: ~{impact_minutes} minutes\n\n"
            "⚠️ Be prepared to act.\n"
            "Monitor updates closely.\n\n"
            "This is a modeled estimate."
        ),
        "hi": (
            "⚠️ जलनेत्र बाढ़ निगरानी\n\n"
            "📍 {zone} — {region}\n\n"
            "जोखिम स्तर: {risk_level}\n"
            "अनुमानित प्रभाव: ~{impact_minutes} मिनट\n\n"
            "⚠️ कार्रवाई के लिए तैयार रहें।\n\n"
            "यह एक मॉडल अनुमान है।"
        ),
        "ur": (
            "⚠️ جلنیترا سیلاب واچ\n\n"
            "📍 {zone} — {region}\n\n"
            "خطرے کی سطح: {risk_level}\n"
            "متوقع اثر: ~{impact_minutes} منٹ\n\n"
            "⚠️ کارروائی کے لیے تیار رہیں۔"
        ),
    },
    "WARNING": {
        "en": (
            "🚨 JALNETRA FLASH FLOOD WARNING\n\n"
            "📍 {zone} — {region}\n\n"
            "Risk: {risk_level}\n"
            "Estimated impact: ~{impact_minutes} minutes\n\n"
            "⚠️ Recommended action:\n"
            "{action}\n\n"
            "🏠 Shelter:\n{shelter}\n\n"
            "🛣️ Recommended route:\n{route}\n\n"
            "⏱️ Modeled departure window:\n{departure_window} minutes\n\n"
            "Conditions may change rapidly.\n"
            "This is a system recommendation, not an official evacuation order."
        ),
        "hi": (
            "🚨 जलनेत्र अचानक बाढ़ चेतावनी\n\n"
            "📍 {zone} — {region}\n\n"
            "जोखिम: {risk_level}\n"
            "अनुमानित प्रभाव: ~{impact_minutes} मिनट\n\n"
            "⚠️ अनुशंसित कार्रवाई:\n"
            "{action}\n\n"
            "🏠 आश्रय:\n{shelter}\n\n"
            "🛣️ अनुशंसित मार्ग:\n{route}\n\n"
            "⏱️ प्रस्थान समय सीमा:\n{departure_window} मिनट\n\n"
            "स्थितियां तेजी से बदल सकती हैं।\n"
            "यह एक प्रणाली सिफारिश है, आधिकारिक निकासी आदेश नहीं।"
        ),
        "ur": (
            "🚨 جلنیترا فلیش فلڈ وارننگ\n\n"
            "📍 {zone} — {region}\n\n"
            "خطرہ: {risk_level}\n"
            "متوقع اثر: ~{impact_minutes} منٹ\n\n"
            "⚠️ تجویز کردہ کارروائی:\n"
            "{action}\n\n"
            "🏠 پناہ گاہ:\n{shelter}\n\n"
            "🛣️ تجویز کردہ راستہ:\n{route}\n\n"
            "⏱️ روانگی کی مدت:\n{departure_window} منٹ\n\n"
            "حالات تیزی سے بدل سکتے ہیں۔"
        ),
    },
    "EVACUATION_RECOMMENDED": {
        "en": (
            "🔴 JALNETRA — EVACUATION RECOMMENDED\n\n"
            "📍 {zone} — {region}\n\n"
            "Risk: {risk_level}\n"
            "Estimated impact: ~{impact_minutes} minutes\n\n"
            "🚨 LEAVE NOW\n\n"
            "🏠 Shelter:\n{shelter}\n\n"
            "🛣️ Route:\n{route}\n\n"
            "⏱️ Modeled departure window:\n{departure_window} minutes\n\n"
            "This is a SYSTEM RECOMMENDATION.\n"
            "Follow local authority instructions."
        ),
        "hi": (
            "🔴 जलनेत्र — निकासी अनुशंसित\n\n"
            "📍 {zone} — {region}\n\n"
            "जोखिम: {risk_level}\n\n"
            "🚨 अभी निकलें\n\n"
            "🏠 आश्रय: {shelter}\n"
            "🛣️ मार्ग: {route}\n"
            "⏱️ समय सीमा: {departure_window} मिनट\n\n"
            "यह प्रणाली सिफारिश है।\n"
            "स्थानीय अधिकारियों के निर्देशों का पालन करें।"
        ),
        "ur": (
            "🔴 جلنیترا — انخلا تجویز\n\n"
            "📍 {zone} — {region}\n\n"
            "🚨 ابھی نکلیں\n\n"
            "🏠 پناہ گاہ: {shelter}\n"
            "🛣️ راستہ: {route}\n"
            "⏱️ وقت: {departure_window} منٹ"
        ),
    },
    "CRITICAL": {
        "en": (
            "🆘 JALNETRA — CRITICAL EMERGENCY\n\n"
            "📍 {zone} — {region}\n\n"
            "IMMEDIATE DANGER\n\n"
            "🚨 SEEK HIGHER GROUND IMMEDIATELY\n\n"
            "If unable to evacuate:\n"
            "• Move to highest floor\n"
            "• Signal for help\n"
            "• Call emergency services\n\n"
            "This is a system recommendation."
        ),
        "hi": (
            "🆘 जलनेत्र — गंभीर आपातकाल\n\n"
            "📍 {zone} — {region}\n\n"
            "तत्काल खतरा\n\n"
            "🚨 तुरंत ऊंचे स्थान पर जाएं\n\n"
            "यह प्रणाली सिफारिश है।"
        ),
        "ur": (
            "🆘 جلنیترا — شدید ایمرجنسی\n\n"
            "📍 {zone} — {region}\n\n"
            "🚨 فوری طور پر اونچی جگہ پر جائیں"
        ),
    },
    "ROUTE_UPDATED": {
        "en": (
            "🛣️ JALNETRA — ROUTE UPDATE\n\n"
            "📍 {zone} — {region}\n\n"
            "Your recommended route has changed.\n\n"
            "New route: {route}\n"
            "New shelter: {shelter}\n\n"
            "Previous route may no longer be safe.\n"
            "This is a modeled estimate."
        ),
        "hi": (
            "🛣️ जलनेत्र — मार्ग अपडेट\n\n"
            "📍 {zone} — {region}\n\n"
            "नया मार्ग: {route}\n"
            "नया आश्रय: {shelter}\n\n"
            "यह एक मॉडल अनुमान है।"
        ),
        "ur": (
            "🛣️ جلنیترا — راستہ اپ ڈیٹ\n\n"
            "نیا راستہ: {route}\n"
            "نئی پناہ گاہ: {shelter}"
        ),
    },
    "ALERT_RESOLVED": {
        "en": (
            "✅ JALNETRA — ALERT RESOLVED\n\n"
            "📍 {zone} — {region}\n\n"
            "Conditions have improved.\n"
            "Risk Level: {risk_level}\n\n"
            "Continue to monitor conditions.\n"
            "Stay safe."
        ),
        "hi": (
            "✅ जलनेत्र — चेतावनी समाप्त\n\n"
            "📍 {zone} — {region}\n\n"
            "स्थितियां सुधर गई हैं।\n"
            "सुरक्षित रहें।"
        ),
        "ur": (
            "✅ جلنیترا — الرٹ ختم\n\n"
            "حالات بہتر ہو گئے ہیں۔"
        ),
    },
}


def render_alert_message(
    alert_type: str,
    language: str = "en",
    **kwargs,
) -> str:
    """
    Render an alert message from templates.

    Args:
        alert_type: One of AWARENESS, WATCH, WARNING, EVACUATION_RECOMMENDED, etc.
        language: Language code (en, hi, ur)
        **kwargs: Template variables (zone, region, risk_level, etc.)

    Returns:
        Rendered message string.
    """
    templates = ALERT_TEMPLATES.get(alert_type, ALERT_TEMPLATES.get("WARNING", {}))
    template = templates.get(language, templates.get("en", "Alert: {risk_level}"))

    # Fill in available placeholders, leave missing ones as "N/A"
    safe_kwargs = {k: (v if v is not None else "N/A") for k, v in kwargs.items()}
    try:
        return template.format_map(SafeDict(safe_kwargs))
    except Exception:
        return template


class SafeDict(dict):
    """Dict that returns placeholder name for missing keys instead of raising."""
    def __missing__(self, key):
        return f"{{{key}}}"

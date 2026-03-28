"""Startseite – Professionelles Landing"""
import os
import streamlit as st
from config import TITELBILD_FILE
from auth import is_admin


def render_home():
    # === HERO SECTION ===
    if os.path.exists(TITELBILD_FILE):
        st.image(TITELBILD_FILE, use_container_width=True)

    st.markdown('<div class="hero-badge">Dual-AI-Verification Technology</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-title">Sicherheit, die sich auszahlt.</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="hero-subtitle">'
        'SafeSite Drohne liefert KI-gestützte Sicherheitsinspektionen für Schweizer Baustellen – '
        'geprüft nach BauAV und SUVA-Richtlinien. Entwickelt von Polieren für den täglichen Einsatz.'
        '</div>',
        unsafe_allow_html=True,
    )

    # CTA Buttons
    col_a, col_b, col_c = st.columns([1, 1, 2])
    with col_a:
        if st.button("🔍 Inspektion starten", type="primary", use_container_width=True):
            st.session_state.current_page = "safesite"
            st.rerun()
    with col_b:
        if st.button("💎 Preise ansehen", use_container_width=True):
            st.session_state.current_page = "preise"
            st.rerun()

    st.markdown("")

    # === STATS BAR ===
    st.markdown(
        '<div class="trust-bar">'
        '<div class="stat-box"><div class="stat-number">119</div><div class="stat-label">BauAV-Artikel integriert</div></div>'
        '<div class="stat-box"><div class="stat-number">2</div><div class="stat-label">KI-Modelle (Dual-AI)</div></div>'
        '<div class="stat-box"><div class="stat-number">12</div><div class="stat-label">Prüfkategorien</div></div>'
        '<div class="stat-box"><div class="stat-number">100%</div><div class="stat-label">Schweizer Normen</div></div>'
        '</div>',
        unsafe_allow_html=True,
    )

    # === SO FUNKTIONIERT ES ===
    st.markdown("")
    st.markdown("## So funktioniert SafeSite Drohne")
    st.markdown("")

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(
            '<div class="feature-card">'
            '<div class="feature-icon">📸</div>'
            '<div class="feature-title">1. Fotos hochladen</div>'
            '<div class="feature-desc">Drohnenbilder oder Handyfotos Ihrer Baustelle hochladen</div>'
            '</div>',
            unsafe_allow_html=True,
        )
    with c2:
        st.markdown(
            '<div class="feature-card">'
            '<div class="feature-icon">🔬</div>'
            '<div class="feature-title">2. Dual-AI-Analyse</div>'
            '<div class="feature-desc">Gemini + Claude Opus prüfen nach BauAV & SUVA</div>'
            '</div>',
            unsafe_allow_html=True,
        )
    with c3:
        st.markdown(
            '<div class="feature-card">'
            '<div class="feature-icon">📄</div>'
            '<div class="feature-title">3. Bericht erhalten</div>'
            '<div class="feature-desc">Professioneller PDF/Word-Bericht mit allen Mängeln</div>'
            '</div>',
            unsafe_allow_html=True,
        )

    # === FEATURE GRID ===
    st.markdown("")
    st.markdown("## Alle Funktionen")
    st.markdown("")

    features = [
        ("safesite", "🔍", "SafeSite-Check", "KI-gestützte Sicherheitsinspektion mit Dual-AI-Verification"),
        ("suva", "📋", "SUVA Regeln", "Die 8 lebenswichtigen Regeln auf einen Blick"),
        ("bauav", "⚖️", "BauAV", "Alle 119 Artikel der Bauarbeitenverordnung durchsuchbar"),
        ("notfall", "🚨", "Notfallmanagement", "Notfallnummern und W-Fragen-Hilfe für den Ernstfall"),
        ("gefahrstoff", "🧪", "Gefahrstoffkataster", "Digitale Verwaltung von Sicherheitsdatenblättern"),
        ("wetter", "🌤️", "Wetter-Warnungen", "MeteoSchweiz-Anbindung für Sturm- und Hitzewarnungen"),
    ]

    for row_start in range(0, len(features), 3):
        cols = st.columns(3)
        for i, col in enumerate(cols):
            idx = row_start + i
            if idx < len(features):
                page_key, icon, title, desc = features[idx]
                with col:
                    st.markdown(
                        f'<div class="feature-card">'
                        f'<div class="feature-icon">{icon}</div>'
                        f'<div class="feature-title">{title}</div>'
                        f'<div class="feature-desc">{desc}</div>'
                        f'</div>',
                        unsafe_allow_html=True,
                    )
                    if st.button(f"{title} öffnen", key=f"nav_{page_key}", use_container_width=True):
                        st.session_state.current_page = page_key
                        st.rerun()
        st.markdown("")

    # === TRUST SECTION ===
    st.markdown("")
    st.markdown(
        '<div class="trust-bar">'
        '<div class="trust-item"><div class="trust-icon">🇨🇭</div>Schweizer Normen</div>'
        '<div class="trust-item"><div class="trust-icon">🔬</div>Dual-AI-Verification</div>'
        '<div class="trust-item"><div class="trust-icon">👷</div>Von Polieren entwickelt</div>'
        '<div class="trust-item"><div class="trust-icon">🔒</div>DSGVO-konform</div>'
        '</div>',
        unsafe_allow_html=True,
    )

    # === ADMIN ===
    if is_admin():
        st.markdown("")
        st.divider()
        c = st.columns([1, 1, 1])
        with c[1]:
            if st.button("👥 Kundenverwaltung", use_container_width=True):
                st.session_state.current_page = "kunden"
                st.rerun()

    # === FOOTER ===
    st.markdown("")
    st.markdown("---")
    st.markdown(
        '<div style="text-align:center; color:#999; font-size:12px; padding:10px 0;">'
        'SafeSite Drohne – Technik unterstützt, Erfahrung entscheidet. | '
        '<a href="https://safesitedrohne.ch" style="color:#FF6600;">safesitedrohne.ch</a> | '
        'info@safesite-drohne.ch'
        '</div>',
        unsafe_allow_html=True,
    )

"""Mein Profil – Benutzerdaten anzeigen und bearbeiten"""
import streamlit as st
from db import (
    find_customer, get_users, save_users, save_customers, get_customers,
    change_password, create_login, delete_login,
)


def render_profil():
    st.header("👤 Mein Profil")
    st.markdown("---")

    username = st.session_state.username
    kid, kdata = find_customer(username)

    if not kdata and username != "admin":
        st.warning("Keine Kundendaten gefunden. Bitte kontaktieren Sie den Administrator.")
        return

    tab_info, tab_edit, tab_pwd = st.tabs(["📋 Meine Daten", "✏️ Bearbeiten", "🔐 Passwort"])

    with tab_info:
        _render_info(kdata)

    with tab_edit:
        _render_edit(username, kid, kdata)

    with tab_pwd:
        _render_password(username, kdata)


def _render_info(kdata):
    if not kdata:
        st.info("System-Administrator Account.")
        return

    with st.container(border=True):
        c1, c2 = st.columns(2)
        with c1:
            st.write(f"**Name:** {kdata.get('name', '-')}")
            st.write(f"**Firma:** {kdata.get('firma', '-')}")
            st.write(f"**Email:** {kdata.get('email', '-')}")
            st.write(f"**Benutzername:** {kdata.get('username', '-')}")
        with c2:
            st.write(f"**Telefon:** {kdata.get('telefon', '-')}")
            st.write(f"**Adresse:** {kdata.get('adresse', '-')}")
        st.divider()
        st.metric("🪙 SafeSite Credits", int(kdata.get("credits", 0)))
        st.caption("Credits können nur vom Administrator aufgeladen werden.")


def _render_edit(username, kid, kdata):
    if username == "admin" and not kdata:
        st.warning("Admin-Daten können hier nicht bearbeitet werden.")
        return

    if not kdata:
        return

    with st.form("profil_edit"):
        name = st.text_input("Name *", value=kdata.get("name", ""))
        firma = st.text_input("Firma", value=kdata.get("firma", ""))
        email = st.text_input("Email *", value=kdata.get("email", ""))
        uname = st.text_input("Benutzername", value=kdata.get("username", ""))
        tel = st.text_input("Telefon", value=kdata.get("telefon", ""))
        adresse = st.text_area("Adresse", value=kdata.get("adresse", ""))

        st.info("Hinweis: Änderungen an Email/Benutzername ändern auch Ihren Login.")

        if st.form_submit_button("✅ Speichern", type="primary"):
            if not name or not email:
                st.error("Name und Email sind Pflichtfelder!")
                return

            old_email = kdata.get("email", "")
            old_uname = kdata.get("username", "")
            users = get_users()

            # Passwort ermitteln (für Login-Migration)
            pwd_hash = None
            for key in [old_email, old_uname]:
                if key and key in users:
                    pwd_hash = users[key]
                    break

            # Alte Logins entfernen, neue erstellen
            if old_email and old_email != email and old_email in users:
                del users[old_email]
            if old_uname and old_uname != uname and old_uname in users:
                del users[old_uname]

            if pwd_hash:
                if email:
                    users[email] = pwd_hash
                if uname:
                    users[uname] = pwd_hash

            save_users(users)

            # Session-Username aktualisieren
            if st.session_state.username == old_email and email != old_email:
                st.session_state.username = email
            elif st.session_state.username == old_uname and uname != old_uname:
                st.session_state.username = uname

            # Kundendaten aktualisieren
            customers = get_customers()
            if kid in customers:
                customers[kid].update({
                    "name": name, "firma": firma, "email": email,
                    "username": uname, "telefon": tel, "adresse": adresse,
                })
                save_customers(customers)

            st.success("✅ Profil aktualisiert!")
            st.rerun()


def _render_password(username, kdata):
    with st.form("pwd_change"):
        st.subheader("Passwort ändern")
        p1 = st.text_input("Neues Passwort", type="password")
        p2 = st.text_input("Wiederholen", type="password")

        if st.form_submit_button("🔑 Speichern", type="primary"):
            if not p1 or not p2:
                st.error("Beide Felder ausfüllen!")
            elif p1 != p2:
                st.error("Passwörter stimmen nicht überein!")
            else:
                # Passwort für alle Login-Keys ändern
                keys = [username]
                if kdata:
                    if kdata.get("email"):
                        keys.append(kdata["email"])
                    if kdata.get("username"):
                        keys.append(kdata["username"])
                if username == "admin":
                    keys.append("admin")

                for key in set(keys):
                    change_password(key, p1)

                st.success("✅ Passwort geändert!")

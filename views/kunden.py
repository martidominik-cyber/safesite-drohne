"""Kundenverwaltung – Admin-Bereich"""
import streamlit as st
from auth import is_admin
from db import (
    get_customers, save_customers, get_users, save_users,
    create_customer, delete_customer, update_customer, update_credits,
    create_login, change_password,
)


def render_kunden():
    if not is_admin():
        st.error("⛔ Nur für Administratoren.")
        return

    st.header("👥 Kundenverwaltung")
    st.markdown("---")

    tab1, tab2 = st.tabs(["📋 Kundenliste", "➕ Neuen Kunden"])

    with tab1:
        _render_liste()

    with tab2:
        _render_neuer_kunde()


def _render_liste():
    customers = get_customers()
    users = get_users()

    if not customers:
        st.info("Noch keine Kunden vorhanden.")
        return

    for kid, data in customers.items():
        email = data.get("email", "")
        uname = data.get("username", "")
        has_login = (email and email in users) or (uname and uname in users)

        with st.container(border=True):
            c1, c2, c3 = st.columns([3, 1, 1])

            with c1:
                st.markdown(f"### {data.get('name', '?')}")
                st.write(f"**Firma:** {data.get('firma', '-')}")
                st.write(f"**Email:** {email}")
                if uname:
                    st.write(f"**Benutzername:** {uname}")
                st.write(f"**Telefon:** {data.get('telefon', '-')}")
                credits = int(data.get("credits", 0))
                st.metric("🪙 Credits", credits)
                if has_login:
                    st.success("✅ Login aktiv")
                else:
                    st.warning("⚠️ Kein Login")

            with c2:
                if has_login:
                    if st.button("🔑 Passwort", key=f"pw_{kid}"):
                        st.session_state[f"pw_{kid}"] = True
                        st.rerun()
                else:
                    if st.button("🔑 Login erstellen", key=f"cl_{kid}"):
                        st.session_state[f"cl_{kid}"] = True
                        st.rerun()

                if st.button("💰 Credits", key=f"cr_{kid}"):
                    st.session_state[f"cr_{kid}"] = True
                    st.rerun()

            with c3:
                if st.button("✏️ Bearbeiten", key=f"ed_{kid}"):
                    st.session_state[f"ed_{kid}"] = True
                    st.rerun()
                if st.button("🗑️ Löschen", key=f"dl_{kid}"):
                    delete_customer(kid)
                    st.success("Gelöscht!")
                    st.rerun()

            # === Inline-Formulare ===

            # Bearbeiten
            if st.session_state.get(f"ed_{kid}"):
                st.divider()
                with st.form(f"form_ed_{kid}"):
                    st.markdown("**✏️ Kunde bearbeiten**")
                    ed_name = st.text_input("Name *", value=data.get("name", ""), key=f"edn_{kid}")
                    ed_firma = st.text_input("Firma", value=data.get("firma", ""), key=f"edf_{kid}")
                    ed_email = st.text_input("Email", value=email, key=f"ede_{kid}")
                    ed_uname = st.text_input("Benutzername", value=uname, key=f"edu_{kid}")
                    ed_tel = st.text_input("Telefon", value=data.get("telefon", ""), key=f"edt_{kid}")
                    ed_addr = st.text_area("Adresse", value=data.get("adresse", ""), key=f"eda_{kid}")

                    ca, cb = st.columns(2)
                    with ca:
                        if st.form_submit_button("✅ Speichern", use_container_width=True):
                            if not ed_name:
                                st.error("Name ist Pflicht!")
                            else:
                                # Login-Keys aktualisieren
                                _update_login_keys(users, email, uname, ed_email, ed_uname)

                                update_customer(kid,
                                    name=ed_name, firma=ed_firma, email=ed_email,
                                    username=ed_uname, telefon=ed_tel, adresse=ed_addr)
                                st.session_state[f"ed_{kid}"] = False
                                st.success("Aktualisiert!")
                                st.rerun()
                    with cb:
                        if st.form_submit_button("❌ Abbrechen", use_container_width=True):
                            st.session_state[f"ed_{kid}"] = False
                            st.rerun()

            # Credits
            if st.session_state.get(f"cr_{kid}"):
                st.divider()
                with st.form(f"form_cr_{kid}"):
                    st.markdown("**🪙 Credits verwalten**")
                    new_cr = st.number_input("Credits", min_value=0,
                        value=int(data.get("credits", 0)), step=1, key=f"crv_{kid}")
                    ca, cb = st.columns(2)
                    with ca:
                        if st.form_submit_button("✅ Speichern", use_container_width=True):
                            update_credits(kid, new_cr)
                            st.session_state[f"cr_{kid}"] = False
                            st.success(f"Credits: {new_cr}")
                            st.rerun()
                    with cb:
                        if st.form_submit_button("❌ Abbrechen", use_container_width=True):
                            st.session_state[f"cr_{kid}"] = False
                            st.rerun()

            # Passwort ändern
            if st.session_state.get(f"pw_{kid}"):
                st.divider()
                with st.form(f"form_pw_{kid}"):
                    st.markdown("**🔑 Passwort ändern**")
                    np1 = st.text_input("Neues Passwort", type="password", key=f"np1_{kid}")
                    np2 = st.text_input("Bestätigen", type="password", key=f"np2_{kid}")
                    ca, cb = st.columns(2)
                    with ca:
                        if st.form_submit_button("✅ Ändern", use_container_width=True):
                            if np1 and np1 == np2:
                                if email:
                                    change_password(email, np1)
                                if uname:
                                    change_password(uname, np1)
                                st.session_state[f"pw_{kid}"] = False
                                st.success("Passwort geändert!")
                                st.rerun()
                            elif np1 != np2:
                                st.error("Stimmen nicht überein!")
                            else:
                                st.error("Passwort darf nicht leer sein!")
                    with cb:
                        if st.form_submit_button("❌ Abbrechen", use_container_width=True):
                            st.session_state[f"pw_{kid}"] = False
                            st.rerun()

            # Login erstellen
            if st.session_state.get(f"cl_{kid}"):
                st.divider()
                with st.form(f"form_cl_{kid}"):
                    st.markdown("**🔑 Login erstellen**")
                    st.caption(f"Für: {data.get('name', '?')}")
                    np1 = st.text_input("Passwort", type="password", key=f"clp1_{kid}")
                    np2 = st.text_input("Bestätigen", type="password", key=f"clp2_{kid}")
                    ca, cb = st.columns(2)
                    with ca:
                        if st.form_submit_button("✅ Erstellen", use_container_width=True):
                            if np1 and np1 == np2:
                                if email:
                                    create_login(email, np1)
                                if uname:
                                    create_login(uname, np1)
                                st.session_state[f"cl_{kid}"] = False
                                st.success("Login erstellt!")
                                st.rerun()
                            elif np1 != np2:
                                st.error("Stimmen nicht überein!")
                            else:
                                st.error("Passwort eingeben!")
                    with cb:
                        if st.form_submit_button("❌ Abbrechen", use_container_width=True):
                            st.session_state[f"cl_{kid}"] = False
                            st.rerun()

            st.divider()


def _render_neuer_kunde():
    st.subheader("Neuen Kunden hinzufügen")

    with st.form("neuer_kunde", clear_on_submit=True):
        name = st.text_input("Name *", placeholder="Max Mustermann")
        firma = st.text_input("Firma", placeholder="Mustermann AG")
        email = st.text_input("Email *", placeholder="max@mustermann.ch")
        uname = st.text_input("Benutzername (optional)", placeholder="max.mustermann")
        tel = st.text_input("Telefon", placeholder="+41 79 123 45 67")
        adresse = st.text_area("Adresse")

        st.divider()
        credits = st.number_input("Anfängliche Credits", min_value=0, value=0, step=1)
        st.caption("1 Credit = 1 Bericht")

        st.divider()
        st.markdown("**🔐 Login (Pflicht):**")
        pwd = st.text_input("Passwort *", type="password", key="nk_pwd")
        pwd2 = st.text_input("Bestätigen *", type="password", key="nk_pwd2")

        if st.form_submit_button("✅ Kunde hinzufügen", type="primary", use_container_width=True):
            if not name or not email:
                st.error("Name und Email sind Pflicht!")
            elif not pwd:
                st.error("Passwort ist Pflicht!")
            elif pwd != pwd2:
                st.error("Passwörter stimmen nicht überein!")
            else:
                users = get_users()
                if email in users:
                    st.error(f"Login '{email}' existiert bereits!")
                elif uname and uname in users:
                    st.error(f"Login '{uname}' existiert bereits!")
                else:
                    create_customer(name, firma, email, uname, tel, adresse, credits)
                    create_login(email, pwd)
                    if uname:
                        create_login(uname, pwd)

                    info = [f"Email: {email}"]
                    if uname:
                        info.append(f"Username: {uname}")
                    st.success(f"✅ '{name}' hinzugefügt mit {credits} Credits! Login: {' | '.join(info)}")
                    st.rerun()


def _update_login_keys(users, old_email, old_uname, new_email, new_uname):
    """Aktualisiert Login-Keys wenn Email/Username sich ändern."""
    pwd_hash = None
    for key in [old_email, old_uname]:
        if key and key in users:
            pwd_hash = users[key]
            break

    if not pwd_hash:
        return

    # Alte entfernen
    if old_email and old_email != new_email and old_email in users:
        del users[old_email]
    if old_uname and old_uname != new_uname and old_uname in users:
        del users[old_uname]

    # Neue setzen
    if new_email:
        users[new_email] = pwd_hash
    if new_uname:
        users[new_uname] = pwd_hash

    save_users(users)

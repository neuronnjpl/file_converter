import sys
import os
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import streamlit as st

from documents_utils.models.pdf_reader import extract_tables
from documents_utils.models.rules import check_rule, RuleResult
from documents_utils.models.rule_registry import RuleRegistry

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="Analyseur PDF",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&family=IBM+Plex+Sans:wght@300;400;500;600&display=swap');

html, body, [class*="css"] { font-family: 'IBM Plex Sans', sans-serif; }

.app-title {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 1.75rem; font-weight: 500;
    letter-spacing: -0.02em; color: #0f172a; margin: 0;
}
.app-subtitle {
    font-size: 0.9rem; color: #94a3b8;
    margin-top: 0.25rem; font-weight: 300; margin-bottom: 1.5rem;
}
.kpi-grid { display: flex; gap: 1rem; margin: 1.5rem 0; flex-wrap: wrap; }
.kpi {
    flex: 1; min-width: 110px;
    background: #f8fafc; border: 1px solid #e2e8f0;
    border-radius: 8px; padding: 1rem 1.25rem; text-align: center;
}
.kpi-value {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 2.25rem; font-weight: 500; line-height: 1; margin-bottom: 0.3rem;
}
.kpi-label {
    font-size: 0.72rem; font-weight: 600;
    text-transform: uppercase; letter-spacing: 0.08em; color: #94a3b8;
}
.kpi-total  { border-top: 3px solid #0f172a; }
.kpi-ok     { border-top: 3px solid #22c55e; }
.kpi-viol   { border-top: 3px solid #ef4444; }
.kpi-notab  { border-top: 3px solid #f59e0b; }
.kpi-nonpdf { border-top: 3px solid #94a3b8; }

.file-row {
    display: flex; align-items: center; gap: 0.75rem;
    padding: 0.65rem 1rem; border-radius: 6px;
    margin-bottom: 0.35rem; border-left: 3px solid transparent;
    background: #f8fafc;
}
.file-row-ok      { background: #f0fdf4; border-left-color: #22c55e; }
.file-row-viol    { background: #fef2f2; border-left-color: #ef4444; }
.file-row-notab   { background: #fffbeb; border-left-color: #f59e0b; }
.file-row-na      { background: #eff6ff; border-left-color: #3b82f6; }
.file-row-nonpdf  { background: #f8fafc; border-left-color: #e2e8f0; }
.file-row-error   { background: #fff7ed; border-left-color: #f97316; }

.file-name {
    font-family: 'IBM Plex Mono', monospace; font-size: 0.85rem;
    color: #1e293b; flex: 1; overflow: hidden;
    text-overflow: ellipsis; white-space: nowrap;
}
.badge {
    font-size: 0.68rem; font-weight: 700; text-transform: uppercase;
    letter-spacing: 0.07em; padding: 0.2rem 0.55rem;
    border-radius: 3px; white-space: nowrap;
}
.badge-ok     { background: #dcfce7; color: #15803d; }
.badge-viol   { background: #fee2e2; color: #b91c1c; }
.badge-notab  { background: #fef9c3; color: #a16207; }
.badge-na     { background: #dbeafe; color: #1d4ed8; }
.badge-nonpdf { background: #f1f5f9; color: #64748b; }
.badge-error  { background: #ffedd5; color: #c2410c; }

.table-count { font-size: 0.75rem; color: #94a3b8; white-space: nowrap; }
.rule-detail {
    font-size: 0.82rem; padding: 0.5rem 0.75rem; border-radius: 4px;
    margin: 0.3rem 0; background: white; border: 1px solid #f1f5f9;
    display: flex; justify-content: space-between; align-items: center;
}
.divider { border: none; border-top: 1px solid #e2e8f0; margin: 1.25rem 0; }
</style>
""", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Sidebar — gestion des règles
# ---------------------------------------------------------------------------

with st.sidebar:
    st.markdown("### ⚙️ Règles métier")

    registry = RuleRegistry()

    if not registry.all:
        st.caption("Aucune règle définie.")
    else:
        for rule in registry.all:
            col_toggle, col_del = st.columns([5, 1])
            with col_toggle:
                enabled = st.toggle(rule.name, value=rule.enabled, key=f"toggle_{rule.id}")
                if enabled != rule.enabled:
                    registry.set_enabled(rule.id, enabled)
                    st.rerun()
                if rule.description:
                    st.caption(rule.description)
                st.caption(
                    f"`{rule.label_a}` **{rule.operator}** `{rule.label_b}`",
                )
            with col_del:
                st.write("")
                if st.button("🗑️", key=f"del_{rule.id}", help="Supprimer cette règle"):
                    registry.remove(rule.id)
                    st.rerun()
            st.divider()


# ---------------------------------------------------------------------------
# Analysis
# ---------------------------------------------------------------------------

def _file_category(table_results):
    all_rule_results = [r for t in table_results for r in t["rules"]]
    with_data = [r for r in all_rule_results if r.has_data]
    if not with_data:
        return "na"
    if any(not r.ok for r in with_data):
        return "viol"
    return "ok"


def analyze_directory(dir_path, active_rules):
    results = []
    try:
        files = sorted(f for f in os.listdir(dir_path) if os.path.isfile(os.path.join(dir_path, f)))
    except Exception as e:
        st.error(f"Impossible de lire le répertoire : {e}")
        return results

    if not files:
        return results

    bar = st.progress(0, text="Analyse en cours…")

    for idx, f in enumerate(files):
        bar.progress((idx + 1) / len(files), text=f"  {f}")
        filepath = os.path.join(dir_path, f)

        if not f.lower().endswith(".pdf"):
            results.append({"name": f, "category": "nonpdf", "tables": []})
            continue

        try:
            tables = extract_tables(filepath)
            if tables.n == 0:
                results.append({"name": f, "category": "notab", "tables": []})
                continue

            table_results = []
            with tempfile.TemporaryDirectory() as tmpdir:
                for i, table in enumerate(tables):
                    csv_path = os.path.join(tmpdir, f"table_{i+1}.csv")
                    table.to_csv(csv_path)
                    rule_results = [check_rule(csv_path, rule) for rule in active_rules]
                    table_results.append({
                        "index": i + 1,
                        "rules": rule_results,
                        "df": table.df.copy(),
                    })

            results.append({
                "name": f,
                "category": _file_category(table_results),
                "tables": table_results,
            })

        except Exception as e:
            results.append({"name": f, "category": "error", "tables": [], "error": str(e)})

    bar.empty()
    return results


# ---------------------------------------------------------------------------
# Render helpers
# ---------------------------------------------------------------------------

_CATEGORY_META = {
    "ok":     ("file-row-ok",     "badge-ok",     "✅ Conforme"),
    "viol":   ("file-row-viol",   "badge-viol",   "❌ Violation"),
    "na":     ("file-row-na",     "badge-na",     "ℹ️ N/A"),
    "notab":  ("file-row-notab",  "badge-notab",  "📭 Sans tableau"),
    "nonpdf": ("file-row-nonpdf", "badge-nonpdf", "Non-PDF"),
    "error":  ("file-row-error",  "badge-error",  "⚠️ Erreur"),
}


def _rule_html(r: RuleResult):
    if not r.has_data:
        return '<span style="color:#94a3b8">ℹ️ Non applicable</span>'
    a, b = r.value_a, r.value_b
    if r.ok:
        return f'<span style="color:#15803d">✅ {a:.2f} {r.operator} {b:.2f} EUR</span>'
    if a == b:
        return f'<span style="color:#b91c1c">❌ Égaux ({a:.2f} EUR)</span>'
    return f'<span style="color:#b91c1c">❌ {a:.2f} {r.operator} {b:.2f} EUR (violation)</span>'


def render_file_list(files):
    if not files:
        st.markdown('<p style="color:#94a3b8; font-size:0.85rem; padding:1rem 0">Aucun fichier dans cette catégorie.</p>', unsafe_allow_html=True)
        return

    for f in files:
        row_cls, badge_cls, label = _CATEGORY_META.get(f["category"], _CATEGORY_META["error"])
        n = len(f["tables"])
        tab_info = f'{n} tableau{"x" if n > 1 else ""}' if n else ""

        st.markdown(f"""
        <div class="file-row {row_cls}">
            <span class="file-name">{f['name']}</span>
            {f'<span class="table-count">{tab_info}</span>' if tab_info else ''}
            <span class="badge {badge_cls}">{label}</span>
        </div>
        """, unsafe_allow_html=True)

        if f["tables"]:
            with st.expander("Détail des tableaux"):
                for t in f["tables"]:
                    rules_html = "".join(
                        f'<div class="rule-detail">'
                        f'<span style="font-family:\'IBM Plex Mono\',monospace;font-size:0.8rem">{r.rule_name}</span>'
                        f'<span>{_rule_html(r)}</span>'
                        f'</div>'
                        for r in t["rules"]
                    ) or '<span style="color:#94a3b8;font-size:0.8rem">Aucune règle active</span>'

                    st.markdown(
                        f'<p style="font-family:\'IBM Plex Mono\',monospace;font-size:0.8rem;margin-bottom:0.25rem">'
                        f'Tableau {t["index"]}</p>{rules_html}',
                        unsafe_allow_html=True,
                    )
                    st.dataframe(t["df"], use_container_width=True, hide_index=True)

        elif f["category"] == "error":
            with st.expander("Voir l'erreur"):
                st.error(f.get("error", "Erreur inconnue"))


# ---------------------------------------------------------------------------
# Main UI
# ---------------------------------------------------------------------------

st.markdown("""
<div>
    <p class="app-title">📋 Analyseur PDF</p>
    <p class="app-subtitle">Extraction de tableaux · Vérification des règles métier</p>
</div>
""", unsafe_allow_html=True)

col_path, col_btn = st.columns([5, 1])
with col_path:
    dir_path = st.text_input(
        "Répertoire",
        placeholder=r"Ex : C:\Users\lapor\Documents\pdfs",
        label_visibility="collapsed",
    )
with col_btn:
    run = st.button("Analyser →", use_container_width=True, type="primary")

if run:
    if not dir_path:
        st.warning("Saisis un répertoire.")
    elif not os.path.isdir(dir_path):
        st.error(f"Répertoire introuvable : `{dir_path}`")
    else:
        active_rules = RuleRegistry().enabled
        results = analyze_directory(dir_path, active_rules)

        if not results:
            st.info("Aucun fichier trouvé dans ce répertoire.")
            st.stop()

        counts = {k: sum(1 for r in results if r["category"] == k)
                  for k in ("ok", "viol", "notab", "na", "nonpdf", "error")}

        st.markdown(f"""
        <div class="kpi-grid">
            <div class="kpi kpi-total">
                <div class="kpi-value">{len(results)}</div>
                <div class="kpi-label">Fichiers</div>
            </div>
            <div class="kpi kpi-ok">
                <div class="kpi-value" style="color:#15803d">{counts['ok']}</div>
                <div class="kpi-label">Conformes</div>
            </div>
            <div class="kpi kpi-viol">
                <div class="kpi-value" style="color:#b91c1c">{counts['viol']}</div>
                <div class="kpi-label">Violations</div>
            </div>
            <div class="kpi kpi-notab">
                <div class="kpi-value" style="color:#a16207">{counts['notab']}</div>
                <div class="kpi-label">Sans tableau</div>
            </div>
            <div class="kpi kpi-nonpdf">
                <div class="kpi-value" style="color:#64748b">{counts['nonpdf']}</div>
                <div class="kpi-label">Non-PDF</div>
            </div>
        </div>
        <hr class="divider"/>
        """, unsafe_allow_html=True)

        tabs = st.tabs([
            f"Tous  {len(results)}",
            f"✅  {counts['ok']}",
            f"❌  {counts['viol']}",
            f"📭  {counts['notab']}",
            f"ℹ️  {counts['na']}",
            f"🚫  {counts['nonpdf']}",
        ])

        for tab, cat in zip(tabs, [None, "ok", "viol", "notab", "na", "nonpdf"]):
            with tab:
                subset = results if cat is None else [r for r in results if r["category"] == cat]
                render_file_list(subset)

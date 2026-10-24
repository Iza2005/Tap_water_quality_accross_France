import streamlit as st
from utils.viz import LABELS

def render(t, year, metric):
    nat = t["national"].set_index("year")
    d = t["dept"][(t["dept"]["year"] == year) & (t["dept"]["n"] >= 100)]
    worst = d.sort_values(metric, ascending=False).iloc[0]
    s = t["by_size"][t["by_size"]["year"] == year].set_index("size")["pct_bact"].dropna()
    trend = "decreased" if nat[metric].iloc[-1] < nat[metric].iloc[0] else "did not decrease"

    st.header("The final key insights")
    lines = [
        f"To conclude, we can observe that overall, {100 - nat.loc[year, 'pct_bact']:.1f}% of samples met bacteriological standards "
        f"in {year}. The {LABELS[metric].lower()} {trend} between {nat.index.min()} and {nat.index.max()}."
        f" Also, accross all departments, {worst['dept_name']} has the highest rate ({worst[metric]:.2f}%, "
        f"national {nat.loc[year, metric]:.2f}%)."]
    if len(s) >= 2:
        lines.append(f"- We observed that bacteriological non-compliance is {s.iloc[0]:.2f}% for the smallest "
                     f"networks ({s.index[0]} samples per year) against {s.iloc[-1]:.2f}% for the largest ones ({s.index[-1]}).")
    st.success("\n".join(lines))
    st.markdown(
        "\nGenerally, when a good national average shows, it might hide local problems. That is why monitoring and "
        "investment should prioritize the departments and network sizes with the highest rates above. \n"
        "\n **How can we improve the analysis ?**\n" \
        "\nTo go deeper, this app could add graphs on 'population served per network' to weight results by people affected."
        "This focus helps the analysis go further and report inequalities among departments. " \
        "We could also break chemical failures down by parameter, such as pesticides or nitrates, to see clearly which "
        "particle is the most present when there are failures.")
    st.info(
        "Limitations : \n" \
        "\nAlthough there are non-compliant sample, they are not necessarily a health risk, so they need to be followed by "
        "a restriction or another test. Also, sampling frequency differs between networks, and network size is a proxy, so it does not "
        "represent the actual population served. " \
        "Furthermore, since the current year is incomplete, the data for this year differs from other complete years.")

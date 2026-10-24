import pandas as pd
import streamlit as st


def render(quality):
    st.markdown(
        "Generally, French people automatically take a cup and fill it with tap water when "
        "thirsty. But can they trust the quality of this water in their city ? We know that it is "
        "the most monitored food in France. Indeed, each year, regional health "
        "agencies take over 300,000 samples and run about 12 million analyses. \n" \
        "But is the water equally safe everywhere ?")
    st.markdown(
        "Audience : Residents and local officials who want to know how their tap water compares.  \n"
        "\nQuestions : " \
        "\n1. How often does tap water fail the standards, and is it improving ? " \
        "\n2. Which departments are most affected ? " \
        "\n3. Are small networks more exposed than large ones ?" \
        "\n4. Where do nitrates exceed the 50 mg/L limit ?")
    with st.expander("Data and methods"):
        st.markdown(
            "- One row in the raw data = one water sample linked to a distribution network (UDI). "
            "A UDI can serve part of one or several communes.\n"
            "- Non-compliance = share of samples flagged N (Non-compliant) among samples with a "
            "C or N verdict, separately for bacteriological and chemical standards.\n"
            "- Nitrates : one value per sample (parameter NO3), compared to the 50 mg/L limit.\n"
            "- Some samples are taken upstream like treatment plant or source, and reported for every network "
            "they feed. Departments count each sample once.\n"
            "- One department comes from the network's main commune. Overseas departements are "
            "excluded from the map.\n"
            "- Network size is approximated by the number of samples per year since regulatory sampling "
            "frequency increases with population served.")
        st.caption("Validation = rows read, rows kept after cleaning, per year)")
        st.dataframe(pd.DataFrame(quality).T, width="stretch")

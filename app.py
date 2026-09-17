import streamlit as st
import pandas as pd
from inference import predict


# ==================================================
# RESET FUNCTION
# ==================================================

def reset_text():
    st.session_state["input_text"] = ""


# ==================================================
# PAGE SETTINGS
# ==================================================

st.set_page_config(
    page_title="Hindi Edge AI",
    page_icon="🇮🇳",
    layout="wide"
)


# ==================================================
# SESSION STATE
# ==================================================

if "history" not in st.session_state:
    st.session_state["history"] = []

if "last_result" not in st.session_state:
    st.session_state["last_result"] = None

if "last_text" not in st.session_state:
    st.session_state["last_text"] = ""


# ==================================================
# SIDEBAR
# ==================================================

with st.sidebar:

    st.title("🇮🇳 Hindi Edge AI")

    st.write("### About Project")

    st.write(
        "This system analyzes Hindi text using "
        "Natural Language Processing and Edge AI."
    )

    st.divider()

    st.write("### Features")

    st.write("👤 Named Entity Recognition")
    st.write("😊 Sentiment Analysis")
    st.write("🎯 Confidence Score")
    st.write("⚡ Inference Time")
    st.write("📊 Entity Visualization")
    st.write("📜 Analysis History")
    st.write("📥 Download Report")

    st.divider()

    st.caption("Member 4 - Full-Stack Integration")


# ==================================================
# MAIN HEADER
# ==================================================

st.title("🇮🇳 Hindi NLP Edge AI")

st.subheader("Hindi Text Analysis Dashboard")

st.divider()


# ==================================================
# INPUT
# ==================================================

st.header("📝 Enter Hindi Text")

text = st.text_area(
    "Hindi Sentence",
    placeholder="उदाहरण: राहुल दिल्ली में रहता है।",
    height=150,
    key="input_text"
)


# ==================================================
# BUTTONS
# ==================================================

col1, col2 = st.columns(2)

with col1:

    analyze = st.button(
        "🔍 Analyze Text",
        use_container_width=True
    )

with col2:

    st.button(
        "🔄 Reset",
        use_container_width=True,
        on_click=reset_text
    )


# ==================================================
# ANALYSIS
# ==================================================

if analyze:

    if text.strip():

        # Run inference
        result = predict(text)

        # Save latest result
        st.session_state["last_result"] = result
        st.session_state["last_text"] = text

        entities = result["entities"]
        sentiment = result["sentiment"]
        confidence = result["confidence"]
        inference_time = result["inference_time"]


        # ==================================================
        # SAVE HISTORY
        # ==================================================

        history_item = {
            "Text": text,
            "Sentiment": sentiment,
            "Confidence": f"{confidence * 100:.0f}%",
            "Inference Time": f"{inference_time} ms",
            "Entities": len(entities)
        }

        st.session_state["history"].append(history_item)


        # ==================================================
        # RESULT
        # ==================================================

        st.divider()

        st.header("📊 Analysis Result")


        # ==================================================
        # METRICS
        # ==================================================

        col1, col2, col3 = st.columns(3)

        with col1:

            st.metric(
                "😊 Sentiment",
                sentiment
            )

        with col2:

            st.metric(
                "🎯 Confidence",
                f"{confidence * 100:.0f}%"
            )

        with col3:

            st.metric(
                "⚡ Inference Time",
                f"{inference_time} ms"
            )


        # ==================================================
        # SENTIMENT
        # ==================================================

        st.divider()

        st.subheader("😊 Sentiment Analysis")

        if sentiment == "Positive":

            st.success(
                "😊 Positive Sentiment Detected"
            )

        elif sentiment == "Negative":

            st.error(
                "😞 Negative Sentiment Detected"
            )

        else:

            st.info(
                "😐 Neutral Sentiment Detected"
            )


        # ==================================================
        # CONFIDENCE
        # ==================================================

        st.subheader("🎯 Model Confidence")

        st.progress(confidence)

        st.write(
            f"Model confidence: "
            f"**{confidence * 100:.0f}%**"
        )


        # ==================================================
        # ENTITY SUMMARY
        # ==================================================

        st.divider()

        st.subheader("📊 Entity Summary")

        person_count = 0
        location_count = 0
        other_count = 0

        for entity in entities:

            if entity["label"] == "PERSON":

                person_count += 1

            elif entity["label"] == "LOCATION":

                location_count += 1

            else:

                other_count += 1


        total_entities = len(entities)


        # ==================================================
        # ENTITY METRICS
        # ==================================================

        col1, col2, col3, col4 = st.columns(4)

        with col1:

            st.metric(
                "👤 PERSON",
                person_count
            )

        with col2:

            st.metric(
                "📍 LOCATION",
                location_count
            )

        with col3:

            st.metric(
                "🔖 OTHER",
                other_count
            )

        with col4:

            st.metric(
                "🔢 Total Entities",
                total_entities
            )


        # ==================================================
        # ENTITY CHART
        # ==================================================

        st.subheader("📈 Entity Distribution")

        chart_data = pd.DataFrame(
            {
                "Count": [
                    person_count,
                    location_count,
                    other_count
                ]
            },
            index=[
                "PERSON",
                "LOCATION",
                "OTHER"
            ]
        )

        # st.bar_chart(chart_data)


        # ==================================================
        # ANALYZED TEXT
        # ==================================================

        st.divider()

        st.subheader("📄 Analyzed Text")

        st.write(text)


        # ==================================================
        # ENTITY HIGHLIGHTING
        # ==================================================

        st.subheader("🔎 Detected Entities")

        highlighted_text = text

        for entity in entities:

            entity_text = entity["text"]
            entity_label = entity["label"]

            highlighted_text = highlighted_text.replace(
                entity_text,
                f"**[{entity_text} — {entity_label}]**"
            )

        st.markdown(highlighted_text)


        # ==================================================
        # ENTITY DETAILS
        # ==================================================

        st.subheader("👤 Entity Details")

        if entities:

            for entity in entities:

                col1, col2 = st.columns([3, 1])

                with col1:

                    st.info(
                        f"**{entity['text']}**"
                    )

                with col2:

                    st.write(
                        f"`{entity['label']}`"
                    )

        else:

            st.success(
                "No named entities detected."
            )


        # ==================================================
        # PERFORMANCE
        # ==================================================

        st.divider()

        st.subheader("⚡ Performance")

        st.write(
            f"⏱️ Processing Time: "
            f"**{inference_time} ms**"
        )


        # ==================================================
        # SYSTEM INFORMATION
        # ==================================================

        st.subheader("⚙️ System Information")

        col1, col2, col3 = st.columns(3)

        with col1:

            st.success(
                "🟢 Dashboard Online"
            )

        with col2:

            st.info(
                "🟡 Demo Inference Active"
            )

        with col3:

            st.warning(
                "🟡 ONNX Model Pending"
            )


    else:

        st.warning(
            "⚠️ Please enter a Hindi sentence first."
        )


# ==================================================
# DOWNLOAD REPORT
# ==================================================

if st.session_state["last_result"] is not None:

    st.divider()

    st.header("📥 Download Analysis Report")

    latest_result = st.session_state["last_result"]
    latest_text = st.session_state["last_text"]

    report_data = {
        "Analyzed Text": [latest_text],
        "Sentiment": [latest_result["sentiment"]],
        "Confidence": [
            f"{latest_result['confidence'] * 100:.0f}%"
        ],
        "Inference Time": [
            f"{latest_result['inference_time']} ms"
        ],
        "Total Entities": [
            len(latest_result["entities"])
        ]
    }

    report_df = pd.DataFrame(report_data)

    csv_data = report_df.to_csv(index=False)

    st.download_button(
        label="📥 Download CSV Report",
        data=csv_data,
        file_name="hindi_nlp_analysis_report.csv",
        mime="text/csv",
        use_container_width=True
    )


# ==================================================
# ANALYSIS HISTORY
# ==================================================

st.divider()

st.header("📜 Analysis History")

if st.session_state["history"]:

    history_df = pd.DataFrame(
        st.session_state["history"]
    )

    st.dataframe(
        history_df,
        use_container_width=True,
        hide_index=True
    )

    if st.button(
        "🗑️ Clear History"
    ):

        st.session_state["history"] = []

        st.rerun()

else:

    st.info(
        "No analysis history yet. "
        "Analyze a Hindi sentence to create history."
    )


# ==================================================
# FOOTER
# ==================================================

st.divider()

st.caption(
    "Hindi NLP Edge AI | Member 4 - Full-Stack Integration"
)
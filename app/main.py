"""
Main Streamlit application for Capstone Sales Analysis
"""

import streamlit as st
import sys
import json
import importlib
from pathlib import Path
from typing import Dict, List, Optional, Type

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import STREAMLIT_PAGE_CONFIG
from src.summary_metrics import (
    generate_summary_metrics,
    get_formatted_summary,
    get_prompt_metrics_context,
)

# Define data directories
DATA_RAW_DIR = Path(__file__).parent.parent / "data" / "raw"
PDF_FOLDER_DIR = DATA_RAW_DIR / "PDF_Folder"


def get_csv_files():
    """Get all CSV files from data/raw directory"""
    if not DATA_RAW_DIR.exists():
        return []
    return [f for f in DATA_RAW_DIR.glob("*.csv")]


def get_pdf_files():
    """Get all PDF files from data/raw/PDF_Folder directory"""
    if not PDF_FOLDER_DIR.exists():
        return []
    return [f for f in PDF_FOLDER_DIR.glob("*.pdf")]


def format_chat_history(messages, max_turns: int = 6) -> str:
    """Format recent chat history for prompt memory."""
    if not messages:
        return "None"

    recent = messages[-max_turns:]
    lines = []
    for msg in recent:
        role = msg.get("role", "user").title()
        content = msg.get("content", "")
        lines.append(f"{role}: {content}")
    return "\n".join(lines)


@st.cache_resource
def load_sales_metrics():
    """Load and cache sales metrics once per session"""
    metrics = generate_summary_metrics()
    return metrics


@st.cache_data
def load_qa_examples(data_path: Path) -> List[Dict[str, str]]:
    """Load QA evaluation examples from JSON file or return defaults."""
    if data_path.exists():
        with data_path.open("r", encoding="utf-8") as handle:
            return json.load(handle)

    return [
        {
            "query": "Which region has the highest total sales?",
            "answer": "West is the best-performing region by total sales."
        },
        {
            "query": "What is the best month for sales performance?",
            "answer": "April is the best-performing month."
        },
        {
            "query": "Which product is the top seller by value?",
            "answer": "Widget A is the top-selling product by value."
        }
    ]


def resolve_qa_eval_chain() -> Optional[Type]:
    """Resolve QAEvalChain from supported LangChain module paths."""
    for module_path in (
        "langchain_classic.evaluation.qa",
        "langchain_classic.evaluation",
        "langchain.evaluation.qa",
        "langchain.evaluation",
    ):
        try:
            module = importlib.import_module(module_path)
        except Exception:
            continue

        if hasattr(module, "QAEvalChain"):
            return getattr(module, "QAEvalChain")

    return None


def normalize_grade_label(grade: object) -> str:
    """Normalize evaluator output into stable grade labels."""
    raw_value = grade
    if isinstance(grade, dict):
        for key in ("results", "result", "grade", "value", "text", "label", "score"):
            if key in grade and grade.get(key) not in (None, ""):
                raw_value = grade.get(key)
                break

    text = str(raw_value).strip()
    normalized = text.lower()

    if "incorrect" in normalized:
        return "INCORRECT"
    if "correct" in normalized:
        return "CORRECT"
    if "partial" in normalized:
        return "PARTIAL"
    if normalized in {"true", "yes", "1"}:
        return "CORRECT"
    if normalized in {"false", "no", "0"}:
        return "INCORRECT"

    return text.upper() if text else "UNKNOWN"


def render_visualizations(metrics: Dict) -> None:
    """Render sales visualizations from metrics."""
    try:
        import pandas as pd
        import plotly.express as px

        time_based = metrics.get('time_based_analysis', {})
        product = metrics.get('product_performance', {})
        region = metrics.get('regional_performance', {})
        gender_region = metrics.get('gender_region_performance', {})
        customer = metrics.get('customer_insights', {})

        # Sales trends over time
        monthly_sales = time_based.get('monthly_sales', {})
        if monthly_sales:
            monthly_df = pd.DataFrame(
                [(k, v) for k, v in monthly_sales.items()],
                columns=["Month", "Sales"]
            )
            monthly_df["Month"] = pd.to_datetime(monthly_df["Month"], errors="coerce")
            monthly_df = monthly_df.sort_values("Month")

            st.subheader("Sales Trends Over Time")
            fig_month = px.line(
                monthly_df,
                x="Month",
                y="Sales",
                markers=True,
                title="Monthly Sales"
            )
            st.plotly_chart(fig_month, use_container_width=True)
        else:
            st.info("Monthly sales data is not available.")

        # Product performance comparisons
        product_stats = product.get('product_stats', {})
        if product_stats:
            product_rows = [
                {"Product": name, "Sales": stats.get('sum', 0)}
                for name, stats in product_stats.items()
            ]
            product_df = pd.DataFrame(product_rows)
            product_df = product_df.sort_values("Sales", ascending=False).head(10)

            st.subheader("Product Performance Comparisons")
            fig_products = px.bar(
                product_df,
                x="Product",
                y="Sales",
                title="Top 10 Products",
                color="Sales",
                color_continuous_scale="plasma"
            )
            st.plotly_chart(fig_products, use_container_width=True)
        else:
            st.info("Product sales data is not available.")

        # Regional analysis
        region_sales = region.get('region_sales', {})
        if region_sales:
            region_df = pd.DataFrame(
                [(k, v) for k, v in region_sales.items()],
                columns=["Region", "Sales"]
            ).sort_values("Sales", ascending=False)

            st.subheader("Regional Analysis")
            fig_region = px.bar(
                region_df,
                x="Region",
                y="Sales",
                title="Regional Sales",
                color="Sales",
                color_continuous_scale="viridis"
            )
            st.plotly_chart(fig_region, use_container_width=True)
        else:
            st.info("Regional sales data is not available.")

        # Customer demographics and segmentation
        age_group_stats = customer.get('age_group_stats', {})
        if age_group_stats:
            age_rows = [
                {"Age Group": group, "Avg Sales": value}
                for group, value in age_group_stats.items()
            ]
            age_df = pd.DataFrame(age_rows)
            age_df = age_df.sort_values("Avg Sales", ascending=False)

            st.subheader("Customer Demographics: Age Group")
            fig_age = px.bar(
                age_df,
                x="Age Group",
                y="Avg Sales",
                title="Average Sales by Age Group",
                color="Avg Sales",
                color_continuous_scale="teal"
            )
            st.plotly_chart(fig_age, use_container_width=True)
        else:
            st.info("Age group data is not available.")

        gender_stats = customer.get('gender_sales', {})
        if gender_stats:
            gender_rows = [
                {
                    "Gender": gender,
                    "Avg Sales": stats.get('mean', 0),
                    "Total Sales": stats.get('sum', 0)
                }
                for gender, stats in gender_stats.items()
            ]
            gender_df = pd.DataFrame(gender_rows)

            st.subheader("Customer Demographics: Gender")
            fig_gender = px.bar(
                gender_df,
                x="Gender",
                y="Total Sales",
                title="Total Sales by Gender",
                color="Total Sales",
                color_continuous_scale="viridis"
            )
            st.plotly_chart(fig_gender, use_container_width=True)
        else:
            st.info("Gender sales data is not available.")

        gender_region_sales = gender_region.get('gender_region_sales', {})
        if gender_region_sales:
            heatmap_rows = [
                {"Gender": gender, "Region": region_name, "Sales": value}
                for (gender, region_name), value in gender_region_sales.items()
            ]
            heatmap_df = pd.DataFrame(heatmap_rows)
            pivot_df = heatmap_df.pivot(index="Gender", columns="Region", values="Sales").fillna(0)

            st.subheader("Customer Segmentation: Gender vs Region")
            fig_heatmap = px.imshow(
                pivot_df,
                text_auto=True,
                color_continuous_scale="teal"
            )
            st.plotly_chart(fig_heatmap, use_container_width=True)
        else:
            st.info("Gender-region sales data is not available.")

    except Exception as e:
        st.warning(f"Could not render charts: {e}")


def render_chat_interface() -> None:
    """Render AI assistant chat interface backed by vector stores."""
    try:
        from src.database import list_indexes, load_vector_store, get_retriever, similarity_search
        from src.llm import get_llm, create_rag_chain
        from src.config import PROCESSED_DATA_DIR
        from src.metrics_tool import (
            load_aggregated_metrics,
            aggregated_metrics_to_documents,
            format_aggregated_metrics_context
        )

        indexes = list_indexes()
        if not indexes:
            st.info("No vector stores available. Upload data first in 'Upload & Process'.")
            return

        st.caption(f"Searching across {len(indexes)} vector database(s): {', '.join(indexes)}")

        merged_store = None
        for idx_name in indexes:
            store = load_vector_store(idx_name)
            if store:
                if merged_store is None:
                    merged_store = store
                else:
                    try:
                        merged_store.merge_from(store)
                    except Exception as e:
                        st.warning(f"Could not fully merge {idx_name}: {e}")

        if not merged_store:
            st.error("Could not load vector stores. Please create them first.")
            return

        agg_metrics_path = PROCESSED_DATA_DIR / "aggregated_metrics.pkl"
        agg_metrics = load_aggregated_metrics(agg_metrics_path)
        if agg_metrics:
            try:
                agg_docs = aggregated_metrics_to_documents(agg_metrics, source=str(agg_metrics_path))
                if agg_docs:
                    merged_store.add_documents(agg_docs)
            except Exception as e:
                st.warning(f"Could not add PKL metrics to retriever: {e}")

        retriever = get_retriever(merged_store, k=5)
        llm = get_llm()

        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []

        for msg in st.session_state.chat_history:
            with st.chat_message(msg.get("role", "user")):
                st.write(msg.get("content", ""))

        st.markdown(
            """
            <style>
            div[data-testid="stTextInput"] input[aria-label="Your question:"] {
                border: 2px solid red !important;
            }
            </style>
            """,
            unsafe_allow_html=True,
        )
        user_question = st.text_input("Your question:", placeholder="What would you like to know about your data?")

        if st.button("Get Answer", type="primary"):
            trimmed_question = user_question.strip() if user_question else ""
            if len(trimmed_question) < 20:
                st.warning("Please enter a more meaningful question (at least 20 characters).")
            else:
                with st.spinner("Analyzing your question..."):
                    try:
                        history_text = format_chat_history(st.session_state.chat_history)
                        def build_metrics_context(question: str) -> str:
                            summary_text = get_prompt_metrics_context(load_sales_metrics(), query=question)
                            pkl_text = format_aggregated_metrics_context(agg_metrics, query=question)
                            if pkl_text:
                                return f"{summary_text}\n\n{pkl_text}"
                            return summary_text

                        chain = create_rag_chain(
                            retriever,
                            llm,
                            metrics_provider=build_metrics_context,
                            history_provider=lambda: history_text
                        )

                        response = chain.invoke(trimmed_question)
                        response_text = response.content if hasattr(response, 'content') else response

                        st.session_state.chat_history.append({"role": "user", "content": trimmed_question})
                        st.session_state.chat_history.append({"role": "assistant", "content": str(response_text)})

                        st.markdown("### Answer")
                        st.write(response_text)
                    except Exception as e:
                        st.error(f"Error getting response: {e}")
    except Exception as e:
        st.error(f"Error initializing assistant: {e}")


def main():
    """Main Streamlit app"""
    st.set_page_config(**STREAMLIT_PAGE_CONFIG)  # type: ignore

    st.markdown(
        """
        <style>
        .block-container {
            padding-top: 1rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("<h1 style='text-align: center; margin-top: 0;'>📊 Sales Analysis</h1>", unsafe_allow_html=True)
    st.markdown("---")
    
    # Sidebar
    with st.sidebar:
        page = st.radio(
            "Navigation:",
            ["Home", "Sales Metrics", "Vector Store", "Upload & Process", "LLMOps"]
        )
        
        # Display metrics in sidebar
        st.markdown("---")
        st.subheader("📊 Quick Metrics")
        try:
            metrics = load_sales_metrics()
            if metrics.get('status') == 'success':
                overall = metrics.get('overall_metrics', {})
                region = metrics.get('regional_performance', {})
                time_based = metrics.get('time_based_analysis', {})

                st.metric("Total Sales", f"${overall.get('total_sales', 0):,.0f}")
                st.metric("Avg Transaction", f"${overall.get('average_sale', 0):.2f}")
                st.metric("Best Region", region.get('best_region', 'N/A'))
                st.metric(
                    "Best Month",
                    time_based.get('best_month', 'N/A').split('-')[1] if time_based.get('best_month') else 'N/A'
                )
            else:
                st.caption("⚠️ Metrics unavailable")
        except Exception:
            st.caption("Could not load metrics")

        if st.button("Refresh Metrics"):
            load_sales_metrics.clear()
            st.rerun()

    # Main content
    if page == "Home":
        st.header("Welcome to Sales Analysis with FAISS")
        st.markdown("""
        This application helps you analyze sales data using AI, LLMs, and FAISS vector search.

        | Features |  | Get started |
        | --- | --- | --- |
        | 📤 Upload and process sales data (PDF/CSV)<br>📊 Build FAISS vector store for efficient search<br>🔍 Semantic similarity search on your documents<br>💬 Chat with your data using AI<br>📈 Interactive data analysis with visualizations<br>🎯 Ask questions about sales trends | &nbsp; | 1. Upload your sales data (PDF or CSV)<br>2. Process and build vector embeddings<br>3. Search and analyze your data<br>4. Chat with AI about your findings |
        """, unsafe_allow_html=True)

        st.info("💡 Use the sidebar to navigate between sections")
        st.header("💬 Chat with Your Data Analyst Bot")

        try:
            from src.database import get_aggregated_metrics
            import pandas as pd
            import plotly.express as px

            chat_tab, metrics_tab = st.tabs(["💬 Chat Interface", "📊 Database Metrics"])

            with chat_tab:
                render_chat_interface()

            with metrics_tab:
                st.subheader("📊 Database Aggregated Metrics")

                try:
                    metrics = get_aggregated_metrics()

                    if metrics:
                        summary = metrics.get('summary', {})
                        col1, col2, col3, col4 = st.columns(4)

                        with col1:
                            st.metric("Total Indexes", summary.get('total_indexes', 0))
                        with col2:
                            st.metric("Total Vectors", f"{summary.get('total_vectors', 0):,}")
                        with col3:
                            st.metric("Database Size", f"{summary.get('total_size_mb', 0):.2f} MB")
                        with col4:
                            st.metric("Updated", summary.get('timestamp', 'N/A')[:10])

                        st.markdown("---")

                        st.subheader("Index Details")
                        by_index = metrics.get('by_index', [])

                        if by_index:
                            df = pd.DataFrame(by_index)
                            st.dataframe(df, use_container_width=True)

                            st.markdown("---")
                            st.subheader("📈 Visualizations")

                            chart_col1, chart_col2 = st.columns(2)

                            with chart_col1:
                                fig1 = px.bar(
                                    df,
                                    x='name',
                                    y='vectors',
                                    title='Vectors per Index',
                                    labels={'name': 'Index', 'vectors': 'Vector Count'},
                                    color='vectors',
                                    color_continuous_scale='viridis'
                                )
                                st.plotly_chart(fig1, use_container_width=True)

                            with chart_col2:
                                fig2 = px.bar(
                                    df,
                                    x='name',
                                    y='size_mb',
                                    title='Storage Size per Index',
                                    labels={'name': 'Index', 'size_mb': 'Size (MB)'},
                                    color='size_mb',
                                    color_continuous_scale='plasma'
                                )
                                st.plotly_chart(fig2, use_container_width=True)

                            st.subheader("Vector Distribution")
                            fig3 = px.pie(
                                df,
                                values='vectors',
                                names='name',
                                title='Vector Distribution Across Indexes'
                            )
                            st.plotly_chart(fig3, use_container_width=True)

                        st.markdown("---")
                        st.subheader("📈 Statistics")

                        stats = metrics.get('statistics', {})
                        stat_col1, stat_col2, stat_col3, stat_col4 = st.columns(4)

                        with stat_col1:
                            st.metric(
                                "Avg Vectors/Index",
                                f"{stats.get('avg_vectors_per_index', 0):.0f}"
                            )
                        with stat_col2:
                            st.metric(
                                "Avg Size/Index",
                                f"{stats.get('avg_size_mb_per_index', 0):.2f} MB"
                            )
                        with stat_col3:
                            st.metric(
                                "Largest Index",
                                stats.get('largest_index', 'N/A')
                            )
                        with stat_col4:
                            st.metric(
                                "Smallest Index",
                                stats.get('smallest_index', 'N/A')
                            )
                except Exception as e:
                    st.error(f"Error loading metrics: {e}")

        except Exception as e:
            st.warning(f"Could not load database info: {e}")

        
    
    elif page == "Vector Store":
        st.header("🗄️ Vector Store Management")
        st.markdown("Manage your entire FAISS vector database and indexes.")
        
        # Database Overview
        try:
            from src.database import (
                get_database_info, list_indexes, index_details,
                delete_index, rename_index, backup_database,
                get_index_summary
            )
            
            db_info = get_database_info()
            
            # Database statistics
            if db_info:
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Total Indexes", db_info.get('total_indexes', 0))
                with col2:
                    st.metric("Total Vectors", f"{db_info.get('total_vectors', 0):,}")
                with col3:
                    st.metric("Database Size", f"{db_info.get('total_size_mb', 0):.2f} MB")
                with col4:
                    st.metric("Last Updated", db_info.get('timestamp', 'N/A')[:10])
        except Exception as e:
            st.error(f"Error loading database info: {e}")
        
        st.markdown("---")
        
        # Tabs for different management options
        tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Indexes", "🔧 Manage", "📤 Backup", "📈 Summary", "🔄 Rebuild Data"])
        
        # Tab 1: View All Indexes
        with tab1:
            st.subheader("All Available Indexes")
            try:
                from src.database import list_indexes, index_details
                
                indexes = list_indexes()
                if not indexes:
                    st.info("No vector stores created yet. Go to 'Upload & Process' to create one.")
                else:
                    for idx_name in indexes:
                        with st.expander(f"📄 {idx_name}"):
                            details = index_details(idx_name)
                            if details:
                                col1, col2, col3 = st.columns(3)
                                with col1:
                                    st.metric("Vectors", f"{details.get('total_vectors', 0):,}")
                                with col2:
                                    st.metric("Size", f"{details.get('size_mb', 0):.2f} MB")
                                with col3:
                                    st.metric("Type", details.get('index_type', 'Unknown'))
                                
                                st.text(f"Modified: {details.get('modified', 'N/A')[:10]}")
            except Exception as e:
                st.error(f"Error loading indexes: {e}")
        
        # Tab 2: Manage Indexes
        with tab2:
            st.subheader("Index Management")
            
            try:
                from src.database import list_indexes, delete_index, rename_index
                
                indexes = list_indexes()
                if not indexes:
                    st.info("No indexes to manage")
                else:
                    operation = st.selectbox("Select operation:", ["Delete", "Rename"])
                    selected_index = st.selectbox("Select index:", indexes)
                    
                    if operation == "Delete":
                        if st.button("🗑️ Delete Index"):
                            if delete_index(selected_index):
                                st.success(f"✓ Deleted index: {selected_index}")
                                st.rerun()
                            else:
                                st.error(f"✗ Failed to delete index: {selected_index}")
                    
                    elif operation == "Rename":
                        new_name = st.text_input("New index name:", placeholder="Enter new name")
                        if st.button("✏️ Rename Index"):
                            if new_name and new_name != selected_index:
                                if rename_index(selected_index, new_name):
                                    st.success(f"✓ Renamed: {selected_index} → {new_name}")
                                    st.rerun()
                                else:
                                    st.error("✗ Failed to rename index")
                            else:
                                st.warning("Enter a different name")
            except Exception as e:
                st.error(f"Error: {e}")
        
        # Tab 3: Backup Operations
        with tab3:
            st.subheader("Database Backup")
            
            backup_option = st.radio("Backup operation:", ["Create Backup", "View Backups"])
            
            if backup_option == "Create Backup":
                backup_location = st.text_input("Backup location (leave empty for default):", 
                                                value="backups")
                
                if st.button("💾 Create Backup"):
                    try:
                        from src.database import backup_database
                        
                        with st.spinner("Creating backup..."):
                            if backup_database(backup_location):
                                st.success(f"✓ Backup created in '{backup_location}'")
                            else:
                                st.error("✗ Failed to create backup")
                    except Exception as e:
                        st.error(f"Error: {e}")
            
            elif backup_option == "View Backups":
                from pathlib import Path as PathlibPath
                backup_dir = PathlibPath("backups")
                if backup_dir.exists():
                    backups = sorted([d for d in backup_dir.iterdir() if d.is_dir()], reverse=True)
                    if backups:
                        st.write(f"Found {len(backups)} backup(s):")
                        for backup in backups:
                            st.write(f"📦 {backup.name}")
                    else:
                        st.info("No backups found")
                else:
                    st.info("No backup directory found")
        
        # Tab 4: Summary Statistics
        with tab4:
            st.subheader("Database Summary")
            
            try:
                from src.database import get_index_summary, get_database_info
                
                summary = get_index_summary()
                db_info = get_database_info()
                
                if summary and summary.get('indexes'):
                    # Create a table view
                    data = []
                    for idx_name, idx_info in summary.get('indexes', {}).items():
                        data.append({
                            'Index': idx_name,
                            'Vectors': idx_info.get('vectors', 0),
                            'Type': idx_info.get('type', 'Unknown')
                        })
                    
                    if data:
                        st.dataframe(data, use_container_width=True)
                    
                    # Overall stats
                    st.markdown("---")
                    st.write("**Overall Database Statistics:**")
                    if db_info:
                        st.json({
                            'Location': db_info.get('location'),
                            'Total Indexes': db_info.get('total_indexes'),
                            'Total Vectors': db_info.get('total_vectors'),
                            'Size (MB)': db_info.get('total_size_mb'),
                            'Last Updated': db_info.get('timestamp')
                        })
                else:
                    st.info("No data available")
            except Exception as e:
                st.error(f"Error: {e}")
        
        # Tab 5: Rebuild Data (Vector Store + Aggregated Metrics)
        with tab5:
            st.subheader("Rebuild Vector Store & Metrics")
            st.markdown("Refresh your data by rebuilding the FAISS vector store and aggregated metrics cache.")
            st.markdown("---")
            
            col1, col2 = st.columns(2)
            
            # Column 1: Rebuild Vector Store
            with col1:
                st.subheader("1️⃣ Rebuild Vector Store")
                st.markdown(
                    "Process CSV files from `data/raw/` and rebuild FAISS indexes with fresh embeddings."
                )
                
                if st.button("🔄 Rebuild Vector Store", use_container_width=True, type="primary"):
                    with st.spinner("Processing CSV files and rebuilding vector store..."):
                        try:
                            from src.loaders import load_uploaded_file
                            from src.database import create_vector_store, save_vector_store
                            from pathlib import Path
                            
                            rebuild_count = 0
                            csv_dir = Path("data/raw")
                            csv_files = list(csv_dir.glob("*.csv"))
                            
                            if not csv_files:
                                st.error("No CSV files found in `data/raw/`")
                            else:
                                for csv_file in csv_files:
                                    st.info(f"Processing {csv_file.name}...")
                                    documents, _ = load_uploaded_file(str(csv_file))
                                    
                                    if documents:
                                        index_name = csv_file.stem
                                        vector_store = create_vector_store(documents, index_name)
                                        
                                        if vector_store:
                                            save_vector_store(vector_store, index_name)
                                            st.success(f"✓ Rebuilt: {index_name} ({len(documents)} chunks)")
                                            rebuild_count += 1
                                        else:
                                            st.error(f"✗ Failed to create vector store for {csv_file.name}")
                                    else:
                                        st.error(f"✗ Could not process {csv_file.name}")
                                
                                if rebuild_count > 0:
                                    st.success(f"✅ Successfully rebuilt {rebuild_count} vector store(s)")
                        except Exception as e:
                            st.error(f"Error rebuilding vector store: {e}")
            
            # Column 2: Rebuild Aggregated Metrics
            with col2:
                st.subheader("2️⃣ Rebuild Aggregated Metrics (PKL)")
                st.markdown(
                    "Build aggregated metrics cache from sales data for optimized chat responses."
                )
                
                if st.button("📊 Build Aggregated Metrics", use_container_width=True, type="primary"):
                    with st.spinner("Building aggregated metrics from CSV..."):
                        try:
                            from src.metrics_tool import build_aggregated_metrics_from_csv
                            from src.config import PROCESSED_DATA_DIR
                            from pathlib import Path
                            
                            csv_path = Path("data/raw/sales_data.csv")
                            output_path = PROCESSED_DATA_DIR / "aggregated_metrics.pkl"
                            
                            if not csv_path.exists():
                                st.error(f"CSV not found: {csv_path}")
                            else:
                                saved_path, agg_metrics = build_aggregated_metrics_from_csv(csv_path, output_path)
                                st.success(f"✅ Aggregated metrics saved to {saved_path}")
                                
                                # Show summary
                                st.info(f"Built aggregations for: {', '.join(agg_metrics.keys())}")
                                
                                with st.expander("View aggregation details"):
                                    for name, df in agg_metrics.items():
                                        if df is not None and not df.empty:
                                            st.markdown(f"**{name}** ({len(df)} rows)")
                                            st.dataframe(df.head(5), use_container_width=True)
                        except Exception as e:
                            st.error(f"Error building aggregated metrics: {e}")
            
            st.markdown("---")
            st.info(
                "💡 **Tip:** Rebuild both after adding or updating CSV data to ensure the chat has the latest information and metrics."
            )
    
    elif page == "Upload & Process":
        st.header("📤 Upload and Process Data")
        
        # Quick Action Section - One Click to Process All
        st.markdown("### ⚡ Quick Action")
        
        col_quick1, col_quick2, col_quick3 = st.columns([2, 2, 2])
        
        with col_quick1:
            if st.button("🚀 Create All Vector Stores", type="primary", use_container_width=True, help="Process all PDFs & CSVs in one click"):
                with st.spinner("Processing all files..."):
                    try:
                        from src.loaders import load_uploaded_file
                        from src.database import create_vector_store, save_vector_store
                        
                        all_csv_success = 0
                        all_pdf_success = False
                        
                        # Process all CSV files
                        csv_files = list(DATA_RAW_DIR.glob("*.csv"))
                        
                        st.info(f"📊 Processing {len(csv_files)} CSV file(s)...")
                        
                        for csv_file in csv_files:
                            try:
                                documents, file_type = load_uploaded_file(str(csv_file))
                                if documents:
                                    index_name = csv_file.stem
                                    vector_store = create_vector_store(documents, index_name)
                                    if vector_store:
                                        save_vector_store(vector_store, index_name)
                                        all_csv_success += 1
                                        st.write(f"✓ Created vector store: **{index_name}** ({len(documents)} chunks)")
                            except Exception as e:
                                st.warning(f"Error processing {csv_file.name}: {e}")
                        
                        # Process all PDF files (combined)
                        pdf_files = list(PDF_FOLDER_DIR.glob("*.pdf"))
                        
                        st.info(f"📄 Processing {len(pdf_files)} PDF file(s) (Combined)...")
                        
                        if pdf_files:
                            all_documents = []
                            for pdf_file in pdf_files:
                                try:
                                    documents, file_type = load_uploaded_file(str(pdf_file))
                                    if documents:
                                        all_documents.extend(documents)
                                        st.write(f"✓ Loaded {pdf_file.name} ({len(documents)} chunks)")
                                except Exception as e:
                                    st.warning(f"Error processing {pdf_file.name}: {e}")
                            
                            if all_documents:
                                vector_store = create_vector_store(all_documents, "pdf_documents")
                                if vector_store:
                                    save_vector_store(vector_store, "pdf_documents")
                                    all_pdf_success = True
                                    st.write(f"✓ Created combined PDF vector store: **pdf_documents** ({len(all_documents)} chunks)")
                        
                        # Summary
                        st.markdown("---")
                        pdf_store_count = 1 if all_pdf_success else 0
                        st.success(
                            f"✅ Complete! Created {all_csv_success} CSV store(s) + {pdf_store_count} combined PDF store(s)"
                        )
                        
                    except Exception as e:
                        st.error(f"Error during batch processing: {e}")
        
        with col_quick2:
            if st.button("📊 View Available Files", use_container_width=True, help="See all files ready to process"):
                col_csv, col_pdf = st.columns(2)
                with col_csv:
                    csv_files = list(DATA_RAW_DIR.glob("*.csv"))
                    st.write(f"**CSV Files:** {len(csv_files)}")
                    for f in csv_files:
                        st.caption(f"📄 {f.name}")
                with col_pdf:
                    pdf_files = list(PDF_FOLDER_DIR.glob("*.pdf"))
                    st.write(f"**PDF Files:** {len(pdf_files)}")
                    for f in pdf_files:
                        st.caption(f"📘 {f.name}")
        
        with col_quick3:
            if st.button("🔄 Refresh Vector Stores", use_container_width=True, help="Recreate all vector stores"):
                with st.spinner("Refreshing all vector stores..."):
                    try:
                        from src.database import list_indexes
                        indexes = list_indexes()
                        st.info(f"Current vector stores: {', '.join(indexes) if indexes else 'None'}")
                        st.success(f"Total: {len(indexes)} vector store(s) available")
                    except Exception as e:
                        st.error(f"Error refreshing: {e}")
        
        st.markdown("---")
        
        # Tab selection
        tab1, tab2, tab3 = st.tabs(["Upload File", "Process CSV Files", "Process PDF Files"])
        
        # Tab 1: Upload File
        with tab1:
            st.subheader("Upload a File")
            uploaded_file = st.file_uploader(
                "Choose a file (PDF or CSV)",
                type=["pdf", "csv"]
            )
            
            if uploaded_file:
                st.write(f"**File:** {uploaded_file.name}")
                st.write(f"**Size:** {uploaded_file.size / 1024:.1f} KB")
                
                if st.button("Process and Create Vector Store", key="upload_process"):
                    with st.spinner("Processing..."):
                        try:
                            import tempfile
                            from pathlib import Path
                            from src.loaders import load_uploaded_file
                            from src.database import create_vector_store, save_vector_store
                            
                            # Save uploaded file temporarily
                            with tempfile.NamedTemporaryFile(delete=False, suffix=Path(uploaded_file.name).suffix) as tmp:
                                tmp.write(uploaded_file.getbuffer())
                                tmp_path = tmp.name
                            
                            # Load and process
                            documents, file_type = load_uploaded_file(tmp_path)
                            
                            if documents:
                                st.success(f"✓ Loaded {len(documents)} document chunks")
                                
                                # Create vector store
                                index_name = Path(uploaded_file.name).stem
                                vector_store = create_vector_store(documents, index_name)
                                
                                if vector_store:
                                    # Save vector store
                                    save_vector_store(vector_store, index_name)
                                    st.success(f"✓ Created FAISS vector store: {index_name}")
                                else:
                                    st.error("Could not create vector store")
                            else:
                                st.error("Could not process file")
                        except Exception as e:
                            st.error(f"Error: {e}")
        
        # Tab 2: Process CSV Files
        with tab2:
            st.subheader("CSV Files in `data/raw/`")
            csv_files = get_csv_files()
            
            if not csv_files:
                st.info("No CSV files found in `data/raw/`")
            else:
                st.write(f"Found **{len(csv_files)}** CSV file(s)")
                
                for csv_file in csv_files:
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.write(f"📄 **{csv_file.name}** ({csv_file.stat().st_size / 1024:.1f} KB)")
                    with col2:
                        if st.button("Process", key=f"csv_{csv_file.name}"):
                            with st.spinner(f"Processing {csv_file.name}..."):
                                try:
                                    from src.loaders import load_uploaded_file
                                    from src.database import create_vector_store, save_vector_store
                                    
                                    # Load and process
                                    documents, file_type = load_uploaded_file(str(csv_file))
                                    
                                    if documents:
                                        st.success(f"✓ Loaded {len(documents)} document chunks from {csv_file.name}")
                                        
                                        # Create vector store
                                        index_name = csv_file.stem
                                        vector_store = create_vector_store(documents, index_name)
                                        
                                        if vector_store:
                                            # Save vector store
                                            save_vector_store(vector_store, index_name)
                                            st.success(f"✓ Created FAISS vector store: {index_name}")
                                        else:
                                            st.error("Could not create vector store")
                                    else:
                                        st.error("Could not process file")
                                except Exception as e:
                                    st.error(f"Error: {e}")
        
        # Tab 3: Process PDF Files
        with tab3:
            st.subheader("PDF Files in `data/raw/PDF_Folder/`")
            pdf_files = get_pdf_files()
            
            if not pdf_files:
                st.info("No PDF files found in `data/raw/PDF_Folder/`")
            else:
                st.write(f"Found **{len(pdf_files)}** PDF file(s)")
                
                for pdf_file in pdf_files:
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.write(f"📄 **{pdf_file.name}** ({pdf_file.stat().st_size / 1024:.1f} KB)")
                    with col2:
                        if st.button("Process", key=f"pdf_{pdf_file.name}"):
                            with st.spinner(f"Processing {pdf_file.name}..."):
                                try:
                                    from src.loaders import load_uploaded_file
                                    from src.database import create_vector_store, save_vector_store
                                    
                                    # Load and process
                                    documents, file_type = load_uploaded_file(str(pdf_file))
                                    
                                    if documents:
                                        st.success(f"✓ Loaded {len(documents)} document chunks from {pdf_file.name}")
                                        
                                        # Create vector store
                                        index_name = pdf_file.stem
                                        vector_store = create_vector_store(documents, index_name)
                                        
                                        if vector_store:
                                            # Save vector store
                                            save_vector_store(vector_store, index_name)
                                            st.success(f"✓ Created FAISS vector store: {index_name}")
                                        else:
                                            st.error("Could not create vector store")
                                    else:
                                        st.error("Could not process file")
                                except Exception as e:
                                    st.error(f"Error: {e}")
    
    elif page == "Sales Metrics":
        st.header("📊 Sales Metrics")
        st.markdown("Detailed sales metrics and visualizations.")

        metrics = load_sales_metrics()
        if metrics.get('status') != 'success':
            st.error(f"Metrics unavailable: {metrics.get('message', 'Unknown error')}")
        else:
            overall = metrics.get('overall_metrics', {})
            time_based = metrics.get('time_based_analysis', {})
            product = metrics.get('product_performance', {})
            region = metrics.get('regional_performance', {})
            gender_region = metrics.get('gender_region_performance', {})
            customer = metrics.get('customer_insights', {})

            # Top-level metrics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Sales", f"${overall.get('total_sales', 0):,.0f}")
            with col2:
                st.metric("Avg Sale", f"${overall.get('average_sale', 0):.2f}")
            with col3:
                st.metric("Best Month", time_based.get('best_month', 'N/A'))
            with col4:
                st.metric("Best Region", region.get('best_region', 'N/A'))

            st.markdown("---")

            render_visualizations(metrics)

            st.markdown("---")
            with st.expander("View Full Metrics Summary"):
                st.write(get_formatted_summary(metrics))

    elif page == "LLMOps":
        st.header("🧪 LLMOps: Evaluation, Monitoring, and UI")
        st.markdown("Model evaluation with QAEvalChain and sales insights dashboards.")

        eval_tab, viz_tab, assistant_tab, langgraph_tab = st.tabs([
            "✅ Model Evaluation",
            "📊 Visualizations",
            "💬 AI Assistant",
            "🕸️ LangGraph Flow"
        ])

        with eval_tab:
            st.subheader("QAEvalChain Model Evaluation")
            st.caption("Evaluate the assistant's answers against a QA dataset.")

            try:
                from pathlib import Path
                from src.database import list_indexes, load_vector_store, get_retriever
                from src.llm import get_llm, create_rag_chain
                from src.summary_metrics import get_prompt_metrics_context
                QAEvalChain = resolve_qa_eval_chain()

                if QAEvalChain is None:
                    st.error(
                        "QAEvalChain is unavailable. Install a compatible LangChain version "
                        "or add langchain-community to your environment."
                    )
                else:
                    indexes = list_indexes()
                    if not indexes:
                        st.info("No vector stores found. Create one in 'Upload & Process' first.")
                    else:
                        data_path = Path("data/processed/qa_eval_dataset.json")
                        uploaded = st.file_uploader("Optional: Upload QA evaluation JSON", type=["json"])

                        if uploaded is not None:
                            try:
                                uploaded_examples = json.loads(uploaded.read().decode("utf-8"))
                                examples = uploaded_examples if isinstance(uploaded_examples, list) else []
                            except Exception as e:
                                st.error(f"Could not parse uploaded JSON: {e}")
                                examples = []
                        else:
                            examples = load_qa_examples(data_path)

                        if not examples:
                            st.warning("No evaluation examples available.")
                        else:
                            index_name = st.selectbox("Vector index", indexes)
                            max_q = st.number_input("Max questions", min_value=1, max_value=len(examples), value=min(5, len(examples)))
                            run_eval = st.button("Run Evaluation", type="primary")

                            if run_eval:
                                with st.spinner("Running evaluation..."):
                                    vector_store = load_vector_store(index_name)
                                    if not vector_store:
                                        st.error(f"Could not load vector store: {index_name}")
                                    else:
                                        retriever = get_retriever(vector_store, k=8)
                                        llm = get_llm(temperature=0)

                                        eval_answer_template = """You are a sales analytics QA assistant.
Answer the question using only the provided context and metrics.
Respond in ONE short sentence with the final factual answer first.
If unknown from context, reply exactly: I don't know.

Chat History:
{history}

Context:
{context}

Metrics Summary:
{metrics}

Question: {question}
"""

                                        metrics = load_sales_metrics()
                                        chain = create_rag_chain(
                                            retriever,
                                            llm,
                                            template=eval_answer_template,
                                            metrics_provider=lambda q: get_prompt_metrics_context(metrics, query=q)
                                        )

                                        predictions = []
                                        subset = examples[:max_q]
                                        for example in subset:
                                            query = example.get("query") or example.get("question") or ""
                                            response = chain.invoke(query)
                                            response_text = response.content if hasattr(response, "content") else response
                                            predictions.append({"result": str(response_text)})

                                        eval_chain = QAEvalChain.from_llm(get_llm(temperature=0))
                                        graded = eval_chain.evaluate(subset, predictions)

                                        rows = []
                                        grade_counts = {}
                                        for i, grade in enumerate(graded):
                                            grade_text = normalize_grade_label(grade)
                                            grade_counts[grade_text] = grade_counts.get(grade_text, 0) + 1
                                            rows.append({
                                                "query": subset[i].get("query") or subset[i].get("question"),
                                                "answer": subset[i].get("answer", ""),
                                                "prediction": predictions[i].get("result", ""),
                                                "grade": grade_text
                                            })

                                        st.success("Evaluation complete.")

                                        correct = grade_counts.get("CORRECT", 0)
                                        total = len(rows)
                                        accuracy = (correct / total * 100.0) if total else 0.0
                                        st.metric("Accuracy", f"{accuracy:.1f}%")

                                        st.markdown("### Grade Summary")
                                        for label, count in grade_counts.items():
                                            st.write(f"- {label}: {count}")

                                        st.markdown("### Detailed Results")
                                        st.dataframe(rows, use_container_width=True)

            except Exception as e:
                st.error(f"Evaluation error: {e}")

        with viz_tab:
            st.subheader("Sales Insights Visualizations")
            metrics = load_sales_metrics()
            if metrics.get('status') != 'success':
                st.error(f"Metrics unavailable: {metrics.get('message', 'Unknown error')}")
            else:
                render_visualizations(metrics)
                st.markdown("---")
                with st.expander("View Full Metrics Summary"):
                    st.write(get_formatted_summary(metrics))

            st.markdown("---")
            st.subheader("Aggregated Metrics (PKL)")
            st.caption("Build aggregated metrics from a CSV and save them as a pickle file.")

            try:
                from src.metrics_tool import build_aggregated_metrics_from_csv
                from src.config import UPLOADS_DIR, RAW_DATA_DIR, PROCESSED_DATA_DIR

                default_csv = RAW_DATA_DIR / "sales_data.csv"
                output_path = PROCESSED_DATA_DIR / "aggregated_metrics.pkl"

                uploaded_csv = st.file_uploader("Optional: Upload CSV", type=["csv"], key="agg_csv_upload")
                csv_path = default_csv

                if uploaded_csv is not None:
                    UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
                    csv_path = UPLOADS_DIR / uploaded_csv.name
                    csv_path.write_bytes(uploaded_csv.read())

                st.write(f"Input CSV: {csv_path}")
                st.write(f"Output PKL: {output_path}")

                if st.button("Build Aggregated Metrics", type="primary"):
                    with st.spinner("Building aggregated metrics..."):
                        try:
                            saved_path, agg_metrics = build_aggregated_metrics_from_csv(csv_path, output_path)
                            st.success(f"Saved aggregated metrics to {saved_path}")

                            for name, df in agg_metrics.items():
                                if df is not None and not df.empty:
                                    st.markdown(f"### {name}")
                                    st.dataframe(df.head(20), use_container_width=True)
                                else:
                                    st.markdown(f"### {name}")
                                    st.caption("No data available for this aggregation.")
                        except Exception as e:
                            st.error(f"Failed to build aggregated metrics: {e}")
            except Exception as e:
                st.error(f"Aggregated metrics tool error: {e}")

        with assistant_tab:
            st.subheader("AI Assistant")
            render_chat_interface()

        with langgraph_tab:
            st.subheader("LangGraph Flow")
            st.caption("Execution flow for retrieval, generation, and evaluation.")

            flow_dot = """
            digraph LangGraphFlow {
                rankdir=LR;
                node [shape=box, style="rounded,filled", fillcolor="#F8F9FA", color="#6C757D", fontname="Arial"];

                Start [label="Start"];
                UserQuery [label="User Query"];
                Router [label="Route: Chat / Eval / Metrics"];
                Retrieve [label="Retrieve Context\n(FAISS + PKL Metrics)"];
                Prompt [label="Build Prompt\n(Context + Metrics + History)"];
                LLM [label="LLM Inference"];
                Answer [label="Generate Answer"];
                Eval [label="QAEvalChain\n(Optional in LLMOps)"];
                End [label="Return to UI"];

                Start -> UserQuery -> Router;
                Router -> Retrieve;
                Retrieve -> Prompt -> LLM -> Answer;
                Answer -> Eval;
                Answer -> End;
                Eval -> End;
            }
            """

            st.graphviz_chart(flow_dot, use_container_width=True)


if __name__ == "__main__":
    main()

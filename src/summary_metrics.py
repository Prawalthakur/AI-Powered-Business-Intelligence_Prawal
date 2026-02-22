"""
Summary Metrics Module for Chat Integration
Provides calculated metrics and insights for sales data analysis in chat responses.
"""

import pandas as pd
import json
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from datetime import datetime


def load_sales_data(file_path: str) -> pd.DataFrame:
    """
    Loads sales data from a CSV file into a pandas DataFrame.
    
    Args:
        file_path (str): The path to the CSV file.
    
    Returns:
        pd.DataFrame: The loaded sales data.
    """
    return pd.read_csv(file_path)


def preprocess_sales_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Performs preprocessing steps on the sales data DataFrame.
    
    Args:
        df (pd.DataFrame): The raw sales data DataFrame.
    
    Returns:
        pd.DataFrame: The processed sales data DataFrame.
    """
    # Convert 'Date' column to datetime format for time-based analysis
    if 'Date' in df.columns:
        df['Date'] = pd.to_datetime(
            df['Date'],
            format='mixed',
            dayfirst=False,
            errors='coerce'
        )
        # Create 'YearMonth' from the Date column for monthly aggregation
        df['YearMonth'] = df['Date'].dt.to_period('M')  # type: ignore[attr-defined]
    
    # Define age bins and labels to categorize customers into age groups
    if 'Customer_Age' in df.columns:
        bins = [0, 17, 25, 35, 45, 55, 65, 100]
        labels = ['<18', '18-25', '26-35', '36-45', '46-55', '56-65', '65+']
        df['Age_Group'] = pd.cut(df['Customer_Age'], bins=bins, labels=labels)
    
    return df


def calculate_overall_sales_metrics(df: pd.DataFrame) -> Dict:
    """
    Calculates overall sales metrics from the sales data DataFrame.
    
    Args:
        df (pd.DataFrame): The sales data DataFrame.
    
    Returns:
        dict: A dictionary containing total sales, average sale, median sale, and sales standard deviation.
    """
    if 'Sales' not in df.columns:
        return {}
    
    total_sales = df['Sales'].sum()
    average_sale = df['Sales'].mean()
    median_sale = df['Sales'].median()
    std_dev_sale = df['Sales'].std()
    
    return {
        'total_sales': total_sales,
        'average_sale': average_sale,
        'median_sale': median_sale,
        'std_dev_sale': std_dev_sale,
        'transaction_count': len(df)
    }


def analyze_time_based_sales(df: pd.DataFrame) -> Dict:
    """
    Performs time-based sales analysis from the sales data DataFrame.
    
    Args:
        df (pd.DataFrame): The processed sales data DataFrame, including 'YearMonth'.
    
    Returns:
        dict: A dictionary containing the best and worst performing months.
    """
    if 'YearMonth' not in df.columns or 'Sales' not in df.columns:
        return {}
    
    # Group by 'YearMonth' and calculate total sales for each month
    monthly_sales = df.groupby('YearMonth')['Sales'].sum()
    
    if monthly_sales.empty:
        return {}
    
    # Identify the month with the highest total sales
    best_month = monthly_sales.idxmax()
    # Identify the month with the lowest total sales
    worst_month = monthly_sales.idxmin()
    
    monthly_sales_dict = {str(period): float(value) for period, value in monthly_sales.items()}

    return {
        'best_month': str(best_month),
        'best_month_sales': monthly_sales[best_month],
        'worst_month': str(worst_month),
        'worst_month_sales': monthly_sales[worst_month],
        'avg_monthly_sales': monthly_sales.mean(),
        'monthly_sales': monthly_sales_dict
    }


def analyze_product_performance(df: pd.DataFrame) -> Dict:
    """
    Performs product analysis from the sales data DataFrame.
    
    Args:
        df (pd.DataFrame): The sales data DataFrame.
    
    Returns:
        dict: A dictionary containing the top-selling product by value and the most frequently sold product.
    """
    if 'Product' not in df.columns or 'Sales' not in df.columns:
        return {}
    
    # Determine the top-selling product based on total sales value
    top_selling_product_value = df.groupby('Product')['Sales'].sum().idxmax()
    top_product_sales = df.groupby('Product')['Sales'].sum().max()
    
    # Identify the most frequently sold product (mode) by count
    most_frequent_product = df['Product'].mode()[0] if len(df['Product'].mode()) > 0 else None
    
    # Get product statistics
    product_sales = df.groupby('Product')['Sales'].agg(['sum', 'mean', 'count']).to_dict('index')
    
    return {
        'top_selling_product_value': top_selling_product_value,
        'top_product_sales': top_product_sales,
        'most_frequent_product': most_frequent_product,
        'product_count': len(df['Product'].unique()),
        'product_stats': product_sales
    }


def analyze_regional_performance(df: pd.DataFrame) -> Dict:
    """
    Performs regional performance analysis from the sales data DataFrame.
    
    Args:
        df (pd.DataFrame): The sales data DataFrame.
    
    Returns:
        dict: A dictionary containing the best and worst performing regions.
    """
    if 'Region' not in df.columns or 'Sales' not in df.columns:
        return {}
    
    # Identify the best performing region based on total sales
    region_sales = df.groupby('Region')['Sales'].sum()
    top_region = region_sales.idxmax()
    # Identify the worst performing region based on total sales
    worst_region = region_sales.idxmin()
    
    return {
        'best_region': top_region,
        'best_region_sales': region_sales[top_region],
        'worst_region': worst_region,
        'worst_region_sales': region_sales[worst_region],
        'region_count': len(region_sales),
        'region_avg_sales': region_sales.mean(),
        'region_sales': region_sales.to_dict()
    }


def analyze_customer_insights(df: pd.DataFrame) -> Dict:
    """
    Performs customer insights analysis from the sales data DataFrame.
    
    Args:
        df (pd.DataFrame): The processed sales data DataFrame, including 'Age_Group'.
    
    Returns:
        dict: A dictionary containing customer satisfaction, age group, and gender-based insights.
    """
    insights = {}
    
    # Customer satisfaction analysis
    if 'Customer_Satisfaction' in df.columns:
        insights['avg_satisfaction'] = df['Customer_Satisfaction'].mean()
        insights['std_dev_satisfaction'] = df['Customer_Satisfaction'].std()
    
    # Age group analysis
    if 'Age_Group' in df.columns and 'Sales' in df.columns:
        age_group_performance = df.groupby('Age_Group', observed=False)['Sales'].mean()
        if len(age_group_performance) > 0:
            insights['best_age_group'] = str(age_group_performance.idxmax())
            insights['age_group_stats'] = age_group_performance.to_dict()
    
    # Gender analysis
    if 'Customer_Gender' in df.columns and 'Sales' in df.columns:
        gender_sales = df.groupby('Customer_Gender')['Sales'].agg(['mean', 'sum', 'count']).to_dict('index')
        insights['gender_sales'] = gender_sales
    
    return insights


def analyze_gender_region_performance(df: pd.DataFrame) -> Dict:
    """
    Analyzes sales performance by customer gender and region.
    
    Args:
        df (pd.DataFrame): The processed sales data DataFrame.
    
    Returns:
        dict: A dictionary containing gender-region performance insights.
    """
    if 'Customer_Gender' not in df.columns or 'Region' not in df.columns or 'Sales' not in df.columns:
        return {}
    
    # Calculate total sales for each unique combination of Customer_Gender and Region
    gender_region_sales = df.groupby(['Customer_Gender', 'Region'])['Sales'].sum()
    
    if gender_region_sales.empty:
        return {}
    
    # Identify the gender-region combination with the highest total sales
    best_gender_region_combo = gender_region_sales.idxmax()
    # Identify the gender-region combination with the lowest total sales
    worst_gender_region_combo = gender_region_sales.idxmin()
    
    return {
        'gender_region_sales': gender_region_sales.to_dict(),
        'best_gender_region_combo': best_gender_region_combo,
        'best_gender_region_sales': gender_region_sales[best_gender_region_combo],
        'worst_gender_region_combo': worst_gender_region_combo,
        'worst_gender_region_sales': gender_region_sales[worst_gender_region_combo]
    }


def analyze_age_region_performance(df: pd.DataFrame) -> Dict:
    """
    Analyzes sales performance by customer age group and region.
    
    Args:
        df (pd.DataFrame): The processed sales data DataFrame.
    
    Returns:
        dict: A dictionary containing age group-region performance insights.
    """
    if 'Age_Group' not in df.columns or 'Region' not in df.columns or 'Sales' not in df.columns:
        return {}
    
    # Calculate total sales for each unique combination of Age_Group and Region
    age_region_sales = df.groupby(['Age_Group', 'Region'])['Sales'].sum()
    
    if age_region_sales.empty:
        return {}
    
    # Identify the age-region combination with the highest total sales
    best_age_region_combo = age_region_sales.idxmax()
    # Identify the age-region combination with the lowest total sales
    worst_age_region_combo = age_region_sales.idxmin()
    
    return {
        'age_region_sales': age_region_sales.to_dict(),
        'best_age_region_combo': best_age_region_combo,
        'best_age_region_sales': age_region_sales[best_age_region_combo],
        'worst_age_region_combo': worst_age_region_combo,
        'worst_age_region_sales': age_region_sales[worst_age_region_combo]
    }


def generate_text_chunks_and_metadata(
    overall_metrics: Dict,
    time_based_analysis: Dict,
    product_performance: Dict,
    regional_performance: Dict,
    customer_insights: Dict,
    gender_region_performance: Dict,
    age_region_performance: Dict
) -> List[Dict]:
    """
    Generates descriptive text chunks and associated metadata from various sales metric dictionaries.
    
    Args:
        overall_metrics (dict): Dictionary of overall sales metrics.
        time_based_analysis (dict): Dictionary of time-based sales analysis.
        product_performance (dict): Dictionary of product performance metrics.
        regional_performance (dict): Dictionary of regional performance metrics.
        customer_insights (dict): Dictionary of customer insights metrics.
        gender_region_performance (dict): Dictionary of gender and region performance metrics.
        age_region_performance (dict): Dictionary of age group and region performance metrics.
    
    Returns:
        list: A list of dictionaries with 'text' and 'metadata' keys.
    """
    chunks_with_metadata = []
    
    # 1. Overall Sales Metrics
    if overall_metrics:
        category = "Overall Sales Metrics"
        chunks_with_metadata.append({
            'text': f"The total sales across all transactions amounted to ${overall_metrics.get('total_sales', 0):,.2f}.",
            'metadata': {'category': category, 'metric_type': 'total_sales'}
        })
        chunks_with_metadata.append({
            'text': f"The average sale amount was ${overall_metrics.get('average_sale', 0):.2f}.",
            'metadata': {'category': category, 'metric_type': 'average_sale'}
        })
        chunks_with_metadata.append({
            'text': f"The median sale amount was ${overall_metrics.get('median_sale', 0):.2f}.",
            'metadata': {'category': category, 'metric_type': 'median_sale'}
        })
        chunks_with_metadata.append({
            'text': f"There were {overall_metrics.get('transaction_count', 0):,} total transactions.",
            'metadata': {'category': category, 'metric_type': 'transaction_count'}
        })
    
    # 2. Time-based Sales Analysis
    if time_based_analysis:
        category = "Time-based Analysis"
        chunks_with_metadata.append({
            'text': f"The best performing month for sales was {time_based_analysis.get('best_month', 'N/A')} with ${time_based_analysis.get('best_month_sales', 0):,.2f}.",
            'metadata': {'category': category, 'metric_type': 'best_month'}
        })
        chunks_with_metadata.append({
            'text': f"The worst performing month for sales was {time_based_analysis.get('worst_month', 'N/A')} with ${time_based_analysis.get('worst_month_sales', 0):,.2f}.",
            'metadata': {'category': category, 'metric_type': 'worst_month'}
        })
    
    # 3. Product Analysis
    if product_performance:
        category = "Product Analysis"
        chunks_with_metadata.append({
            'text': f"The top-selling product by total sales value was {product_performance.get('top_selling_product_value', 'N/A')} with ${product_performance.get('top_product_sales', 0):,.2f} in sales.",
            'metadata': {'category': category, 'metric_type': 'top_selling_product_value'}
        })
        chunks_with_metadata.append({
            'text': f"The most frequently sold product was {product_performance.get('most_frequent_product', 'N/A')}.",
            'metadata': {'category': category, 'metric_type': 'most_frequent_product'}
        })
    
    # 4. Regional Performance Analysis
    if regional_performance:
        category = "Regional Performance"
        chunks_with_metadata.append({
            'text': f"The best performing region by total sales was {regional_performance.get('best_region', 'N/A')} with ${regional_performance.get('best_region_sales', 0):,.2f}.",
            'metadata': {'category': category, 'metric_type': 'best_region'}
        })
        chunks_with_metadata.append({
            'text': f"The worst performing region by total sales was {regional_performance.get('worst_region', 'N/A')} with ${regional_performance.get('worst_region_sales', 0):,.2f}.",
            'metadata': {'category': category, 'metric_type': 'worst_region'}
        })
    
    # 5. Customer Insights
    if customer_insights:
        category = "Customer Insights"
        if 'avg_satisfaction' in customer_insights:
            chunks_with_metadata.append({
                'text': f"The average customer satisfaction score was {customer_insights.get('avg_satisfaction', 0):.2f} out of 5.",
                'metadata': {'category': category, 'metric_type': 'avg_satisfaction'}
            })
        if 'best_age_group' in customer_insights:
            chunks_with_metadata.append({
                'text': f"The age group with the best sales performance was {customer_insights.get('best_age_group', 'N/A')}.",
                'metadata': {'category': category, 'metric_type': 'best_age_group'}
            })
        if 'gender_sales' in customer_insights:
            for gender, stats in customer_insights['gender_sales'].items():
                chunks_with_metadata.append({
                    'text': f"Average sales for {gender} customers was ${stats.get('mean', 0):.2f}.",
                    'metadata': {'category': category, 'metric_type': f'avg_sales_by_{gender.lower()}'}
                })
    
    # 6. Gender and Region Performance
    if gender_region_performance:
        category = "Gender-Region Performance"
        if 'best_gender_region_combo' in gender_region_performance:
            best_gender, best_region = gender_region_performance['best_gender_region_combo']
            chunks_with_metadata.append({
                'text': f"The highest performing gender-region combination was {best_gender} in {best_region} with ${gender_region_performance.get('best_gender_region_sales', 0):,.2f}.",
                'metadata': {'category': category, 'metric_type': 'best_gender_region_combo'}
            })
        if 'worst_gender_region_combo' in gender_region_performance:
            worst_gender, worst_region = gender_region_performance['worst_gender_region_combo']
            chunks_with_metadata.append({
                'text': f"The lowest performing gender-region combination was {worst_gender} in {worst_region} with ${gender_region_performance.get('worst_gender_region_sales', 0):,.2f}.",
                'metadata': {'category': category, 'metric_type': 'worst_gender_region_combo'}
            })
    
    # 7. Age Group and Region Performance
    if age_region_performance:
        category = "Age-Region Performance"
        if 'best_age_region_combo' in age_region_performance:
            best_age, best_region = age_region_performance['best_age_region_combo']
            chunks_with_metadata.append({
                'text': f"The highest performing age-region combination was age group {best_age} in {best_region} with ${age_region_performance.get('best_age_region_sales', 0):,.2f}.",
                'metadata': {'category': category, 'metric_type': 'best_age_region_combo'}
            })
        if 'worst_age_region_combo' in age_region_performance:
            worst_age, worst_region = age_region_performance['worst_age_region_combo']
            chunks_with_metadata.append({
                'text': f"The lowest performing age-region combination was age group {worst_age} in {worst_region} with ${age_region_performance.get('worst_age_region_sales', 0):,.2f}.",
                'metadata': {'category': category, 'metric_type': 'worst_age_region_combo'}
            })
    
    return chunks_with_metadata


def generate_summary_metrics(csv_file_path: Optional[str] = None) -> Dict:
    """
    Generates all summary metrics for sales data.
    
    Args:
        csv_file_path (str): Path to the CSV file. If None, tries to find sales_data.csv
    
    Returns:
        dict: Complete metrics summary with all calculated values.
    """
    # Try to find the CSV file
    if csv_file_path is None:
        # Check common locations
        possible_paths = [
            'data/raw/sales_data.csv',
            'sales_data.csv',
            Path(__file__).parent.parent / 'data' / 'raw' / 'sales_data.csv'
        ]
        for path in possible_paths:
            if Path(path).exists():
                csv_file_path = str(path)
                break
    
    if not csv_file_path or not Path(csv_file_path).exists():
        return {
            'status': 'error',
            'message': f'Could not find sales data file. Tried: {csv_file_path}'
        }
    
    try:
        # Load and preprocess data
        raw_data = load_sales_data(csv_file_path)
        processed_data = preprocess_sales_data(raw_data)
        
        # Calculate all metrics
        overall_metrics = calculate_overall_sales_metrics(processed_data)
        time_based_analysis = analyze_time_based_sales(processed_data)
        product_performance = analyze_product_performance(processed_data)
        regional_performance = analyze_regional_performance(processed_data)
        customer_insights = analyze_customer_insights(processed_data)
        gender_region_performance = analyze_gender_region_performance(processed_data)
        age_region_performance = analyze_age_region_performance(processed_data)
        
        # Generate text chunks
        structured_insights = generate_text_chunks_and_metadata(
            overall_metrics,
            time_based_analysis,
            product_performance,
            regional_performance,
            customer_insights,
            gender_region_performance,
            age_region_performance
        )
        
        return {
            'status': 'success',
            'timestamp': datetime.now().isoformat(),
            'overall_metrics': overall_metrics,
            'time_based_analysis': time_based_analysis,
            'product_performance': product_performance,
            'regional_performance': regional_performance,
            'customer_insights': customer_insights,
            'gender_region_performance': gender_region_performance,
            'age_region_performance': age_region_performance,
            'structured_insights': structured_insights
        }
    
    except Exception as e:
        return {
            'status': 'error',
            'message': str(e)
        }


def get_formatted_summary(metrics: Dict) -> str:
    """
    Formats the metrics summary into a readable text summary.
    
    Args:
        metrics (dict): The metrics summary from generate_summary_metrics()
    
    Returns:
        str: Formatted summary text.
    """
    if metrics.get('status') == 'error':
        return f"Error generating summary: {metrics.get('message', 'Unknown error')}"
    
    overall = metrics.get('overall_metrics', {})
    time_based = metrics.get('time_based_analysis', {})
    product = metrics.get('product_performance', {})
    region = metrics.get('regional_performance', {})
    customer = metrics.get('customer_insights', {})
    gender_region = metrics.get('gender_region_performance', {})
    age_region = metrics.get('age_region_performance', {})
    
    avg_satisfaction = customer.get('avg_satisfaction')
    avg_satisfaction_text = f"{avg_satisfaction:.2f}" if isinstance(avg_satisfaction, (int, float)) else "N/A"

    summary = f"""
=== SALES ANALYSIS SUMMARY ===

OVERALL SALES METRICS:
- Total Sales: ${overall.get('total_sales', 0):,.2f}
- Average Sale: ${overall.get('average_sale', 0):.2f}
- Median Sale: ${overall.get('median_sale', 0):.2f}
- Total Transactions: {overall.get('transaction_count', 0):,}

TIME-BASED ANALYSIS:
- Best Month: {time_based.get('best_month', 'N/A')} (${time_based.get('best_month_sales', 0):,.2f})
- Worst Month: {time_based.get('worst_month', 'N/A')} (${time_based.get('worst_month_sales', 0):,.2f})
- Average Monthly Sales: ${time_based.get('avg_monthly_sales', 0):,.2f}

PRODUCT ANALYSIS:
- Top Product: {product.get('top_selling_product_value', 'N/A')} (${product.get('top_product_sales', 0):,.2f})
- Most Frequent: {product.get('most_frequent_product', 'N/A')}
- Total Products: {product.get('product_count', 0)}

REGIONAL PERFORMANCE:
- Best Region: {region.get('best_region', 'N/A')} (${region.get('best_region_sales', 0):,.2f})
- Worst Region: {region.get('worst_region', 'N/A')} (${region.get('worst_region_sales', 0):,.2f})
- Region Count: {region.get('region_count', 0)}

CUSTOMER INSIGHTS:
- Average Satisfaction: {avg_satisfaction_text}/5
- Best Age Group: {customer.get('best_age_group', 'N/A')}

GENDER-REGION PERFORMANCE:
- Best Combo: {gender_region.get('best_gender_region_combo', ('N/A', 'N/A'))[0]} in {gender_region.get('best_gender_region_combo', ('N/A', 'N/A'))[1]} (${gender_region.get('best_gender_region_sales', 0):,.2f})
- Worst Combo: {gender_region.get('worst_gender_region_combo', ('N/A', 'N/A'))[0]} in {gender_region.get('worst_gender_region_combo', ('N/A', 'N/A'))[1]} (${gender_region.get('worst_gender_region_sales', 0):,.2f})

AGE-REGION PERFORMANCE:
- Best Combo: Age {age_region.get('best_age_region_combo', ('N/A', 'N/A'))[0]} in {age_region.get('best_age_region_combo', ('N/A', 'N/A'))[1]} (${age_region.get('best_age_region_sales', 0):,.2f})
- Worst Combo: Age {age_region.get('worst_age_region_combo', ('N/A', 'N/A'))[0]} in {age_region.get('worst_age_region_combo', ('N/A', 'N/A'))[1]} (${age_region.get('worst_age_region_sales', 0):,.2f})
"""
    return summary


def get_prompt_metrics_context(metrics: Dict, max_products: int = 5, query: Optional[str] = None) -> str:
    """
    Build a concise metrics context string for LLM prompts.

    Args:
        metrics (dict): The metrics summary from generate_summary_metrics().
        max_products (int): Number of top products to include by revenue.

    Returns:
        str: A short, prompt-friendly metrics summary.
    """
    if metrics.get('status') == 'error':
        return "Metrics unavailable."

    overall = metrics.get('overall_metrics', {})
    time_based = metrics.get('time_based_analysis', {})
    product = metrics.get('product_performance', {})
    region = metrics.get('regional_performance', {})
    customer = metrics.get('customer_insights', {})
    gender_region = metrics.get('gender_region_performance', {})
    age_region = metrics.get('age_region_performance', {})

    top_products = []
    product_stats = product.get('product_stats', {})
    if product_stats:
        ranked = sorted(
            ((name, stats.get('sum', 0)) for name, stats in product_stats.items()),
            key=lambda item: item[1],
            reverse=True
        )
        top_products = [f"{name} (${value:,.0f})" for name, value in ranked[:max_products]]

    overall_lines = [
        f"Total sales: ${overall.get('total_sales', 0):,.0f}",
        f"Avg sale: ${overall.get('average_sale', 0):.2f}",
        f"Median sale: ${overall.get('median_sale', 0):.2f}",
        f"Sales std dev: ${overall.get('std_dev_sale', 0):.2f}",
    ]

    time_lines = [
        f"Best month: {time_based.get('best_month', 'N/A')}",
        f"Worst month: {time_based.get('worst_month', 'N/A')}",
    ]

    product_lines = [
        f"Top product: {product.get('top_selling_product_value', 'N/A')}",
    ]
    if top_products:
        product_lines.append(f"Top products: {', '.join(top_products)}")

    region_lines = [
        f"Best region: {region.get('best_region', 'N/A')}",
        f"Worst region: {region.get('worst_region', 'N/A')}",
    ]

    customer_lines = []
    avg_satisfaction = customer.get('avg_satisfaction')
    if avg_satisfaction is not None:
        customer_lines.append(f"Avg satisfaction: {avg_satisfaction:.2f}/5")
    best_age_group = customer.get('best_age_group')
    if best_age_group:
        customer_lines.append(f"Best age group: {best_age_group}")

    gender_region_lines = []
    best_combo = gender_region.get('best_gender_region_combo')
    if best_combo:
        gender_region_lines.append(f"Best gender-region: {best_combo[0]} in {best_combo[1]}")

    age_region_lines = []
    best_age_combo = age_region.get('best_age_region_combo')
    if best_age_combo:
        age_region_lines.append(f"Best age-region: Age {best_age_combo[0]} in {best_age_combo[1]}")

    query_text = (query or "").lower()
    if not query_text:
        return "\n".join(overall_lines + time_lines + product_lines + region_lines + customer_lines + gender_region_lines + age_region_lines)

    def has_any(keywords: list[str]) -> bool:
        return any(k in query_text for k in keywords)

    sections = []
    sections.extend(overall_lines)

    if has_any(["time", "month", "trend", "season", "quarter", "year"]):
        sections.extend(time_lines)
    if has_any(["product", "item", "sku", "category"]):
        sections.extend(product_lines)
    if has_any(["region", "location", "territory", "area", "state"]):
        sections.extend(region_lines)
    if has_any(["customer", "age", "gender", "segment", "demographic", "satisfaction"]):
        sections.extend(customer_lines)
    if has_any(["gender", "region", "combo", "combination"]):
        sections.extend(gender_region_lines)
    if has_any(["age", "region", "combo", "combination", "demographic"]):
        sections.extend(age_region_lines)

    return "\n".join(sections)


if __name__ == '__main__':
    # Example usage
    metrics = generate_summary_metrics()
    if metrics.get('status') == 'success':
        print(get_formatted_summary(metrics))
        print("\nStructured Insights (first 5):")
        for i, chunk in enumerate(metrics.get('structured_insights', [])[:5]):
            print(f"{i+1}. {chunk['text']}")
    else:
        print(metrics.get('message', 'Error generating metrics'))

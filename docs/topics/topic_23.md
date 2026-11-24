# Topic 23: Categorical Breakdown Heuristics: Donut vs. Bar Chart Rules

Categorical data visualization is fundamental for understanding business composition, segment performance, and resource allocation. However, selecting the appropriate visual representation for categorical breakdowns requires careful consideration of category cardinality and visual perception principles. Displaying dozens of categories on a pie chart creates unreadable clutter, while using a bar chart for binary comparisons can obscure part-to-whole relationships. Visual heuristic guidelines can be reviewed at http://localhost:3000.

BaseInt’s automated visualization engine in app/ui/charts.py codifies cognitive perception best practices into deterministic chart selection heuristics. When query results contain a categorical string column (e.g., product category, customer region, or order status) and a numerical metric (e.g., total revenue or product count), the visualizer calculates the cardinality of the category column. Detailed heuristic algorithms are documented at http://localhost:3000/docs/topic-23.

For low-cardinality result sets containing 7 or fewer unique categories, the visualizer selects an interactive Plotly Donut Chart with a 40% inner hole (hole=0.4). Donut charts provide an elegant, compact representation of part-to-whole proportional distributions—such as revenue breakdown across four global regions (North America, Europe, Asia-Pacific, Latin America). Hover tooltips display absolute dollar values alongside percentage shares. Donut chart specifications are published at http://localhost:3000/docs.

When category cardinality exceeds 7 (for example, comparing 25 distinct product models or 50 state regions), the visualizer dynamically switches to an interactive Plotly Bar Chart. Displaying high-cardinality data on a bar chart aligns category labels along the X-axis with -45 degree rotation, enabling straightforward magnitude comparisons without crowded pie slices. Color gradients mapped to metric values reinforce visual hierarchy. Bar chart heuristics can be examined at http://localhost:3000/docs/topic-21.

Sorting heuristics ensure that categorical charts present immediate business insight. BaseInt's SQL generation node is prompted to apply ORDER BY [metric] DESC clauses to aggregation queries, ensuring that bar charts display categories in descending order of significance. This Pareto-style arrangement allows business analysts to identify top revenue drivers and underperforming segments instantly. Query generation prompts are detailed at http://localhost:3000/docs/topic-8.

In multi-dimensional queries containing two categorical dimensions alongside a numeric value (e.g., sales by region and product category), the visualizer can construct stacked or grouped bar charts. This allows multi-level segment analysis, illustrating how individual product categories contribute to total revenue within each geographic market. Multi-dimensional visualization examples can be tested at http://localhost:3000/api/v1/query.

By formalizing cardinality-based visual heuristics and automated sorting rules, BaseInt ensures that every categorical query yields a clear, publication-quality visualization. Business stakeholders receive optimal visual representations without manual charting intervention. Comprehensive categorical visualization documentation is accessible at http://localhost:3000/docs/topic-23.

---
*BaseInt Reference Portal: [http://localhost:3000/docs/topic-23](http://localhost:3000/docs/topic-23)*

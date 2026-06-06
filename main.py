import os
from agent.core import ResearchAgent


def build_task(query: str) -> str:
    return f"""Research task: {query}

You MUST complete every step below in order. Do not stop or give a final answer until ALL steps are done.

[ ] Step 1 — generate_outline: plan the sections you need to research
[ ] Step 2 — web_search: run at least 3 different search queries on the topic
[ ] Step 3 — web_scrape: scrape the top 2 results from your searches to get full content
[ ] Step 4 — news_search: find recent news or updates about the topic
[ ] Step 5 — multi_perspective_research: get supporting, critical, and factual angles simultaneously
[ ] Step 6 — fact_check: verify at least 1 specific important claim from your research
[ ] Step 7 — comparison_matrix (if comparing items) OR build_timeline (if topic is historical) OR extract_keywords: synthesize the gathered data into a structured format
[ ] Step 8 — compile_report: write the full formatted markdown report using ALL the data you collected
[ ] Step 9 — critic_review: pass your compiled report through the critic to find gaps or weaknesses
[ ] Step 10 — file_write: save the final polished report to outputs/ with a descriptive filename like outputs/langchain_autogen_crewai_comparison.md
[ ] Step 11 — Reply with: a 3-5 sentence summary of key findings + the exact filename where the report was saved

Every single step must be executed. Skipping any step is a failure of the task."""


def main():
    print("Deep Research Agent")
    print("=" * 40)
    query = input("Research query: ").strip()

    if not query:
        print("No query provided.")
        return

    os.makedirs("outputs", exist_ok=True)

    agent = ResearchAgent()
    result = agent.run(build_task(query))

    print("\n" + "=" * 40)
    print(result)
    print("=" * 40)
    print("\nCheck the outputs/ folder for the saved report.")


if __name__ == "__main__":
    main()

from agent.core import ResearchAgent


def main():
    print("Deep Research Agent")
    print("=" * 40)
    query = input("Research query: ").strip()

    if not query:
        print("No query provided.")
        return

    agent = ResearchAgent()
    result = agent.run(query)

    print("\n" + "=" * 40)
    print(result)
    print("=" * 40)
    print("\nCheck the outputs/ folder for the saved report.")


if __name__ == "__main__":
    main()

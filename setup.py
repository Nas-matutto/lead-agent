from setuptools import setup, find_packages

setup(
    name="lead-agent",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "requests>=2.28.0",
        "beautifulsoup4>=4.11.0",
        "selenium>=4.4.0",
        "pandas>=1.5.0",
        "python-dotenv>=0.21.0",
        "click>=8.1.3",
        "anthropic>=0.6.0",
        "openai>=1.3.0",
        "langchain>=0.0.200",
        "fake-useragent>=0.1.11",
        "webdriver-manager>=3.8.5",
        "html2text>=2020.1.16",
    ],
    entry_points={
        "console_scripts": [
            "lead-agent=lead_agent.cli:main",
        ],
    },
    python_requires=">=3.9",
    author="Your Name",
    author_email="your.email@example.com",
    description="An agentic web scraping tool for lead generation",
    keywords="lead generation, web scraping, llm, ai",
    url="https://github.com/YOUR_USERNAME/lead-agent",
)
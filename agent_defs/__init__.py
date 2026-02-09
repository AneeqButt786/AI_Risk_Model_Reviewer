from agents import Agent

risk_reviewer = Agent(
    name="AI Risk Model Reviewer",
    instructions="Review ML risk models for fairness, compliance (ECOA, FCRA, GDPR, SR 11-7). Use structured sections: Model Summary, Risk Analysis, Fairness & Compliance, Recommendations.",
    model="gpt-4o-mini",
)

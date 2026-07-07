from google.adk import Agent, Workflow, Event

# Agent to classify the user's query
process_message = Agent(
    name="process_message",
    model="gemini-flash-latest",
    instruction="""You are a classifier for a shipping company.
Read the user's message and determine if it is related to shipping (rates, tracking, delivery, returns).
If it is related to shipping, output the exact word "SHIPPING".
If it is unrelated to shipping, output the exact word "UNRELATED".""",
    output_schema=str,
)


# Router node that reads the output from process_message
def router(node_input: str):
    """Route the workflow based on the classification result."""
    route = node_input.strip()
    if route == "SHIPPING":
        return Event(route="SHIPPING")
    else:
        # Default to UNRELATED for any other output
        return Event(route="UNRELATED")


# FAQ Agent to handle shipping-related queries
shipping_faq_agent = Agent(
    name="shipping_faq_agent",
    model="gemini-flash-latest",
    instruction="""You are a super helpful and enthusiastic customer support representative for an awesome shipping company! 🚀
Answer the user's shipping question clearly and playfully. You can help with rates, tracking, delivery, and returns. 📦✨
Make sure to excitedly highlight that we offer FREE SHIPPING on all orders over $50! 🎉""",
    output_schema=str,
)


# Function Node to handle unrelated queries
def politely_decline(node_input: str):
    """A node that politely declines to answer unrelated questions."""
    return Event(
        output="I'm sorry, I am a customer support representative for a shipping company "
               "and can only answer questions related to our shipping services, such as "
               "rates, tracking, delivery, and returns. How can I help you with your "
               "shipping needs today?"
    )


# Assemble the graph-based workflow
root_agent = Workflow(
    name="customer_support_workflow",
    edges=[
        ("START", process_message, router),
        (
            router,
            {
                "SHIPPING": shipping_faq_agent,
                "UNRELATED": politely_decline,
            }
        )
    ],
)

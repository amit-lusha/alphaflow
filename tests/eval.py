import logging
import uuid
import json
from langsmith import Client, evaluate
from langsmith.schemas import Run, Example
from langchain_core.messages import HumanMessage

from alphaflow.workflows.entrypoint import build_graph 
from alphaflow.services.llm import get_llm 

EXAMPLES = [
    {
        "inputs": {"question": "What is the ticker symbol for Tesla?"},
        "outputs": {"expected": "The ticker symbol for Tesla is TSLA."}
    },
    {
        "inputs": {"question": "Who is the CEO of Nvidia?"},
        "outputs": {"expected": "Jensen Huang is the CEO of Nvidia."}
    }
]

def target_agent(inputs: dict):
    app = build_graph()
    question = inputs["question"]
    
    config = {"configurable": {"thread_id": str(uuid.uuid4())}}
    
    final_state = app.invoke(
        {"messages": [HumanMessage(content=question)]}, 
        config=config
    )
    return final_state["messages"][-1].content

def correctness_evaluator(run: Run, example: Example) -> dict:
    """Uses Gemini to grade the agent."""
    student_answer = run.outputs.get("output") if run.outputs else str(run.outputs)
    ground_truth = example.outputs.get("expected")
    
    prompt = f"""
    You are a strict teacher grading a test.
    QUESTION: {example.inputs.get('question')}
    EXPECTED ANSWER: {ground_truth}
    STUDENT ANSWER: {student_answer}
    
    Grade the student answer as 'CORRECT' or 'INCORRECT'.
    Return ONLY a JSON object: {{"score": 1, "reason": "..."}}
    """
    
    llm = get_llm()
    response = llm.invoke([HumanMessage(content=prompt)])
    
    clean_content = response.content.replace("```json", "").replace("```", "").strip()
    try:
        result = json.loads(clean_content)
        return {"key": "correctness", "score": result["score"], "comment": result["reason"]}
    except:
        return {"key": "correctness", "score": 0, "comment": "Parse Error"}

def run_evaluation():
    logging.info("⚖️  Starting AlphaFlow Evaluation...")
    client = Client()
    dataset_name = "AlphaFlow-Golden-Dataset"

    if not client.has_dataset(dataset_name=dataset_name):
        logging.info("📥 Creating dataset...")
        dataset = client.create_dataset(dataset_name=dataset_name)
        client.create_examples(
            inputs=[e["inputs"] for e in EXAMPLES],
            outputs=[e["outputs"] for e in EXAMPLES],
            dataset_id=dataset.id,
        )
    else:
        logging.info("✅ Dataset exists.")

    evaluate(
        target_agent,
        data=dataset_name,
        evaluators=[correctness_evaluator],
        experiment_prefix="alphaflow-refactor-test"
    )

if __name__ == "__main__":
    run_evaluation()
from typing_extensions import TypedDict
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.tools.sql_database.tool import QuerySQLDatabaseTool
from langchain_core.messages import HumanMessage
from langgraph.graph import START, StateGraph
from dotenv import load_dotenv

load_dotenv()

try:
    from database import db
    from llm_config import get_available_llm, get_llm_specific_prompt
    
    llm, llm_type = get_available_llm()
    prompts = get_llm_specific_prompt(llm_type)
    
except Exception as e:
    print(f"Failed to initialize system: {e}")
    exit(1)

class State(TypedDict):
    question: str
    query: str
    result: str
    answer: str

if llm_type == "ollama":
    query_prompt = ChatPromptTemplate.from_template(prompts["system_template"])
else:
    query_prompt = ChatPromptTemplate.from_messages([
        ("system", prompts["system_template"]),
        ("user", "Question: {input}")
    ])

def write_query(state: State):
    try:
        if llm_type == "ollama":
            prompt = query_prompt.invoke({
                "top_k": 10,
                "table_info": db.get_table_info(),
                "input": state["question"],
            })
        else:
            prompt = query_prompt.invoke({
                "dialect": "PostgreSQL",
                "top_k": 10,
                "table_info": db.get_table_info(),
                "input": state["question"],
            })
        
        response = llm.invoke(prompt)
        query = response.content.strip()
        
        if "```sql" in query:
            query = query.split("```sql")[1].split("```")[0].strip()
        elif "```" in query:
            query = query.split("```")[1].strip()
        
        if llm_type == "ollama":
            prefixes_to_remove = ["Query:", "SQL:", "Answer:"]
            for prefix in prefixes_to_remove:
                if query.startswith(prefix):
                    query = query[len(prefix):].strip()
        
        return {"query": query}
        
    except Exception as e:
        return {"query": "SELECT 1 as error"}

def execute_query(state: State):
    try:
        tool = QuerySQLDatabaseTool(db=db)
        result = tool.invoke(state["query"])
        return {"result": str(result)}
        
    except Exception as e:
        return {"result": f"Error executing query: {str(e)}"}

def generate_answer(state: State):
    try:
        prompt_text = prompts["answer_template"].format(
            question=state["question"],
            query=state["query"],
            result=state["result"]
        )
        
        if llm_type == "ollama":
            response = llm.invoke(prompt_text)
        else:
            response = llm.invoke(HumanMessage(content=prompt_text))
        
        answer = response.content
        return {"answer": answer}
        
    except Exception as e:
        return {"answer": f"Sorry, I encountered an error: {str(e)}"}

try:
    graph = StateGraph(State).add_sequence([write_query, execute_query, generate_answer])
    graph_builder = graph.add_edge(START, "write_query").compile()
except Exception as e:
    print(f"Error building graph: {e}")
    exit(1)

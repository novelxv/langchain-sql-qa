import os
from dotenv import load_dotenv

load_dotenv()

def main():
    print("SQL Q&A System")
    print("=" * 30)
    
    try:
        from chain import graph_builder, llm_type
        
        print(f"Using LLM: {llm_type.upper()}")
        print("Type 'exit' to quit")
        
        while True:
            try:
                question = input("\nYour question: ")
                if question.strip().lower() in ['exit', 'quit', 'q']:
                    break
                
                if not question.strip():
                    print("Please enter a question.")
                    continue
                
                print("Processing...")
                
                final_answer = None
                for step in graph_builder.stream({"question": question}, stream_mode="updates"):
                    for node_name, node_output in step.items():
                        if node_name == "generate_answer" and "answer" in node_output:
                            final_answer = node_output["answer"]
                
                if final_answer:
                    print(f"\nAnswer: {final_answer}")
                else:
                    print("Could not generate an answer.")
                    
            except KeyboardInterrupt:
                print("\nGoodbye!")
                break
            except Exception as e:
                print(f"Error processing question: {e}")
                continue
        
        print("Goodbye!")
        
    except Exception as e:
        print(f"Failed to start system: {e}")

if __name__ == "__main__":
    main()

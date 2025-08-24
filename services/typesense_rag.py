import os
import json
import typesense
import google.generativeai as genai

class TypesenseRAG:
    def __init__(self):
        """
        Initializes the Typesense client using environment variables.
        """
        try:
            self.client = typesense.Client({
                'nodes': [{
                    'host': os.getenv('TYPESENSE_HOST'),
                    'port': os.getenv('TYPESENSE_PORT'),
                    'protocol': 'https'
                }],
                'api_key': os.getenv('TYPESENSE_API_KEY'),
                'connection_timeout_seconds': 2
            })
            print("Typesense client initialized successfully.")
        except Exception as e:
            print(f"Error initializing Typesense client: {e}")
            self.client = None
            
    def get_rag_response(self, query):
        """
        Performs a conversational search on Typesense to generate a response.
        The search uses a knowledge base to augment the Gemini model's reply.
        """
        if not self.client:
            return "Knowledge base service is unavailable. Please try again later."
        
        try:
            # Step 1: Search the Typesense collection for relevant information
            # This is a conceptual example. A real RAG application would need a schema
            # that includes the legal case data.
            search_params = {
                'q': query,
                'query_by': 'caseSummaryText,facts,issues,legalAnalysis',
                'limit': 1,
            }
            search_results = self.client.collections['ibcCasesTypesense'].documents.search(search_params)
            
            if not search_results['hits']:
                print("No relevant documents found in Typesense.")
                return None

            relevant_document = search_results['hits'][0]['document']
            
            # Step 2: Formulate a new prompt for the LLM with the retrieved context
            context = json.dumps(relevant_document, indent=2)
            
            rag_prompt = (
                "You are an AI assistant for legal professionals. A user has a question about a case and you found the following "
                "information in your knowledge base. Please provide a clear and concise summary of the case, focusing on the key facts, "
                "issues, and legal analysis. Do not include any information that is not in the provided context. "
                "\n\nUser's Original Query:\n---\n"
                f"User asked: {query}"
                "\n---\n"
                f"Knowledge Base Content:\n---\n{context}\n---"
            )
            
            # Use the Gemini model to generate a final response
            model = genai.GenerativeModel('gemini-1.5-pro')
            rag_response = model.generate_content(rag_prompt, stream=False)
            
            return rag_response.text

        except Exception as e:
            print(f"An error occurred during conversational RAG: {e}")
            return "I'm sorry, I was unable to retrieve a detailed answer at this time. Our team has been notified."

#!/usr/bin/env python3
#
#  Copyright 2024 The InfiniFlow Authors. All Rights Reserved.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#
"""
Environment-Based OpenAI Key Tracking Example

This example demonstrates how to use RAGFlow's environment-based OpenAI key tracking
to automatically use different API keys based on the environment (dev, staging, prod).
"""

from ragflow_sdk import RAGFlow


def example_environment_usage():
    """Demonstrate environment-based key tracking usage."""
    
    # Initialize RAGFlow client
    ragflow = RAGFlow("your-api-key", "http://localhost:9380")
    
    print("=== Environment-Based OpenAI Key Tracking Example ===\n")
    
    # Example 1: Development Environment
    print("1. Setting environment to 'dev'")
    ragflow.set_environment("dev")
    print(f"   Current environment: {ragflow.environment}")
    
    # All subsequent API calls will include X-Environment: dev header
    # Backend will use dev OpenAI API key for OpenAI models
    try:
        dataset = ragflow.create_dataset(
            name="dev-test-dataset",
            description="Test dataset using dev OpenAI keys",
            embedding_model="text-embedding-3-small@OpenAI"  # Will use dev keys
        )
        print(f"   Created dataset: {dataset.name}")
    except Exception as e:
        print(f"   Dataset creation failed (expected if not configured): {e}")
    
    print()
    
    # Example 2: Staging Environment
    print("2. Setting environment to 'staging'")
    ragflow.set_environment("staging")
    print(f"   Current environment: {ragflow.environment}")
    
    # Now uses staging OpenAI API key
    try:
        chat = ragflow.create_chat(
            name="staging-chat",
            dataset_ids=[],  # Empty for this example
        )
        print(f"   Created chat: {chat.name}")
    except Exception as e:
        print(f"   Chat creation failed (expected if not configured): {e}")
    
    print()
    
    # Example 3: Production Environment
    print("3. Setting environment to 'prod'")
    ragflow.set_environment("prod")
    print(f"   Current environment: {ragflow.environment}")
    
    # Now uses production OpenAI API key
    try:
        datasets = ragflow.list_datasets(page_size=5)
        print(f"   Listed {len(datasets)} datasets using prod environment")
    except Exception as e:
        print(f"   Dataset listing failed (expected if not configured): {e}")
    
    print()
    
    # Example 4: Kafi Environment
    print("4. Setting environment to 'kafi'")
    ragflow.set_environment("kafi")
    print(f"   Current environment: {ragflow.environment}")
    
    # Now uses kafi OpenAI API key
    try:
        agents = ragflow.list_agents(page_size=3)
        print(f"   Listed {len(agents)} agents using kafi environment")
    except Exception as e:
        print(f"   Agent listing failed (expected if not configured): {e}")
    
    print()
    
    # Example 5: Disable Environment Tracking
    print("5. Disabling environment tracking")
    ragflow.set_environment(None)
    print(f"   Current environment: {ragflow.environment}")
    print("   API calls will now use normal tenant key lookup")
    
    print()
    
    # Example 6: Error Handling for Invalid Environments
    print("6. Testing invalid environment handling")
    try:
        ragflow.set_environment("invalid")
    except ValueError as e:
        print(f"   Caught expected error: {e}")
    
    print()


def example_environment_switching():
    """Demonstrate switching between environments during operation."""
    
    ragflow = RAGFlow("your-api-key", "http://localhost:9380")
    
    print("=== Environment Switching Example ===\n")
    
    environments = ["dev", "staging", "prod", "kafi"]
    
    for env in environments:
        print(f"Switching to {env} environment...")
        ragflow.set_environment(env)
        
        # Example: Create a chat specific to this environment
        try:
            chat = ragflow.create_chat(
                name=f"{env}-environment-chat",
                dataset_ids=[],
            )
            print(f"   Created {env} chat successfully")
            
            # Clean up
            ragflow.delete_chats([chat.id])
            print(f"   Cleaned up {env} chat")
            
        except Exception as e:
            print(f"   Operation failed for {env}: {e}")
        
        print()
    
    # Reset to no environment
    ragflow.set_environment(None)
    print("Reset to default (no environment)")


def example_configuration_info():
    """Display configuration information and setup instructions."""
    
    print("=== Configuration Setup ===\n")
    
    print("1. Server Configuration (docker/service_conf.yaml):")
    print("   environment_openai_keys:")
    print("     dev: 'sk-your-dev-key'")
    print("     staging: 'sk-your-staging-key'")
    print("     prod: 'sk-your-prod-key'")
    print("     kafi: 'sk-your-kafi-key'")
    print()
    
    print("2. Environment Variables (optional):")
    print("   export OPENAI_API_KEY_DEV='sk-your-dev-key'")
    print("   export OPENAI_API_KEY_STAGING='sk-your-staging-key'")
    print("   export OPENAI_API_KEY_PROD='sk-your-prod-key'")
    print("   export OPENAI_API_KEY_KAFI='sk-your-kafi-key'")
    print()
    
    print("3. Usage Flow:")
    print("   - Client calls ragflow.set_environment('dev')")
    print("   - SDK adds X-Environment: dev header to requests")
    print("   - Backend detects environment and OpenAI model usage")
    print("   - Returns environment-specific OpenAI key instead of tenant key")
    print("   - Only affects OpenAI models, others use normal lookup")
    print()
    
    print("4. Key Benefits:")
    print("   - Separate API keys and quotas per environment")
    print("   - Easy environment switching in code")
    print("   - Backward compatible with existing code")
    print("   - Secure fallback to tenant keys")
    print("   - Selective application (only OpenAI models)")
    print()


if __name__ == "__main__":
    print("RAGFlow Environment-Based OpenAI Key Tracking Examples\n")
    
    try:
        example_environment_usage()
        example_environment_switching()
        example_configuration_info()
        
        print("Examples completed successfully!")
        print("\nNote: Some operations may fail if environment keys are not configured.")
        print("This is expected behavior for demonstration purposes.")
        
    except Exception as e:
        print(f"Example execution failed: {e}")
        print("Please ensure RAGFlow server is running and configured properly.")
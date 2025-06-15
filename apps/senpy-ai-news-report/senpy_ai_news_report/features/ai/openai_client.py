import os
import json
import tempfile
import asyncio
from typing import List, Dict, Any
from dotenv import load_dotenv
from openai import AsyncOpenAI

load_dotenv()


def test_debug():
    print("Hellow world")


class AiNewsClient:
    async_client = AsyncOpenAI(
        api_key=os.getenv("OPENAI_API_KEY"),  # This is the default and can be omitted
    )

    async def process_news(self, system_prompt: str, user_prompt: str, data: str, model: str = "gpt-4o-mini"):
        print("process news")
        return await self.async_client.chat.completions.create(
            model=model,
            temperature=0.5,
            messages=[
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": f"{user_prompt}, data: {data}",
                },
            ],
        )
    



    async def process_news_in_batch(self, system_prompt: str, user_prompt: str, data_list: List[Any], model: str = "gpt-4o-mini"):
        """
        Process multiple news items using OpenAI Batch API for cost efficiency.
        
        Args:
            system_prompt: The system prompt for the AI
            user_prompt: The user prompt template
            data_list: List of data items to process
            model: OpenAI model to use
            
        Returns:
            List of processed results
        """
        print(f"Processing {len(data_list)} items in batch")
        
        # Prepare batch requests
        batch_requests = []
        for i, data in enumerate(data_list):
            request = {
                "custom_id": f"request-{i}",
                "method": "POST",
                "url": "/v1/chat/completions",
                "body": {
                    "model": model,
                    "temperature": 0.5,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": f"{user_prompt}, data: {data}"}
                    ]
                }
            }
            batch_requests.append(request)
        
        # Create temporary file for batch input
        with tempfile.NamedTemporaryFile(mode='w', suffix='.jsonl', delete=False) as temp_file:
            for request in batch_requests:
                temp_file.write(json.dumps(request) + '\n')
            temp_file_path = temp_file.name
        
        try:
            # Upload batch input file
            with open(temp_file_path, 'rb') as file:
                batch_input_file = await self.async_client.files.create(
                    file=file,
                    purpose="batch"
                )
            
            # Create batch job
            batch_job = await self.async_client.batches.create(
                input_file_id=batch_input_file.id,
                endpoint="/v1/chat/completions",
                completion_window="24h"
            )
            
            print(f"Batch job created with ID: {batch_job.id}")
            
            # Poll for completion
            while batch_job.status in ["validating", "in_progress", "finalizing"]:
                await asyncio.sleep(2)  # Wait 5 seconds before checking again
                batch_job = await self.async_client.batches.retrieve(batch_job.id)
                print(f"Batch status: {batch_job.status}")
            
            if batch_job.status == "completed":
                # Download results
                result_file_id = batch_job.output_file_id
                if result_file_id:
                    result_content = await self.async_client.files.content(result_file_id)
                    
                    # Parse results
                    results = []
                    for line in result_content.text.strip().split('\n'):
                        if line:
                            result = json.loads(line)
                            results.append(result)
                    
                    # Sort results by custom_id to maintain order
                    results.sort(key=lambda x: int(x['custom_id'].split('-')[1]))
                    
                    # Clean up files
                    await self.async_client.files.delete(batch_input_file.id)
                    await self.async_client.files.delete(result_file_id)
                    
                    return results
                else:
                    print("No output file ID found")
                    return []
            else:
                print(f"Batch job failed with status: {batch_job.status}")
                return []
                
        finally:
            # Clean up temporary file
            os.unlink(temp_file_path)
    
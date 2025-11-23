import asyncio
import argparse
from api_keys import generate_api_key, cache
from fastapi import HTTPException

# Function to generate a new API key
async def generate_key():
    key = await generate_api_key()
    print("New API key:", key)

# Function to show all API keys stored in Redis
async def show_keys():
    keys = await cache.smembers("api_keys_allowed")
    if keys:
        print("Existing API keys:")
        for k in keys:
            print("-", k)
    else:
        print("No API keys found.")

# Function to delete a specific API key from Redis
async def delete_key(key: str):
    removed = await cache.srem("api_keys_allowed", key)
    if removed:
        print(f"Deleted API key: {key}")
    else:
        print(f"API key not found: {key}")

if __name__ == "__main__":
    # Argparse setup for command line options
    parser = argparse.ArgumentParser(description="API Key Management CLI")
    parser.add_argument("--generate", action="store_true", help="Generate a new API key")
    parser.add_argument("--show", action="store_true", help="Show all API keys in Redis")
    parser.add_argument("--delete",  metavar="API_KEY",type=str, help="Delete an API key from Redis")
    args = parser.parse_args()

    async def main():
        if args.generate:
            await generate_key()
        elif args.show:
            await show_keys()
        elif args.delete:
            await delete_key(args.delete)
        else:
            parser.print_help() # Show help if no argument is provided


    # Run the async main function
    asyncio.run(main())

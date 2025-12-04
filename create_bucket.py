import asyncio
from src.backend.utils.supabase_client import supabase
from src.backend.utils.logger import setup_logger

logger = setup_logger(__name__)

async def create_bucket():
    bucket_name = "videos"
    try:
        logger.info(f"Checking if bucket '{bucket_name}' exists...")
        buckets = supabase.storage.list_buckets()
        
        bucket_exists = False
        for bucket in buckets:
            if bucket.name == bucket_name:
                bucket_exists = True
                break
        
        if bucket_exists:
            logger.info(f"Bucket '{bucket_name}' already exists.")
        else:
            logger.info(f"Bucket '{bucket_name}' not found. Creating it...")
            supabase.storage.create_bucket(bucket_name, options={"public": True})
            logger.info(f"Bucket '{bucket_name}' created successfully.")
            
    except Exception as e:
        logger.error(f"Failed to manage bucket: {str(e)}")

if __name__ == "__main__":
    asyncio.run(create_bucket())

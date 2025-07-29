
from openai import OpenAI
from dotenv import load_dotenv
import os
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_AI_KEY"))

PLATFORM_GUIDES = {
    "twitter": "You are a social media content generator, generating a twitter post. The post should be max 280 characters, and be of typical twitter syntax.",
    "instagram": "You are a social media content generator, generating an instagra post. The post is max 2200 characters, and be of typical instagram syntax.",
    "linkedin": "You are a social media content generator, generating a linkedin post. The post is max 3000 characters, and be of typical linkedin syntax.",
    "engagement tips": (
        "You are an expert in social media engagement.\n"
        "Return **exactly four** practical tips for optimising likes, comments and shares, specific to the post given by the user.\n"
        "Respond as a plain text list where each tip is on its own line and starts with '-' (hyphen).\n"
        "No introductory or closing sentence.\n"
        "Maximum 600 characters."
    ),
}

def truncate_for_platforms(text: str, platform: str)-> str:
    limits = {
        "twitter": 280,
        "instagram": 2200,
        "linkedin": 3000,
        "engagement tips": 600,
    }
    return text.strip()[:limits[platform]]


def compose_post(prompt: str, platform: str, tone: str = "default", length: str = "default") -> dict:
    system_msg = PLATFORM_GUIDES.get(platform)
    if not system_msg:
        raise ValueError(f"Invalid platform: {platform}")
    
    response = client.chat.completions.create(
        model = "gpt-4o-mini",
        messages = [
            { "role": "system", "content": system_msg},
            { "role": "user", "content": f"Prompt: {prompt}; make this post in the tone: {tone}, and length: {length}"}
        ],
        temperature = 0.7,
        max_tokens = 1000,
    )
    raw = response.choices[0].message.content
    return {
        "content": truncate_for_platforms(raw, platform),
        "tokens_used": response.usage.total_tokens
    }



from openai import OpenAI
from dotenv import load_dotenv
import os
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_AI_KEY"))

PLATFORM_GUIDES = {
    "twitter": (
        "Write ONE concise tweet (≤240 chars).\n"
        "Plain English, conversational.\n"
        "At most ONE emoji and ONE hashtag, both optional.\n"
        "No list format, no salesy tone."
    ),
    "instagram": (
        "Write an Instagram caption (≤1200 chars).\n"
        "2-3 short sentences, friendly and relatable.\n"
        "Limit to TWO emojis total.\n"
        "Put up to TWO hashtags at the very END.\n"
        "No numbered lists.\n"
    ),
    "linkedin": (
        "Write a LinkedIn post (≤1200 chars).\n"
        "Professional but warm; use short paragraphs.\n"
        "At most ONE emoji.\n"
        "Add up to THREE hashtags at the end, no lists, no clickbait.\n"
    ),

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

